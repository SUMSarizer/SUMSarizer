SUMSarizer
===

The Berkeley SUMSarizer

Install
---

Create virtual environment:

	virtualenv venv

Activate virtual environment

	source venv/bin/activate

Install dependencies

	pip install -r requirements.txt

Config
---

The file `.env` contains API ids and secrets.

Install the config plugin:

	heroku plugins:install git://github.com/ddollar/heroku-config.git

Pull the initial `.env`

	heroku config:pull --overwrite --interactive

If you add config items, add them in the management CLI. There are some settings that will only apply to the production server, and you don't want to overwrite them.

Run
---

	source venv/bin/activate
	source .env
	python run.py

Run like prod:

	foreman start

Deploy
---

	git push heroku master

Make sure there is a web process running:

	heroku ps:scale web=1

Migrations
---

Change a model file in `models.py`, then run:

	python manage.py db migrate

to genereate the migration file. Inspect the migration file in `migrations/versions/...py` If it looks good, run it with:

	python manage.py db upgrade

Running the migration on prod:

	heroku run python manage.py db upgrade

Database set up notes
---

Added db from the addons page:

	https://addons.heroku.com/heroku-postgresql#hobby-dev

To see credentials:

	heroku pg:credentials DATABASE


Secrets
---

Secrets stored in the repository with Ansible Vault. Contact the repository maintainer for the password.

Install [Ansible](http://www.ansible.com/home). 

Edit files:

	ansible-value edit secrets.txt

More: http://docs.ansible.com/playbooks_vault.html#id6
