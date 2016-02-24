import os
import datetime
import time
from fabric.api import *

env.hosts = ['marc@50.116.4.99']

def host_type():
  run('uname -s')

def deploy():
  code_dir = '/home/jrcoyle/SUMSarizer'

  put('/home/www/.bashrc', 'deployments/linode/.bashrc')
  put('/home/www', 'secrets_/prod_env')

  with cd(code_dir):
    sudo("git pull")
    sudo("supervisorctl restart all")

# TODO: Migrations
  # run alembic on db

def snapshot():
  snapshot_dir = '/home/www'
  outdir = 'dumps'
  outfilename = "dump-%s" % datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%H%M%S')
  outpath = os.path.join(outdir, outfilename)
  with cd(snapshot_dir):
    sudo('pg_dump -Fc --no-acl --no-owner sums > mydb.dump', user='www')
  get('/home/www/mydb.dump', outpath)

def logs():
  # Does this filename change from time to time?
  sudo('tail -n 300 /var/log/supervisor/SUMSarizer_worker-stderr---supervisor-Oopgek.log')