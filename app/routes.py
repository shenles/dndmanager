from flask import request, render_template, flash, redirect, url_for, session
from werkzeug.urls import url_parse
from app import app, db
from flask_login import login_required
from app.forms import LoginForm, RegistrationForm, EquipFilterForm, WeaponArmorFilterForm, SpellFilterForm
from app.forms import CreateCharacterForm, ChooseSubraceForm, AssignAbilitiesForm, HalfElfForm, ChooseBgForm
from flask_login import current_user, login_user, logout_user
from app.models import User, Character, Dndclass, Dndspell, Dndrace, Dndsubrace, Dndequipment, Dndbackground

def intersection(l1, l2):
    l3 = [val for val in l1 if val in l2]
    return l3

@app.route('/')
@app.route('/index')
@login_required
def index():
    if not current_user:    
        return render_template('index.html', title='Home')
    characters = Character.query.filter_by(user_id=current_user.id)
    return render_template('index.html', title='Home', allchars=characters)

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
def dndclasses():
    ddclasses = Dndclass.query.all() 
    return render_template('dndclasses.html', title='D&D Classes', allclasses=ddclasses)

# first step of character creation
# user chooses a race, class, & alignment for their character, then rolls scores.
# also chooses a subrace if applicable.
@app.route('/createcharacter', methods=['GET', 'POST'])
@login_required
def createcharacter():
    form = CreateCharacterForm()
    form2 = ChooseSubraceForm()
    if not session.get('subraceDone'):
        session['subraceDone'] = 'no'
    # user has chosen a race but hasn't yet chosen a subrace
    if form.is_submitted() and session.get('subraceDone') == 'no':
        #print('reached block 1')
        char_race = form.races_list.data
        char_class = form.classes_list.data
        char_align = form.alignment_list.data
        # clear existing session variables
        if session.get('characterRace'):
            session.pop('characterRace')
        if session.get('characterClass'):
            session.pop('characterClass')
        if session.get('characterAlign'):
            session.pop('characterAlign')
        if session.get('characterSubrace'):
            session.pop('characterSubrace')
        # store new session data
        session['characterRace'] = char_race
        session['characterClass'] = char_class
        session['characterAlign'] = char_align
        # if chosen race has subraces, let user choose a subrace
        #print(char_race)
        if char_race in ["Elf", "Dwarf", "Halfling", "Gnome"]:
            # mark subrace step as done so it is not repeated
            if session.get('subraceDone'):
                session.pop('subraceDone')
            session['subraceDone'] = 'yes'
            return render_template('createcharacter.html', title='Create Character',
                class_pick=form.classes_list.data, race_pick=form.races_list.data,
                align_pick=form.alignment_list.data, message='Creating your character:', form2=form2)
        # otherwise, just start rolling ability scores
        else:
            # mark subrace step as done so it is not displayed
            if session.get('subraceDone'):
                session.pop('subraceDone')
            session['subraceDone'] = 'yes'
            return render_template('createcharacter.html', title='Create Character',
                class_pick=form.classes_list.data, race_pick=form.races_list.data,
                align_pick=form.alignment_list.data, message='Creating your character:', start_rolling='yes')  
    # user has chosen a subrace
    if form2.is_submitted() and session.get('subraceDone') == 'yes':
        if form2.subrace1.data:
            subracedata = form2.subrace1.data
        elif form2.subrace2.data:
            subracedata = form2.subrace2.data
        elif form2.subrace3.data:
            subracedata = form2.subrace3.data
        elif form2.subrace4.data:
            subracedata = form2.subrace4.data
        else:
            subracedata = None
        # save subrace to session
        if session.get('characterSubrace'):
            session.pop('characterSubrace')
        session['characterSubrace'] = subracedata
        #print(subracedata)
        if session.get('subraceDone'):
            session.pop('subraceDone')
        session['subraceDone'] = 'no'
        return render_template('createcharacter.html', title='Create Character',
                class_pick=session.get('characterClass'), race_pick=session.get('characterRace'),
                align_pick=session.get('characterAlign'), message='Creating your character:',
                start_rolling='yes', subrace=subracedata)
    if session.get('subraceDone'):
        session.pop('subraceDone')
    session['subraceDone'] = 'no'
    return render_template('createcharacter.html', title='Create Character', form=form)

