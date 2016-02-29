#!/bin/bash
source venv/bin/activate
source /home/www/prod_env
python -m tasks.ml_worker
