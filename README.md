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
	python app.py

