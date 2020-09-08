from flask import request, render_template, flash, redirect, url_for
from werkzeug.urls import url_parse
from app import app, db
from flask_login import login_required
from app.forms import LoginForm, RegistrationForm, SpellFilterForm, EquipFilterForm, WeaponArmorFilterForm
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
def dndclasses():
    if not current_user:
        return render_template('dndclasses.html', title='Classes')
    ddclasses = Dndclass.query.all() 
    return render_template('dndclasses.html', title='D&D Classes', allclasses=ddclasses)

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
    if form.validate_on_submit():
        level_ints = [int(l) for l in form.level_list.data] 
        desired_levels = Dndspell.query.filter(Dndspell.level.in_(level_ints)).all() 
        desired_schools = Dndspell.query.filter(Dndspell.school.in_(form.school_list.data)).all()
        desired_class = Dndspell.query.filter(Dndspell.casters.contains(form.class_list.data)) 

        desired_levels_list = list(desired_levels)
        desired_schools_list = list(desired_schools)
        desired_class_list = list(desired_class)

        if len(desired_levels_list) > 0 and (len(desired_schools_list) > 0 and len(desired_class_list) > 0):
            desired_spells = intersection(desired_levels_list, desired_class_list)
            desired_spells = intersection(desired_spells, desired_schools_list)
        elif len(desired_levels_list) == 0 and (len(desired_schools_list) > 0 and len(desired_class_list) > 0):
            desired_spells = intersection(desired_schools_list, desired_class_list) 
        elif len(desired_levels_list) > 0 and (len(desired_schools_list) == 0 and len(desired_class_list) > 0):
            desired_spells = intersection(desired_levels_list, desired_class_list)
        elif len(desired_levels_list) > 0 and (len(desired_schools_list) > 0 and len(desired_class_list) == 0):
            desired_spells = intersection(desired_levels_list, desired_schools_list)
        elif len(desired_levels_list) == 0 and (len(desired_schools_list) == 0 and len(desired_class_list) > 0):
            desired_spells = desired_class_list
        elif len(desired_levels_list) == 0 and (len(desired_schools_list) > 0 and len(desired_class_list) == 0):
            desired_spells = desired_schools_list
        else:
            desired_spells = []

        return render_template('dndspells.html', title='Spells', form=form, lvl_data=form.level_list.data, class_data=form.class_list.data, school_data=form.school_list.data, selected_spells=desired_spells)  

    else:
        if form.is_submitted():
            level_ints = [int(l) for l in form.level_list.data]
            if len(level_ints) > 0:
                desired_levels = Dndspell.query.filter(Dndspell.level.in_(level_ints)).all()
                return render_template('dndspells.html', title='Spells', form=form, lvl_data=form.level_list.data, class_data=form.class_list.data, school_data=form.school_list.data, selected_spells=desired_levels)
            elif len(list(form.school_list.data)) > 0:
                desired_schools = Dndspell.query.filter(Dndspell.school.in_(form.school_list.data)).all()
                return render_template('dndspells.html', title='Spells', form=form, lvl_data=form.level_list.data, class_data=form.class_list.data, school_data=form.school_list.data, selected_spells=desired_schools) 
            else:
                ddspells = Dndspell.query.all()
                return render_template('dndspells.html', title='Spells', form=form, allspells=ddspells)

    ddspells = Dndspell.query.all()
    return render_template('dndspells.html', title='Spells', form=form, allspells=ddspells)
