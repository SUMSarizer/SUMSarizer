#!/bin/bash
source .env
source venv/bin/activate
gunicorn app:app -b 0.0.0.0:5005
