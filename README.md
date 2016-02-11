SUMSarizer
===

The Berkeley SUMSarizer

The SUMSarizer reduces raw SUMS data into a log of "cooking events" using machine learning. Upload your CSV files, train the algorithm by manually annotating a few data sets (with a nice UI), and the SUMSarizer will do the rest.

Guaranteed to save you a month of data wrangling!

Development Prerequisites
---

The development environment uses Vagrant to make it easy to spin up consistent dev environments on any host machine. Install the following:

* [Vagrant](https://www.vagrantup.com/)
* [VirtualBox](https://www.virtualbox.org/)
* The Vagrant-cachier plugin for faster provisions:

    vagrant plugin install vagrant-cachier

Installation of Vagrant on Ubuntu can be tricky depending on what version you are using. For 14.04 [these instructions](http://foorious.com/devops/vagrant-virtualbox-trusty-install/) were good.

On Mac, there is sometimes an issue where the Vagrant binary in installed (in `/opt/vagrant/bin/vagrant`) but not symlinked as `/usr/bin/vagrant`.

Install Dev Environment
---

First clone this repository.

Then, add a file `.vault_pass.txt` to the root of the repo with the Vault password in it (contact the maintainer to get this password).

Then, provision and start the virtual machine using:

    vagrant up

Login to the machine:

    vagrant ssh

Run
---

	./scripts/start.sh

Run like prod (useful to test if foreman is crashing on deploy):

	./scripts/prod.sh

Migrations
---

To initialize the DB schema run:

	python manage.py db upgrade

If you change a model file in `models.py`, run:

	python manage.py db migrate

to generate the migration file. Inspect the migration file in `migrations/versions/...py` If it looks good, run it with:

	python manage.py db upgrade

Running the migration on prod:

	heroku run python manage.py db upgrade

Secrets
---

Secrets stored in the repository with Ansible Vault in the `secrets` directory.

Run

  ./scripts/open-secret <secret name>

to unencrypt a secret to the `secrets_` directory.

To re-encrypt the secret, copy the new file to the `secrets` directory, then run:

  ./scripts/encrypt-secret <secret name>

**If you commit and push an unencrypted file in the `secrets` directory it will no longer be secret!**

Config
---

The secret file `.env` contains API ids and secrets.

Deploy
---

* We're using a linode at http://50.116.4.99/
* The app lives in /home/jrcoyle/SUMSarizer
* www group has permissions
* Currently on port 5005
** If you want to change the port, forward the new port in iptables
* Logs in /var/log/supervisor

To deploy:
* git pull
* restart workers with supervisorctl


