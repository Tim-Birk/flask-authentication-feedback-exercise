from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, TextAreaField, BooleanField
from wtforms.validators import InputRequired, URL, NumberRange, Optional

class AddUserForm(FlaskForm):
    """Form for adding user."""

    # name = StringField("Pet Name", validators=[InputRequired()])
    # species = SelectField("Species", choices=[("dog","Dog"), ("cat","Cat"), ("porcupine","Porcupine")])
    # photo_url = StringField("Photo URL", validators=[Optional(), URL()])
    # age = IntegerField("Age", validators=[NumberRange(min=0, max=30)])
    # notes = TextAreaField("Notes")
    # available = BooleanField("Available")