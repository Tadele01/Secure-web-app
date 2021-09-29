from wtforms import Form, BooleanField, StringField, PasswordField, SubmitField, validators
from flask_wtf import FlaskForm
class RegistrationForm(FlaskForm):
    username = StringField('User Name ', [validators.DataRequired( message='Username is required'),
                                        validators.Length(min=4, max=25,  message='Username Length invalid')])
    email = StringField('Email  ', [ validators.DataRequired( message='Email is required'),
                                   validators.Email()])
    password = PasswordField('Password  ', [
        validators.Length(min=6, max=12, message='Password Length invalid'),
        validators.DataRequired( message='Password is required'),
        ])
    confirm = PasswordField('Confirm Password  ', [
        validators.EqualTo('password', message='Password must match')
    ])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('User Name ', [validators.DataRequired( message='Username or Password incorrect'),
                                        validators.Length(min=4, max=25,  message='Username or Password incorrect')])
    password = PasswordField('Password  ', [
        validators.Length(min=6, max=12, message='Username or Password incorrect'),
        validators.DataRequired( message='Username or Password incorrect'),
        ])
    submit = SubmitField('Login')


