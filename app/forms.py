from flask_wtf import FlaskForm
from wtforms import widgets, RadioField, SelectMultipleField, StringField
from wtforms import PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, InputRequired, Optional, Email, EqualTo, Length
from app.models import User, SpellLevel, SpellClass, SpellSchool, Dndclass, Dndrace, Dndsubrace, Dndbackground

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class CreateCharacterForm(FlaskForm):
    class_res = Dndclass.query.with_entities(Dndclass.name).all()
    race_res = Dndrace.query.with_entities(Dndrace.name).all()
    class_options = [x[0] for x in class_res]
    race_options = [x[0] for x in race_res]
    name_box = StringField('Name', validators=[Optional(), Length(max=120)])
    type_options = ['PC (Player character)', 'NPC (Non-player character)']
    type_list = SelectField('Type', choices=type_options)
    races_list = SelectField('Race', choices=race_options)
    classes_list = SelectField('Class', choices=class_options)
    alignment_options = [
                            'Lawful good', 'Neutral good', 'Chaotic good',
                            'Lawful neutral', 'Neutral', 'Chaotic neutral',
                            'Lawful evil', 'Neutral evil', 'Chaotic evil',
                            'Other alignment', 'No alignment'
                        ]
    alignment_list = SelectField('Alignment', choices=alignment_options)
    submit = SubmitField('Submit')

class ChooseSubraceForm(FlaskForm):
    subrace_res = Dndsubrace.query.with_entities(Dndsubrace.name).all()
    allsubraces = [x[0] for x in subrace_res if len(x[0]) > 0]
    options1 = [allsubraces[0], 'None']
    options2 = [allsubraces[1], 'None']
    options3 = [allsubraces[2], 'None']
    options4 = [allsubraces[3], 'None']
    subrace1 = SelectField('Subrace', choices=options1)
    subrace2 = SelectField('Subrace', choices=options2)
    subrace3 = SelectField('Subrace', choices=options3)
    subrace4 = SelectField('Subrace', choices=options4)
    submit = SubmitField('Submit')

class AssignAbilitiesForm(FlaskForm):
    all_abilities = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']
    abilities0 = SelectField('Abilities0', choices=all_abilities)
    abilities1 = SelectField('Abilities1', choices=all_abilities)
    abilities2 = SelectField('Abilities2', choices=all_abilities)
    abilities3 = SelectField('Abilities3', choices=all_abilities)
    abilities4 = SelectField('Abilities4', choices=all_abilities)
    abilities5 = SelectField('Abilities5', choices=all_abilities)
    submit = SubmitField('Submit')

class HalfElfForm(FlaskForm):
    all_abilities = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom']
    abilities = [(x, x) for x in all_abilities]
    increase_list = MultiCheckboxField('Increases', choices=abilities)
    submit = SubmitField('Submit')

class ChooseBgForm(FlaskForm):
    bg_res = Dndbackground.query.with_entities(Dndbackground.name).all()
    all_backgrounds = [x[0] for x in bg_res]
    all_backgrounds.append('None')
    bg_list = RadioField('Backgrounds', choices=all_backgrounds)
    submit = SubmitField('Submit')

# forms for choosing proficiencies
class ChooseProfForm1_1(FlaskForm):
    choices1 = Dndclass.query.filter_by(id=1).first()
    allchoices1 = choices1.profchoices
    listchoices = allchoices1.split(', ')
    listchoices1 = [(x, x) for x in listchoices]
    field1 = MultiCheckboxField('Proficiency options', choices=listchoices1)
    submit = SubmitField('Submit')

class ChooseProfForm1_2(FlaskForm):
    choices1 = Dndclass.query.filter_by(id=2).first()
    allchoices1 = choices1.profchoices
    listchoices = allchoices1.split(', ')
    listchoices1 = [(x, x) for x in listchoices]
    field1 = MultiCheckboxField('Proficiency options', choices=listchoices1)
    submit = SubmitField('Submit')

