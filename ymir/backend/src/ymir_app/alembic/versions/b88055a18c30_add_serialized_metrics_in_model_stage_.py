"""add serialized_metrics in model_stage table

Revision ID: b88055a18c30
Revises: c91513775753
Create Date: 2022-11-10 14:42:54.676584

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b88055a18c30"
down_revision = "c91513775753"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("model_stage", schema=None) as batch_op:
        batch_op.add_column(sa.Column("serialized_metrics", sa.Text(length=500), nullable=True))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("model_stage", schema=None) as batch_op:
        batch_op.drop_column("serialized_metrics")

    # ### end Alembic commands ###
