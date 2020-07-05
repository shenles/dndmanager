from flask import request, render_template, flash, redirect, url_for
from werkzeug.urls import url_parse
from app import app, db, cache
from flask_login import login_required
from app.forms import LoginForm, RegistrationForm 
from flask_login import current_user, login_user, logout_user
from app.models import User, Character
import requests
import json

@app.route('/')
@app.route('/index')
@login_required
def index():
    if not current_user:    
        return render_template('index.html', title='Home')
    characters = Character.query.filter_by(user_id=current_user.id)
    return render_template('index.html', title='Home', characters=characters)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dndclasses')
@login_required
@cache.cached(timeout=300)
def dndclasses():
    url = 'https://www.dnd5eapi.co/api/classes'
    r = requests.get(url).content
    rj = json.loads(r) # json to python dict 
    allclassesinfo = {}
    for item in rj["results"]:
        currclassinfo = [] 
        currname = item["name"] # e.g. "Bard"
        currurl = 'https://www.dnd5eapi.co' + item["url"] # e.g. "/api/classes/bard" 
        curr_r = requests.get(currurl).content 
        curr_rj = json.loads(curr_r)
        currhitdie = curr_rj["hit_die"]
        currsaves = [savingthrow["name"] for savingthrow in curr_rj["saving_throws"]] # e.g. ["DEX", "CHA"] 
        currprofs = [armorweapon["name"] for armorweapon in curr_rj["proficiencies"]]
        currclassinfo.append(currhitdie)
        currclassinfo.append(currsaves)
        currclassinfo.append(currprofs) 
        allclassesinfo[currname] = currclassinfo 
    return render_template('dndclasses.html', title='D&D Classes', allclasses=allclassesinfo)
