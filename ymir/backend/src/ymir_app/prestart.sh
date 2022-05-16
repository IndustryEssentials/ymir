#! /usr/bin/env bash

# Let the DB start
python app/backend_pre_start.py

# Run migrations for MySQL
alembic upgrade head

# Run migrations for clickhouse
python app/init_clickhouse.py

# Create initial data in DB
python app/initial_data.py

# Clean legacy tasks
python app/clean_tasks.py

# Fix dirty repos
python app/fix_dirty_repos.py
