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

