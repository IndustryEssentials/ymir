#! /usr/bin/env bash
set -e

# Let the DB start
python auth/prestart.py

# Run migrations for MySQL
alembic upgrade head

# Create initial data in DB
python auth/initial_data.py
