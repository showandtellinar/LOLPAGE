import os
import json
import time
import urllib
import re
from collections import namedtuple
import logging
<<<<<<< HEAD
from urllib2 import urlopen
=======
import cgi
>>>>>>> 3d8166852d43e94e336f014e39fc2be9414a7116

DANNY_API_KEY = "ed6ffbec-a07d-4e27-8f75-194f7fd44af9"
SLEEP_SECONDS = 1.2
DIRECTORY_SEPERATOR = '/'
RETRY_ERROR_CODES = [429]
GIVE_UP_ERROR_CODES = [400, 401, 404, 500, 503]
MAX_RETRY = 10

Result = namedtuple('Result', 'jsonString gotFromFile')
log = logging.getLogger()
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)


def NormalizeSummonerName(summonerName):
    return cgi.escape(re.sub(r"\s+", "", summonerName.lower()))


def APICallWithRetry(url):
    data = urllib.urlopen(url)
    retry_count = 0
    response_code = data.getcode()
    if response_code in GIVE_UP_ERROR_CODES:
        log.error('Giving up on retrying because of error code: ' + response_code)
        return Result("", False)
    while response_code in RETRY_ERROR_CODES and retry_count < MAX_RETRY:
        log.warn('Error code ' + data.getcode() + ' retrying')
        time.sleep(SLEEP_SECONDS * 2)
        data = urllib.urlopen(url)
        response_code = data.getcode()
        retry_count += 1
    if retry_count == MAX_RETRY:
        log.error('Giving up on retrying')
        return Result("", False)
    return Result(data.read(), True)


def GetSummonerInfo(summonerName, tryGetFromFile=True, onlyGetFromFile=False):
    summoner_file = 'data/summoners/' + NormalizeSummonerName(summonerName) + "/SummonerDetails.json"
    if tryGetFromFile:
        if os.path.exists(summoner_file):
            with open(summoner_file, 'r') as f:
                log.debug("Got summoner data from " + summoner_file)
                return Result(f.read(), True)

    if onlyGetFromFile:
        return Result("", False)

    url = "https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/{}?api_key={}".format(summonerName, DANNY_API_KEY)
    result = APICallWithRetry(url)
    if result[1] == False:
        return result

    try:
        if not os.path.exists(os.path.dirname(summoner_file)):
            os.makedirs(os.path.dirname(summoner_file))
    except:
        return Result("", False)
    summoner = json.loads(result[0])
    with open(summoner_file, 'w') as outfile:
        json.dump(summoner, outfile, sort_keys=True, indent=4)
    log.debug("Just created " + summoner_file)
    return Result(json.dumps(summoner, sort_keys=True, indent=4), False)


def GetMatchHistory(summonerName, tryGetFromFile=True, onlyGetFromFile=False):
    norm_summoner_name = NormalizeSummonerName(summonerName)
    history_file = 'data/summoners/' + norm_summoner_name + "/MatchHistory.json"
    if tryGetFromFile:
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                log.debug("Got history data from " + history_file)
                return Result(f.read(), True)

    if onlyGetFromFile:
        return Result('', False)

    summoner, got_from_file = GetSummonerInfo(norm_summoner_name)
    if not got_from_file:
        time.sleep(SLEEP_SECONDS)
    try:
        summoner_id = json.loads(summoner)[norm_summoner_name]['id']
    except:
        return Result("", False)

    if not os.path.exists(os.path.dirname(history_file)):
        os.makedirs(os.path.dirname(history_file))
    url_template = "https://na.api.pvp.net/api/lol/na/v2.2/matchhistory/{}?beginIndex={}&api_key={}"
    with open(history_file, 'w') as outfile:
        begin_ind = 0
        whole_history = None

        url = url_template.format(summoner_id, begin_ind, DANNY_API_KEY)
        result = APICallWithRetry(url)
        if result[1] == False:
            return result

        history = json.loads(result[0])
        while history.get('matches'):
            if whole_history is None:
                whole_history = history
            else:
                whole_history['matches'].extend(history['matches'])
            log.debug(len(whole_history['matches']))
            time.sleep(SLEEP_SECONDS)
            begin_ind += 15

            result = APICallWithRetry(url_template.format(summoner_id, begin_ind, DANNY_API_KEY))
            if result[1] == False:
                return result

            history = json.loads(result[0])
        if whole_history is not None:
            json.dump(whole_history, outfile, separators=(',',':'))
            return Result(json.dumps(whole_history), False)
    return Result("", False)


def GetMatch(matchId, tryGetFromFile=True):
    match_file = 'data/matches/' + str(matchId) + ".json"
    if not os.path.exists(os.path.dirname(match_file)):
        os.makedirs(os.path.dirname(match_file))
    if tryGetFromFile:
        if os.path.exists(match_file):
            with open(match_file, 'r') as f:
                log.debug("Got match data from " + match_file)
                return Result(f.read(), True)
    url = "https://na.api.pvp.net/api/lol/na/v2.2/match/{}?api_key={}".format(matchId, DANNY_API_KEY)
    result = APICallWithRetry(url)
    if result[1] == False:
        return result

    try:
        match = json.loads(result[0])
    except:
        return Result("", False)
    with open(match_file, 'w') as outfile:
        json.dump(match, outfile, separators=(',',':'))
    log.debug("Just created " + match_file)
    return Result(json.dumps(match, sort_keys=True, indent=4), False)


