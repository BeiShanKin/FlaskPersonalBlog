from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required


class NameForm(Form):
    name = StringField('What is your name ?', validators=[Required()])
    password = PasswordField(
        'Please input your password', validators=[Required()])
    submit = SubmitField('Submit')
