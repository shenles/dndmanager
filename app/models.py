from app import login
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    characters = db.relationship('Character', backref='player', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    type = db.Column(db.String(12)) # pc or npc 
    race = db.Column(db.String(64))
    dndclass = db.Column(db.String(64))
    level = db.Column(db.Integer)
    alignment = db.Column(db.String(64))
    background = db.Column(db.String(64))
    backstory = db.Column(db.String(7200))
    xp = db.Column(db.Integer)
    profbonus = db.Column(db.Integer)
    ac = db.Column(db.Integer)
    initiative = db.Column(db.Integer)
    speed = db.Column(db.Integer)
    hpmax = db.Column(db.Integer)
    abilityscores = db.Column(db.String(320)) # store scores/modifiers as dictionaries
    abilitymods = db.Column(db.String(320))
    savemods = db.Column(db.String(320))
    skillmods = db.Column(db.String(320))  
    hitdice = db.Column(db.String(12)) 
    darkvision = db.Column(db.String(12)) 
    languages = db.Column(db.String(640))
    magicschool = db.Column(db.String(64))
    spellability = db.Column(db.String(64))
    spellsavedc = db.Column(db.Integer)
    spellatkbonus = db.Column(db.Integer) 
    spellsknown = db.Column(db.String(6400))
    spellslots = db.Column(db.String(640))
    weaponsowned = db.Column(db.String(6400)) 
    armorowned = db.Column(db.String(6400))
    equipmentowned = db.Column(db.String(6400))
    features = db.Column(db.String(6400)) 
    miscinventory = db.Column(db.String(9600))
    money = db.Column(db.String(240))
    friends = db.Column(db.String(6400))
    enemies = db.Column(db.String(6400))
    acquaintances = db.Column(db.String(6400))
    campaignnotes = db.Column(db.String(9600))
    miscnotes = db.Column(db.String(9600)) 
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Character {}>'.format(self.name)

class Dndclass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    hitdie = db.Column(db.Integer)
    saveprofs = db.Column(db.String(64)) 
    armweapprofs = db.Column(db.String(800))
    profchoices = db.Column(db.String(3200))
    subclasses = db.Column(db.String(320)) 
    startequip = db.Column(db.String(120)) # e.g. "/api/starting-equipment/2" 
    spellcastclass = db.Column(db.String(64))
    pageurl = db.Column(db.String(120)) # e.g. "/api/classes/wizard" 

    def __repr__(self):
        return '<Dndclass {}>'.format(self.name)

class Dndspell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)

    def __repr__(self):
        return '<Dndspell {}>'.format(self.name)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
