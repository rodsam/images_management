from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegiForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password',validators=[DataRequired()])
    password_check = PasswordField('password_check', validators=[DataRequired(), EqualTo('password')])
    address = StringField('address')
    email = StringField('email', validators=[Email()])
    submit = SubmitField('Register')