import logging
import os

from clickhouse_driver import Client, errors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


CLICKHOUSE_URI = os.environ.get("CLICKHOUSE_URI", "clickhouse")

project_table = """\
CREATE TABLE project
(
    created_time DateTime,
    user_id Integer,
    id Integer,
    name String,
    training_type LowCardinality(String),
    training_keywords Array(LowCardinality(String))
)
ENGINE = MergeTree()
ORDER BY created_time;"""


task_table = """\
CREATE TABLE task_create
(
    created_time DateTime,
    user_id Integer,
    project_id Integer,
    name String,
    hash String,
    type LowCardinality(String),
    dataset_ids Array(Integer),
    model_ids Array(Integer),
    keyword_ids Array(LowCardinality(String))
)
ENGINE = MergeTree()
ORDER BY created_time;"""


model_table = """\
CREATE TABLE model
(
    created_time DateTime,
    user_id Integer,
    project_id Integer,
    group_id Integer,
    id Integer,
    name String,
    hash String,
    map Float,
    keyword_ids Array(LowCardinality(String))
)
ENGINE = MergeTree()
ORDER BY created_time;"""


keyword_table = """\
CREATE TABLE dataset_keywords
(
    created_time DateTime,
    user_id Integer,
    project_id Integer,
    group_id Integer,
    dataset_id Integer,
    keyword_ids Array(LowCardinality(String))
)
ENGINE = MergeTree()
ORDER BY created_time;"""


clickhouse_tables = [project_table, task_table, model_table, keyword_table]


def init() -> None:
    client = Client(host=CLICKHOUSE_URI)
    existing_tables = client.execute("show tables")

    if not existing_tables:
        for create_sql in clickhouse_tables:
            client.execute(create_sql)


def main() -> None:
    logger.info("Creating ClickHouse tables")
    try:
        init()
    except (ConnectionRefusedError, errors.NetworkError) as e:
        logger.info(f"Fail to init clickhouse client, error: {e}.")
        return
    logger.info("ClickHouse tables created")


if __name__ == "__main__":
    main()
