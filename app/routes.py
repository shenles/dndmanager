from flask import request, render_template, flash, redirect, url_for, session
from werkzeug.urls import url_parse
from app import app, db
from flask_login import login_required
from app.forms import LoginForm, RegistrationForm, EquipFilterForm, WeaponArmorFilterForm, SpellFilterForm, CreateCharacterForm, AssignAbilitiesForm
from flask_login import current_user, login_user, logout_user
from app.models import User, Character, Dndclass, Dndspell, Dndrace, Dndequipment

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

@app.route('/createcharacter', methods=['GET', 'POST'])
@login_required
def createcharacter():
    form = CreateCharacterForm()
    if form.is_submitted():
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
        # store new session data
        session['characterRace'] = char_race
        session['characterClass'] = char_class
        session['characterAlign'] = char_align
        return render_template('createcharacter.html', title='Create Character',
            class_pick=form.classes_list.data, race_pick=form.races_list.data,
            align_pick=form.alignment_list.data, message='Creating your character:')
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
        session['roll0'] = assign_0
        session['roll1'] = assign_1
        session['roll2'] = assign_2
        session['roll3'] = assign_3
        session['roll4'] = assign_4
        session['roll5'] = assign_5
        return "success"
    return "failure"

@app.route('/createcharacter2', methods=['GET', 'POST'])
@login_required
def createcharacter2():
    form1 = AssignAbilitiesForm()
    if form1.is_submitted():
        # clear previously existing ability scores
        '''
        if session.get('strength'):
            session.pop('strength')
        if session.get('dexterity'):
            session.pop('dexterity')
        if session.get('constitution'):
            session.pop('constitution')
        if session.get('intelligence'):
            session.pop('intelligence')
        if session.get('wisdom'):
            session.pop('wisdom')
        if session.get('charisma'):
            session.pop('charisma')
        '''
        return render_template('createcharacter2.html', title='Create Character')
    else:
        curr_result = None
        if session.get('characterRace'):
            curr_race = session['characterRace']
            curr_result = Dndrace.query.filter_by(name=curr_race).first()
        #print(session.get('characterRace'))
        #print(session.get('characterClass'))
        #print(session.get('characterAlign'))
        #print(session.get('roll0'))
        #print(session.get('roll1'))
        #print(session.get('roll2'))
        #print(session.get('roll3'))
        #print(session.get('roll4'))
        #print(session.get('roll5'))
        return render_template('createcharacter2.html', title='Create Character',
                myrace=session.get('characterRace'), myclass=session.get('characterClass'),
                myalign=session.get('characterAlign'), assign0=session.get('roll0'),
                assign1=session.get('roll1'), assign2=session.get('roll2'), assign3=session.get('roll3'),
                assign4=session.get('roll4'), assign5=session.get('roll5'), form1=form1, thisrace=curr_result)

@app.route('/dndraces')
@login_required
def dndraces():
    ddraces = Dndrace.query.all()
    return render_template('dndraces.html', title='D&D Races', allraces=ddraces)

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
