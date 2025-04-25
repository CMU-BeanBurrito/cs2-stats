import requests
from pprint import pprint
import json

"""
series json
{
    series ID: Match Key (G4, S2M1, etc.)

    maps: []
}
"""
"""
map json
{
    team A: {name: ..., score: ..., players: []}
    team B: {name: ..., score: ..., players: []}
}
"""
"""
player json
{
    name: faceit IGN
    kills:
    deaths:
    ADR:
    multikills (3+):
    clutches:
    first kills:
    first deaths:
    trade kills:
    traded deaths:
}
"""
"""
"""

map = {}
map["de_ancient"] = "Ancient"
map["de_anubis"] = "Anubis"
map["de_dust2"] = "Dust2"
map["de_inferno"] = "Inferno"
map["de_mirage"] = "Mirage"
map["de_nuke"] = "Nuke"
map["de_train"] = "Train"

# match name : leetify game ID
matchbank = {
    # "G1" : {"phase" : "Group Stage", "leetify" : "6ea9ed88-c09b-4763-9580-e7e3043b9a1c/"},
    # "G3" : {"phase" : "Group Stage", "leetify" : "deac3665-aaa1-4ae8-ad26-ab0069020839/"},
    # "G5" : {"phase" : "Group Stage", "leetify" : "d1c7ea66-6537-472e-8773-5c5a99eb07fe/"},
    # "G6" : {"phase" : "Group Stage", "leetify" : "6fe9a159-7801-4280-b6a8-de33b900ce88/"},
    # "G8" : {"phase" : "Group Stage", "leetify" : "97f11848-b013-45a0-ab9a-8b691d877f37/"},
    # "G9" : {"phase" : "Group Stage", "leetify" : "be507a3e-2a8b-45fd-b362-5a61e82d4b4f/"}
}

# team name : players
teambank = {
    "4TH PLACE" : ['Tylenol553', 'DuckWings', 'neetsk', 'Consolo28', 'fan_'],
    "NO H1BHWEE" : ['izmattk', 'PENTAKIM', 'RickieC', 'Kiri7989', 'PehPehYe'],
    "brothaPEEKv2" : ['H4pless', 'Sambo412', 'HumChip', 'owoboros1442', 'CsCN2'],
    "Three-Fifths Compromise" : ['han', 'BobaDoba_', 'Arcus144', 'haiwei', 'notKARLx'],
    "PMA: Pure Mass Autism" : ['vqle', 'TheDon--', "HouR_", "ChimpSZN", "Demon10X"]
}

# destination for json and csv files
location = ""

