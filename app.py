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
    abort,
    make_response
)
from flask_sqlalchemy import SQLAlchemy
from flask_security import (
    Security,
    SQLAlchemyUserDatastore,
    login_required,
)
from flask_login import current_user
from flask_mail import Mail
from werkzeug import secure_filename

app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS'))
# app.config['PROFILE'] = True
# app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
db = SQLAlchemy(app)
mail = Mail(app)

from models import *

user_datastore = SQLAlchemyUserDatastore(db, Users, Role)
security = Security(app, user_datastore)

SUBSET_SIZE = datetime.timedelta(7)


@app.route('/')
def index():
    """Basic home page."""
    return render_template('hi.html')

@app.route('/eula')
def eula():
    """Basic EULA page."""
    return render_template('eula.html')


@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    page = int(request.args.get('page') or 1)
    mystudies = current_user.studies().filter(StudyUsers.role == "owner").all()
    tolabel = current_user.studies().filter(StudyUsers.role == "labeller").all()
    return render_template('dashboard.html',
                           mystudies=mystudies,
                           tolabel=tolabel
                           )


@app.route('/new_study', methods=['POST'])
@login_required
def new_study():
    study = Studies(request.form['title'])
    db.session.add(study)
    study.add_user(current_user, "owner")
    study.add_user(current_user, "labeller")
    return redirect(url_for('study', study_id=study.id))


@app.route('/label_study/<study_id>', methods=['GET'])
@login_required
def label_study(study_id):
    study = Studies.query.get(study_id)

    if not study.is_labeller(current_user):
        abort(401)

    first_dataset = study.datasets\
        .order_by(Datasets.created_at.desc())\
        .first()

    return redirect(url_for('dataset', dataset_id=first_dataset.id, mode="label"))


@app.route('/study/<study_id>', methods=['GET'])
@login_required
def study(study_id):
    study = Studies.query.get(study_id)

    if not study.is_owner(current_user):
        abort(401)

    if study.token is None:
        study.generate_token()
        db.session.add(study)

    page = int(request.args.get('page') or 1)

    datasets = study.datasets\
        .order_by(Datasets.created_at.desc())\
        .paginate(page, per_page=15)

    has_datasets = datasets.total > 0

    study.users.filter_by(role="labeller").all()
    labellers = Users.query.\
        filter(study.is_labeller(Users)).\
        all()

    labellers = study.labellers()
    users = labellers.all()
    notusers = Users.query.except_(labellers).all()

    first_dataset = study.datasets.order_by(Datasets.created_at.desc()).first()
    if first_dataset:
        first_dataset_id = first_dataset.id
    else:
        first_dataset_id = None

    db.session.commit()

    return render_template('study.html',
                           study=study,
                           datasets=datasets.items,
                           pagination=datasets,
                           users=users,
                           notusers=notusers,
                           uploads=study.uploads,
                           has_datasets=has_datasets,
                           first_dataset_id=first_dataset_id)


@app.route('/delete_study/<study_id>', methods=['GET'])
@login_required
def delete_study(study_id):
    study = Studies.query.get(study_id)
    if not study.is_owner(current_user):
        abort(401)
    study.delete()
    return redirect(url_for('dashboard'))

@app.route('/study/<id>/export_user_labels', methods=['GET'])
@login_required
def export_user_labels(id):
    study = Studies.query.get(id)
    if not study.is_owner(current_user):
        abort(401)
    output = make_response(study.user_labels_as_csv())
    output.headers["Content-Disposition"] = "attachment; filename=%s_user_labels.csv" % study.title
    output.headers["Content-type"] = "text/csv"
    return output


@app.route('/delete_dataset/<dataset_id>', methods=['GET'])
@login_required
def delete_dataset(dataset_id):
    dataset = Datasets.query.get(dataset_id)
    study = dataset.study

    if not study.is_owner(current_user):
        abort(401)

    # db.session.delete(dataset)
    # db.session.commit()
    dataset.delete()
    return redirect(url_for('study', study_id=study.id))


@app.route('/add_study_labeller/<study_id>', methods=['GET'])
@login_required
def add_study_labeller(study_id):

    study = Studies.query.get(study_id)

    if not study.is_owner(current_user):
        abort(401)

    user_id = request.args.get('user_id')
    study_user = Users.query.get(user_id)
    study.add_user(study_user, "labeller")
    return redirect(url_for('study', study_id=study.id))


