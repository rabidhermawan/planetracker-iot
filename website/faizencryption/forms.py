from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, EmailField, PasswordField, SubmitField, SelectField, SelectMultipleField, FileField, ValidationError
from wtforms.validators import DataRequired, EqualTo

from faizencryption import db
from faizencryption.models import User, UserDocument

class LoginAccountForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('Email doesn\'t exist')

class UpdateAccountForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    submit = SubmitField("Submit")
    
    def validate_name(self, name):
        user = User.query.filter_by(name=name.data).first()
        if user and user.id != current_user.id:
            raise ValidationError('Username is taken. Choose a different username')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and user.id != current_user.id:
            raise ValidationError('Email is taken. Choose a different username')

class RegisterAccountForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat Password')
    submit = SubmitField("Submit")
    
    def validate_name(self, name):
        user = User.query.filter_by(name=name.data).first()
        if user:
            raise ValidationError('Username is taken. Choose a different username')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is taken. Choose a different username')
            
class UploadFileForm(FlaskForm):
    enc_method = SelectField("Encryption Method", 
                           choices=[
                               ('aes_cbc', "AES (CBC)"), 
                               ('des_cbc', "DES (CBC)"), 
                               ('rc4', "RC4")
                               ],
                           validators=[DataRequired()])
    file_upload = FileField("Upload File", validators=[DataRequired()])
    
    submit = SubmitField("Submit")

class ShareForm(FlaskForm):
    users = SelectMultipleField("Select Users to Share With", validators=[DataRequired()])
    submit = SubmitField("Share")