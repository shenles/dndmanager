from app import app, db
from app.models import Dndclass, Dndspell, Dndrace, Dndsubrace, Dndequipment, SpellLevel, SpellClass, SpellSchool, Dndbackground, Dndfeature, Dndtrait
import requests
import json

# pull class info from API to populate Dndclass table 
def populateClasses():
    url = "https://www.dnd5eapi.co/api/classes"
    r = requests.get(url).content
    rj = json.loads(r) # json to python dict

    for item in rj["results"]:
        currname = item["name"] # e.g. "Bard"
        currurl = "https://www.dnd5eapi.co" + item["url"] # e.g. "/api/classes/bard"
        curr_r = requests.get(currurl).content
        curr_rj = json.loads(curr_r)
        currhitdie = curr_rj["hit_die"]
        currsaves = [savingthrow["name"] for savingthrow in curr_rj["saving_throws"]]
        currsavesstr = ", ".join(currsaves)
        currprofs = [armorweapon["name"] for armorweapon in curr_rj["proficiencies"]] 
        currprofsstr = ", ".join(currprofs) 
        numprof1, numprof2, numprof3 = 0, 0, 0
        prof1, prof2, prof3 = "", "", ""
        # retrieve & parse proficiency selection info for current class
        if "proficiency_choices" in curr_rj:
            profnums = [x["choose"] for x in curr_rj["proficiency_choices"]]
            for i in range(len(profnums)):
                if i + 1 == 1:
                    numprof1 = max(0, profnums[i])
                elif i + 1 == 2:
                    numprof2 = max(0, profnums[i])
                else:
                    numprof3 = max(0, profnums[i])
            counter = 0
            for choice_set in curr_rj["proficiency_choices"]:
                counter += 1
                current_options = choice_set["from"]
                currlist = [op["name"] for op in current_options]
                currstr = ", ". join(currlist)
                if counter == 1:
                    prof1 = currstr
                elif counter == 2:
                    prof2 = currstr
                else:
                    prof3 = currstr               
        
        currsubclass = str(curr_rj["subclasses"])
        currequip = curr_rj["starting_equipment"]
        currclasslevels = curr_rj["class_levels"]
        currspellclass = ""
        if "spellcasting" in curr_rj:
            currspellclass = curr_rj["spellcasting"]
        currpageurl = item["url"]

        newdndclass = Dndclass(name=currname, hitdie=currhitdie, saveprofs=currsavesstr,
            armweapprofs=currprofsstr, num_pchoices=numprof1, num_pchoices_two=numprof2,
            num_pchoices_three=numprof3, profchoices=prof1, profchoices_two=prof2,
            profchoices_three=prof3, subclasses=currsubclass, startequip=currequip,
            classlevels=currclasslevels, spellcastclass=currspellclass, pageurl=currpageurl)
        db.session.add(newdndclass)
    db.session.commit()

# pull spells info from API to populate Dndspell table
def populateSpells():
    url = "https://www.dnd5eapi.co/api/spells"
    r = requests.get(url).content
    rj = json.loads(r)

    for item in rj["results"]:
        currname = item["name"] # e.g. "Acid Arrow"
        currurl = "https://www.dnd5eapi.co" + item["url"] # e.g. "/api/spells/acid-arrow"
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

        newdndspell = Dndspell(name=currname, level=currlvl, school=currschool,
            casttime=currcasttime, sprange=curr_range, duration=currduration,
            casters=currclass_str, components=currcomps, material=currmat,
            ritual=curr_ritual, concentration=currconc, higherlvl=currhigher, description=currdescrip)
        db.session.add(newdndspell)
    db.session.commit()

def populateSpellLevels():
    for currid in range(10):
        spell_level = SpellLevel(id=currid+1, level=currid)
        db.session.add(spell_level)
    db.session.commit()

