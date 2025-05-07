#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as per your project requirements
pip install -r requirements.txt

# Run migrations
python manage.py migrate