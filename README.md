SUMSarizer
===

The Berkeley SUMSarizer

The SUMSarizer reduces raw SUMS data into a log of "cooking events" using machine learning. Upload your CSV files, train the algorithm by manually annotating a few data sets (with a nice UI), and the SUMSarizer will do the rest.

Guaranteed to save you a month of data wrangling!

Development
---

Check out the [sample development environment](https://github.com/SUMSarizer/develop) for getting started on SUMSARIZER development.

Run
---

	python run.py

Migrations
---

To initialize the DB schema run:

	python manage.py db upgrade

If you change a model file in `models.py`, run:

	python manage.py db migrate

to generate the migration file. Inspect the migration file in `migrations/versions/...py` If it looks good, run it with:

	python manage.py db upgrade

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

The secret file `.env` contains API keys and secrets.

Deploy
---

Setup:

**Add a file `login.txt` with your ssh login. e.g. `marc@sumsarizer.com`**

**Also add a file `sudo.txt` with your sudo password**

To push app changes to Linode:

    fab deploy

Check out `fabfile.py` to see how the app is laid out.

* Currently on port 5005. If you want to change the port, forward the new port in iptables
* Logs in /var/log/supervisor

Managing Production
---

Take a database snapshot:

    fab snapshot

Misc Provisioning
---

Eventually this should live in some sort of script to automate reprovisions.

Nginx fronts the gunicorn server. The config file (`/etc/nginx/sites-available/smzr`) is in `deployments/linode/smzr`

Enable the site:

    sudo ln -s /etc/nginx/sites-available/smzr /etc/nginx/sites-enabled

Restart nginx:

    sudo service nginx restart

Test configs:

    sudo nginx -t

If nginx has issues starting, check the logs:

    sudo tail -n 100 /var/log/nginx/error.log