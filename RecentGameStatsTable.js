var p1Data = null;
var p2Data = null;
var p1Name = null;
var p2Name = null;

function getRecentGamesForName(playerNum){
    //Figure out if this is p1 or p2 and get the summoner name
    var summoner_name = (playerNum == 1) ? document.getElementById("summonerNameForRecentGames").value : document.getElementById("comparerSummonerNameForRecentGames").value;    
    $.getJSON("/GetRecentGamesForName", {summonerName:summoner_name}, function(result){        
        if(playerNum == 1){ p1Name = summoner_name; p1Data = result; }
        else if(playerNum == 2){ p2Name = summoner_name; p2Data = result; }

        //Figure out if we have both sets of data, or just one
        var both_players_entered = (p1Data != null && p2Data != null ? true : false);

        //Create games played count text
        var games_played_text = "";
        var p1_games, p2_games;
        if(p1Data){
            p1_games = p1Data['games'].length;
            games_played_text = '<p class="p1">' + p1Name + ' has played '+ p1_games +' games recently</p>';
        }
        if(p2Data){            
            p2_games = p2Data['games'].length;
            games_played_text = games_played_text + '<p class="p2">' + p2Name + ' has played '+ p2_games +' games recently</p>';            
        }
        
        $('#RecentGameStats').html(games_played_text);

        //Clear chart data except headers
        $('#RecentGameStatsTable tr').slice(1).remove();
        if(both_players_entered){
            $('#RecentGameStatsTable th').slice(1).attr("colspan", "2");

        }
        else{
            $('#RecentGameStatsTable th').slice(1).removeAttr("column-span");
        }

        $('#RecentGameStatsTable th').unbind('click');
        $('#RecentGameStatsTable th').on('click', updateRecentStats);
        var stat_table = $('#RecentGameStatsTable');
        var stat_variables = ['minionsKilled', 'championsKilled', 'numDeaths', 'goldEarned'];
        if(both_players_entered){
            var min_games = Math.min(p1_games, p2_games);
            for (var i = 0; i < min_games; i++) {                
                var row = $('<tr></tr>');
                row.append($('<td></td>').text(i + 1));
                for(var j = 0; j < stat_variables.length; j++){
                    row.append($('<td class=p1></td>').text(p1Data['games'][i]['stats'][stat_variables[j]] || 0));
                    row.append($('<td class=p2></td>').text(p2Data['games'][i]['stats'][stat_variables[j]] || 0));
                }
                stat_table.append(row);
            };
        }
        else if(p1Data){
            for (var i = 0; i < p1_games; i++) {                
                var row = $('<tr></tr>');
                row.append($('<td></td>').text(i + 1));
                for(var j = 0; j < stat_variables.length; j++){
                    var stats = p1Data
                    row.append($('<td class=p1></td>').text(p1Data['games'][i]['stats'][stat_variables[j]] || 0));
                }
                stat_table.append(row);
            };
        }
        else if(p2Data){
            for (var i = 0; i < p2_games; i++) {                
                var row = $('<tr></tr>');
                row.append($('<td></td>').text(i + 1));
                for(var j = 0; j < stat_variables.length; j++){
                    row.append($('<td class=p2></td>').text(p2Data['games'][i]['stats'][stat_variables[j]] || 0));
                }
                stat_table.append(row);
            };
        }

        var summoner_id = (playerNum == 1) ? p1Data['summonerId'] : p2Data['summonerId'];
        //Display match history link
        $('#matchHistoryLink').removeClass('hide')
            .attr('href', "ShowMatchHistory?summonerId=" + summoner_id);

    }).fail(function(a,b,c){alert(c);});
}

function updateRecentStats(){
    var clicked_col = this.innerHTML;        
    var col_index = 0;        
    var table = $('#RecentGameStatsTable');
    var headers = $('#RecentGameStatsTable > tbody > tr > th');
    $.each(headers, function(i, val){
        if(val.innerHTML == clicked_col){
            col_index = i;
        }
    });

    //Return if they click the Game# column
    if(col_index == 0){
        return;
    }
    var comparison_col = col_index * 2 - 1;

    var rows = $('#RecentGameStatsTable > tbody > tr');
    var vals = [];
    var for_grouped_chart = [];
    grouped_header = {'Game':1};
    grouped_header[p1Name] = 1;
    grouped_header[p2Name] = 1;
    for_grouped_chart.push(grouped_header);
    var both_players_entered = (p1Data != null && p2Data != null ? true : false);
    for(i = 1; i < rows.length; i++){
        var row = rows[i];
        var cells = row.cells;
        var game_num = cells[0].innerHTML;
        var val = parseInt(cells[col_index].innerHTML);
        vals.push([game_num, val]);
        if(both_players_entered){
            var obj = {};
            obj['Game'] = i;
            obj[p1Name] = parseInt(cells[comparison_col].innerHTML);
            obj[p2Name] = parseInt(cells[comparison_col+1].innerHTML);
        for_grouped_chart.push(obj);
        }        
    }
    
    if(both_players_entered){
        GroupedBarChart(for_grouped_chart);
    }    
    
    $('.chart').html('');
        var svg = d3.select(".chart"); 
        var chart = SimpleBarChart(
        {
          'parent': svg, 'width' : 600, 'height': 600,
          'labels': [ "Game", clicked_col ],
          'data'  : vals, 'mleft' : 50,
          'mright' : 20, 'mbottom': 60, 'mtop' : 20
        });             
        chart();

}