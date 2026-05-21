from flask import Flask, render_template, request, redirect, url_for, jsonify, g
from werkzeug.utils import secure_filename
import sqlite3
import os
import re

app = Flask(__name__)

app.config['DATABASE'] = os.path.join(app.root_path, 'database.db')
app.config['SECRET_KEY'] = 'dev-secret-key'

# STATUS LIST
DEFAULT_STATUSES = [
    'Office',
    'Meeting',
    'Site',
    'Training',
    'Business Trip',
    'MC',
    'On Leave',
    'Remote'
]

# DEFAULT STAFF
DEFAULT_STAFF = [

    (
        'Yusni',
        'yusni.kamludian@technipfmc.com',
        'Office'
    ),

    (
        'Azmie',
        'mohamadazmi.rahim@external.technipfmc.com',
        'Meeting'
    ),

    (
        'Sarah',
        'sitisaharah.zahari@technipfmc.com',
        'Remote'
    ),

    (
        'Abdullah',
        'abdullahi.ubandomaabubakar@technipfmc.com',
        'Training'
    )
]

LOGO_FILENAME = 'technipfmc.png'

IMAGE_FOLDER = os.path.join(
    app.root_path,
    'static',
    'images'
)

STORAGE_FOLDER = os.path.join(
    app.root_path,
    'static',
    'storage'
)


# DATABASE CONNECTION
def get_db():

    db = getattr(g, '_database', None)

    if db is None:

        db = g._database = sqlite3.connect(
            app.config['DATABASE']
        )

        db.row_factory = sqlite3.Row

    return db


# CLOSE DATABASE
@app.teardown_appcontext
def close_db(exception):

    db = getattr(g, '_database', None)

    if db is not None:
        db.close()


# CREATE DATABASE TABLES
def init_db():

    db = get_db()

    # STAFF TABLE
    db.execute(

        'CREATE TABLE IF NOT EXISTS staff ('
        'id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'name TEXT UNIQUE NOT NULL, '
        'email TEXT NOT NULL, '
        'status TEXT NOT NULL'
        ')'
    )

    # SLIDES TABLE
    db.execute(

        'CREATE TABLE IF NOT EXISTS slides ('
        'id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'filename TEXT UNIQUE NOT NULL, '
        'active INTEGER NOT NULL DEFAULT 1'
        ')'
    )

    db.commit()


# INSERT DEFAULT DATA
def seed_defaults():

    db = get_db()

    row = db.execute(
        'SELECT COUNT(*) AS count FROM staff'
    ).fetchone()

    # INSERT STAFF ONLY IF EMPTY
    if row is None or row['count'] == 0:

        for name, email, status in DEFAULT_STAFF:

            db.execute(

                'INSERT OR IGNORE INTO staff '
                '(name, email, status) '
                'VALUES (?, ?, ?)',

                (name, email, status)
            )

    # LOAD SLIDES AUTOMATICALLY
    supported_files = [

        f for f in os.listdir(IMAGE_FOLDER)

        if f.lower().endswith(
            ('.png', '.jpg', '.jpeg', '.gif')
        )

        and f != LOGO_FILENAME
    ]

    for filename in sorted(supported_files):

        db.execute(

            'INSERT OR IGNORE INTO slides '
            '(filename, active) VALUES (?, 1)',

            (filename,)
        )

    db.commit()


# SETUP DATABASE
def setup_database():

    init_db()
    seed_defaults()
    os.makedirs(STORAGE_FOLDER, exist_ok=True)


with app.app_context():
    setup_database()


# GET STAFF
def get_staff():

    db = get_db()

    return db.execute(
        'SELECT * FROM staff ORDER BY id'
    ).fetchall()


# GET SLIDES
def get_slide_records():

    db = get_db()

    return db.execute(
        'SELECT filename FROM slides '
        'WHERE active = 1 ORDER BY id'
    ).fetchall()


def get_storage_files():

    os.makedirs(STORAGE_FOLDER, exist_ok=True)

    return sorted(
        f for f in os.listdir(STORAGE_FOLDER)
        if os.path.isfile(os.path.join(STORAGE_FOLDER, f))
    )