def GetChampionInfo(tryGetFromFile=True, onlyGetFromFile=False):
    champion_info_file = 'data{0}champions{0}championInfo.json'.format(DIRECTORY_SEPERATOR)
    if tryGetFromFile:
        if os.path.exists(champion_info_file):
            with open(champion_info_file, 'r') as f:
                log.debug("Got champion info from " + champion_info_file)
                return Result(f.read(), True)

    if onlyGetFromFile:
        return Result("", False)

    url = 'https://na.api.pvp.net/api/lol/static-data/na/v1.2/champion?champData=all&api_key={}'.format(DANNY_API_KEY)
    result = APICallWithRetry(url)
    if result[1] == False:
        return result

    try:
        if not os.path.exists(os.path.dirname(champion_info_file)):
            os.makedirs(os.path.dirname(champion_info_file))
    except:
        return Result("", False)
    champion_info = json.loads(result[0])
    with open(champion_info_file, 'w') as outfile:
        json.dump(champion_info, outfile)
    log.debug("Just created " + champion_info_file)
    return Result(result[0], False)


def Crawl(summonerName):
    players_crawled = set()
    players_to_crawl = set()
    players_to_crawl.add(summonerName)
    while len(players_to_crawl) > 0:
        summoner_name = players_to_crawl.pop()
        log.info("Crawling " + summoner_name)
        summoner, got_from_file = GetSummonerInfo(summoner_name)
        if summoner == "":
            continue
        if not got_from_file:
            time.sleep(SLEEP_SECONDS)

        history, got_from_file = GetMatchHistory(summoner_name)
        if history == "":
            continue
        if not got_from_file:
            time.sleep(SLEEP_SECONDS)

        for match_id in [m['matchId'] for m in json.loads(history)['matches']]:
            match, got_from_file = GetMatch(match_id)
            if match == "":
                continue
            if not got_from_file:
                time.sleep(SLEEP_SECONDS)
            try:
                summoner_names = [p['player']['summonerName'] for p in json.loads(match)['participantIdentities']]
            except:
                continue
            for sn in summoner_names:
                if sn not in players_crawled:
                    players_to_crawl.add(sn)
        players_crawled.add(summoner_name)

if __name__ == '__main__':
    print "Add your code here or import this file and create your own using these functions"
<<<<<<< HEAD
    
def getPeoplePlayedWith(summonerName): 
   summoner_history = GetMatchHistory(summonerName)
   listed_gameinfo = json.loads(summoner_history[0])
   
   matchIdList = []
   for i in range(0,len(listed_gameinfo['matches'])): 
       matchIdList.append(listed_gameinfo['matches'][i]['matchId'])
       
   nameList=[]
   for j in range(0,len(matchIdList)): 
       match = json.loads(GetMatch(matchIdList[j])[0])
       for participant_identity in match['participantIdentities']:
          nameList.append(participant_identity['player']['summonerName'])
   counter = collections.Counter(nameList)
   return counter
   
test = urlopen('https://na.api.pvp.net/api/lol/static-data/na/v1.2/champion?locale=en_US&champData=info&api_key=ed6ffbec-a07d-4e27-8f75-194f7fd44af9')
champinfo = json.loads(test.read())
 
def comparePlayers(player1,player2,champ): 
    
    player1history = GetMatchHistory(player1)
    player1matches = json.loads(player1history[0])
    player2history = GetMatchHistory(player2)
    player2matches = json.loads(player2history[0])
    
    champID = champinfo['data'][champ]['id']
    
    p1k = 0
    p1d = 0
    p1a = 0
    p1g = 0
    p2k = 0
    p2d = 0
    p2a = 0
    p2g = 0
    games = 0
    games2 = 0
    #test['matches'][0]['participants'][0]['stats']['assists']
    #test['matches'][0]['participants'][0]['championId']
    
    for i in range(0,len(player1matches['matches'])): 
        if(champID == player1matches['matches'][i]['participants'][0]['championId']): 
            p1k += player1matches['matches'][i]['participants'][0]['stats']['kills']
            p1d += player1matches['matches'][i]['participants'][0]['stats']['deaths']
            p1a += player1matches['matches'][i]['participants'][0]['stats']['assists']
            p1g += player1matches['matches'][i]['participants'][0]['stats']['goldEarned']
            games += 1

    for i in range(0,len(player2matches['matches'])): 
        if(champID == player2matches['matches'][i]['participants'][0]['championId']): 
            p2k += player2matches['matches'][i]['participants'][0]['stats']['kills']
            p2d += player2matches['matches'][i]['participants'][0]['stats']['deaths']
            p2a += player2matches['matches'][i]['participants'][0]['stats']['assists']
            p2g += player2matches['matches'][i]['participants'][0]['stats']['goldEarned']
            games2 +=1
    
    avgp1k = float(p1k) / games
    avgp1d = float(p1d) / games
    avgp1a = float(p1a) / games
    avgp1g = float(p1g) / games
    avgp2k = float(p2k) / games2
    avgp2d = float(p2d) / games2
    avgp2a = float(p2a) / games2
    avgp2g = float(p2g) / games2
    
    output = "Player Name: " +str(player1)+" Average Kills: " +str(avgp1k) + " Average Deaths: " + str(avgp1d) +" Average Assists: " + str(avgp1a) + " Average Gold Earned: " + str(avgp1g)
    output2 = "Player Name: " +str(player2)+" Average Kills: " +str(avgp2k) + " Average Deaths: " + str(avgp2d) +" Average Assists: " + str(avgp2a) + " Average Gold Earned: " + str(avgp2g)
    return output,output2
    
=======
    #Crawl('fastuss')
>>>>>>> 3d8166852d43e94e336f014e39fc2be9414a7116
