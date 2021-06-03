from flask import request, render_template, flash, redirect, url_for, session
from werkzeug.urls import url_parse
from app import app, db
from flask_login import login_required
from app.forms import LoginForm, RegistrationForm, EquipFilterForm, WeaponArmorFilterForm
from app.forms import SpellFilterForm, FeatureFilterForm, CreateCharacterForm, ChooseSubraceForm
from app.forms import AssignAbilitiesForm, HalfElfForm, ChooseBgForm, ChooseProfForm2_1, ChooseProfForm2_2
from app.forms import ChooseProfForm1_1, ChooseProfForm1_2, ChooseProfForm1_3, ChooseProfForm1_4
from app.forms import ChooseProfForm1_5, ChooseProfForm1_6, ChooseLangForm1_1, ChooseLangForm1_2
from app.forms import ChooseProfForm3_1, ChooseProfForm4, ChooseProfForm1_7, ChooseProfForm1_8
from app.forms import ChooseProfForm1_9, ChooseProfForm1_10, ChooseProfForm1_11, ChooseProfForm1_12
from flask_login import current_user, login_user, logout_user
from app.models import User, Character, Dndclass, Dndspell, Dndrace, Dndsubrace
from app.models import Dndequipment, Dndbackground, Dndfeature, Dndtrait

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

@app.route('/delete', methods=['POST'])
def delete():
    if request:
        id_to_delete = int(request.data)
        char_to_delete = Character.query.filter_by(id=id_to_delete).first()
        db.session.delete(char_to_delete)
        db.session.commit()
        return "success"
    return "failure"

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
        char_name = form.name_box.data
        char_type = form.type_list.data
        char_race = form.races_list.data
        char_class = form.classes_list.data
        char_align = form.alignment_list.data
        # clear existing session variables
        if session.get('characterName'):
            session.pop('characterName')
        if session.get('characterType'):
            session.pop('characterType')
        if session.get('characterRace'):
            session.pop('characterRace')
        if session.get('characterClass'):
            session.pop('characterClass')
        if session.get('characterAlign'):
            session.pop('characterAlign')
        if session.get('characterSubrace'):
            session.pop('characterSubrace')
        # store new session data
        session['characterName'] = char_name
        session['characterType'] = char_type
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
                align_pick=form.alignment_list.data, type_pick=session.get('characterType'),
                name_pick=form.name_box.data,
                message='Creating your character:', form2=form2)
        # otherwise, just start rolling ability scores
        else:
            # mark subrace step as done so it is not displayed
            if session.get('subraceDone'):
                session.pop('subraceDone')
            session['subraceDone'] = 'yes'
            return render_template('createcharacter.html', title='Create Character',
                class_pick=form.classes_list.data, race_pick=form.races_list.data,
                align_pick=form.alignment_list.data, type_pick=session.get('characterType'),
                name_pick=form.name_box.data,
                message='Creating your character:', start_rolling='yes')  
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
                type_pick=session.get('characterType'), name_pick=form.name_box.data,
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
    curr_result, curr_subrace_result = None, None
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
            mytype=session.get('characterType'), myname=session.get('characterName'),
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
            # save character background to session
            if bg_form.data['bg_list'] != None:
                session['background'] = bg_form.data['bg_list']
            final_msg = 'Great! You\'ve made excellent choices.'
            final_msg2 = 'In the next step, you\'ll make a few more choices about your character.'
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
                chosen_increases = he_form.data['increase_list']
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

