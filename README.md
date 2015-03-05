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

If you add config items:

	heroku config:push

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



Database set up notes
---

