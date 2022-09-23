#! /usr/bin/env bash
set -e

# Make sure existing mir repos are up to date
python app/check_mir_repo_version.py

# Let the DB start
python app/backend_pre_start.py

# Get current alembic version if possible
base_alembic_revision=$(alembic current)

# Run migrations for MySQL
alembic upgrade head

# Create initial data in DB
python app/initial_data.py ${base_alembic_revision}

# Clean legacy tasks
python app/clean_tasks.py

# Fix dirty repos
python app/fix_dirty_repos.py