# 4th step of character creation
# user chooses proficiencies from a list of options based on their class
@app.route('/chooseprofs', methods=['GET', 'POST'])
@login_required
def chooseprofs():
    # start at level 1
    if not session.get('characterLevel'):
        session['characterLevel'] = 1
    profmsg1 = 'You have the following proficiencies from your class/race/background:'
    donemsg1 = 'Great! Click Continue to proceed.'
    profmsg2 = 'Please choose additional proficiencies below.'
    bgskills = []
    # retrieve existing proficiencies from bg, race, class
    if session.get('background'):
        currbg = session.get('background')
        getbg = Dndbackground.query.filter_by(name=currbg).first()
        if getbg is not None:
            bgskills = getbg.skillprofs.split(', ')
            bgtools = getbg.toolprofs.split(', ')
            bgskills.extend(bgtools)
    if session.get('characterRace'):
        curr_race = session.get('characterRace')
        getrace = Dndrace.query.filter_by(name=curr_race).first()
        if getrace is not None:
            rskills = getrace.startingprofs.split(', ')
            bgskills.extend(rskills)
    if session.get('characterClass'):
        currentclass = session.get('characterClass')
        getclass = Dndclass.query.filter_by(name=currentclass).first()
        if getclass is not None:
            classidx = getclass.id
            numchoices1 = getclass.num_pchoices
            numchoices2 = getclass.num_pchoices_two
            cskills = getclass.armweapprofs.split(', ')
            bgskills.extend(cskills)
    else:
        classidx = -1
        numchoices1, numchoices2 = 0, 0
    # use correct form depending on chosen class
    if classidx == 1:
        form1 = ChooseProfForm1_1()
    elif classidx == 2:
        form1 = ChooseProfForm1_2()
    elif classidx == 3:
        form1 = ChooseProfForm1_3()
    elif classidx == 4:
        form1 = ChooseProfForm1_4()
    elif classidx == 5:
        form1 = ChooseProfForm1_5()
    elif classidx == 6:
        form1 = ChooseProfForm1_6()
    elif classidx == 7:
        form1 = ChooseProfForm1_7()
    elif classidx == 8:
        form1 = ChooseProfForm1_8()
    elif classidx == 9:
        form1 = ChooseProfForm1_9()
    elif classidx == 10:
        form1 = ChooseProfForm1_10()
    elif classidx == 11:
        form1 = ChooseProfForm1_11()
    elif classidx == 12:
        form1 = ChooseProfForm1_12()

    if form1 and not form1.is_submitted():
        bgskills = [sk for sk in bgskills if len(sk) > 0]
        profstring = ', '.join(bgskills)
        #print(bgskills)
        return render_template('chooseprofs.html', title='Create Character', form1=form1, num1=numchoices1,
            msg1=profmsg1, msg2=profmsg2, profs_str=profstring)
    elif form1 and form1.is_submitted():
        chosen_profs = form1.data['field1']
        #print(chosen_profs)
        #print(', '.join(chosen_profs))
        # notify user if user has not chosen correct number of proficiencies
        if len(chosen_profs) != numchoices1:
            flash('Please choose exactly ' + str(numchoices1))
            return render_template('chooseprofs.html', title='Create Character', form1=form1, num1=numchoices1)
        # notify user if they have chosen a proficiency they already had
        prof_overlap = []
        prof_overlap = [prf for prf in bgskills if prf in ', '.join(chosen_profs)]
        prof_overlap = [p for p in prof_overlap if len(p) > 0]
        #print(prof_overlap)
        if len(prof_overlap) > 0:
            flash('Try choosing proficiencies you don\'t already have.')
            return render_template('chooseprofs.html', title='Create Character', form1=form1, num1=numchoices1)
        # save chosen proficiencies to session
        session['character_proficiencies'] = ', '.join(bgskills)
        session['chosen_proficiencies'] = ', '.join(chosen_profs)
        return render_template('chooseprofs.html', title='Create Character', msg3=donemsg1, num2=numchoices2)
    else:
        return render_template('chooseprofs.html', title='Create Character', msg3=donemsg1, num2=numchoices2)

