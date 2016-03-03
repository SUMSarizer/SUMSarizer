#
# Provision script that is designed to be idempotent; you should be able to
# run it as many times as you want.
#


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
  nginx \
  python-dev \
  python-pip \
  r-base

sudo pip install memory_profiler \
                 virtualenv

# install deps to the virtual env

sudo R -e "install.packages('plyr', repos = 'http://cran.rstudio.com/')"
sudo R -e "install.packages('devtools', repos = 'http://cran.rstudio.com/')"
sudo R -e "install.packages('pspline', repos = 'http://cran.rstudio.com/')"
sudo R -e "install.packages('caTools', repos = 'http://cran.rstudio.com/')"
sudo R -e "install.packages('glmnet', repos = 'http://cran.rstudio.com/')"
sudo R -e "devtools::install_github('jeremyrcoyle/origami')"