import json

from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)

from pymongo import MongoClient
import League_opgg_bootleg as lob
import user
from user import User
from database import Database


app = Flask(__name__)

app.config['SECRET_KEY'] = 'smash like now'


# @app.before_first_request
# def initialize_database():
#     Database.initialize()

# class NameForm(FlaskForm):
#     name = StringField('What is your name?', validators=[DataRequired()])
#     submit = SubmitField('Submit')


# class MatchForm(FlaskForm):
#     match_id = StringField('What match do you want to view', validators=[DataRequired()])
#     submit = SubmitField('Submit')

@app.route("/")
def home_page():
    return render_template("index.html")

@app.route('/validuser', methods=['GET', 'POST'])
def index():
    name = request.form["name"]
    User.login(name)
    # if User.login_valid(name):
    player_data = league_app(name)

    session['matches'] = player_data['matchIds']
    print(player_data)
    return render_template("match_list.html", matches=player_data)
    # return render_template('index.html')


# @app.route('/match', methods=['GET', 'POST'])
# def match():
#     match_form = MatchForm()
#     if match_form.validate_on_submit():
#         session['selected_match'] = match_form.match_id.data
#         return redirect('/match/{}'.format(session['selected_match']))
#     matches=session.get('matches')
#     return render_template('match_list.html', form=match_form, matches=session["matches"])



@app.route('/match/<matchid>', methods=['GET', 'POST'])
def selected_match(matchid):

    player_info = league_app(session["name"])
    # print(player_info)
    match = [x for x in player_info["matchHistory"] if x["gameId"] == int(matchid)]
    return match[0]


def league_app(name):
    var = lob.pull_user_data(name)
    # print(var)
    return var