# continuing with character creation
# user chooses additional proficiencies, if their class grants extra choices
@app.route('/chooseprofs2', methods=['GET', 'POST'])
@login_required
def chooseprofs2():
    existing_msg = 'You have the following proficiencies from your race/class/background:'
    chosen_msg = 'You have also added these proficiencies:'
    choose_msg = 'Please choose additional proficiencies below.'
    donemsg1 = 'Great! Click Continue to proceed.'
    profs_str2, chosen_str = '', ''

    if session.get('characterClass'):
        currclass = session.get('characterClass')
        getclass = Dndclass.query.filter_by(name=currclass).first()
        classidx = getclass.id
        numchoices2 = getclass.num_pchoices_two
        numchoices3 = getclass.num_pchoices_three
    else:
        classidx = -1
        numchoices2, numchoices3 = 0, 0
    # create correct form depending on chosen class
    if classidx == 2: # Bard
        form2 = ChooseProfForm2_1()
    elif classidx == 6: # Monk
        form2 = ChooseProfForm2_2()
    # retrieve existing profiencies and recently selected proficiencies
    if session.get('character_proficiencies'):
        profs_str2 = session.get('character_proficiencies')
    if session.get('chosen_proficiencies'):
        chosen_str = session.get('chosen_proficiencies')

    if form2 and not form2.is_submitted():
        return render_template('chooseprofs2.html', title='Create Character', form2=form2,
            num2=numchoices2, currentprofs=profs_str2, recentchoices=chosen_str, msg1=existing_msg,
            msg2=chosen_msg, msg3=choose_msg)
    elif form2 and form2.is_submitted():
        chosen_profs = form2.data['field1']
        # notify user if user has not chosen correct number of proficiencies
        if len(chosen_profs) != numchoices2:
            flash('Please choose exactly ' + str(numchoices2))
            return render_template('chooseprofs2.html', title='Create Character', form2=form2, num2=numchoices2)
        # save new proficiencies to session
        if session.get('chosen_proficiencies'):
            existing_chosen = session.get('chosen_proficiencies')
            new_existing = ', '.join(chosen_profs)
            session['chosen_proficiencies'] = existing_chosen + ', ' + new_existing
            #print(session.get('chosen_proficiencies'))
        return render_template('chooseprofs2.html', title='Create Character', msg4=donemsg1, num3=numchoices3)
    else:
        return render_template('chooseprofs2.html', title='Create Character', msg4=donemsg1, num3=numchoices3)

# continuing with character creation
# user chooses additional proficiencies, if their class grants extra choices
@app.route('/chooseprofs3', methods=['GET', 'POST'])
@login_required
def chooseprofs3():
    existing_msg = 'You have the following proficiencies from your race/class/background:'
    chosen_msg = 'You have also added these proficiencies:'
    choose_msg = 'Please choose additional proficiencies below.'
    donemsg1 = 'Great! Click Continue to proceed.'
    profs_str3, chosen_str3 = '', ''

    # use user's dnd class to determine how many selections the user gets to make
    if session.get('characterClass'):
        currclass = session.get('characterClass')
        getclass = Dndclass.query.filter_by(name=currclass).first()
        classidx = getclass.id
        numchoices3 = getclass.num_pchoices_three
    else:
        classidx = -1
        numchoices3 = 0

    if classidx == 6: # Monk
        form3 = ChooseProfForm3_1()
    # retrieve existing profiencies and recently selected proficiencies
    if session.get('character_proficiencies'):
        profs_str3 = session.get('character_proficiencies')
    if session.get('chosen_proficiencies'):
        chosen_str3 = session.get('chosen_proficiencies')

    if form3 and not form3.is_submitted():
        return render_template('chooseprofs3.html', title='Create Character', form3=form3,
            num3=numchoices3, currentprofs=profs_str3, recentchoices=chosen_str3, msg1=existing_msg,
            msg2=chosen_msg, msg3=choose_msg)
    elif form3 and form3.is_submitted():
        chosen_profs = form3.data['field1']
        # notify user if user has not chosen correct number of proficiencies
        if len(chosen_profs) != numchoices3:
            flash('Please choose exactly ' + str(numchoices3))
            return render_template('chooseprofs3.html', title='Create Character', form3=form3, num3=numchoices3)
        # save new proficiencies to session
        if session.get('chosen_proficiencies'):
            existing_chosen = session.get('chosen_proficiencies')
            new_existing = ', '.join(chosen_profs)
            session['chosen_proficiencies'] = existing_chosen + ', ' + new_existing
            #print(session.get('chosen_proficiencies'))
        return render_template('chooseprofs3.html', title='Create Character', msg4=donemsg1, num3=numchoices3)
    else:
        return render_template('chooseprofs3.html', title='Create Character', msg4=donemsg1, num3=numchoices3)

