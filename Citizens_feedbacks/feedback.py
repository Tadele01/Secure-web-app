from flask import (Blueprint, redirect, render_template, flash, url_for, g, request)
from werkzeug.exceptions import abort
from Citizens_feedbacks.auth import login, login_required
from werkzeug.utils import secure_filename
from Citizens_feedbacks.db import get_db
import os 
ALLOWED_EXTENSIONS = {'pdf'}
UPLOAD_FOLDER = '/home/tade/Downloads/files'
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
bp = Blueprint('feedback', __name__)

@bp.route('/')
def index():
    if g.user:
        return redirect(url_for('feedback.logged_as_user'))
    return render_template('feedback/index.html')

@bp.route('/user')
@login_required
def logged_as_user():
    db = get_db()
    if g.user:
        role = g.user['role']
        if role == 'admin':
            feedbacks = db.execute(
                                "SELECT p.id, title, body, created, author_id, username, is_active"
                                " FROM PETITIONS p JOIN USER u ON p.author_id = u.id"
                                " ORDER BY created DESC"
                            ).fetchall()

            return render_template('feedback/admin_dashboard.html', feedbacks=feedbacks)
        else:
            id = g.user['id']
            feedbacks = db.execute(
                                "SELECT p.id, title, body, created, author_id, username"
                                " FROM PETITIONS p JOIN USER u ON p.author_id = u.id"
                                " WHERE author_id = ?", (id,)
                            ).fetchall()
        
            return render_template('feedback/citizen_index.html', feedbacks=feedbacks)

    return redirect(url_for('index'))


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if g.user:
        if g.user['role'] == 'admin':
            return render_template('404.html')
    if request.method == 'POST':
        title = request.form.get('title', None)
        body = request.form.get('body', None)
        error = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = str(g.user['id']) + '_' + title + '.pdf'
                file.save(os.path.join(UPLOAD_FOLDER, filename))
            elif file:
                error = 'File not Supported'
        if not title:
            error = 'Title is required.'

        if error:
            flash(error)
        else: 
            db = get_db()
            db.execute(
                'INSERT INTO petitions (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('feedback.logged_as_user'))

    return render_template('feedback/create.html')

def get_post(id, check_author=True):
    petition = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM petitions p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if petition is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and petition['author_id'] != g.user['id']:
        abort(403)

    return petition

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    petition = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        title = request.form.get('title', None)
        body = request.form.get('body', None)
        error = None
        if not title:
            error = 'Title is required.'

        if error:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE petitions SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('feedback.logged_as_user'))

    return render_template('feedback/update.html', petition=petition)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM petitions WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('feedback.logged_as_user'))

@bp.route('/<int:author_id>/ban/<int:is_active>', methods=('GET', 'POST'))
@login_required
def ban_user(author_id, is_active):
    db = get_db()
    db.execute('UPDATE USER SET is_active = ? WHERE id = ?', (int(not is_active), author_id))
    db.commit()
    return redirect(url_for('feedback.logged_as_user'))