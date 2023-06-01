"""add recommended_model_id in project

Revision ID: 06947daa7700
Revises: 27ae716547a2
Create Date: 2023-06-01 14:23:01.280470

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "06947daa7700"
down_revision = "27ae716547a2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("project", schema=None) as batch_op:
        batch_op.add_column(sa.Column("recommended_model_id", sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("project", schema=None) as batch_op:
        batch_op.drop_column("recommended_model_id")