# continue with character creation
# user finishes choosing proficiencies and chooses languages
@app.route('/chooseprofs4', methods=['GET', 'POST'])
@login_required
def chooseprofs4():
    existing_msg = 'You have the following proficiencies:'
    chosen_msg = 'You have also added these proficiencies:'
    existing_langs = 'You know the following languages:'
    choose_prof = 'Please choose additional proficiencies below.'
    choose_langs = 'Please choose additional languages below.'
    donemsg1 = 'You\'re done choosing proficiencies and languages! Click Continue.'
    profs_str4, langs_str, chosen_str4 = '', '', ''
    raceidx = -1
    numlangchoices, numprofchoices = 0, 0
    form4, form5 = None, None
    existlangs, existsublangs, langoptions, sublangoptions, existbglangs = None, None, None, None, None

    # retrieve languages already known from race, subrace, bg
    if session.get('characterSubrace'):
        currsub = session.get('characterSubrace')
        getsub = Dndsubrace.query.filter_by(name=currsub).first()
        if getsub is not None:
            subidx = getsub.id
            existsublangs = getsub.languages
            sublangoptions = getsub.langoptions
    if session.get('background'):
        currbg = session.get('background')
        getbg = Dndbackground.query.filter_by(name=currbg).first()
        if getbg is not None:
            bgidx = getbg.id
            existbglangs = getbg.langs
    if session.get('characterRace'):
        curr_race = session.get('characterRace')
        getrace = Dndrace.query.filter_by(name=curr_race).first()
        if getrace is not None:
            raceidx = getrace.id
            existlangs = getrace.languages
            langoptions = getrace.langoptions
        # Dwarf race has additional proficiency choice
        # other races go straight to language selection
        if raceidx == 2: # Dwarf
            form4 = ChooseProfForm4()
            numprofchoices = getrace.numprofchoices
        if raceidx == 5: # Half-Elf
            form5 = ChooseLangForm1_1()
            numlangchoices = getrace.numlangchoices
        if raceidx == 8: # Human
            form5 = ChooseLangForm1_2()
            numlangchoices = getrace.numlangchoices

    # retrieve existing profiencies
    if session.get('character_proficiencies'):
        profs_str4 = session.get('character_proficiencies')
    if session.get('chosen_proficiencies'):
        chosen_str4 = session.get('chosen_proficiencies')

    if form4 and not form4.is_submitted():
        #print('block4 reached')
        return render_template('chooseprofs4.html', title='Create Character', form4=form4,
            num4=numprofchoices, currentprofs=profs_str4, recentchoices=chosen_str4, msg1=existing_msg,
            msg2=chosen_msg, msg3=choose_prof)
    elif form4 and form4.is_submitted():
        #print('block4a reached')
        chosen_profs = form4.data['field1']
        # notify user if user has not chosen correct number of proficiencies
        if len(chosen_profs) != numprofchoices:
            flash('Please choose exactly ' + str(numprofchoices))
            return render_template('chooseprofs4.html', title='Create Character',
                form4=form4, num4=numprofchoices)
        # save new proficiencies to session
        if session.get('chosen_proficiencies'):
            existing_chosen = session.get('chosen_proficiencies')
            new_existing = ', '.join(chosen_profs)
            session['chosen_proficiencies'] = existing_chosen + ', ' + new_existing
        # save known languages to session
        if existlangs is not None:
            session['knownlangs'] = existlangs
        if existsublangs is not None and session.get('knownlangs') is not None:
            if existsublangs != '':
                templangs = session.get('knownlangs')
                session['knownlangs'] = templangs + ', ' + existsublangs
        if existbglangs is not None and session.get('knownlangs') is not None:
            if existbglangs != '':
                templg = session.get('knownlangs')
                session['knownlangs'] = templg + ', ' + existbglangs
        return render_template('chooseprofs4.html', title='Create Character',
            msg4=existing_langs, msg1=existing_msg, known=session.get('knownlangs'),
            currentprofs=session.get('character_proficiencies'), recentchoices=session.get('chosen_proficiencies'))
    elif form5 and not form5.is_submitted():
        #print('block5 reached')
        # build string of known languages to display to user
        if existlangs is not None:
            session['knownlangs'] = existlangs
        if existsublangs is not None and session.get('knownlangs') is not None:
            if existsublangs != '':
                templangs = session.get('knownlangs')
                session['knownlangs'] = templangs + ', ' + existsublangs
        if existbglangs is not None and session.get('knownlangs') is not None:
            if existbglangs != '':
                templg = session.get('knownlangs')
                session['knownlangs'] = templg + ', ' + existbglangs
        return render_template('chooseprofs4.html', title='Create Character', form5=form5,
            num5=numlangchoices, msg4=existing_langs, msg5=choose_langs, known=session.get('knownlangs'))
    elif form5 and form5.is_submitted():
        #print('block5a reached')
        chosen_langs = form5.data['field1']
        # notify user if user has not chosen correct number of languages
        if len(chosen_langs) != numlangchoices:
            flash('Please choose exactly ' + str(numlangchoices))
            return render_template('chooseprofs4.html', title='Create Character',
                form5=form5, num5=numlangchoices)
        # save new languages to session
        newknown = ', '.join(chosen_langs)
        if session.get('knownlangs') is not None:
            tempknown = session.get('knownlangs')
            session['knownlangs'] = tempknown + ', ' + newknown
        else:
            session['knownlangs'] = newknown
        return render_template('chooseprofs4.html', title='Create Character',
            msg6=donemsg1, known=session.get('knownlangs'), msg4=existing_langs)
    else:
        #print('block5b reached')
        # display known languages to user
        if existlangs is not None:
            session['knownlangs'] = existlangs
        if existsublangs is not None and session.get('knownlangs') is not None:
            if existsublangs != '':
                templangs = session.get('knownlangs')
                session['knownlangs'] = templangs + ', ' + existsublangs
        if existbglangs is not None and session.get('knownlangs') is not None:
            if existbglangs != '':
                templg = session.get('knownlangs')
                session['knownlangs'] = templg + ', ' + existbglangs
        return render_template('chooseprofs4.html', title='Create Character',
            msg6=donemsg1, known=session.get('knownlangs'), msg4=existing_langs,
            currentprofs=session.get('character_proficiencies'), recentchoices=session.get('chosen_proficiencies'),
            msg1=existing_msg)

