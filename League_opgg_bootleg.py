import json
import os
from datetime import datetime
import requests as r
from pymongo import MongoClient
import re
from pprint import pprint
from database import Database


with open("./config/config.json") as file:
    configsettings = json.load(file)
client = MongoClient(f"mongodb://{configsettings['host']}:{configsettings['port']}")
db = client.leagueData
# serverStatusResult=db.command("serverStatus")


def write_to_file(file_name, inputdata):
    """Writes all given input data to a file dumped as json"""
    with open(file_name, "a") as f:
        json.dump(inputdata, f)


def write_to_db(inputdata):
    """creates a object in a mongo database"""
    db.leagueData.insert_one()


def pull_user_data(league_name, update_info):
    client = MongoClient("mongodb://localhost:27017")
    db = client.leagueData
    existing_player_info = db.playerData
    player_in_database = existing_player_info.find_one(
        {'name': re.compile('^' + re.escape(league_name) + '$', re.IGNORECASE)})
    if update_info == False:
        if player_in_database:
            return player_in_database
        # print(player_in_database)
    try:
        api_key = os.environ.get("RIOT_ENV_VAR")
    except FileNotFoundError:
        print("No api key file found")
        exit()
    # current_date = datetime.today().strftime("%Y-%m-%d_%H-%M")
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

    try:
        summoner_entries = r.get("https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{}".format(
            user_data.json()["id"]), headers=headers).json()  # end_index, start_index),
    except Exception as e:
        print("failed to pull user data: error: {}".format(e))

    try:
        match_history = r.get("https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids?start=0&count=20".format(
            user_data.json()["puuid"]), headers=headers).json()
    except Exception as e:
        print("failed to pull user data: error: {}".format(e))

    # game_ids = [{str(x["gameId"]): x["timestamp"]}
    #             for x in match_history["matches"]]

    # temp_dict = {}
    # for my_dict in game_ids:
    #     temp_dict.update(my_dict)

    # json_of_match_ids = return_match_ids(league_name)
    # match_ids = {}
    # for x in game_ids:
    #     match_ids.update(x)
    try:
        for match_id in player_in_database["matchIds"]:
            if match_id not in match_history:
                match_history.append(match_id)
    except:
        pass
    player_info = {

        "name": league_name,
        "userData": [user_data.json(), ],
        "summonerEntries": summoner_entries,
        # "matchHistory": match_history["matches"],
        # "indices": [{
        #     "startIndex": match_history["startIndex"], "endIndex": match_history["endIndex"],
        #     "totalGames": match_history["totalGames"]
        # }],
        "matchIds": match_history

    }
    if update_info == True:
        db.playerData.update_one({'name': re.compile('^' + re.escape(league_name) + '$', re.IGNORECASE)}, {'$set':{
                                 'userData': player_info['userData'], 'summonerEntries': player_info['summonerEntries']}})
        for match_id in player_info['matchIds']:
            db.playerData.update_one({'name': re.compile('^' + re.escape(league_name) + '$', re.IGNORECASE)}, {'$addToSet': {'matchIds': match_id}})
    else:
        db.playerData.insert_one(player_info)
    client.close()
    return player_info


def display_match(match_id=None, league_name=None):
    try:
        api_key = os.environ.get("RIOT_ENV_VAR")
    except FileNotFoundError:
        print("No api key file found")
        exit()
    headers = {"Content-Type": "application/json",
               "Application-Type": "application/json", "X-Riot-Token": api_key}
    
    existing_match_info = db.matchData.find_one({"_id" : match_id})
    if existing_match_info:
        return existing_match_info
    else:
        try:
            match_display = r.get("https://americas.api.riotgames.com/lol/match/v5/matches/{}".format(
                match_id), headers=headers).json()
        except Exception as e:
            print("failed to pull match data: error: {}".format(e))
        match_display["_id"] = match_id
        db.matchData.insert_one(match_display)
        existing_match_info = db.matchData.find_one({"_id": match_id})
    if existing_match_info:
        return existing_match_info
    
def get_item_info(match_id):
    existing_match_info = db.matchData.find_one({"_id": match_id})
    item_info = {}
    # for player in existing_match_info["info"]["participants"]:
    #     for item_index in range(7):
            # "/static/12.5.1/data/en_US/item.json"
            # player[f"item{item_index}"]
            
            


def return_match_ids(league_name=None):
    pass


if __name__ == "__main__":
    league_name = input("Enter your league username ")

    existing_player_info = db.playerData
    player_in_database = existing_player_info.find_one(
        {'name': re.compile('^' + re.escape(league_name) + '$', re.IGNORECASE)})

    if player_in_database is None:
        print("Info Not in database")
        pud = pull_user_data(league_name)


# db.playerData.update_one({'_id}, {player_})
#
    # match_id = input("input match id ")


#this comment is for testing
