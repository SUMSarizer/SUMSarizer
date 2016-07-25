import traceback
import logging
import subprocess
import uuid
import csv
import tempfile
import os
import shutil

def write_csv(items, headers, filename):
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, headers)
        writer.writeheader()
        for row in items:
            writer.writerow(row)


def run_ml(study_id, job_id):

    from app import db, app
    from models import ResultDataPoints

    guid = uuid.uuid4()

    userlabels_filename = "/tmp/userlabels_%s.csv" % guid

    # studydata_filename = "/tmp/studydata_%s.csv" % guid
    # output_filename = "/tmp/ml_output_%s.csv" % guid

    studydata_dir = tempfile.mkdtemp()
    output_dir = tempfile.mkdtemp()
    output_zipname = "/tmp/ml_output_%s" % guid

    logging.info("Exporting user labels to CSV")
    resp = db.session.execute("""
    SELECT 
        dp.id as datapoint_id,
        ds.title as filename,
        dp.timestamp as timestamp, 
        dp.value as value,
        avg(ul.label::integer) as combinedlabel
    FROM datasets as ds
    INNER JOIN datapoints as dp ON ds.id=dp.dataset_id
    INNER JOIN user_labels as ul ON dp.id=ul.datapoint_id
    INNER JOIN labelled_datasets as lab_ds ON ds.id=lab_ds.dataset_id AND ul.user_id=lab_ds.user_id
    INNER JOIN users ON ul.user_id=users.id
    WHERE ds.study_id=%s
    GROUP BY dp.id, ds.id
    ORDER BY ds.id, user, timestamp
    """ % (study_id))

    write_csv(map(dict, resp),
              ['datapoint_id', 'filename', 'timestamp', 'value', 'combinedlabel'],
              userlabels_filename)

    logging.info("Exporting study data to CSV")

    resp = db.session.execute("""
        SELECT id,title
        FROM datasets 
        WHERE study_id = :study_id
    """, {"study_id": study_id})

    for (dataset_id, title) in resp:
        resp = db.session.execute("""
        SELECT dp.id as datapoint_id,
             ds.title as filename,
             dp.timestamp as timestamp,
             dp.value as value,
             ds.id as dataset_id
        FROM datasets as ds
        INNER JOIN datapoints as dp ON ds.id=dp.dataset_id
        WHERE ds.id = :dataset_id
        ORDER BY ds.id, timestamp
        """, {"dataset_id": dataset_id})

        title = title.replace("/", "__")

        studydata_filename = os.path.join(studydata_dir, title)

        logging.info("Writing study data to %s" % studydata_filename)

        write_csv(map(dict, resp),
                  ['datapoint_id', 'filename', 'timestamp', 'value', 'dataset_id'],
                  studydata_filename)

    ml_script_resp = subprocess.check_output([
        "Rscript",
        "ml_script.R",
        userlabels_filename,
        studydata_dir,
        output_dir],
        cwd=app.config['ML_FOLDER'])

    logging.info(ml_script_resp)

    # Update datapoints in DB with prediction values
    for output_filename in os.listdir(output_dir):
        result_datapoints = []
        with open(os.path.join(output_dir, output_filename)) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                result_datapoint = ResultDataPoints()
                result_datapoint.timestamp = row['timestamp']
                result_datapoint.value = float(row['value'])
                assert row['pred'] in ["TRUE", "FALSE"]
                if row['pred'] == "TRUE":
                    result_datapoint.prediction = 1.0
                else:
                    result_datapoint.prediction = 0.0
                result_datapoint.job_id = job_id
                result_datapoint.datapoint_id = row['datapoint_id']
                result_datapoint.dataset_id = row['dataset_id']
                result_datapoints.append(result_datapoint)
        db.session.bulk_save_objects(result_datapoints)
        db.session.commit()


    # Prepare output CSV
    output_zipname = shutil.make_archive(output_zipname, 'zip', output_dir)

    with open(output_zipname, 'rb') as zfile:
        out_blob = zfile.read()

    return {
        'message': ml_script_resp,
        'csv_binary_blob': out_blob
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
        result = run_ml(job.study_id, job.id)
    except :
        failed = True
        error_message = traceback.format_exc()

    if failed:
        job.state = 'failed'
        job.message = error_message
    else:
        job.state = 'success'
        job.message = result['message']
        job.csv_binary_blob = result['csv_binary_blob']

    db.session.add(job)
    db.session.commit()