def populateSpellClasses():
    caster_classes = ["Bard", "Cleric", "Druid", "Paladin", "Sorcerer", "Ranger", "Warlock", "Wizard"]
    for currnum in range(len(caster_classes)):
        spell_class = SpellClass(id=currnum+1, name=caster_classes[currnum])
        db.session.add(spell_class)
    db.session.commit()

def populateSpellSchools():
    magic_schools = ["Abjuration", "Conjuration", "Divination", "Enchantment", "Evocation", "Illusion", "Necromancy", "Transmutation"]
    for currnum in range(len(magic_schools)):
        spell_school = SpellSchool(id=currnum+1, name=magic_schools[currnum])
        db.session.add(spell_school)
    db.session.commit()   

# pull races info from API to populate Dndrace table
def populateRaces():
    url = "https://www.dnd5eapi.co/api/races"
    r = requests.get(url).content
    rj = json.loads(r)

    for item in rj["results"]:
        currname = item["name"] # e.g. "Human"
        currurl = "https://www.dnd5eapi.co" + item["url"] # e.g. "/api/races/human"
        curr_r = requests.get(currurl).content
        curr_rj = json.loads(curr_r)
        currspeed = curr_rj["speed"] # e.g. 30

        currabilitybonuses = [x["name"] for x in curr_rj["ability_bonuses"]]  
        currabilitystr = ", ".join(currabilitybonuses)
        bonus1, bonus2, bonus3, bonus4, bonus5, bonus6 = 0, 0, 0, 0, 0, 0
        bonusname1, bonusname2, bonusname3, bonusname4, bonusname5, bonusname6 = "", "", "", "", "", ""
        bonus1 = curr_rj["ability_bonuses"][0]["bonus"]
        bonusname1 = curr_rj["ability_bonuses"][0]["name"]
        if len(curr_rj["ability_bonuses"]) > 5:
            bonus6 = curr_rj["ability_bonuses"][5]["bonus"]
            bonusname6 = curr_rj["ability_bonuses"][5]["name"]
        if len(curr_rj["ability_bonuses"]) > 4:
            bonus5 = curr_rj["ability_bonuses"][4]["bonus"]
            bonusname5 = curr_rj["ability_bonuses"][4]["name"]
        if len(curr_rj["ability_bonuses"]) > 3:
            bonus4 = curr_rj["ability_bonuses"][3]["bonus"]
            bonusname4 = curr_rj["ability_bonuses"][3]["name"]
        if len(curr_rj["ability_bonuses"]) > 2:
            bonus3 = curr_rj["ability_bonuses"][2]["bonus"]
            bonusname3 = curr_rj["ability_bonuses"][2]["name"]
        if len(curr_rj["ability_bonuses"]) > 1:
            bonus2 = curr_rj["ability_bonuses"][1]["bonus"]
            bonusname2 = curr_rj["ability_bonuses"][1]["name"]       
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

        newdndrace = Dndrace(name=currname, pageurl=currurl, speed=currspeed,
            size=currsize, sizedescrip=currsizedesc, age=currage,
            abilitybonuses=currabilitystr, bonus1=bonus1, bonus2=bonus2, bonus3=bonus3,
            bonus4=bonus4, bonus5=bonus5, bonus6=bonus6, bonusname1=bonusname1, bonusname2=bonusname2,
            bonusname3=bonusname3, bonusname4=bonusname4, bonusname5=bonusname5, bonusname6=bonusname6,
            numbonuschoices=bonuschoices, bonusoptions=bonusoptionstr, startingprofs=profnamestr,
            startprofoptions=profoptionstr, numprofchoices=profchoices,
            languages=langstr, langoptions=langoptionstr, numlangchoices=langchoices,
            langdescrip=langdesc, traits=traitstr, traiturls=traiturlstr,
            traitoptions=traitoptionstr, numtraitchoices=traitchoices,
            subraces=subracestr, subraceurls=subraceurlstr)
        db.session.add(newdndrace) 
    db.session.commit()

