#!/bin/bash
source .env
source venv/bin/activate
#python run.py
gunicorn app:app -b 0.0.0.0:5000