class ChooseProfForm1_3(FlaskForm):
    choices1 = Dndclass.query.filter_by(id=3).first()
    allchoices1 = choices1.profchoices
    listchoices = allchoices1.split(', ')
    listchoices1 = [(x, x) for x in listchoices]
    field1 = MultiCheckboxField('Proficiency options', choices=listchoices1)
    submit = SubmitField('Submit')

class ChooseProfForm1_4(FlaskForm):
    choices1 = Dndclass.query.filter_by(id=4).first()
    allchoices1 = choices1.profchoices
    listchoices = allchoices1.split(', ')
    listchoices1 = [(x, x) for x in listchoices]
    field1 = MultiCheckboxField('Proficiency options', choices=listchoices1)
    submit = SubmitField('Submit')

class ChooseProfForm1_5(FlaskForm):
    choices1 = Dndclass.query.filter_by(id=5).first()
    allchoices1 = choices1.profchoices
    listchoices = allchoices1.split(', ')
    listchoices1 = [(x, x) for x in listchoices]
    field1 = MultiCheckboxField('Proficiency options', choices=listchoices1)
    submit = SubmitField('Submit')

class ChooseProfForm1_6(FlaskForm):
    choices1 = Dndclass.query.filter_by(id=6).first()
    allchoices1 = choices1.profchoices
    listchoices = allchoices1.split(', ')
    listchoices1 = [(x, x) for x in listchoices]
    field1 = MultiCheckboxField('Proficiency options', choices=listchoices1)
    submit = SubmitField('Submit')

class ChooseProfForm1_7(FlaskForm):
    choices1 = Dndclass.query.filter_by(id=7).first()
    allchoices1 = choices1.profchoices
    listchoices = allchoices1.split(', ')
    listchoices1 = [(x, x) for x in listchoices]
    field1 = MultiCheckboxField('Proficiency options', choices=listchoices1)
    submit = SubmitField('Submit')

class ChooseProfForm1_8(FlaskForm):
    choices1 = Dndclass.query.filter_by(id=8).first()
    allchoices1 = choices1.profchoices
    listchoices = allchoices1.split(', ')
    listchoices1 = [(x, x) for x in listchoices]
    field1 = MultiCheckboxField('Proficiency options', choices=listchoices1)
    submit = SubmitField('Submit')

class ChooseProfForm1_9(FlaskForm):
    choices1 = Dndclass.query.filter_by(id=9).first()
    allchoices1 = choices1.profchoices
    listchoices = allchoices1.split(', ')
    listchoices1 = [(x, x) for x in listchoices]
    field1 = MultiCheckboxField('Proficiency options', choices=listchoices1)
    submit = SubmitField('Submit')

class ChooseProfForm1_10(FlaskForm):
    choices1 = Dndclass.query.filter_by(id=10).first()
    allchoices1 = choices1.profchoices
    listchoices = allchoices1.split(', ')
    listchoices1 = [(x, x) for x in listchoices]
    field1 = MultiCheckboxField('Proficiency options', choices=listchoices1)
    submit = SubmitField('Submit')

class ChooseProfForm1_11(FlaskForm):
    choices1 = Dndclass.query.filter_by(id=11).first()
    allchoices1 = choices1.profchoices
    listchoices = allchoices1.split(', ')
    listchoices1 = [(x, x) for x in listchoices]
    field1 = MultiCheckboxField('Proficiency options', choices=listchoices1)
    submit = SubmitField('Submit')

class ChooseProfForm1_12(FlaskForm):
    choices1 = Dndclass.query.filter_by(id=12).first()
    allchoices1 = choices1.profchoices
    listchoices = allchoices1.split(', ')
    listchoices1 = [(x, x) for x in listchoices]
    field1 = MultiCheckboxField('Proficiency options', choices=listchoices1)
    submit = SubmitField('Submit')

class ChooseProfForm2_1(FlaskForm):
    choices1 = Dndclass.query.filter_by(id=2).first()
    allchoices1 = choices1.profchoices_two
    listchoices = allchoices1.split(', ')
    listchoices1 = [(x, x) for x in listchoices]
    field1 = MultiCheckboxField('Proficiency options', choices=listchoices1)
    submit = SubmitField('Submit')

