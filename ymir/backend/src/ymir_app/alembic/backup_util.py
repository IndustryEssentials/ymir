import os
import subprocess

env = os.environ
MYSQL_USER = env("MYSQL_INITIAL_USER")
MYSQL_PASSWORD = env("MYSQL_INITIAL_PASSWORD")
MYSQL_DATABASE = env("MYSQL_DATABASE")
MYSQL_HOST = "db"

MYSQLDUMP_COMMAND_TEMPLATE = f"mysqldump --host {MYSQL_HOST} -u {MYSQL_USER} -p{MYSQL_PASSWORD} --databases {MYSQL_DATABASE} --no-tablespaces --result-file %s"

RECOVER_COMMAND_TEMPLATE = f"mysql --host {MYSQL_HOST} -u {MYSQL_USER} -p{MYSQL_PASSWORD} < %s"


def create_backup(backup_filename: str) -> None:
    subprocess.run(MYSQLDUMP_COMMAND_TEMPLATE % backup_filename)


def recover_from_backup(backup_filename: str) -> None:
    subprocess.run(RECOVER_COMMAND_TEMPLATE % backup_filename)
