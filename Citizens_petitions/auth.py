import functools
from flask import (Blueprint, redirect, render_template, flash, g, 
                    request, session, url_for)
from werkzeug import useragents
from werkzeug.security import check_password_hash, generate_password_hash
from Citizens_petitions.db import get_db
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required !'
        elif not password:
            error = 'Password is required !'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)", 
                        (username, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already existed"
            else:
                return redirect(url_for('auth.login'))
        flash(error)
    
    return render_template('auth/register.html')
    
