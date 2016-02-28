# So that we can install the latest stable version of R.
sudo sh -c 'echo "deb http://cran.rstudio.com/bin/linux/ubuntu trusty/" >> /etc/apt/sources.list'
gpg --keyserver keyserver.ubuntu.com --recv-key E084DAB9
gpg -a --export E084DAB9 | sudo apt-key add -


sudo apt-get update

# libpq-dev, python-dev: necessary for compiling C extensions
sudo apt-get install -y \
  git-core \
  htop \
  libcurl4-gnutls-dev \
  libpq-dev \
  libxml2-dev \
  libssl-dev \
  python-dev \
  python-pip \
  r-base

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

echo 'source /vagrant/scripts/env.sh' >> ~/.bash_profile

source /vagrant/scripts/env.sh

#
## Database
#

sudo -u postgres psql -c "CREATE USER sums WITH PASSWORD 'sums' SUPERUSER;"
sudo -u postgres createdb sums

# Jump right into the dev DB CLI with `psql`
echo 'alias psql="sudo -u postgres psql sums"' >> ~/.bash_profile

echo 'Running Migrations'
./scripts/upgrade.sh

#
# R
#

sudo R -e "install.packages('plyr', repos = 'http://cran.rstudio.com/')"
sudo R -e "install.packages('devtools', repos = 'http://cran.rstudio.com/')"
sudo R -e "install.packages('pspline', repos = 'http://cran.rstudio.com/')"
sudo R -e "install.packages('caTools', repos = 'http://cran.rstudio.com/')"
sudo R -e "install.packages('glmnet', repos = 'http://cran.rstudio.com/')"
sudo R -e "devtools::install_github('jeremyrcoyle/origami')"
