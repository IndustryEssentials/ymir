#! /usr/bin/env bash

# Let the DB start
python app/backend_pre_start.py

# Prepare database tables
current_rev=$(alembic current)
if [ -z "$current_rev" ]
then
    echo create database tables from scratch
    python app/db/init_tables.py
else
    echo migrating database from $current_rev
    alembic upgrade head
fi

# Run migrations for clickhouse
python app/init_clickhouse.py

# Create initial data in DB
python app/initial_data.py

# Clean legacy tasks
python app/clean_tasks.py

# Fix dirty repos
python app/fix_dirty_repos.py
