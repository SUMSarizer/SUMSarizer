import logging
import subprocess

def work():

  from app import db
  from models import StudyUploads

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
    ) To '/tmp/%s' With CSV HEADER;
  """ % (1, "new_userlabels.csv"))

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
    ) To '/tmp/%s' With CSV HEADER;
  """ % (1, "new_studydata.csv"))

  # Generate a unique filename with guid

  resp = subprocess.check_output(["Rscript", "ml_script.R", "/tmp/new_studydata.csv", "/tmp/new_userlabels.csv", "/tmp/ml_output.csv"], cwd="/vagrant/ml_labeler")

  print resp

  # Export the required studydata_<guid>.csv

  # Export the required userlabels_<guid>.csv

  # cd and execute the R script on these files

  # Toggle the status field on the job

  # wait...

  # Upload the results

  # Toggle the status field on the job


  # Catch exceptions and toggle "Failed"