from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, ValidationError
import mongoengine
from wtforms.validators import DataRequired
from .models import User
import bcrypt

def validate_password(form, field):
    password = form.password.data
    email = form.email.data
    user = User.objects(email=email).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
        return
    raise ValidationError("Usuário ou senha inválidos.")

def validate_email(form, field):
    email = field.data
    if User.objects(email=email).first():
        raise ValidationError("Email já existe na base de dados.")
    user = User(email=email)

def validate_user(form, field):
    username = form.name.data
    email = form.email.data
    password = form.password.data
    #solução temporária
    user = User(
        username=username,
        email=email,
        password=b''
    )
    try:
        user.validate()
    except mongoengine.ValidationError as e:
        raise ValidationError("Algo deu errado. Por favor, tente novamente.")

class RegisterForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), validate_email, validate_user])
    password = PasswordField('Senha', validators=[DataRequired()])
    
class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired(), validate_password])