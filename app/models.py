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
    name = db.Column(db.String(120), index=True)
    campaign = db.Column(db.String(240), index=True)
    numsessions = db.Column(db.Integer)
    chartype = db.Column(db.String(12)) # pc or npc 
    race = db.Column(db.String(64))
    subrace = db.Column(db.String(64))
    charclass = db.Column(db.String(64))
    level = db.Column(db.Integer)
    alignment = db.Column(db.String(64))
    background = db.Column(db.String(64))
    backstory = db.Column(db.String(7200))
    xp = db.Column(db.Integer)
    profbonus = db.Column(db.Integer)
    ac = db.Column(db.Integer)
    initiative = db.Column(db.Integer)
    speed = db.Column(db.Integer)
    size = db.Column(db.String(20))
    hpmax = db.Column(db.Integer)
    abilityscores = db.Column(db.String(320)) # store scores as dictionaries
    abilitymods = db.Column(db.String(320)) # store modifiers as dictionaries
    savemods = db.Column(db.String(320))
    skillmods = db.Column(db.String(640))  
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
    num_pchoices = db.Column(db.Integer)
    num_pchoices_two = db.Column(db.Integer)
    num_pchoices_three = db.Column(db.Integer)
    profchoices = db.Column(db.String(3200))
    profchoices_two = db.Column(db.String(3200))
    profchoices_three = db.Column(db.String(3200))
    startequip = db.Column(db.String(320))
    subclasses = db.Column(db.String(320))
    classlevels =  db.Column(db.String(320))
    spellcastclass = db.Column(db.String(64))
    pageurl = db.Column(db.String(120)) # e.g. "/api/classes/wizard" 

    def __repr__(self):
        return '<Dndclass {}>'.format(self.name)

'''
class ClassEquip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(120), index=True, unique=True)
    num_choices_one = db.Column(db.Integer)
    num_choices_two = db.Column(db.Integer)
    num_choices_three = db.Column(db.Integer)
    num_choices_four = db.Column(db.Integer)
    choices_one = db.Column(db.String(1000))
    choices_two = db.Column(db.String(1000))
    choices_three = db.Column(db.String(1000))
    choices_four = db.Column(db.String(1000))
    start_equip = db.Column(db.String(600))

    def __repr__(self):
        return '<ClassEquip {}>'.format(self.classname)
'''

class Dndspell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    level = db.Column(db.Integer)    
    school = db.Column(db.String(64))
    casttime = db.Column(db.String(64))
    sprange = db.Column(db.String(64))
    duration = db.Column(db.String(64))
    casters = db.Column(db.String(320)) 
    components = db.Column(db.String(64))
    material = db.Column(db.String(640))
    ritual = db.Column(db.String(12)) 
    concentration = db.Column(db.String(12))
    higherlvl = db.Column(db.String(640))
    description = db.Column(db.String(9600))   

    def __repr__(self):
        return '<Dndspell {}>'.format(self.name)

class SpellLevel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer)

    def __repr__(self):
        return '<SpellLevel {}>'.format(self.level)

class SpellClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)

    def __repr__(self):
        return '<SpellClass {}>'.format(self.name)

class SpellSchool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)

    def __repr__(self):
        return '<SpellSchool {}>'.format(self.name)

class Dndrace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True) 
    speed = db.Column(db.Integer)
    size = db.Column(db.String(32))
    sizedescrip = db.Column(db.String(640))
    age = db.Column(db.String(640))
    abilitybonuses = db.Column(db.String(500)) # e.g. "DEX, CON"
    bonus1 = db.Column(db.Integer)
    bonus2 = db.Column(db.Integer)
    bonus3 = db.Column(db.Integer)
    bonus4 = db.Column(db.Integer)
    bonus5 = db.Column(db.Integer)
    bonus6 = db.Column(db.Integer)
    bonusname1 = db.Column(db.String(60)) # e.g. "DEX"
    bonusname2 = db.Column(db.String(60))
    bonusname3 = db.Column(db.String(60))
    bonusname4 = db.Column(db.String(60))
    bonusname5 = db.Column(db.String(60))
    bonusname6 = db.Column(db.String(60))
    numbonuschoices = db.Column(db.Integer)
    bonusoptions = db.Column(db.String(900))
    startingprofs = db.Column(db.String(800))
    startprofoptions = db.Column(db.String(900))
    numprofchoices = db.Column(db.Integer) 
    numlangchoices = db.Column(db.Integer)
    languages = db.Column(db.String(320))
    langoptions = db.Column(db.String(640))
    langdescrip = db.Column(db.String(640))
    traits = db.Column(db.String(3200))
    traiturls = db.Column(db.String(3200)) # e.g. "/api/traits/fey-ancestry
    traitoptions = db.Column(db.String(900))
    numtraitchoices = db.Column(db.Integer)
    subraces = db.Column(db.String(320))
    subraceurls = db.Column(db.String(900)) # e.g. "/api/subraces/high-elf
    pageurl = db.Column(db.String(120)) # e.g. "/api/races/elf"

    def __repr__(self):
        return '<Dndrace {}>'.format(self.name)

class Dndsubrace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True) 
    race = db.Column(db.String(60))
    description = db.Column(db.String(3200))
    bonus1 = db.Column(db.Integer)
    bonusname1 = db.Column(db.String(60)) # e.g. "DEX"
    startingprofs = db.Column(db.String(1600))
    languages = db.Column(db.String(1600))
    numlangchoices = db.Column(db.Integer)
    langoptions = db.Column(db.String(3200))
    racialtraits = db.Column(db.String(3200))
    numtraitchoices = db.Column(db.Integer)
    traitoptions = db.Column(db.String(3200))

    def __repr__(self):
        return '<Dndsubrace {}>'.format(self.name)

class Dndequipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    cost = db.Column(db.String(32))
    weight = db.Column(db.Integer)
    description = db.Column(db.String(3200))
    properties = db.Column(db.String(3200))
    propertyurls = db.Column(db.String(3200))
    maincategory = db.Column(db.String(120))
    secondcategory = db.Column(db.String(120))
    damagetype = db.Column(db.String(32))
    damagedice = db.Column(db.String(32))
    base_ac = db.Column(db.Integer)     
    dexteritybonus = db.Column(db.String(32)) 
    maximumbonus = db.Column(db.String(32))
    minimumstrength = db.Column(db.Integer)
    disadvantage = db.Column(db.String(32))
    normrange = db.Column(db.Integer)
    longrange = db.Column(db.Integer)

class Dndbackground(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    skillprofs = db.Column(db.String(240))
    toolprofs = db.Column(db.String(240))
    langs = db.Column(db.String(240))
    equipment = db.Column(db.String(800))
    feature = db.Column(db.String(120))
    #feature_descrip = db.Column(db.String(3200))
    variant = db.Column(db.String(120))
    #variant_descrip = db.Column(db.String(3200))
    variant_feature = db.Column(db.String(120))
    #variant_feature_descrip = db.Column(db.String(3200))

class Dndfeature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(240), index=True)
    description = db.Column(db.String(6400))
    numoptions = db.Column(db.Integer)
    choiceoptions = db.Column(db.String(6400))
    fclass = db.Column(db.String(240))
    fsubclass = db.Column(db.String(240))
    level = db.Column(db.Integer)
    fgroup = db.Column(db.String(240))
    prereq = db.Column(db.String(900))

class Dndtrait(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    description = db.Column(db.String(6400))
    races = db.Column(db.String(680))
    subraces = db.Column(db.String(680))
    profs = db.Column(db.String(3200))
    numprofchoices = db.Column(db.Integer)
    profoptions = db.Column(db.String(3200))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
