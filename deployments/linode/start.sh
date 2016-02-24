#!/bin/bash
source venv/bin/activate
gunicorn app:app -b 0.0.0.0:5005