@app.route('/dataset/<dataset_id>', methods=['GET'])
@login_required
def dataset(dataset_id):
    mode = request.args.get('mode')
    if not mode in ["view", "label", "results"]:
        abort(400)

    dataset = Datasets.query.get(dataset_id)
    if not dataset.study.is_labeller(current_user):
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
        data_labels = dataset.labels_for_user(current_user)

        # populate labels if they're currently empty
        if data_labels.count() == 0:
            dicts = UserLabels.dicts_from_datapoints(dataset.data_points.filter_by(training=True), dataset.id, current_user.id)
            db.session.execute(UserLabels.__table__.insert(), dicts)
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
    elif mode == 'view':
        graph_points = [{
            "id": x.id,
            "temp_c": x.value,
            "time": x.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "training": x.training
        } for x in dataset.data_points.order_by(DataPoints.timestamp)]
    elif mode == 'results':
        # Show most recent successful results
        job = dataset.study.most_recent_successful_job()
        datapoints = ResultDataPoints.query\
                                     .filter(ResultDataPoints.job_id == job.id,
                                             ResultDataPoints.dataset_id == dataset.id)\
                                     .order_by(ResultDataPoints.timestamp).all()
        graph_points = [{
            "id": x.id,
            "temp_c": x.value,
            "time": x.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "prediction": x.prediction,
            "cooking": x.prediction > 0.5
        } for x in datapoints]

    is_owner = dataset.study.is_owner(current_user)
    y_min = dataset.study.y_min
    y_max = dataset.study.y_max

    # Which datasets has this user labelled?
    user_labels = LabelledDatasets.query.filter(LabelledDatasets.user_id == current_user.id).all()
    labelled_by_user = {label.dataset_id: True for label in user_labels}

    # How many labellers total?
    count_labellers = dataset.study.labellers().count()

    # How many labellers have fully labelled each dataset
    resp = db.session.execute("""
        SELECT
            COUNT(*) as count_labelled,
            datasets.id as dataset_id
        FROM labelled_datasets
        JOIN datasets ON labelled_datasets.dataset_id = datasets.id
        JOIN studies ON studies.id = datasets.study_id
        WHERE studies.id = :study_id
        GROUP BY datasets.id
    """, {'study_id': dataset.study.id})

    labelled_counts = {dataset_id: count_labelled for count_labelled, dataset_id in resp}

    # Flag that is True is all the datasets have been labelled by all
    # the labellers.
    all_labelled = sum(labelled_counts.values()) == count_labellers *  dataset.study.datasets.count()


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
                           all_labelled=all_labelled,
                           count_labellers=count_labellers,
                           labelled_counts=labelled_counts,
                           current_user=current_user,
                           labelled_by_user=labelled_by_user)


@app.route('/labelled_dataset/<dataset_id>', methods=['GET'])
@login_required
def labelled_dataset(dataset_id):


    dataset = Datasets.query.get(dataset_id)
    if not dataset.study.is_labeller(current_user):
        abort(401)

    # mark as labelled if not already
    if not dataset.user_has_labelled(current_user):
        labelled = LabelledDatasets(dataset.id, current_user.id)
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

    if not dataset.study.is_labeller(current_user):
        abort(401)

    data_labels = dataset.labels_for_user(current_user)

    # mark as unlabelled
    if dataset.user_has_labelled(current_user):
        dataset.labelled.filter_by(user_id=current_user.id).delete()
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
        if file.startswith("__MACOSX"):
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

    study = Studies.query.get(study_id)
    study.update_range()

    db.session.add(study)
    db.session.commit()

@app.route('/upload/<study_id>', methods=['POST'])
@login_required
def upload(study_id):
    study = Studies.query.get(study_id)

    if not study.is_owner(current_user):
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


@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401

# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404

@app.route('/study/<study_id>/sumsarize', methods=['GET'])
@login_required
def sumsarize(study_id):
    job = SZJob()
    job.study_id = study_id
    db.session.add(job)
    db.session.commit()
    return redirect(url_for('study', study_id=study_id))

@app.route('/job/<id>/download_csv_file', methods=['GET'])
@login_required
def download_csv_file(id):
   job = SZJob.query.get(id)
   output = make_response(job.csv_blob)
   output.headers["Content-Disposition"] = "attachment; filename=%s_sumsarized.csv" % job.study.title
   output.headers["Content-type"] = "text/csv"
   return output

@app.route('/job/<id>/download_csv_archive', methods=['GET'])
@login_required
def download_csv_archive(id):
    job = SZJob.query.get(id)
    output = make_response(job.csv_binary_blob)
    output.headers["Content-Disposition"] = "attachment; filename=%s_sumsarized.zip" % job.study.title
    output.headers["Content-type"] = "application/zip"
    return output

@app.route('/job/<id>/archive', methods=['GET'])
@login_required
def archive_job(id):
    job = SZJob.query.get(id)
    if not job.study.is_owner(current_user):
        abort(401)
    job.archived = True
    db.session.add(job)
    db.session.commit()
    return redirect(url_for('study', study_id=job.study_id))

@app.route('/study/<study_id>/archived_jobs', methods=['GET'])
@login_required
def archived_jobs(study_id):
    study = Studies.query.get(study_id)
    if not study.is_owner(current_user):
        abort(401)
    return render_template('archived_jobs.html',
                           study=study)

@app.route('/uploads/<id>/delete', methods=['GET'])
@login_required
def delete_upload(id):
    upload = StudyUploads.query.get(id)
    if not upload.study.is_owner(current_user):
        abort(401)
    db.session.delete(upload)
    db.session.commit()
    return redirect(url_for('study', study_id=upload.study_id))

@app.route('/study/<id>/invite_link', methods=['GET'])
@login_required
def invite_link(id):
    study = Studies.query.get(id)

    if not study.token == request.args.get('token'):
        abort(401)

    study.add_user(current_user, "labeller")
    return redirect(url_for('label_study', study_id=id))