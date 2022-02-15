from curses import resizeterm
from http.client import OK
import json
import os
import re
from decorators import requires_user
from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)

from pymongo import MongoClient
import League_opgg_bootleg as lob
import user
from user import User
from database import Database
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
    reg_compile = re.compile(".*dragontail-.*")
    directories = os.listdir()
    results = list(filter(reg_compile.match, directories))
    if f"dragontail-{r.json()[0]}" not in results:
        urllib.request.urlretrieve(f"https://ddragon.leagueoflegends.com/cdn/dragontail-{r.json()[0]}.tgz", f"dragontail-{r.json()[0]}.tgz")
        temp_tar = tarfile.open(f"dragontail-{r.json()[0]}.tgz")
        os.mkdir(f"dragontail-{r.json()[0]}")
        temp_tar.extractall(f"dragontail-{r.json()[0]}")
        temp_tar.close()
        os.remove(f"dragontail-{r.json()[0]}.tgz")


@app.route("/")
def home_page():
    return render_template("index.html")


@app.route('/validuser', methods=['GET', 'POST'])
def index():
    name = request.form["username"]
    User.login(name)
    return redirect("/matchlist")
    # return render_template('index.html')


@app.route("/matchlist", methods=["GET"])
def matchlist():
    player_info = league_app(session["name"])
    try:
        del player_info["_id"]
    except:
        pass
    session['matches'] = player_info['matchIds']
    return render_template("match_list.html", player_info=player_info, name=session["name"])


@app.route("/matchlist/updated", methods=['GET'])
def update_matchlist():
    player_info = league_app(session["name"], True)
    return render_template("match_list.html", player_info=player_info, name=session["name"])

# @app.route('/match', methods=['GET', 'POST'])
# def match():
#     match_form = MatchForm()
#     if match_form.validate_on_submit():
#         session['selected_match'] = match_form.match_id.data
#         return redirect('/match/{}'.format(session['selected_match']))
#     matches=session.get('matches')
#     return render_template('match_list.html', form=match_form, matches=session["matches"])


@app.route('/match/<matchid>', methods=['GET', 'POST'])
@requires_user
def selected_match(matchid):
    player_info = league_app(session["name"])
    del player_info["_id"]
    match = lob.display_match(matchid)
    return render_template("match_display.html", match_data=match, player_info=player_info, name=session["name"], mydate=datetime)


def league_app(name, update_info=False):
    var = lob.pull_user_data(name, update_info)
    # print(var)
    return var
