import os
from decorators import requires_user
from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
import shutil
from pymongo import MongoClient
import League_opgg_bootleg as lob
from datetime import datetime
import requests
import urllib.request
import tarfile


app = Flask(__name__)

app.config['SECRET_KEY'] = 'smash like now'


@app.before_first_request
def check_version():
    url = "https://ddragon.leagueoflegends.com/api/versions.json"
    r = requests.get(url)
    directories = os.listdir("./static/")
    current_version = r.json()[0]
    session["current_version"] = r.json()[0]
    if current_version not in directories:
        urllib.request.urlretrieve(f"https://ddragon.leagueoflegends.com/cdn/dragontail-{current_version}.tgz", f"dragontail-{current_version}.tgz")
        temp_tar = tarfile.open(f"dragontail-{current_version}.tgz")
        for f in directories:
            if f not in ["css", "dragonhead.js", "languages.js", "languages.json"]:
                shutil.rmtree(f"./static/{f}")
        temp_tar.extractall(f"./static", numeric_owner=True)
        temp_tar.close()
        os.remove(f"dragontail-{current_version}.tgz")
        lob.db_patch_data(current_version)

        
@app.route("/")
def home_page():
    return render_template("index.html")


@app.route('/validuser', methods=['GET', 'POST'])
def index():
    name = request.form["username"]
    session["name"] = name
    return redirect("/matchlist")
    # return render_template('index.html')


@app.route("/matchlist", methods=["GET"])
@requires_user
def matchlist():
    player_info = league_app(session["name"])
    try:
        del player_info["_id"]
    except:
        pass
    session['matches'] = player_info['matchIds']
    return render_template("match_list.html", player_info=player_info, name=session["name"], current_version=session["current_version"])


@app.route("/matchlist/updated", methods=['GET'])
@requires_user
def update_matchlist():
    player_info = league_app(session["name"], True)
    return render_template("match_list.html", player_info=player_info, name=session["name"], current_version=session["current_version"])

@app.route('/match/<matchid>', methods=['GET', 'POST'])
@requires_user
def selected_match(matchid):
    player_info = league_app(session["name"])
    del player_info["_id"]
    match = lob.display_match(matchid)
    for x in range(10):
        try:
            del match["info"]["participants"][x]["challenges"]
        except:
            pass
    item_info = lob.get_item_info(matchid)
    rune_info = lob.get_rune_info()
    print()
    return render_template("match_display.html", match_data=match, player_info=player_info, name=session["name"], mydate=datetime,  current_version=session["current_version"], item_info=item_info, rune_info=rune_info)


def league_app(name, update_info=False):
    var = lob.pull_user_data(name, update_info)
    # print(var)
    return var
