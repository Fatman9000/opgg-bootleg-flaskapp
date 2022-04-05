import json
import os
import requests as r
from pymongo import MongoClient
import re


with open("./config/config.json") as file:
    configsettings = json.load(file)
client = MongoClient(
    f"mongodb://{configsettings['host']}:{configsettings['port']}")
db = client.leagueData
# serverStatusResult=db.command("serverStatus")
try:
    api_key = os.environ.get("RIOT_ENV_VAR")
except FileNotFoundError:
    print("No api key file found")
    exit()
# current_date = datetime.today().strftime("%Y-%m-%d_%H-%M")
headers = {"Content-Type": "application/json",
            "Application-Type": "application/json", "X-Riot-Token": api_key}


def pull_user_data(league_name, update_info):
    """
    pull_user_data sets the mongo database client and queries the riot games api
    in order to build and return a dictionary of player information while also updating
    stored info in the playerData collection.
    """
    client = MongoClient("mongodb://localhost:27017")
    db = client.leagueData
    existing_player_info = db.playerData
    player_in_database = existing_player_info.find_one(
        {'name': re.compile('^' + re.escape(league_name) + '$', re.IGNORECASE)})
    
    if update_info == False:
        if player_in_database:
            return player_in_database
        # print(player_in_database)

    user_data = get_summoner(league_name)
    summoner_entries = get_summoner_entries(user_data)
    match_history = get_summoner_history(user_data)

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
        "matchIds": match_history
    }

    if update_info == True:
        update_info(player_info)
    else:
        db.playerData.insert_one(player_info)
    client.close()
    return player_info


def get_summoner(league_name):
    """
    Takes the summoner's name to query the riot games api for basic account info.
    """
    url = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}".format(
        league_name)
    try:
        user_data = r.get(url=url, headers=headers)
    except Exception:
        return {"status": "something really went wrong"}
    if user_data.status_code == 404:
        return {"status": "user not found"}
    return user_data


def get_summoner_entries(user_data):
    """
    Takes the account information returned by get_summoner to query the riot games api for
    the user's, leagueId, summonerId, wins and losses, and rank info.
    """
    try:
        summoner_entries = r.get("https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{}".format(
            user_data.json()["id"]), headers=headers).json()  # end_index, start_index),
    except Exception as e:
        print("failed to pull user data: error: {}".format(e))
    return summoner_entries


def get_summoner_history(user_data):
    try:
        match_history = r.get("https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids?start=0&count=20".format(
            user_data.json()["puuid"]), headers=headers).json()
    except Exception as e:
        print("failed to pull user data: error: {}".format(e))
    return match_history


def update_info(player_info):
    """
    Updates existing player info in the database with provided player info
    """
    db.playerData.update_one({'name': re.compile('^' + re.escape(league_name) + '$', re.IGNORECASE)}, {'$set': {
        'userData': player_info['userData'], 'summonerEntries': player_info['summonerEntries']}})
    for match_id in player_info['matchIds']:
        db.playerData.update_one({'name': re.compile(
            '^' + re.escape(league_name) + '$', re.IGNORECASE)}, {'$addToSet': {'matchIds': match_id}})


def display_match(match_id=None, league_name=None):
    """
    Pulls existing match info for the provided match_id from the database and returns it.
    """
    try:
        api_key = os.environ.get("RIOT_ENV_VAR")
    except FileNotFoundError:
        print("No api key file found")
        exit()
    headers = {"Content-Type": "application/json",
               "Application-Type": "application/json", "X-Riot-Token": api_key}

    existing_match_info = db.matchData.find_one({"_id": match_id})
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


def db_patch_data(patch):
    """
    Updates the database with new information when the games is patched
    """
    db.patchData.delete_many({})
    db.runeData.delete_many({})
    with open(f"./static/{patch}/data/en_US/item.json") as f:
        data = json.load(f)
        db.patchData.insert_one(data)
    with open(f"./static/{patch}/data/en_US/runesReforged.json") as f:
        data = json.load(f)
        db.runeData.insert_many(data)
    with open(f"./static/{patch}/data/en_US/champion.json") as f:
        data = json.load(f)
        db.patchData.insert_one(data)
    with open(f"./static/{patch}/data/en_US/summoner.json") as f:
        data = json.load(f)
        db.patchData.insert_one(data)


def get_item_info(match_id):
    """
    Pulls item info for a given match from the database and returns it
    """
    existing_match_info = db.matchData.find_one({"_id": match_id}, {"info.participants.item0": 1, "info.participants.item1": 1, "info.participants.item2": 1,
                                                "info.participants.item3": 1, "info.participants.item4": 1, "info.participants.item5": 1, "info.participants.item6": 1})
    player_num = 0
    item_info = {}
    for player_items in existing_match_info["info"]["participants"]:

        for item in player_items:
            item_id = existing_match_info["info"]["participants"][player_num][item]
            item_desc = db.patchData.find_one({"type" : "item"}, {f"data.{item_id}.plaintext" : 1, f"data.{item_id}.name" : 1, "_id" : 0})
            
            if item_id != 0 and item_desc['data'][f"{item_id}"]['plaintext'] != '':
                item_info[item_id] = item_desc['data'][f"{item_id}"]['name'], item_desc['data'][f"{item_id}"]['plaintext']
            elif item_id != 0 and item_desc['data'][f"{item_id}"]['name'] != '':
                item_info[item_id] = item_desc['data'][f"{item_id}"]['name'], ''
        player_num+=1  
    return item_info 
    


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


#this comment is for testing
