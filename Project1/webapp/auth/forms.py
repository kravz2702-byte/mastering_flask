from flask_wtf import FlaskForm as Form, recaptcha
from flask_wtf.recaptcha.fields import RecaptchaField
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, URL 
from .models import User


class LoginForm(Form):
    username = StringField('Username', [DataRequired(), Length(255)])
    password = PasswordField('Password', [DataRequired()])
    remember = BooleanField('Remember Me')

    def validate(self):
        check_validate = super(LoginForm, self).validate()

        #If our validators do not pass
        if not check_validate:
            return False
        #Does our user exist
        user = User.query.filter_by(username=self.username.data).first()
        if not user:
            self.username.errors.append('Invalid username or password')
            return False
        
        #Do the password match
        if not user.check_password(self.password.data):
            self.password.errors.append('Invalid username or password')
        return True

class RegisterForm(Form):
    username = StringField('Username', [Length(255), DataRequired()])
    password = PasswordField('Password', [DataRequired(), Length(min=8)])
    confirm = PasswordField('Confirm Password', [DataRequired(), EqualTo('password')])
    recaptcha = RecaptchaField()
    def validate(self):
        check_validate = super(RegisterForm, self).__init__()
        #if our validators do not pass
        if not check_validate:
            return False
        user = User.query.filter_by(self.username.data).first()
        #if the username already being used
        if user:
            self.username.errors.append(
                'USer with this name already exists'
            )
            return False
        return True