# TV DASHBOARD
@app.route('/')
def tv_dashboard():

    staff = get_staff()

    supported_files = [

        f for f in os.listdir(IMAGE_FOLDER)

        if f.lower().endswith(
            ('.png', '.jpg', '.jpeg', '.gif')
        )

        and f != LOGO_FILENAME
    ]

    def slide_key(name):

        match = re.search(r'(\d+)', name)

        return int(match.group(1)) if match else name.lower()

    supported_files.sort(key=slide_key)

    slides = [

        {
            'src': url_for(
                'static',
                filename='images/' + filename
            )
        }

        for filename in supported_files
    ]
    return render_template(
        'tv.html',
        staff=staff,
        slides=slides
    )


# STATUS PAGE
@app.route('/status')
def status_page():

    staff = get_staff()

    return render_template(
        'status.html',
        staff=staff,
        statuses=DEFAULT_STATUSES
    )


# API STATUS UPDATE
@app.route('/api/status/<int:staff_id>', methods=['POST'])
def api_update_status(staff_id):

    data = request.get_json(silent=True) or request.form

    status = data.get('status', '').strip()

    if status not in DEFAULT_STATUSES:

        return jsonify(
            success=False,
            message='Invalid status provided.'
        ), 400

    db = get_db()

    row = db.execute(

        'SELECT name FROM staff WHERE id = ?',

        (staff_id,)
    ).fetchone()

    if row is None:

        return jsonify(
            success=False,
            message='Staff member not found.'
        ), 404

    db.execute(

        'UPDATE staff SET status = ? WHERE id = ?',

        (status, staff_id)
    )

    db.commit()

    return jsonify(
        success=True,
        status=status,
        name=row['name']
    )


# ADMIN PAGE
@app.route('/admin', methods=['GET', 'POST'])
def admin_page():

    db = get_db()

    if request.method == 'POST':

        action = request.form.get('action', '')

        # ADD STAFF
        if action == 'add':

            name = request.form.get('name', '').strip()

            email = request.form.get('email', '').strip()

            status = request.form.get(
                'status',
                DEFAULT_STATUSES[0]
            )

            if name and email and status in DEFAULT_STATUSES:

                db.execute(

                    'INSERT OR IGNORE INTO staff '
                    '(name, email, status) '
                    'VALUES (?, ?, ?)',

                    (name, email, status)
                )

                db.commit()

        # EDIT STATUS
        elif action == 'edit':

            staff_id = request.form.get('staff_id')

            status = request.form.get(
                'status',
                DEFAULT_STATUSES[0]
            )

            if staff_id and status in DEFAULT_STATUSES:

                db.execute(

                    'UPDATE staff SET status = ? '
                    'WHERE id = ?',

                    (status, staff_id)
                )

                db.commit()

        # DELETE STAFF
        elif action == 'delete':

            staff_id = request.form.get('staff_id')

            if staff_id:

                db.execute(

                    'DELETE FROM staff WHERE id = ?',

                    (staff_id,)
                )

                db.commit()

        # UPLOAD RESOURCE
        elif action == 'upload':

            upload_file = request.files.get('file')

            if upload_file and upload_file.filename:
                filename = secure_filename(upload_file.filename)
                if filename:
                    os.makedirs(STORAGE_FOLDER, exist_ok=True)
                    upload_file.save(os.path.join(STORAGE_FOLDER, filename))

        # DELETE STORAGE FILE
        elif action == 'delete-file':

            filename = request.form.get('filename', '').strip()
            filename = secure_filename(filename)

            if filename:
                path = os.path.join(STORAGE_FOLDER, filename)
                if os.path.exists(path) and os.path.isfile(path):
                    os.remove(path)

        return redirect(url_for('admin_page'))

    staff = get_staff()
    storage_files = get_storage_files()

    return render_template(
        'admin.html',
        staff=staff,
        statuses=DEFAULT_STATUSES,
        storage_files=storage_files
    )


if __name__ == '__main__':
    app.run(debug=True)