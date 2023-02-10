from pymongo import MongoClient
from pprint import pprint

client = MongoClient("mongodb://localhost:27017")
db = client.leagueData


summonerEntries = db.playerData.find_one(
    {"name": "Fatman9000"}, {"summonerEntries": 1}
)["summonerEntries"][0]

print(summonerEntries["tier"] + summonerEntries["rank"])
