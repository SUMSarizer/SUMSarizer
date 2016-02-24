#!/bin/bash
source venv/bin/activate
source /home/www/prod_env
gunicorn app:app -b 0.0.0.0:5005