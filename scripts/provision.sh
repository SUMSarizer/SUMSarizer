sudo apt-get update

# libpq-dev, python-dev: necessary for compiling C extensions
sudo apt-get install -y \
  git-core \
  htop \
  libpq-dev \
  python-dev \
  python-pip

sudo pip install memory_profiler \
                 virtualenv

# create a virtual environment for the project
cd ~
rm -rf venv # in case there's an old one lying around
virtualenv venv

# install deps to the virtual env
source venv/bin/activate
cd /vagrant
pip install -r requirements.txt

echo 'source scripts/env.sh' >> ~/.bash_profile

source scripts/env.sh

#
## Database
#

sudo -u postgres psql -c "CREATE USER sums WITH PASSWORD 'sums' SUPERUSER;"
sudo -u postgres createdb sums

# Jump right into the dev DB CLI with `psql`
echo 'alias psql="sudo -u postgres psql sums"' >> ~/.bash_profile

echo 'Running Migrations'
./scripts/upgrade.sh

