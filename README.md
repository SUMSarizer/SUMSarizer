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

Run
---

	source venv/bin/activate
	source .env
	python app.py