# user chooses equipment for their character
@app.route('/chooseequip', methods=['GET', 'POST'])
@login_required
def chooseequip():
    existing_equip_bg = 'You have the following equipment from your background:'
    return render_template('chooseequip.html', title='Character Options',
        bg_msg=existing_equip_bg)

# character is added to db
# user is prompted for next steps
@app.route('/charcreated', methods=['GET', 'POST'])
@login_required
def charcreated():
    congrats = 'Congratulations! Your character has been created.'
    ask = 'What would you like to do now?'

    ch_name = session.get('characterName')
    ch_type = session.get('characterType')
    ch_race = session.get('characterRace')
    ch_subrace = session.get('characterSubrace')
    ch_class = session.get('characterClass')
    ch_align = session.get('characterAlign')
    ch_level = session.get('characterLevel')
    ch_background = session.get('background')
    ch_stren = session.get('Strength')
    ch_dex = session.get('Dexterity')
    ch_constn = session.get('Constitution')
    ch_intell = session.get('Intelligence')
    ch_wis = session.get('Wisdom')
    ch_cha = session.get('Charisma')
    ch_langs = session.get('knownlangs')
    ch_profs = session.get('character_proficiencies')
    ch_profs = ch_profs + ', ' + session.get('chosen_proficiencies')
    all_abilities = [ch_stren, ch_dex, ch_constn, ch_intell, ch_wis, ch_cha]

    # calculate modifiers based on ability scores
    abil_mods = []
    for asc in all_abilities:
        diff = asc - 10
        if diff % 2 == 0: # even
            modifier = diff // 2
        else:
            modifier = (diff-1) // 2
        abil_mods.append(modifier)

    # use level to determine proficiency bonus
    if ch_level <= 4:
        ch_pb = 2
    elif ch_level <= 8:
        ch_pb = 3
    elif ch_level <= 12:
        ch_pb = 4
    elif ch_level <= 16:
        ch_pb = 5
    elif ch_level <= 20:
        ch_pb = 6
    else:
        ch_pb = 0

    ch_abilities = {'Strength': ch_stren, 'Dexterity': ch_dex, 'Constitution': ch_constn, 'Intelligence': ch_intell, 'Wisdom': ch_wis, 'Charisma': ch_cha}
    ch_abil_mods = {'Strength': abil_mods[0], 'Dexterity': abil_mods[1], 'Constitution': abil_mods[2], 'Intelligence': abil_mods[3], 'Wisdom': abil_mods[4], 'Charisma': abil_mods[5]}

    # determine darkvision based on race
    if ch_race in ['Human', 'Halfling', 'Dragonborn']:
        ch_darkvis = 'no'
    else:
        ch_darkvis = 'yes'

    # determine unarmored AC based on Constitution modifier
    ch_ac = 10 + ch_abil_mods['Constitution']
    # determine initiative modifier based on Dexterity modifier
    ch_init = ch_abil_mods['Dexterity']
    # determine speed based on race
    if ch_race in ['Halfling', 'Dwarf', 'Gnome']:
        ch_speed = 25
    else:
        ch_speed = 30
    # determine size based on race
    if ch_race in ['Halfling', 'Gnome']:
        ch_size = 'Small'
    else:
        ch_size = 'Medium'
    # calculate max HP based on Constitution modifier and hitdie
    ch_res = Dndclass.query.filter_by(name=ch_class).first()
    ch_hpmax = ch_res.hitdie + ch_abil_mods['Constitution']
    ch_hitdice = str(ch_level) + 'd' + str(ch_res.hitdie)
    # clean up strings
    profslist = ch_profs.split(', ')
    langslist = ch_langs.split(', ')
    finalprofslist = [p for p in profslist if len(p) > 2]
    ch_profs = ', '.join(finalprofslist)
    finallangslist = []
    for l in langslist:
        if l not in finallangslist and len(l) > 2:
            finallangslist.append(l)
    ch_langs = ', '.join(finallangslist)

    # determine spellcasting class and ability, if any
    # determine spell save DC and spell attack modifier
    if ch_class in ['Bard', 'Cleric', 'Druid', 'Paladin', 'Ranger', 'Sorcerer', 'Warlock', 'Wizard']:
        ch_spellclass = ch_class
    elif ch_class in ['Fighter', 'Rogue']:
        ch_spellclass = 'Wizard'
    else:
        ch_spellclass = None

    if ch_spellclass is not None:
        if ch_spellclass in ['Bard', 'Warlock', 'Sorcerer', 'Paladin']:
            ch_spellabil = 'Charisma'
            ch_spelldc = 8 + ch_pb + ch_abil_mods[ch_spellabil]
            ch_spellmod = ch_pb + ch_abil_mods[ch_spellabil]
        elif ch_spellclass in ['Cleric', 'Druid', 'Ranger']:
            ch_spellabil = 'Wisdom'
            ch_spelldc = 8 + ch_pb + ch_abil_mods[ch_spellabil]
            ch_spellmod = ch_pb + ch_abil_mods[ch_spellabil]
        elif ch_spellclass in ['Wizard']:
            ch_spellabil = 'Intelligence'
            ch_spelldc = 8 + ch_pb + ch_abil_mods[ch_spellabil]
            ch_spellmod = ch_pb + ch_abil_mods[ch_spellabil]
        else:
            ch_spellabil = None
            ch_spelldc = None
            ch_spellmod = None
    else:
        ch_spellabil = None
        ch_spelldc = None
        ch_spellmod = None
    
    # determine modifiers for skill checks and saving throws
    skill_list = ['Acrobatics', 'Animal Handling', 'Arcana', 'Athletics', 'Deception',
                  'History', 'Insight', 'Intimidation', 'Investigation', 'Medicine', 'Nature', 'Perception',
                  'Performance', 'Persuasion', 'Religion', 'Sleight of Hand', 'Stealth', 'Survival']

    skill_categories = {'Acrobatics': 'Dexterity', 'Animal Handling': 'Wisdom', 'Arcana': 'Intelligence', 'Athletics': 'Strength',
                        'Deception': 'Charisma', 'History': 'Intelligence', 'Insight': 'Wisdom', 'Intimidation': 'Charisma',
                        'Investigation': 'Intelligence', 'Medicine': 'Wisdom', 'Nature': 'Intelligence', 'Perception': 'Wisdom',
                        'Performance': 'Charisma', 'Persuasion': 'Charisma', 'Religion': 'Intelligence', 'Sleight of Hand': 'Dexterity',
                        'Stealth': 'Dexterity', 'Survival': 'Wisdom'}

    all_saves = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']
    abbrevs = {'Strength': 'STR', 'Dexterity': 'DEX', 'Constitution': 'CON', 'Intelligence': 'INT', 'Wisdom': 'WIS', 'Charisma': 'CHA'}
    ch_skill_mods = {}
    ch_save_mods = {}

    # fill the dictionary of skill modifiers
    for currskill in skill_list:
        # add proficiency bonus if character is proficient in a skill
        if currskill in finalprofslist and currskill in skill_categories:
            currabil = skill_categories[currskill]
            if currabil in ch_abil_mods:
                currmod = ch_abil_mods[currabil]
                currmod = currmod + ch_pb
        elif currskill in skill_categories:
            # if not proficient in this skill, do not add proficiency bonus
            # use the modifier for the relevant ability
            currabil = skill_categories[currskill]
            if currabil in ch_abil_mods:
                currmod = ch_abil_mods[currabil]
        else:
            currmod = 0
        # add each skill and its modifier to the ch_skill_mods dictionary
        ch_skill_mods[currskill] = currmod

    # fill dictionary of saving throw modifiers
    for sv in all_saves:
        if abbrevs[sv] in ch_res.saveprofs and sv in ch_abil_mods:
            # add proficiency bonus if proficient in this saving throw
            currsavemod = ch_abil_mods[sv]
            currsavemod = currsavemod + ch_pb
        elif sv not in ch_res.saveprofs and sv in ch_abil_mods:
            # do not add proficiency bonus if not proficient in this saving throw
            currsavemod = ch_abil_mods[sv]
        else:
            currsavemod = 0
        ch_save_mods[sv] = currsavemod

    newchar = Character(name=ch_name, numsessions=0, chartype=ch_type, race=ch_race, subrace=ch_subrace,
        charclass=ch_class, level=ch_level, alignment=ch_align, background=ch_background, xp=0,
        profbonus=ch_pb, ac=ch_ac, initiative=ch_init, speed=ch_speed, size=ch_size, hpmax=ch_hpmax,
        abilityscores=str(ch_abilities), abilitymods=str(ch_abil_mods), savemods=str(ch_save_mods), skillmods=str(ch_skill_mods),
        hitdice=ch_hitdice, darkvision=ch_darkvis, languages=ch_langs, proficiencies=ch_profs, spellclass=ch_spellclass,
        spellability=ch_spellabil, spellsavedc=ch_spelldc, spellatkbonus=ch_spellmod, user_id=current_user.id)
    db.session.add(newchar)
    db.session.commit()
    return render_template('charcreated.html', title='Create Character',
        msg1=congrats, msg2=ask)

