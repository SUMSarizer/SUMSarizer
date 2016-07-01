SUMSarizer
===

The Berkeley SUMSarizer

The SUMSarizer reduces raw SUMS data into a log of "cooking events" using machine learning. Upload your CSV files, train the algorithm by manually annotating a few data sets (with a nice UI), and the SUMSarizer will do the rest.

Guaranteed to save you a month of data wrangling!

Development
---

Check out the [sample development environment](https://github.com/SUMSarizer/develop) for getting started on SUMSARIZER development.

Install
---

SUMSarizer is a Python 2.7 app.

Install its requirements:

    pip install -r requirements.txt

R should also be installed with the following packages:

    plyr
    devtools
    pspline
    caTools
    glmnet
    devtools::install_github('jeremyrcoyle/origami')

Configure
---

The current config expects a Postgres database at the following URI: `postgresql://sums:sums@localhost/sums`

The following environment variables should be set:

    APP_SETTINGS="config.DevelopmentConfig"

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

