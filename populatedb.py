from app import app, db
from app.models import Dndclass, Dndspell
import requests
import json

# pull class info from API to populate Dndclass table 
def populateClasses():
    url = 'https://www.dnd5eapi.co/api/classes'
    r = requests.get(url).content
    rj = json.loads(r) # json to python dict
    for item in rj["results"]:
        currname = item["name"] # e.g. "Bard"
        currurl = 'https://www.dnd5eapi.co' + item["url"] # e.g. "/api/classes/bard"
        curr_r = requests.get(currurl).content
        curr_rj = json.loads(curr_r)
        currhitdie = curr_rj["hit_die"]
        currsaves = [savingthrow["name"] for savingthrow in curr_rj["saving_throws"]]
        currsavesstr = ", ".join(currsaves)
        currprofs = [armorweapon["name"] for armorweapon in curr_rj["proficiencies"]] 
        currprofsstr = ", ".join(currprofs) 
        currchoices = str(curr_rj["proficiency_choices"])
        currsubclass = str(curr_rj["subclasses"])
        currequip = curr_rj["starting_equipment"]["url"]
        currspellclass = ""
        if "spellcasting" in curr_rj:
            currspellclass = curr_rj["spellcasting"]["class"]
        currpageurl = item["url"]
        newdndclass = Dndclass(name=currname, hitdie=currhitdie, saveprofs=currsavesstr, armweapprofs=currprofsstr, profchoices=currchoices, subclasses=currsubclass, startequip=currequip, spellcastclass=currspellclass, pageurl=currpageurl)
        db.session.add(newdndclass)
    db.session.commit()

# pull spells info from API to populate Dndspell table
def populateSpells():
    url = 'https://www.dnd5eapi.co/api/spells'
    r = requests.get(url).content
    rj = json.loads(r)
    allspellsinfo = {}
    for item in rj["results"]:
        currname = item["name"] # e.g. "Acid Arrow"
        currurl = 'https://www.dnd5eapi.co' + item["url"] # e.g. "/api/spells/acid-arrow"
        curr_r = requests.get(currurl).content
        curr_rj = json.loads(curr_r)
        allspellsinfo[currname] = [curr_rj["level"]]
        allspellsinfo[currname].append(curr_rj["school"]["name"]) # e.g. "Evocation"
        allspellsinfo[currname].append(curr_rj["casting_time"]) # e.g. "1 action"
        allspellsinfo[currname].append(curr_rj["range"]) # e.g. "90 feet"
        allspellsinfo[currname].append(curr_rj["duration"]) # e.g. "Instantaneous"
        currclasses = [spclass["name"] for spclass in curr_rj["classes"]]
        allspellsinfo[currname].append(currclasses)
        allspellsinfo[currname].append(curr_rj["desc"])

#populateClasses() # done already, do not run again 
#populateSpells()
