import traceback
import logging
import subprocess
import uuid
import csv

def run_ml(study_id):

    from app import db

    guid = uuid.uuid4()

    userlabels_filename = "/tmp/userlabels_%s.csv" % guid
    studydata_filename = "/tmp/studydata_%s.csv" % guid
    output_filename = "/tmp/ml_output_%s.csv" % guid

    logging.info("Exporting user labels to CSV")
    db.session.execute("""
    COPY (SELECT dp.id as datapoint_id,
         ds.title as filename,
         dp.timestamp as timestamp, dp.value as value,
         ul.user_id as labeller, users.email as email, ul.label as cooking_label
    FROM datasets as ds
    INNER JOIN datapoints as dp ON ds.id=dp.dataset_id
    INNER JOIN user_labels as ul ON dp.id=ul.datapoint_id
    INNER JOIN labelled_datasets as lab_ds ON ds.id=lab_ds.dataset_id AND ul.user_id=lab_ds.user_id
    INNER JOIN users ON ul.user_id=users.id
    WHERE ds.study_id=%s
    ORDER BY ds.id, user, timestamp
    ) To '%s' With CSV HEADER;
    """ % (study_id, userlabels_filename))

    logging.info("Exporting study data to CSV")
    db.session.execute("""
    COPY (
    SELECT dp.id as datapoint_id,
         ds.title as filename,
         dp.timestamp as timestamp, dp.value as value
    FROM datasets as ds
    INNER JOIN datapoints as dp ON ds.id=dp.dataset_id
    WHERE ds.study_id=%s
    ORDER BY ds.id, timestamp
    ) To '%s' With CSV HEADER;
    """ % (study_id, studydata_filename))

    ml_script_resp = subprocess.check_output([
        "Rscript",
        "ml_script.R",
        studydata_filename,
        userlabels_filename,
        output_filename],
        cwd="/vagrant/ml_labeler")

    logging.info(ml_script_resp)

    # Prepare output CSV
    out = []
    with open(output_filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            new_row = {
                'timestamp': row['timestamp'],
                'temp_c': row['temp_c'],
                'is_cooking': float(row['pred']) > 0.5
            }
            out.append(new_row)
    with open(output_filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, ['timestamp', 'temp_c', 'is_cooking'])
        writer.writeheader()
        for row in out:
            writer.writerow(row)

    out_blob = open(output_filename).read()

    # Prepare output PDF

    return {
        'message': ml_script_resp,
        'csv_blob': out_blob
    }

def work():

    from app import db
    from models import SZJob

    job = SZJob.query.filter(SZJob.state == 'submitted').first()

    if not job:
      return

    logging.info("Running SZ job for study %s" % job.study_id)

    job.state = 'running'
    db.session.add(job)
    db.session.commit()

    failed = False
    try:
        result = run_ml(job.study_id)
    except :
        failed = True
        error_message = traceback.format_exc()

    if failed:
        job.state = 'failed'
        job.message = error_message
    else:
        job.state = 'success'
        job.message = result['message']
        job.csv_blob = result['csv_blob']

    db.session.add(job)
    db.session.commit()
