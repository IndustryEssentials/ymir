# Import all the models, so that Base has them before being
# imported by Alembic
from auth.db.base_class import Base  # noqa
from auth.models.user import User  # noqa
