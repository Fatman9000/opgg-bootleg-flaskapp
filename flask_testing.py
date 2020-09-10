import json

from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

import League_opgg_bootleg as lob

app = Flask(__name__)

app.config['SECRET_KEY'] = 'smash like now'

bootstrap = Bootstrap(app)
moment = Moment(app)



class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class MatchForm(FlaskForm):
    match_id = StringField('What match do you want to view', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    session['name'] = ''
    if form.validate_on_submit():
        session['name'] = form.name.data
        print(form.name.data)
        session['matches'] = league_app(form.name.data)['matchIds']
        return redirect("/match")
    return render_template('index.html', form=form, name=session.get('name'))


@app.route('/match', methods=['GET', 'POST'])
def match():
    match_form = MatchForm()
    if match_form.validate_on_submit():
        session['selected_match'] = match_form.match_id.data
        return redirect('/match/{}'.format(session['selected_match']))
    matches=session.get('matches')
    return render_template('match_list.html', form=match_form, matches=session["matches"])



@app.route('/match/<id>', methods=['GET', 'POST'])
def selected_match(id):
    # match_form = MatchForm()
    match_info = lob.display_match(id, session['name'])
    return match_info


def league_app(name):
    var = lob.pull_user_data(name)
    # print(var)
    return var