for match in matchbank:
    url = "https://api.leetify.com/api/games/" + matchbank[match]['leetify']
    openers = url + "opening-duels/"
    clutches = url + "clutches/"

    # collect all data
    response = requests.get(url)
    opener_response = requests.get(openers)
    clutch_response = requests.get(clutches)

    # combine all data into 1 json
    jsonfilename = location + match + ".json"
    open(jsonfilename, 'w').close()
    jsonfile = open(jsonfilename, 'a')
    data = response.json()
    data['openerEvents'] = opener_response.json()
    data['clutchEvents'] = clutch_response.json()
    jsonfile.write(json.dumps(data, indent = 4))

    csvfilename = location + match + ".csv"
    open(csvfilename, 'w').close()
    csvfile = open(csvfilename, 'a')

    # Construct game header
    team1name = ''
    team2name = ''
    team1score = -1
    team2score = -1
    for player in data['playerStats']:
        for team in teambank:
            if player['name'] in teambank[team]:
                if team1name == '':
                    team1name = team
                    team1score = player['tRoundsWon'] + player['ctRoundsWon']
                    break
                elif team2name == '' and team != team1name:
                    team2name = team
                    team2score =  player['tRoundsWon'] + player['ctRoundsWon']
                    break
        if team1name != '' and team2name != '': # found both teams and the score
            break

    team1win = '1' if team1score > team2score else '0'
    team2win = '1' if team1win == '0' else '0'        
    
    csvfile.write(team1name + ',,' + team1win + ',,,' + map[data["mapName"]] + ',' + str(team1score) + ',,,,,,,,,,,' + str(team1score+team2score) + "\n")
    csvfile.write(team2name + ',,' + team2win + ',,,,' + str(team2score))
    
    csvfile.write("\n\n")

    # team1 stats, order players by kills
    csvfile.write(team1name + ',Kills,Deaths,ADR,Multikills,Clutches,Opening Kills,Opening Deaths,Trade Kills,Traded Deaths\n')
    team1stats = []
    for player in data['playerStats']:
        if player['name'] in teambank[team1name]:
            playerStats = {}
            playerStats[player['name']]= []
            playerStats[player['name']].append(player['totalKills'])
            playerStats[player['name']].append(player['totalDeaths'])
            playerStats[player['name']].append(round(player['totalDamage']/(team1score+team2score), 1))
            playerStats[player['name']].append(player['multi3k']+player['multi4k']+player['multi5k'])

            clutches = 0
            for clutchEvent in data['clutchEvents']:
                if player['steam64Id'] == clutchEvent['steam64Id'] and clutchEvent['clutchesWon'] == 1:
                    clutches += 1
            playerStats[player['name']].append(clutches)

            opKills = 0
            opDeaths = 0
            for openerEvent in data['openerEvents']:
                if player['name'] == openerEvent['attackerName'] and player['name'] != openerEvent['victimName']:
                    opKills += 1
                elif player['name'] == openerEvent['victimName']:
                    opDeaths += 1

            playerStats[player['name']].append(opKills)
            playerStats[player['name']].append(opDeaths)
            playerStats[player['name']].append(player['tradeKillsSucceeded'])
            playerStats[player['name']].append(player['tradedDeathsSucceeded'])
            team1stats.append(playerStats)

    team1stats = sorted(team1stats, key = lambda d : -1*d[next(iter(d))][0])
    for player in team1stats:
        playername = next(iter(player))
        player = [playername] + player[playername]
        player = ','.join(str(x) for x in player)
        csvfile.write(player)
        csvfile.write('\n')

    csvfile.write('\n')
    
    # team2 stats, order players by kills
    csvfile.write(team2name + ',Kills,Deaths,ADR,Multikills,Clutches,Opening Kills,Opening Deaths,Trade Kills,Traded Deaths\n')
    team2stats = []
    for player in data['playerStats']:
        if player['name'] in teambank[team2name]:
            playerStats = {}
            playerStats[player['name']]= []
            playerStats[player['name']].append(player['totalKills'])
            playerStats[player['name']].append(player['totalDeaths'])
            playerStats[player['name']].append(round(player['totalDamage']/(team1score+team2score), 1))
            playerStats[player['name']].append(player['multi3k']+player['multi4k']+player['multi5k'])

            clutches = 0
            for clutchEvent in data['clutchEvents']:
                if player['steam64Id'] == clutchEvent['steam64Id'] and clutchEvent['clutchesWon'] == 1:
                    clutches += 1
            playerStats[player['name']].append(clutches)

            opKills = 0
            opDeaths = 0
            for openerEvent in data['openerEvents']:
                if player['name'] == openerEvent['attackerName'] and player['name'] != openerEvent['victimName']:
                    opKills += 1
                elif player['name'] == openerEvent['victimName']:
                    opDeaths += 1

            playerStats[player['name']].append(opKills)
            playerStats[player['name']].append(opDeaths)
            playerStats[player['name']].append(player['tradeKillsSucceeded'])
            playerStats[player['name']].append(player['tradedDeathsSucceeded'])
            team2stats.append(playerStats)

    team2stats = sorted(team2stats, key = lambda d : -1*(d[next(iter(d))][0]))
    for player in team2stats:
        playername = next(iter(player))
        player = [playername] + player[playername]
        player = ','.join(str(x) for x in player)
        csvfile.write(player)
        csvfile.write('\n')
    
    csvfile.write("\n")
    csvfile.write("https://leetify.com/app/match-details/" + matchbank[match]["leetify"] + "overview\n")
