import sys

from alembic.config import Config
from alembic import command

from app.db.session import engine
from app.db.base import Base


def init_tables(alembic_cfg_file) -> None:
    Base.metadata.create_all(bind=engine)

    alembic_cfg = Config(alembic_cfg_file)
    command.stamp(alembic_cfg, "head")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        alembic_cfg_file = "./alembic.ini"
    else:
        alembic_cfg_file = sys.argv[1]
    init_tables(alembic_cfg_file)
