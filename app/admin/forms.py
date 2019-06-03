from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_wtf.file import FileField, FileRequired
from app.models import User

class UserForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    address = StringField('address')
    email = StringField('email')
    submit = SubmitField('Add User')

class ImageForm(FlaskForm):
    title = StringField('title', validators= [DataRequired()])
    image = FileField('image', validators=[FileRequired()])
    description = TextAreaField('description', validators=[DataRequired()])
    submit = SubmitField('Add Image')

class CommentForm(FlaskForm):
    content = TextAreaField('content', validators=[DataRequired()])
    submit = SubmitField('Add Comment')