@app.route('/ajax', methods=['POST'])
def ajax_request():
    if request:
        # clear previously stored rolls from session
        if session.get('roll0'):
            session.pop('roll0')
        if session.get('roll1'):
            session.pop('roll1')
        if session.get('roll2'):
            session.pop('roll2')
        if session.get('roll3'):
            session.pop('roll3')
        if session.get('roll4'):
            session.pop('roll4')
        if session.get('roll5'):
            session.pop('roll5')
        # store new rolls in session
        assign_0 = request.form["assign0"]
        assign_1 = request.form["assign1"]
        assign_2 = request.form["assign2"]
        assign_3 = request.form["assign3"]
        assign_4 = request.form["assign4"]
        assign_5 = request.form["assign5"]
        session['roll0'] = int(assign_0)
        session['roll1'] = int(assign_1)
        session['roll2'] = int(assign_2)
        session['roll3'] = int(assign_3)
        session['roll4'] = int(assign_4)
        session['roll5'] = int(assign_5)
        return "success"
    return "failure"

# second step of character creation
# user assigns each roll to an ability score.
# race/subrace-based increases are applied.
@app.route('/createcharacter2', methods=['GET', 'POST'])
@login_required
def createcharacter2():
    form1 = AssignAbilitiesForm()
    curr_result = None
    curr_subrace_result = None
    # user has assigned each roll to an ability
    if form1.is_submitted():
        # get user's choices
        pos0 = form1.abilities0.data
        pos1 = form1.abilities1.data
        pos2 = form1.abilities2.data
        pos3 = form1.abilities3.data
        pos4 = form1.abilities4.data
        pos5 = form1.abilities5.data
        # check for duplicate choices (e.g. assigning Dexterity twice)
        my_list = [pos0, pos1, pos2, pos3, pos4, pos5]
        if len(my_list) != len(set(my_list)):
            flash('Each ability must be used exactly once. Please try again.')
        else:
            # no duplicates, can proceed with setting ability scores
            # clear previously existing ability scores
            if session.get(pos0):
                session.pop(pos0)
            if session.get(pos1):
                session.pop(pos1)
            if session.get(pos2):
                session.pop(pos2)
            if session.get(pos3):
                session.pop(pos3)
            if session.get(pos4):
                session.pop(pos4)
            if session.get(pos5):
                session.pop(pos5)
            # save the new ability scores to the session
            session[pos0] = session.get('roll0')
            session[pos1] = session.get('roll1')
            session[pos2] = session.get('roll2')
            session[pos3] = session.get('roll3')
            session[pos4] = session.get('roll4')
            session[pos5] = session.get('roll5')
            rawstrength = session.get('Strength')
            rawdex = session.get('Dexterity')
            rawconst = session.get('Constitution')
            rawintel = session.get('Intelligence')
            rawwisdom = session.get('Wisdom')
            rawcharisma = session.get('Charisma')
            # gather info to pass to the template
            msg1 = 'Great! Here are your ability scores, before increases:'
            msg2 = 'Here are your scores after race/subrace increases:'
            if session.get('characterRace'):
                curr_race = session['characterRace']
                curr_result = Dndrace.query.filter_by(name=curr_race).first()
            if session.get('characterSubrace'):
                curr_subrace = session['characterSubrace']
                curr_subrace_result = Dndsubrace.query.filter_by(name=curr_subrace).first()
            # calculate new, increased scores based on race & subrace
            abilitydict = {'STR': 'Strength', 'DEX': 'Dexterity', 'CON': 'Constitution', 'INT': 'Intelligence', 'WIS': 'Wisdom', 'CHA': 'Charisma'}
            if curr_result:
                bonuses = [curr_result.bonus1, curr_result.bonus2, curr_result.bonus3, curr_result.bonus4, curr_result.bonus5, curr_result.bonus6]
                bonusnames = [curr_result.bonusname1, curr_result.bonusname2, curr_result.bonusname3, curr_result.bonusname4, curr_result.bonusname5, curr_result.bonusname6]
                # add bonuses to raw scores
                for i in range(len(bonuses)):
                    if bonuses[i] > 0:
                        cn = bonusnames[i]
                        cn_full = abilitydict[cn]
                        if session.get(cn_full):
                            curr_score = session.get(cn_full)
                            session.pop(cn_full)
                            session[cn_full] = curr_score + bonuses[i]
            # add any bonuses related to subrace
            if curr_subrace_result:
                shortname = curr_subrace_result.bonusname1
                fullname = abilitydict[shortname]
                if session.get(fullname):
                    currscore = session.get(fullname)
                    session.pop(fullname)
                    session[fullname] = currscore + curr_subrace_result.bonus1
            # special choice for half-elves
            if session.get('characterRace') == 'Half-Elf':
                #print('half elf')
                msg3 = 'You will choose your half-elf bonuses in the next step.'
            else:
                msg3 = ''
            return render_template('createcharacter2.html', title='Create Character',
                success_message=msg1, message2=msg2, message3=msg3, currstr=rawstrength, currdex=rawdex,
                currcon=rawconst, currint=rawintel, currwis=rawwisdom, currcha=rawcharisma,
                finalstr=session.get('Strength'), finaldex=session.get('Dexterity'),
                finalcon=session.get('Constitution'), finalint=session.get('Intelligence'),
                finalwis=session.get('Wisdom'), finalcha=session.get('Charisma'))

    else:
        if session.get('characterRace'):
            curr_race = session['characterRace']
            curr_result = Dndrace.query.filter_by(name=curr_race).first()
        if session.get('characterSubrace'):
            curr_subrace = session['characterSubrace']
            curr_subrace_result = Dndsubrace.query.filter_by(name=curr_subrace).first()
    return render_template('createcharacter2.html', title='Create Character',
            myrace=session.get('characterRace'), myclass=session.get('characterClass'),
            myalign=session.get('characterAlign'), mysubrace=curr_subrace_result,
            assign0=session.get('roll0'), assign1=session.get('roll1'),
            assign2=session.get('roll2'), assign3=session.get('roll3'),
            assign4=session.get('roll4'), assign5=session.get('roll5'),
            form1=form1, thisrace=curr_result)

