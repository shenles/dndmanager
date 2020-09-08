from flask_wtf import FlaskForm
from wtforms import widgets, RadioField, SelectMultipleField, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User, SpellLevel, SpellClass, SpellSchool

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

class SpellFilterForm(FlaskForm):
    spell_levels = SpellLevel.query.with_entities(SpellLevel.level).all()
    spell_classes = SpellClass.query.with_entities(SpellClass.name).all()
    spell_schools = SpellSchool.query.with_entities(SpellSchool.name).all() 
    lvl_choices = [x[0] for x in spell_levels]
    class_choices = [x[0] for x in spell_classes]
    school_choices = [x[0] for x in spell_schools] 
    level_list = MultiCheckboxField('Level', choices=[(str(l), l) for l in lvl_choices])
    class_list = RadioField('Class', choices=[(c, c) for c in class_choices])
    school_list = MultiCheckboxField('School', choices=[(s, s) for s in school_choices])
    submit = SubmitField('Filter spells')

class EquipFilterForm(FlaskForm):
    equip_categories = ['All Adventuring Gear', 'All Tools', 'All Mounts and Vehicles', 'Artisan\'s Tools', 'Equipment Packs', 'Kits', 'Musical Instrument', 'Gaming Sets', 'Druidic Foci', 'Holy Symbols', 'Standard Gear', 'Ammunition'] 
    category_list = RadioField('Category/Subcategory', choices=equip_categories) 
    submit = SubmitField('Filter equipment')