# pull info from API to populate Dndsubrace table
def populateSubraces():
    url = "https://www.dnd5eapi.co/api/subraces"
    r = requests.get(url).content
    rj = json.loads(r)

    for item in rj["results"]:
        currname = item["name"] # e.g. "High Elf"
        currurl = "https://www.dnd5eapi.co" + item["url"]
        curr_r = requests.get(currurl).content
        curr_rj = json.loads(curr_r)
        assoc_race = curr_rj["race"]["name"] # e.g. "Elf"
        desc = curr_rj["desc"]
        curritem = curr_rj["ability_bonuses"][0]
        increase = curritem["bonus"]
        increased_score = curritem["name"]
        startprofs = [x["name"] for x in curr_rj["starting_proficiencies"]]
        startprofs_str = ", ".join(startprofs)
        langs = [x["name"] for x in curr_rj["languages"]]
        langstr = ", ".join(langs)
        numlangs = 0
        numtraits = 0
        langchoices = ""
        traitchoices = ""
        if "language_options" in curr_rj:
            numlangs = curr_rj["language_options"]["choose"]
            langlist = [l["name"] for l in curr_rj["language_options"]["from"]]
            langchoices = ", ".join(langlist)
        traitslist = [x["name"] for x in curr_rj["racial_traits"]]
        traits_str = ", ".join(traitslist)
        if "racial_trait_options" in curr_rj:
            numtraits = curr_rj["racial_trait_options"]["choose"]
            traitchoicelist = [t["name"] for t in curr_rj["racial_trait_options"]["from"]]

        newdndsubrace = Dndsubrace(name=currname, race=assoc_race, description=desc,
            bonus1=increase, bonusname1=increased_score, startingprofs=startprofs_str,
            languages=langstr, numlangchoices=numlangs, langoptions=langchoices,
            racialtraits=traits_str, numtraitchoices=numtraits, traitoptions=traitchoices)
        db.session.add(newdndsubrace)
    db.session.commit()

# pull equipment info from API to populate Dndequipment table
def populateEquipment():
    url = "https://www.dnd5eapi.co/api/equipment"
    r = requests.get(url).content
    rj = json.loads(r)

    for item in rj["results"]:
        currname = item["name"] # e.g. "Dagger" or "Soap"
        currurl = "https://www.dnd5eapi.co" + item["url"] # e.g. "/api/equipment/dagger"
        curr_r = requests.get(currurl).content
        curr_rj = json.loads(curr_r)
        currtype = curr_rj["equipment_category"]["name"] # e.g. "Weapon" or "Adventuring Gear"
        currcost = str(curr_rj["cost"]["quantity"]) + " " + curr_rj["cost"]["unit"] # e.g. "2 gp" 
        if "weight" in curr_rj:
            currweight = curr_rj["weight"]
        else:
            currweight = 0
        dmgtype, dmgdice, subcategory, itempropstr, propurlstr, stealthdis = "", "", "", "", "", ""
        maxbonus, normalrg, longrg, baseac, strengthmin = 0, 0, 0, 0, 0 
        itemdesc, dexbonus = "", ""
        itemproperties = []
        propurls = []

        if "Gear" in currtype:
            subcategory = curr_rj["gear_category"]["name"] 
        elif "Tools" in currtype:
            subcategory = curr_rj["tool_category"]
        elif "Weapon" in currtype:
            subcategory = curr_rj["category_range"] # e.g. "Martial Melee"
            if "damage" in curr_rj:
                dmgtype = curr_rj["damage"]["damage_type"]["name"] 
                dmgdice = curr_rj["damage"]["damage_dice"]
            if "range" in curr_rj:
                normalrg = curr_rj["range"]["normal"]
                longrg = curr_rj["range"]["long"] 
        elif "Armor" in currtype:
            subcategory = curr_rj["armor_category"]
            baseac = curr_rj["armor_class"]["base"]
            if curr_rj["armor_class"]["dex_bonus"] is True:
                dexbonus = "Yes"
            if curr_rj["armor_class"]["max_bonus"] is not None:
                maxbonus = str(curr_rj["armor_class"]["max_bonus"])
            strengthmin = curr_rj["str_minimum"]
            if curr_rj["stealth_disadvantage"] is True:
                stealthdis = "Yes"
        elif "Mounts" in currtype:
            subcategory = curr_rj["vehicle_category"]
        else:
            subcategory = ""

        if "properties" in curr_rj:
            itemproperties = [p["name"] for p in curr_rj["properties"]]
            propurls = [x["url"] for x in curr_rj["properties"]] 
            itempropstr = ", ".join(itemproperties)
            propurlstr = ", ".join(propurls)
        if "desc" in curr_rj:
            itemdesc = " ".join(curr_rj["desc"])

        newdndequipment = Dndequipment(name=currname, cost=currcost,
            weight=currweight, maincategory=currtype, secondcategory=subcategory,
            properties=itempropstr, propertyurls=propurlstr, damagetype=dmgtype,
            damagedice=dmgdice, base_ac=baseac, description=itemdesc,
            dexteritybonus=dexbonus, maximumbonus=maxbonus, minimumstrength=strengthmin,
            disadvantage=stealthdis, normrange=normalrg, longrange=longrg) 
        db.session.add(newdndequipment)
    db.session.commit()