class ChooseProfForm2_2(FlaskForm):
    choices1 = Dndclass.query.filter_by(id=6).first()
    allchoices1 = choices1.profchoices_two
    listchoices = allchoices1.split(', ')
    listchoices1 = [(x, x) for x in listchoices]
    field1 = MultiCheckboxField('Proficiency options', choices=listchoices1)
    submit = SubmitField('Submit')

class ChooseProfForm3_1(FlaskForm):
    choices1 = Dndclass.query.filter_by(id=6).first()
    allchoices1 = choices1.profchoices_three
    listchoices = allchoices1.split(', ')
    listchoices1 = [(x, x) for x in listchoices]
    field1 = MultiCheckboxField('Proficiency options', choices=listchoices1)
    submit = SubmitField('Submit')

class ChooseProfForm4(FlaskForm):
    choices1 = Dndrace.query.filter_by(id=2).first()
    allchoices1 = choices1.startprofoptions
    listchoices = allchoices1.split(', ')
    listchoices1 = [(x, x) for x in listchoices]
    field1 = MultiCheckboxField('Proficiency options', choices=listchoices1)
    submit = SubmitField('Submit')

# forms for choosing languages
class ChooseLangForm1_1(FlaskForm):
    choices1 = Dndrace.query.filter_by(id=5).first() # Half-Elf
    allchoices1 = choices1.langoptions
    listchoices = allchoices1.split(', ')
    listchoices.append('Other')
    listchoices1 = [(x, x) for x in listchoices]
    field1 = MultiCheckboxField('Language options', choices=listchoices1)
    submit = SubmitField('Submit')

class ChooseLangForm1_2(FlaskForm):
    choices1 = Dndrace.query.filter_by(id=8).first() # Human
    allchoices1 = choices1.langoptions
    listchoices = allchoices1.split(', ')
    listchoices.append('Other')
    listchoices1 = [(x, x) for x in listchoices]
    field1 = MultiCheckboxField('Language options', choices=listchoices1)
    submit = SubmitField('Submit')

# forms for choosing equipment

class SpellFilterForm(FlaskForm):
    spell_levels = SpellLevel.query.with_entities(SpellLevel.level).all()
    spell_classes = SpellClass.query.with_entities(SpellClass.name).all()
    spell_schools = SpellSchool.query.with_entities(SpellSchool.name).all() 
    lvl_choices = [x[0] for x in spell_levels]
    class_choices = [x[0] for x in spell_classes]
    school_choices = [x[0] for x in spell_schools] 
    level_list = RadioField('Level', choices=[(str(l), l) for l in lvl_choices])
    class_list = RadioField('Class', choices=[(c, c) for c in class_choices])
    school_list = MultiCheckboxField('School', choices=[(s, s) for s in school_choices])
    submit = SubmitField('Submit')

class FeatureFilterForm(FlaskForm):
    fclasses = ['Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 'Monk', 'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 'Warlock', 'Wizard']
    fclass_list = RadioField('Class', choices=fclasses) 
    submit = SubmitField('Submit')

class EquipFilterForm(FlaskForm):
    equip_categories = ['All Adventuring Gear', 'All Tools', 'All Mounts and Vehicles', 'Artisan\'s Tools', 'Equipment Packs', 'Kits', 'Musical Instrument', 'Gaming Sets', 'Druidic Foci', 'Holy Symbols', 'Standard Gear', 'Ammunition'] 
    category_list = RadioField('Category/Subcategory', choices=equip_categories) 
    submit = SubmitField('Submit')

class WeaponArmorFilterForm(FlaskForm):
    weaponarmor_categories = ['All Weapons', 'All Armor', 'Simple Weapons', 'Martial Weapons', 'Melee Weapons', 'Ranged Weapons', 'Two-Handed Weapons', 'Thrown Weapons', 'Monk Weapons'] 
    category_list = RadioField('Category', choices=weaponarmor_categories) 
    submit = SubmitField('Submit')
