import os

from StringIO import StringIO
from app import app, db, zip_ingress
from models import StudyUploads
from time import sleep
import traceback

while(1):
    study_uploads = StudyUploads.query.all()
    for study_upload in study_uploads:
        print "ingress for {0}".format(study_upload.filename)
        try:
            zip_ingress(StringIO(study_upload.data), study_upload.study_id)
            print "Successful ingress"
        except:
            print "Failed ingress"
            traceback.print_exc()

        db.session.delete(study_upload)
        db.session.commit()
    sleep(1)