# pull features info from API to populate Dndfeatures table
def populateFeatures():
    url = "https://www.dnd5eapi.co/api/features"
    r = requests.get(url).content
    rj = json.loads(r)

    for item in rj["results"]:
        currname = item["name"] # e.g. "Channel Divinity"
        currurl = "https://www.dnd5eapi.co" + item["url"] # e.g. "/api/features/channel-divinity"
        curr_r = requests.get(currurl).content
        curr_rj = json.loads(curr_r)

        feature_descrip, feature_class, feature_group, feature_subclass = "", "", "", ""
        feature_lvl = None
        numchoices = 0
        choices, all_prereqs = "", ""
        if "desc" in curr_rj:
            feature_descrip = ", ".join(curr_rj["desc"])
        if "class" in curr_rj:
            if "name" in curr_rj["class"]:
                feature_class = curr_rj["class"]["name"]
        if "subclass" in curr_rj:
            if "name" in curr_rj["subclass"]:
                feature_subclass = curr_rj["subclass"]["name"]
        if "level" in curr_rj:
            feature_lvl = curr_rj["level"]
        if "group" in curr_rj:
            feature_group = curr_rj["group"]
        if "choice" in curr_rj:
            if "choose" in curr_rj["choice"]:
                numchoices = curr_rj["choice"]["choose"]
            if "from" in curr_rj["choice"]:
                choicelist = [x["name"] for x in curr_rj["choice"]["from"]]
                choices = ", ".join(choicelist)
        if "prerequisites" in curr_rj:
            for prereq in curr_rj["prerequisites"]:
                currptype = prereq["type"]
                all_prereqs = all_prereqs + currptype + ": "
                if "proficiency" in prereq:
                    if "api/proficiencies/" in prereq["proficiency"]:
                        proflist = prereq["proficiency"].split("api/proficiencies/")
                        req_prof = proflist[len(proflist)-1]
                        all_prereqs = all_prereqs + req_prof + ". "
                elif "level" in prereq:
                    levelstr = str(prereq["level"])
                    all_prereqs = all_prereqs + levelstr + ". "

        newdndfeature = Dndfeature(name=currname, description=feature_descrip,
            numoptions=numchoices, choiceoptions=choices, fclass=feature_class,
            fsubclass=feature_subclass, level=feature_lvl, fgroup=feature_group)
        db.session.add(newdndfeature)
    db.session.commit()

