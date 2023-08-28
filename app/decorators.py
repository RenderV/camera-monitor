from functools import wraps
from flask import session, redirect, abort, jsonify
from app.user.models import User
from mongoengine import DoesNotExist

def redirect_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('logged_in'):
            return f(*args, **kwargs)
        else:
            return redirect('/')
    return wrap

def api_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            abort(403)
    return wrap

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            user = User.objects(email=session['user']['email']).first()
            if user.admin:
                return f(*args, **kwargs)
        except (DoesNotExist, AttributeError, KeyError):
            pass
        abort(403)
    return wrap