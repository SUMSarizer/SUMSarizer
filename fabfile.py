from fabric.api import *

env.hosts = ['marc@50.116.4.99']

def host_type():
  run('uname -s')

def deploy():
  code_dir = '/home/jrcoyle/SUMSarizer'
  with cd(code_dir):
    run("git pull")
    sudo("supervisorctl restart all")

# TODO: Migrations
  # run alembic on db