# pull traits info from API to populate Dndtraits table
def populateTraits():
    url = "https://www.dnd5eapi.co/api/traits"
    r = requests.get(url).content
    rj = json.loads(r)

    for item in rj["results"]:
        currname = item["name"] # e.g. "Darkvision"
        currurl = "https://www.dnd5eapi.co" + item["url"] # e.g. "/api/traits/darkvision"
        curr_r = requests.get(currurl).content
        curr_rj = json.loads(curr_r)

        trait_descrip, trait_race, trait_subrace, trait_profs, p_choices_str = "", "", "", "", ""
        num_p_choices = None
        if "desc" in curr_rj:
            trait_descrip = ", ".join(curr_rj["desc"])
        if "proficiencies" in curr_rj:
            if len(curr_rj["proficiencies"]) > 0:
                trait_plist = [p["name"] for p in curr_rj["proficiencies"]]
                trait_profs = ", ".join(trait_plist)
        if "races" in curr_rj:
            if len(curr_rj["races"]) > 0:
                trait_racelist = [r["name"] for r in curr_rj["races"]]
                trait_race = ", ".join(trait_racelist)
        if "subraces" in curr_rj:
            if len(curr_rj["subraces"]) > 0:
                trait_subracelist = [s["name"] for s in curr_rj["subraces"]]
                trait_subrace = ", ".join(trait_subracelist)
        if "proficiency_choices" in curr_rj:
            num_p_choices = curr_rj["proficiency_choices"]["choose"]
            all_p_choices = [c["name"] for c in curr_rj["proficiency_choices"]["from"]]
            p_choices_str = ", ".join(all_p_choices)

        newdndtrait = Dndtrait(name=currname, description=trait_descrip,
            races=trait_race, subraces=trait_subrace, profs=trait_profs,
            numprofchoices=num_p_choices, profoptions=p_choices_str)
        db.session.add(newdndtrait)
    db.session.commit()

