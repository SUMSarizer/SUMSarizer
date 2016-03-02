#!/bin/bash
source venv/bin/activate
source /home/www/prod_env
gunicorn app:app -b 127.0.0.1:5005 -w 4