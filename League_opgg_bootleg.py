import json
import os
from datetime import datetime
import requests as r


def write_to_file(file_name, inputdata):
    """Writes all given input data to a file dumped as json"""
    with open(file_name, "a") as f:
        json.dump(inputdata, f)


def pull_user_data(league_name):
    try:
        with open("G:\\api_key.txt") as f:
            api_key = f.read()
    except FileNotFoundError:
        print("No api key file found")
        exit()
    curent_date = datetime.today().strftime("%Y-%m-%d_%H-%M")
    headers = {"Content-Type": "application/json",
               "Application-Type": "application/json", "X-Riot-Token": api_key}
    url = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}".format(
        league_name)
    try:
        user_data = r.get(url=url, headers=headers)
    except Exception:
        return {"status": "something really went wrong"}
    if user_data.status_code == 404:
        return {"status": "user not found"}
    write_to_file("{}'s_UserData_{}.json".format(
        league_name, curent_date), user_data.json())

    try:
        summoner_entries = r.get("https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{}".format(
            user_data.json()["id"]), headers=headers).json()  # end_index, start_index),
    except Exception as e:
        print("failed to pull user data: error: {}".format(e))

    write_to_file("{}'s_SummonerEntries_{}.json".format(
        league_name, curent_date), summoner_entries)

    try:
        match_history = r.get("https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/{}?endIndex=4&beginIndex=1".format(
            user_data.json()["accountId"]), headers=headers).json()
    except Exception as e:
        print("failed to pull user data: error: {}".format(e))

    write_to_file("{}'s_MatchHistory_{}.json".format(
        league_name, curent_date), match_history)

    # List comprehension for getting game ids
    game_ids = [{str(x["gameId"]): x["timestamp"]} for x in match_history["matches"]]

    temp_dict = {}
    for my_dict in game_ids:
        temp_dict.update(my_dict)
    # create file
    with open("{}_MatchIds.json".format(league_name), "w") as f:
        json.dump(temp_dict, f)
    # create directory
    os.makedirs("{}_MatchHistory".format(league_name), exist_ok=True)

    for k, v in temp_dict.items():
        my_files = os.listdir(path="./{}_MatchHistory".format(league_name)) 
        if "{}_MatchInfo.json".format(k) in my_files:
            print("Already have match {}".format(k))
            continue
        print("Getting match {}".format(k))
        try:
            match_info = r.get(
                "https://na1.api.riotgames.com/lol/match/v4/matches/{}".format(k), headers=headers).json()
            write_to_file(
                "./{}_MatchHistory/{}_MatchInfo.json".format(league_name, k), match_info)
            participant_id = [x['participantId'] for x in match_info["participantIdentities"]
                            if x['player']['summonerName'].lower() == league_name.lower()]
            write_to_file("./{}_MatchHistory/{}_PlayerPerformance.json".format(
                league_name, k), match_info['participants'][participant_id[0]-1])
            # time.sleep(2)
        except Exception as e:
            print("failed to pull user data: error: {}".format(e))

    return {"status": 200}

# Json parsing below here
def display_match(match_id=None, league_name=None):
    try:
        with open("./{}_MatchHistory/{}_PlayerPerformance.json".format(league_name, match_id)) as j:
            json_file = json.load(j)
        return json_file
    except FileNotFoundError:
        return {
            "status": {
                "status_code": 404,
                "message": "Data not found"
            }
        }


def return_match_ids(league_name=None):
    try:
        with open("{}_MatchIds.json".format(league_name).lower()) as f:
            match_ids = json.load(f)
        return match_ids
    except FileNotFoundError:
        return {
            "status": {
                "status_code": 404,
                "message": "Data not found"
            }
        }

if __name__ == "__main__":
    print("Press Ctrl + c to exit")
    league_name = input("Enter your league username ")
    pull_user_data(league_name)
    match_id = input("input match id ")