# pull backgrounds info from API to populate Dndbackgrounds table
def populateBackgrounds():
    bg_names = ["Acolyte", "Charlatan", "Criminal", "Entertainer", "Folk Hero", "Guild Artisan", "Hermit", "Noble", "Outlander", "Sage", "Sailor", "Soldier", "Urchin"]
    bg_skillprofs = {"Acolyte": "Insight, Religion", "Charlatan": "Deception, Sleight of Hand", "Criminal": "Deception, Stealth", "Entertainer": "Acrobatics, Performance", "Folk Hero": "Animal Handling, Survival", "Guild Artisan": "Insight, Persuasion", "Hermit": "Medicine, Religion", "Noble": "History, Persuasion", "Outlander": "Athletics, Survival", "Sage": "Arcana, History", "Sailor": "Athletics, Persuasion", "Soldier": "Athletics, Intimidation", "Urchin": "Sleight of Hand, Stealth"}
    bg_toolprofs = {"Acolyte": "", "Charlatan": "disguise kit, forgery kit", "Criminal": "one type of gaming set, thieve\'s tools", "Entertainer": "disguise kit, one type of musical instrument", "Folk Hero": "one type of artisan\'s tools, vehicles (land)", "Guild Artisan": "one type of artisan\'s tools", "Hermit": "herbalism kit", "Noble": "one type of gaming set", "Outlander": "one type of musical instrument", "Sage": "", "Sailor": "navigator\'s tools, vehicles (water)", "Soldier": "one type of gaming set, vehicles (land)", "Urchin": "disguise kit, thieve\'s tools"}
    bg_langs = {"Acolyte": "two of your choice", "Charlatan": "", "Criminal": "", "Entertainer": "", "Folk Hero": "", "Guild Artisan": "one of your choice", "Hermit": "one of your choice", "Noble": "one of your choice", "Outlander": "one of your choice", "Sage": "two of your choice", "Sailor": "", "Soldier": "", "Urchin": ""}
    bg_equipment = {"Acolyte": "holy symbol, prayer book or prayer wheel, 5 sticks incense, vestments, set of common clothes, pouch with 15 gp", "Charlatan": "set of fine clothes, disguise kit, tools of con of your choice (10 stoppered bottles of colored liquid, set of weighted dice, deck of marked cards, or signet ring of an imaginary duke), pouch with 15 gp", "Criminal": "crowbar, set of dark common clothes including a hood, pouch with 15 gp", "Entertainer": "1 musical instrument of your choice, token from an admirer (love letter, lock of hair, or trinket), costume, pouch with 15 gp", "Folk Hero": "set of artisan\'s tools (1 of your choice), shovel, iron pot, set of common clothes, pouch with 10 gp", "Guild Artisan": "set of artisan\'s tools (1 of your choice), letter of introduction from your guild, set of traveler\'s clothes, pouch with 15 gp", "Hermit": "scroll case with notes from studies or prayers, winter blanket, set of common clothes, herbalism kit, 5 gp", "Noble": "set of fine clothes, signet ring, scroll of pedigree, purse with 25 gp", "Outlander": "staff, hunting trap, trophy from an animal you killed, set of traveler\'s clothes, pouch with 10 gp", "Sage": "bottle of black ink, quill, small knife, letter from your dead colleague posing a question you have not been able to answer, set of common clothes, pouch with 10 gp", "Sailor": "belaying pin (club), 50 ft silk rope, lucky charm (e.g. rabbit foot, small stone with hole in center, set of common clothes, pouch with 10 gp", "Soldier": "Insignia of rank, trophy from a fallen enemy (dagger, broken blade, piece of a banner), set of bone dice or deck of cards, set of common clothes, pouch with 10 gp", "Urchin": "small knife, map of city you grew up in, pet mouse, token to remember your parents by, set of common clothes, pouch with 10 gp"}
    bg_variants = {"Acolyte": "", "Charlatan": "", "Criminal": "Spy", "Entertainer": "Gladiator", "Folk Hero": "", "Guild Artisan": "Guild Merchant", "Hermit": "", "Noble": "", "Outlander": "", "Sage": "", "Sailor": "Pirate", "Soldier": "", "Urchin": ""}
    bg_features = {"Acolyte": "Shelter of the Faithful", "Charlatan": "False Identity", "Criminal": "Criminal Contact", "Entertainer": "By Popular Demand", "Folk Hero": "Rustic Hospitality", "Guild Artisan": "Guild Membership", "Hermit": "Discovery", "Noble": "Position of Privilege", "Outlander": "Wanderer", "Sage": "Researcher", "Sailor": "Ship\'s Passage", "Soldier": "Military Rank", "Urchin": "City Secrets"}
    variant_features = {"Sailor": "Bad Reputation"}

    for bg in bg_names:
        curr_bgskills, curr_bgtools, curr_bglangs, curr_bgequip = "", "", "", ""
        curr_bgfeature, curr_bgvariant, curr_variant_feature = "", "", ""

        if bg in bg_skillprofs:
            curr_bgskills = bg_skillprofs[bg]
        if bg in bg_toolprofs:
            curr_bgtools = bg_toolprofs[bg]
        if bg in bg_langs:
            curr_bglangs = bg_langs[bg]
        if bg in bg_equipment:
            curr_bgequip = bg_equipment[bg]
        if bg in bg_variants:
            curr_bgvariant = bg_variants[bg]
        if bg in bg_features:
            curr_bgfeature = bg_features[bg]
        if bg in variant_features:
            curr_variant_feature = variant_features[bg]

        newdndbg = Dndbackground(name=bg, skillprofs=curr_bgskills, toolprofs=curr_bgtools,
            langs=curr_bglangs, equipment=curr_bgequip,
            feature=curr_bgfeature, variant=curr_bgvariant, variant_feature=curr_variant_feature)
        db.session.add(newdndbg)
    db.session.commit()

#populateClasses() # done, do not run again 
#populateSpells() # done
#populateSpellLevels() # done
#populateSpellClasses() # done
#populateSpellSchools() # done
#populateRaces() # done
#populateSubraces() # done
#populateEquipment() # done
#populateBackgrounds() # done
#populateFeatures()
#populateTraits()
