#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Convert static files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

# Populate database with test data (admin/admin123 and test barbers)
python manage.py repopulate_db
