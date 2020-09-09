from flask import request, render_template, flash, redirect, url_for
from werkzeug.urls import url_parse
from app import app, db
from flask_login import login_required
from app.forms import LoginForm, RegistrationForm, EquipFilterForm, WeaponArmorFilterForm, SpellFilterForm
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
    if not current_user:
        return render_template('dndclasses.html', title='Classes')
    ddclasses = Dndclass.query.all() 
    return render_template('dndclasses.html', title='D&D Classes', allclasses=ddclasses)

@app.route('/createcharacter')
@login_required
def createcharacter():
    if not current_user:
        return render_template('createcharacter.html', title='Create Character')
    return render_template('createcharacter.html', title='Create a D&D Character', message='hello!')

@app.route('/dndraces')
@login_required
def dndraces():
    if not current_user:
        return render_template('dndraces.html', title='Races')
    ddraces = Dndrace.query.all()
    return render_template('dndraces.html', title='D&D Races', allraces=ddraces)

@app.route('/dndequipment', methods=['GET', 'POST'])
@login_required
def dndequipment():
    if not current_user:
        return render_template('dndequipment.html', title='Equipment')
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
    if not current_user:
        return render_template('dndweaponsarmor.html', title='Weapons & Armor')
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
    if not current_user:   
        return render_template('dndspells.html', title='Spells')
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
