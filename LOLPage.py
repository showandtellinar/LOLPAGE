import sys
import os
from flask import Flask, render_template, request, session, redirect
import json
import pandas as pd
import numpy as np
sys.path.append(os.path.realpath('Scraper'))
import Scraper


app = Flask(__name__,)
app.debug = True
app.secret_key = 'slkjflkjl24j5l34j534'

DANNY_API_KEY = "ed6ffbec-a07d-4e27-8f75-194f7fd44af9"

champion_recommendation_info = None
champion_info = None


@app.route("/", methods=["GET"])
def MainPage():
    return render_template("index.html")


@app.route('/RecentGameStats', methods=['GET'])
def recentGameStats():
    if 'summoner_name' not in session:
        print 'redirecting'
        return redirect('/')

    return render_template('recentGameStats.html')


@app.route('/ChampionRecommend', methods=['GET'])
def championRecommend():
    return render_template('championRecommender.html')


@app.route("/SetSessionSummoner", methods=['POST'])
def setSessionSummoner():
    summoner_name = request.form['summonerName']
    summoner_result = Scraper.GetSummonerInfo(summoner_name, onlyGetFromFile=True)
    if summoner_result.jsonString != '':
        session['summoner_name'] = summoner_name
        session['summoner_info'] = json.loads(summoner_result.jsonString)
        message = 'Found cached data for ' + summoner_name
    else:
        session.pop('summoner_name')
        session.pop('summoner_info')
        message = 'Could not find cached data for ' + summoner_name + ', try another name'
    return message


@app.route("/ShowMatchHistory", methods=['GET'])
def ShowMatchHistory():
    return render_template("matchHistory.html")


@app.route("/GetMatchHistory", methods=['GET'])
def getMatchHistory():
    history = Scraper.GetMatchHistory(session['summoner_name'], onlyGetFromFile=True)
    return history.jsonString


@app.route("/getChampionNames", methods=['GET'])
def getChampionNames():
    champion_info = json.loads(Scraper.GetChampionInfo().jsonString)
    keys = champion_info['keys']
    names = keys.values()
    return json.dumps(sorted(names))


@app.route("/getChampionRecommendations", methods=['GET'])
def getChampionRecommendations():
    champion_name = request.args['champion_name']
    champion_id = -1
    for k in champion_info['keys'].keys():
        if champion_info['keys'][k] == champion_name:
            champion_id = int(k)
            break

    other_good_champs = []
    for summoner_name in champion_recommendation_info:
        if champion_id in champion_recommendation_info[summoner_name]:
            if champion_recommendation_info[summoner_name][champion_id][2] <= 1:
                continue
            for champion in champion_recommendation_info[summoner_name]:
                if champion == champion_id:
                    continue
                if champion_recommendation_info[summoner_name][champion][2] > 1:
                    champion_name = champion_info['keys'][str(champion)]
                    other_good_champs.append([champion_name, champion_recommendation_info[summoner_name][champion]])
    df = pd.DataFrame(columns=['champion', 'kills', 'deaths', 'ratio', 'games', 'wins'])
    for ogc in other_good_champs:
        df = df.append({'champion':ogc[0], 'kills':ogc[1][0], 'deaths':ogc[1][1], 'ratio':ogc[1][2], 'games':ogc[1][3], 'wins':ogc[1][4]}, ignore_index=True)

    if len(df.index) == 0:
        print 'Empty dataframe, probably a bad champion id'
        return '{}'
    else:
        grouped = df.groupby("champion").mean().sort('ratio', ascending=False)
        grouped['rank'] = grouped['ratio'] * np.sqrt(grouped['games'])
        print grouped.sort('rank', ascending=False).head()

    return grouped.sort('rank', ascending=False).head().to_json(orient='index')


def loadAllHistory():
    print "Reading in cached data..."

    global champion_info
    champion_info = json.loads(Scraper.GetChampionInfo().jsonString)
    global champion_recommendation_info
    champion_recommendation_info = {}

    with open('data{0}champions{0}all_history.json'.format(Scraper.DIRECTORY_SEPERATOR), 'r') as f:
        all_history = json.loads(f.read())

    for history in all_history:
        participant_identity = history['matches'][0]['participantIdentities'][0]
        summoner_name = participant_identity['player']['summonerName']
        champion_history = {}  # 0:kills,1:deaths,2:ratio,3:games,4:wins

        for match in history['matches']:
            participant = match['participants'][0]
            champion_id = participant['championId']
            win = participant['stats']['winner']
            kills = float(participant['stats']['kills'])
            deaths = float(participant['stats']['deaths'])
            if champion_id in champion_history:
                old = champion_history[champion_id]
                champion_history[champion_id] = (old[0] + kills, old[1] + deaths, (old[0] + kills) / (old[1] + deaths + 1),
                                                 old[3] + 1, old[4] + (1 if win else 0))
            else:
                champion_history[champion_id] = (kills, deaths, kills / (deaths + 1), 1, (1 if win else 0))

        champion_recommendation_info[summoner_name] = champion_history

    print "... finished reading"


import os
if __name__ == "__main__":
	port = int(os.environ.get('PORT', 33507))
	loadAllHistory()
	app.run(host="0.0.0.0", port=port)
