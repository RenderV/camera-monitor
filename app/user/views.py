from flask import redirect, request, jsonify, Blueprint, session, render_template, url_for
import bcrypt
from app.user.models import User
from app.user.forms import RegisterForm, LoginForm

user_bp = Blueprint('user', __name__, url_prefix='/user/')
def gen_pass(passw):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(passw.encode('utf-8'), salt)

def start_session(user):
    user = user.asdict()
    session['logged_in'] = True
    session['user'] = user
    return redirect(url_for('home'))


@user_bp.route('/entrar/', methods=["GET", "POST"])
def signin():
    lform = LoginForm()
    if request.method == "POST" and lform.validate():
        email = lform.email.data
        password = lform.password.data
        user = User.objects(email=email).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
            return start_session(user)
    return render_template('login.html', lform=lform, page_name="Login - CV SECURITY")

@user_bp.route('/cadastrar/', methods=['GET', 'POST'])
def signup():
    sform = RegisterForm()
    if request.method == 'POST' and sform.validate():
        username = sform.name.data
        email = sform.email.data
        password = sform.password.data

        password = gen_pass(password)

        user = User(
            username=username,
            email=email,
            password=password
        )
        
        user.save()

        return start_session(user)

    return render_template('signup.html', sform=sform, page_name="Cadastro - CV SECURITY")

@user_bp.route('/signout/')
def signout():
    session.clear()
    return redirect('/')