# third step of character creation
@app.route('/createcharacter3', methods=['GET', 'POST'])
@login_required
def createcharacter3():
    he_form = HalfElfForm()
    bg_form = ChooseBgForm()

    if not session.get('halfelfBonusDone'):
        session['halfelfBonusDone'] = 'no'
    if not session.get('addHalfElfDone'):
        session['addHalfElfDone'] = 'no'

    if session.get('characterRace') != 'Half-Elf':
        session['addHalfElfDone'] = 'yes'

    if session.get('characterRace') == 'Half-Elf' and session.get('halfelfBonusDone') == 'no':
        # mark this step as done
        if session.get('halfelfBonusDone'):
            session.pop('halfelfBonusDone')
        session['halfelfBonusDone'] = 'yes' 
        # show half elf bonus selection form
        return render_template('createcharacter3.html', title='Create Character', form1=he_form)      
    else:
        if bg_form.is_submitted() and session.get('addHalfElfDone') == 'yes':
            # display stats, class, and race info that is now complete
            #print(bg_form.data)
            # save character background to session
            if bg_form.data['bg_list'] != None:
                session['background'] = bg_form.data['bg_list']
            final_msg = 'Great! You can record the following details on your character sheet:'
            final_msg2 = 'In the next steps, you\'ll choose other skills and equipment.'
            if session.get('halfelfBonusDone'):
                session.pop('halfelfBonusDone')
            session['halfelfBonusDone'] = 'no'
            if session.get('addHalfElfDone'):
                session.pop('addHalfElfDone')
            session['addHalfElfDone'] = 'no'
            return render_template('createcharacter3.html', title='Create Character',
                msg2=final_msg, msg3=final_msg2)
        else:
            if session.get('characterRace') == 'Half-Elf' and he_form.is_submitted():
                #print(he_form.data)
                chosen_increases = he_form.data['increase_list']
                #print(chosen_increases)
                # check if user has picked exactly 2 abilities to increase
                if chosen_increases != None and len(chosen_increases) == 2:
                    # increase the two chosen ability scores and save the new scores
                    first = chosen_increases[0]
                    second = chosen_increases[1]
                    ability1 = session.get(first)
                    ability2 = session.get(second)
                    if ability1 != None:
                        session[first] = ability1 + 1
                    if ability2 != None:
                        session[second] = ability2 + 1

                    he_msg = 'Here are your final ability scores:'
                    if session.get('addHalfElfDone'):
                        session.pop('addHalfElfDone')
                    session['addHalfElfDone'] = 'yes'
                    return render_template('createcharacter3.html', title='Create Character',
                        form2=bg_form, success_message=he_msg, currstr=session.get('Strength'),
                        currdex=session.get('Dexterity'), currcon=session.get('Constitution'),
                        currint=session.get('Intelligence'), currwis=session.get('Wisdom'),
                        currcha=session.get('Charisma'))
                else:
                    flash('Please choose exactly 2')
                    return render_template('createcharacter3.html',
                        title='Create Character', form1=he_form)
            # show background selection form
            return render_template('createcharacter3.html', title='Create Character',
                    form2=bg_form)

@app.route('/dndraces')
@login_required
def dndraces():
    ddraces = Dndrace.query.all()
    return render_template('dndraces.html', title='D&D Races', allraces=ddraces)

@app.route('/dndbackgrounds')
@login_required
def dndbackgrounds():
    dd_bgs = Dndbackground.query.all()
    return render_template('dndbackgrounds.html', title='D&D Backgrounds', allbgs=dd_bgs)

