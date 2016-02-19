"""
"""

import os
import json
import datetime
import random
import zipfile
import re
import sumsparser as parser
from dateutil.parser import parse as date_parse

from werkzeug.contrib.profiler import ProfilerMiddleware
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
    abort
)
from flask.ext.stormpath import (
    StormpathManager,
    User,
    login_required,
    login_user,
    logout_user,
    user as stormpath_user,
)
from flask.ext.sqlalchemy import SQLAlchemy
from stormpath.error import Error as StormpathError
from werkzeug import secure_filename

app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS'))
# app.config['PROFILE'] = True
# app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
db = SQLAlchemy(app)
stormpath_manager = StormpathManager(app)

from models import Datasets, Studies, StudyUploads, DataPoints, Notes, Users, StudyUsers, UserLabels, LabelledDatasets

SUBSET_SIZE = datetime.timedelta(7)
# Website


@app.route('/')
def index():
    """Basic home page."""
    return render_template('index.html')

@app.route('/hi')
def hi():
    """New home page."""
    return render_template('hi.html')

@app.route('/eula')
def eula():
    """Basic EULA page."""
    return render_template('eula.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    This view allows a user to register for the site.

    This will create a new User in Stormpath, and then log the user into their
    new account immediately (no email verification required).
    """
    if request.method == 'GET':
        return render_template('register.html')

    try:
        # Create a new Stormpath User.
        _user = stormpath_manager.application.accounts.create({
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'given_name': 'John',
            'surname': 'Doe',
        })
        _user.__class__ = User
    except StormpathError, err:
        # If something fails, we'll display a user-friendly error message.
        return render_template('register.html', error=err.message['message'])

    login_user(_user, remember=True)

    # add user to internal DB
    user = Users(stormpath_user)
    db.session.add(user)
    db.session.commit()

    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    This view logs in a user given an email address and password.

    This works by querying Stormpath with the user's credentials, and either
    getting back the User object itself, or an exception (in which case well
    tell the user their credentials are invalid).

    If the user is valid, we'll log them in, and store their session for later.
    """
    if request.method == 'GET':
        return render_template('login.html')

    try:
        _user = User.from_login(
            request.form.get('email'),
            request.form.get('password'),
        )
    except StormpathError, err:
        return render_template('login.html', error=err.message['message'])

    login_user(_user, remember=True)
    print stormpath_user.get_id()
    user = Users.from_stormpath(stormpath_user)
    print user.id
    return redirect(request.args.get('next') or url_for('dashboard'))


@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    page = int(request.args.get('page') or 1)
    user = Users.from_stormpath(stormpath_user)
    mystudies = user.studies().filter(StudyUsers.role == "owner").all()
    tolabel = user.studies().filter(StudyUsers.role == "labeller").all()
    return render_template('dashboard.html',
                           mystudies=mystudies,
                           tolabel=tolabel
                           )


@app.route('/new_study', methods=['POST'])
@login_required
def new_study():
    study = Studies(request.form['title'])
    db.session.add(study)
    user = Users.from_stormpath(stormpath_user)
    study.add_user(user, "owner")
    study.add_user(user, "labeller")
    return redirect(url_for('study', study_id=study.id))


@app.route('/label_study/<study_id>', methods=['GET'])
@login_required
def label_study(study_id):
    study = Studies.query.get(study_id)
    user = Users.from_stormpath(stormpath_user)
    if not study.is_labeller(user):
        abort(401)

    first_dataset = study.datasets\
        .order_by(Datasets.created_at.desc())\
        .first()

    return redirect(url_for('dataset', dataset_id=first_dataset.id, mode="label"))


@app.route('/study/<study_id>', methods=['GET'])
@login_required
def study(study_id):
    study = Studies.query.get(study_id)
    user = Users.from_stormpath(stormpath_user)
    if not study.is_owner(user):
        abort(401)

    page = int(request.args.get('page') or 1)

    datasets = study.datasets\
        .order_by(Datasets.created_at.desc())\
        .paginate(page, per_page=15)

    study.users.filter_by(role="labeller").all()
    labellers = Users.query.\
        filter(study.is_labeller(Users)).\
        all()

    labellers = study.labellers()
    users = labellers.all()
    notusers = Users.query.except_(labellers).all()

    return render_template('study.html',
                           study=study,
                           datasets=datasets.items,
                           pagination=datasets,
                           users=users,
                           notusers=notusers,
                           uploads=study.uploads)


@app.route('/delete_study/<study_id>', methods=['GET'])
@login_required
def delete_study(study_id):
    study = Studies.query.get(study_id)
    user = Users.from_stormpath(stormpath_user)
    if not study.is_owner(user):
        abort(401)

    study.delete()

    return redirect(url_for('dashboard'))


@app.route('/delete_dataset/<dataset_id>', methods=['GET'])
@login_required
def delete_dataset(dataset_id):
    dataset = Datasets.query.get(dataset_id)
    study = dataset.study
    user = Users.from_stormpath(stormpath_user)
    if not study.is_owner(user):
        abort(401)

    # db.session.delete(dataset)
    # db.session.commit()
    dataset.delete()
    return redirect(url_for('study', study_id=study.id))


@app.route('/add_study_labeller/<study_id>', methods=['GET'])
@login_required
def add_study_labeller(study_id):

    study = Studies.query.get(study_id)
    user = Users.from_stormpath(stormpath_user)
    if not study.is_owner(user):
        abort(401)

    user_id = request.args.get('user_id')
    study_user = Users.query.get(user_id)
    study.add_user(study_user, "labeller")
    return redirect(url_for('study', study_id=study.id))


@app.route('/dataset/<dataset_id>', methods=['GET'])
@login_required
def dataset(dataset_id):

    mode = request.args.get('mode')
    if not mode in ["view", "label"]:
        abort(400)

    user = Users.from_stormpath(stormpath_user)
    dataset = Datasets.query.get(dataset_id)
    if not dataset.study.is_labeller(user):
        abort(401)

    # Grab the list of datasets in this study
    # What page is this dataset?
    # has_next?
    # has_prev?
    prev_ds = dataset.prev()
    next_ds = dataset.next()
    all_ds = dataset.items()

    if mode == "label":
        # join labels for this user with datapoints for this dataset
        data_labels = dataset.labels_for_user(user)

        # populate labels if they're currently empty
        if data_labels.count() == 0:
            conn = db.engine.connect()
            dicts = UserLabels.dicts_from_datapoints(dataset.data_points.filter_by(training=True), dataset.id, user.id)
            conn.execute(UserLabels.__table__.insert(), dicts)
            db.session.commit()

        # json data for d3

        def clean_selected(sel):
            if not sel:
                return 0
            if sel:
                return 1
            return 0

        graph_points = [{
            "id": x.UserLabels.id,
            "temp_c": x.DataPoints.value,
            "time": x.DataPoints.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "selected": clean_selected(x.UserLabels.label)
        } for x in data_labels]
    else:
        graph_points = [{
            "id": x.id,
            "temp_c": x.value,
            "time": x.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "training": x.training
        } for x in dataset.data_points.order_by(DataPoints.timestamp)]

    is_owner = dataset.study.is_owner(user)
    y_min = dataset.study.y_min
    y_max = dataset.study.y_max
    return render_template('dataset.html',
                           dataset=dataset,
                           title=dataset.title,
                           study=dataset.study.title,
                           studyid=dataset.study_id,
                           notes=dataset.notes,
                           points_json=json.dumps(graph_points),
                           mode_json=json.dumps(mode),
                           y_min_json=json.dumps(y_min),
                           y_max_json=json.dumps(y_max),
                           mode=mode,
                           next_ds=next_ds,
                           prev_ds=prev_ds,
                           all_ds=all_ds,
                           is_owner=is_owner,
                           current_user=user)


@app.route('/labelled_dataset/<dataset_id>', methods=['GET'])
@login_required
def labelled_dataset(dataset_id):

    user = Users.from_stormpath(stormpath_user)
    dataset = Datasets.query.get(dataset_id)
    if not dataset.study.is_labeller(user):
        abort(401)

    # mark as labelled if not already
    if not dataset.user_has_labelled(user):
        labelled = LabelledDatasets(dataset.id, user.id)
        db.session.add(labelled)
        db.session.commit()

    next_ds = dataset.next()
    if(next_ds):
        return redirect(url_for('dataset', dataset_id=next_ds.id, mode="label"))
    else:
        return redirect(url_for('dataset', dataset_id=dataset.id, mode="label"))


@app.route('/reset_labels/<dataset_id>', methods=['GET'])
@login_required
def reset_labels(dataset_id):

    dataset = Datasets.query.get(dataset_id)
    user = Users.from_stormpath(stormpath_user)
    if not dataset.study.is_labeller(user):
        abort(401)

    data_labels = dataset.labels_for_user(user)

    # mark as unlabelled
    if dataset.user_has_labelled(user):
        dataset.labelled.filter_by(user_id=user.id).delete()
        db.session.commit()

    dicts = [dict(id=data_label.UserLabels.id, label=False) for data_label in data_labels]
    db.session.bulk_update_mappings(UserLabels, dicts)
    db.session.commit()

    return jsonify({
        "success": True
    })


@app.route('/labels', methods=['POST'])
@login_required
def labels():
    json = request.get_json()
    dicts = [dict(id=graph_point['id'], label=graph_point['selected'] == 1) for graph_point in json]
    db.session.bulk_update_mappings(UserLabels, dicts)
    db.session.commit()

    return jsonify({
        "success": True
    })


def generate_selector(data):
    first_time = date_parse(data[1][0])
    last_time = date_parse(data[-1][0])
    time_length = last_time-first_time-SUBSET_SIZE
    subset_start = first_time +\
        datetime.timedelta(
            seconds=random.random() * time_length.total_seconds())
    if subset_start < first_time:
        subset_start = first_time
    subset_end = subset_start+SUBSET_SIZE

    def selector(timestamp):
        return (subset_start <= timestamp) & (timestamp <= subset_end)

    return selector


def zip_ingress(data, study_id):
    print "Starting zip ingress for study %s" % study_id

    conn = db.engine.connect()
    zpf = zipfile.ZipFile(data)

    print zpf.namelist()

    for file in zpf.namelist():

        if not file.endswith(".csv"):
            continue

        print "Trying to parse %s" % file

        # first add empty dataset to get key
        dataset = Datasets(file, study_id)
        db.session.add(dataset)
        db.session.commit()
        dataset_id = dataset.id

        # then parse file and add notes and points with Core bulk inserts
        parsed = parser.parse(zpf.open(file))
        selector = generate_selector(parsed['data'])

        notes = [Notes.dict_from_parsed(note_text, dataset_id) for note_text in parsed['notes']]
        data_points = [DataPoints.dict_from_parsed(parsed_point, dataset_id, selector) for parsed_point in parsed['data']]

        # db.session.bulk_insert_mappings(DataPoints, data_points)
        conn.execute(DataPoints.__table__.insert(), data_points)
        # db.session.bulk_insert_mappings(Notes, notes)
        conn.execute(Notes.__table__.insert(), notes)
    db.session.commit()
    study = Studies.query.get(study_id)
    study.update_range()


@app.route('/upload/<study_id>', methods=['POST'])
@login_required
def upload(study_id):
    study = Studies.query.get(study_id)
    user = Users.from_stormpath(stormpath_user)
    if not study.is_owner(user):
        abort(401)

    zfile = request.files['file']
    # zfilename = secure_filename(zfile.filename)
    # zpath = os.path.join(app.config['UPLOAD_FOLDER'], zfilename)
    # zfile.save(zpath)
    db.session.add(StudyUploads(zfile.filename, zfile.read(), study_id))
    db.session.commit()

    return jsonify({
        'success': True
    })


@app.route('/api', methods=['GET'])
@login_required
def api():
    return jsonify({'hello': 'world'})


@app.route('/logout')
@login_required
def logout():
    """
    Log out a logged in user.  Then redirect them back to the main page of the
    site.
    """
    logout_user()
    return redirect(url_for('index'))


@app.route('/sumsarize_study/<study_id>', methods=['POST'])
@login_required
def sumsarize_study(study_id):
    queryfile = open("querydump.sql", "r")
    query = queryfile.read()

    query.replace("[study_id]", study_id)

    conn = db.session.connection()
    conn.execute(query)

    return jsonify({
        'success': True
    })


@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401

# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404
4
4
4