@app.route('/viewid', methods=['POST'])
def viewid():
    if request:
        # clear previously stored character id from session
        if session.get('charIdToView'):
            session.pop('charIdToView')
        # save new character id in session
        session['charIdToView'] = int(request.data)
        #print(session.get('charIdToView'))
        return "success"
    return "failure"

# user views details for one character
@app.route('/viewchar', methods=['GET', 'POST'])
@login_required
def viewchar():
    # get id for the character to be viewed
    view_id = session.get('charIdToView')
    if view_id is not None:
        # retrieve the desired character from the db
        char_to_view = Character.query.filter_by(id=view_id).first()
        if char_to_view is not None:
            return render_template('viewchar.html', title='Character Details', viewing=char_to_view)
    return render_template('viewchar.html', title='Character Details')

@app.route('/editid', methods=['POST'])
def editid():
    if request:
        # clear previously stored character id from session
        if session.get('charIdToEdit'):
            session.pop('charIdToEdit')
        # save new character id in session
        session['charIdToEdit'] = int(request.data)
        #print(session.get('charIdToView'))
        return "success"
    return "failure"

# user edits details for one character
@app.route('/editchar', methods=['GET', 'POST'])
@login_required
def editchar():
    # get id for the character to be edited
    edit_id = session.get('charIdToEdit')
    print(edit_id)
    return render_template('editchar.html', title='Edit Character')

