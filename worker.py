import os

import redis
from rq import Worker, Queue, Connection
from app import app, db, zip_ingress
from models import StudyUploads
from time import sleep
listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)
ufolder = app.config['UPLOAD_FOLDER']
while(1):
    study_uploads = StudyUploads.query.all()
    for study_upload in study_uploads:
        path = os.path.join(ufolder, study_upload.filename)
        print "ingress for {0}".format(path)
        zip_ingress(path, study_upload.study_id)
        os.remove(path)
        db.session.delete(study_upload)
        db.session.commit()
    sleep(10)
