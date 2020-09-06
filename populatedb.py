from app import app, db
from app.models import Dndclass, Dndspell, Dndrace
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
    for item in rj["results"]:
        currname = item["name"] # e.g. "Acid Arrow"
        currurl = 'https://www.dnd5eapi.co' + item["url"] # e.g. "/api/spells/acid-arrow"
        curr_r = requests.get(currurl).content
        curr_rj = json.loads(curr_r)
        currlvl = curr_rj["level"]
        currschool = curr_rj["school"]["name"] # e.g. "Evocation"
        currcasttime = curr_rj["casting_time"] # e.g. "1 action"
        curr_range = curr_rj["range"] # e.g. "90 feet"
        currduration = curr_rj["duration"] # e.g. "Instantaneous"
        currclasses = [spclass["name"] for spclass in curr_rj["classes"]]
        currclass_str = ", ".join(currclasses) # e.g. "Sorcerer, Wizard" 
        currcomps = ", ".join(curr_rj["components"]) # e.g. "V, S, M" 
        currmat = ""
        if "material" in curr_rj:
            currmat = curr_rj["material"] # e.g. "A sprig of mistletoe." 
        curr_ritual = curr_rj["ritual"]
        currconc = curr_rj["concentration"]
        currhigher = ""
        if "higher_level" in curr_rj:
            currhigher = " ".join(curr_rj["higher_level"]) 
        currdescrip = " ".join(curr_rj["desc"])
        newdndspell = Dndspell(name=currname, level=currlvl, school=currschool, casttime=currcasttime, range=curr_range, duration=currduration, casters=currclass_str, components=currcomps, material=currmat, ritual=curr_ritual, concentration=currconc, higherlvl=currhigher, description=currdescrip)
        db.session.add(newdndspell)
    db.session.commit()

# pull races info from API to populate Dndrace table
def populateRaces():
    url = 'https://www.dnd5eapi.co/api/races'
    r = requests.get(url).content
    rj = json.loads(r)
    for item in rj["results"]:
        currname = item["name"] # e.g. "Human"
        currurl = 'https://www.dnd5eapi.co' + item["url"] # e.g. "/api/races/human"
        curr_r = requests.get(currurl).content
        curr_rj = json.loads(curr_r)
        currspeed = curr_rj["speed"] # e.g. 30
        currabilitybonuses = [x["name"] for x in curr_rj["ability_bonuses"]]  
        currabilitystr = ", ".join(currabilitybonuses)
        currabilstr = ", ".join(currabilitybonuses) 
        bonusoptionlist = []
        bonuschoices = 0
        if "ability_bonus_options" in curr_rj:
            bonusoptionlist = [b["name"] for b in curr_rj["ability_bonus_options"]["from"]]
            bonuschoices = curr_rj["ability_bonus_options"]["choose"] 
        bonusoptionstr = ", ".join(bonusoptionlist)
        currage = curr_rj["age"] # e.g. "Humans reach adulthood in their late teens." 
        currsize = curr_rj["size"]
        currsizedesc = curr_rj["size_description"]
        profnames = []
        if len(curr_rj["starting_proficiencies"]) > 0:
            profnames = [p["name"] for p in curr_rj["starting_proficiencies"]] # e.g. "Handaxes" 
        profnamestr = ", ".join(profnames)
        profoptions = [] 
        profchoices = 0
        if "starting_proficiency_options" in curr_rj:
            profchoices = curr_rj["starting_proficiency_options"]["choose"]
            profoptions = [c["name"] for c in curr_rj["starting_proficiency_options"]["from"]] 
        profoptionstr = ", ".join(profoptions)
        langs = [l["name"] for l in curr_rj["languages"]] 
        langstr = ", ".join(langs)
        langdesc = curr_rj["language_desc"]
        langoptionlist = []
        langchoices = 0
        if "language_options" in curr_rj:
            langchoices = curr_rj["language_options"]["choose"]
            langoptionlist = [l["name"] for l in curr_rj["language_options"]["from"]] 
        langoptionstr = ", ".join(langoptionlist)
        traitlist = [t["name"] for t in curr_rj["traits"]] 
        traiturllist = [t["url"] for t in curr_rj["traits"]]
        traitoptionlist = []
        traitchoices = 0
        if "trait_options" in curr_rj:
            traitchoices = curr_rj["trait_options"]["choose"] 
            traitoptionlist = [t["name"] for t in curr_rj["trait_options"]["from"]] 
        subracelist = [] 
        subraceurllist = []
        if "subraces" in curr_rj:
            subracelist = [s["name"] for s in curr_rj["subraces"]]
            subraceurllist = [s["url"] for s in curr_rj["subraces"]] 
        traitstr = ", ".join(traitlist)
        traiturlstr = ", ".join(traiturllist)
        traitoptionstr = ", ".join(traitoptionlist)
        subracestr = ", ".join(subracelist)
        subraceurlstr = ", ".join(subraceurllist)
        newdndrace = Dndrace(name=currname, pageurl=currurl, speed=currspeed, size=currsize, sizedescrip=currsizedesc, age=currage, abilitybonuses=currabilitystr, bonusoptions=bonusoptionstr, numbonuschoices=bonuschoices, startingprofs=profnamestr, startprofoptions=profoptionstr, numprofchoices=profchoices, languages=langstr, langoptions=langoptionstr, numlangchoices=langchoices, langdescrip=langdesc, traits=traitstr, traiturls=traiturlstr, traitoptions=traitoptionstr, numtraitchoices=traitchoices, subraces=subracestr, subraceurls=subraceurlstr)
        db.session.add(newdndrace) 
    db.session.commit()

#populateClasses() # done already, do not run again 
#populateSpells() # done
#populateRaces() #done
#populateEquipment() #todo