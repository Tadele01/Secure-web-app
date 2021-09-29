import functools
from flask import (Blueprint, redirect, render_template, flash, g, 
                    request, session, url_for)
from werkzeug import useragents
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import form
from Citizens_feedbacks.db import get_db
from Citizens_feedbacks.form_validator import RegistrationForm, LoginForm
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    registeration_form = RegistrationForm()
    if registeration_form.validate_on_submit():
        db = get_db()
        error = None
        username = ''.join(e for e in registeration_form.username.data if e.isalnum()) 
        email = ''.join(e for e in registeration_form.email.data if e.isalnum()) 
        password = ''.join(e for e in registeration_form.password.data if e.isalnum()) 
        if username != registeration_form.username.data or email != registeration_form.email.data or \
            password != registeration_form.password.data:
            error = "Some Fields Contain Special Characters !"
        if not error:
            try:
                db.execute(
                    "INSERT INTO user (username, email, password) VALUES (?, ?, ?)", 
                        (username, email, 
                        generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {registeration_form.username.data} is already existed"
            else:
                return redirect(url_for('auth.login'))
        flash(error)
    else:
        for error, msg in registeration_form.errors.items():
            flash(''.join(msg))
    return render_template('auth/register.html', form=registeration_form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        db = get_db()
        error = None
        user = db.execute('SELECT * FROM user WHERE username = ?', (login_form.username.data, )).fetchone()
        if user is None:
            error = "User does not exists"
        elif not check_password_hash(user['password'], login_form.password.data):
            error = "Username or Password incorrect"
        elif user['role'] == 'admin':
                session.clear()
                session['user_id'] = user['id']
                return redirect(url_for('feedback.logged_as_user'))
        elif user['is_active'] == 0:
            error = 'User is banned contact the adminstrator !'
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('feedback.logged_as_user'))
        
        flash(error)
    else:
        for error, msg in login_form.errors.items():
            flash(''.join(msg))
    return render_template('auth/login.html', form=login_form)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute("SELECT * FROM user WHERE id = ?", (user_id, )).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

