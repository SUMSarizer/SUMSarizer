import os

from StringIO import StringIO
from app import app, db, zip_ingress
from models import StudyUploads
from time import sleep
import traceback

while(1):
    study_uploads = StudyUploads.query.all()
    for study_upload in study_uploads:

        if study_upload.state != 'submitted':
            continue

        print "ingress for {0}".format(study_upload.filename)
        try:
            zip_ingress(StringIO(study_upload.data), study_upload.study_id)
            print "Successful ingress"
            db.session.delete(study_upload)
        except:
            study_upload.error_message = traceback.format_exc()
            study_upload.state = 'failed'
            db.session.add(study_upload)
            print "Failed ingress"
            traceback.print_exc()
        db.session.commit()
    sleep(1)