# user chooses languages for their character
@app.route('/chooselangs', methods=['GET', 'POST'])
@login_required
def chooselangs():
    existing_langs = 'You know the following languages:'
    choose_langs = 'You can choose additional languages below.'
    return render_template('chooselangs.html', title='Character Options',
        msg1=congrats, msg2=ask)

# display races table
@app.route('/dndraces')
@login_required
def dndraces():
    ddraces = Dndrace.query.all()
    return render_template('dndraces.html', title='D&D Races', allraces=ddraces)

# display traits table
@app.route('/dndtraits')
@login_required
def dndtraits():
    ddtraits = Dndtrait.query.all()
    return render_template('dndtraits.html', title='D&D Traits', alltraits=ddtraits)

# display features table with filtering options
@app.route('/dndfeatures', methods=['GET', 'POST'])
@login_required
def dndfeatures():
    form = FeatureFilterForm()
    if form.is_submitted():
        selected_radio = form.fclass_list.data
        desired_features = Dndfeature.query.filter(Dndfeature.fclass.contains(selected_radio))
        return render_template('dndfeatures.html', title='D&D Features', form=form, selectedfeatures=desired_features)
    ddfeatures = Dndfeature.query.all()
    return render_template('dndfeatures.html', title='D&D Features', form=form, allfeatures=ddfeatures)

# display backgrounds table
@app.route('/dndbackgrounds')
@login_required
def dndbackgrounds():
    dd_bgs = Dndbackground.query.all()
    return render_template('dndbackgrounds.html', title='D&D Backgrounds', allbgs=dd_bgs)

# display equipment table with filtering options
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

# display weapons and armor table with filtering options
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

# display spells table with filtering options
@app.route('/dndspells', methods=['GET', 'POST'])
@login_required
def dndspells():
    form = SpellFilterForm()
    if form.is_submitted():
        level_int = None
        desired_level, desired_class, desired_schools, desired_spells = [], [], [], []

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
