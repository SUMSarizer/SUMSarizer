SUMSarizer
===

The Berkeley SUMSarizer

Install
---

Install Python 2.7 and pip. 

https://www.python.org/download/releases/2.7/
https://pip.pypa.io/en/latest/

Then,

	./scripts/install.sh

Install a local Postgres database. The app expects a database named "sums".

To deploy to the server, install the Heroku toolbelt:

https://toolbelt.heroku.com/

Config
---

The file `.env` contains API ids and secrets.

See the file `env.sample` for what needs to go here. API keys are stored in the encrypted `secrets.txt`.

You can also retrieve API keys from the Heroku management UI.

Secrets
---

Secrets stored in the repository with Ansible Vault. Contact the repository maintainer for the password.

Install [Ansible](http://www.ansible.com/home). 

Edit files:

	ansible-value edit secrets.txt

More: http://docs.ansible.com/playbooks_vault.html#id6

Run
---

	./scripts/start.sh

Run like prod (useful to test if foreman is crashing on deploy):

	./scripts/prod.sh

Deploy
---

	git push heroku master

Make sure there is a web process running:

	heroku ps:scale web=1

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