@app.route('/dndequipment', methods=['GET', 'POST'])
@login_required
def dndequipment():
    form = EquipFilterForm()
    if form.is_submitted():
        selected_radio = form.category_list.data
        if "All" in selected_radio: # e.g. "All Adventuring Gear" 
            search_string = selected_radio[4:]
            desired_equipment = Dndequipment.query.filter(Dndequipment.maincategory.contains(search_string))
        else:
            # e.g. "Ammunition"
            desired_equipment = Dndequipment.query.filter(Dndequipment.secondcategory.contains(selected_radio))
        return render_template('dndequipment.html', title='D&D Equipment', form=form, selectedequip=desired_equipment)

    ddequip = Dndequipment.query.filter(Dndequipment.maincategory.notin_(['Weapon', 'Armor']))
    return render_template('dndequipment.html', title='D&D Equipment', form=form, allequip=ddequip)

@app.route('/dndweaponsarmor', methods=['GET', 'POST'])
@login_required
def dndweaponsarmor():
    form = WeaponArmorFilterForm()
    if form.is_submitted():
        selected_radio = form.category_list.data
        if "Weapon" in selected_radio and "All" in selected_radio: # e.g. "All Weapons"
            desired_equip = Dndequipment.query.filter(Dndequipment.maincategory.contains("Weapon"))
        elif "Weapon" in selected_radio: # e.g. "Melee Weapons" or "Monk Weapons"
            search_list = selected_radio.split()
            search_string = search_list[0] # e.g. "Melee"
            if search_string in ['Simple', 'Martial', 'Melee', 'Ranged']:
                desired_equip = Dndequipment.query.filter(Dndequipment.secondcategory.contains(search_string))
            else:
                desired_equip = Dndequipment.query.filter(Dndequipment.properties.contains(search_string))
        else:
            desired_equip = Dndequipment.query.filter(Dndequipment.maincategory.contains("Armor"))
        return render_template('dndweaponsarmor.html', title='D&D Weapons & Armor', form=form, selectedequip=desired_equip)
    ddequip = Dndequipment.query.filter(Dndequipment.maincategory.in_(['Weapon', 'Armor']))
    return render_template('dndweaponsarmor.html', title='D&D Weapons & Armor', form=form, allequip=ddequip)

@app.route('/dndspells', methods=['GET', 'POST'])
@login_required
def dndspells():
    form = SpellFilterForm()
    if form.is_submitted():
        level_int = None
        desired_level = []
        desired_class = []
        desired_schools = []

        if form.level_list.data is not None:
            level_int = int(form.level_list.data)
            desired_level = Dndspell.query.filter(Dndspell.level.contains(level_int))
        if form.class_list.data is not None:
            desired_class = Dndspell.query.filter(Dndspell.casters.contains(form.class_list.data))
        if form.school_list.data is not None:
            desired_schools = Dndspell.query.filter(Dndspell.school.in_(form.school_list.data))

        level_result_list = list(desired_level)
        class_result_list = list(desired_class)
        school_result_list = list(desired_schools)
        desired_spells = []

        # all three checkbox fields have option(s) selected
        if len(level_result_list) > 0 and (len(class_result_list) > 0 and len(school_result_list) > 0):
            desired_spells = intersection(level_result_list, class_result_list)
            desired_spells = intersection(desired_spells, school_result_list)
        # first two fields have options selected
        elif len(level_result_list) > 0 and (len(class_result_list) > 0 and len(school_result_list) <= 0):
            desired_spells = intersection(level_result_list, class_result_list) 
        # last two fields have options selected
        elif len(level_result_list) <= 0 and (len(class_result_list) > 0 and len(school_result_list) > 0):
            desired_spells = intersection(class_result_list, school_result_list) 
        # first and third fields have options selected
        elif len(level_result_list) > 0 and (len(class_result_list) <= 0 and len(school_result_list) > 0):
            desired_spells = intersection(level_result_list, school_result_list) 
        # only first field is filled
        elif len(level_result_list) > 0 and (len(class_result_list) <= 0 and len(school_result_list) <= 0):
            desired_spells = level_result_list
        # only 2nd field is filled
        elif len(level_result_list) <= 0 and (len(class_result_list) > 0 and len(school_result_list) <= 0):
            desired_spells = class_result_list
        # only 3rd field is filled
        elif len(level_result_list) <= 0 and (len(class_result_list) <= 0 and len(school_result_list) > 0):
            desired_spells = school_result_list
        else:
            desired_spells = []

        return render_template('dndspells.html', title='Spells', form=form, selected_spells=desired_spells)

    ddspells = Dndspell.query.all()
    return render_template('dndspells.html', title='Spells', form=form, allspells=ddspells)
