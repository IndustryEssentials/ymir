"""update: make user_id in workspace required

Revision ID: 8a0ec02bf344
Revises: 09fd83a1be56
Create Date: 2022-01-07 15:45:43.669933

"""
import sqlalchemy as sa

from alembic import context, op

# revision identifiers, used by Alembic.
revision = "8a0ec02bf344"
down_revision = "09fd83a1be56"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    if context.get_x_argument(as_dictionary=True).get("sqlite", None):
        with op.batch_alter_table("workspace") as batch_op:
            batch_op.alter_column("user_id", existing_type=sa.INTEGER(), nullable=False)
    else:
        op.alter_column(
            "workspace", "user_id", existing_type=sa.INTEGER(), nullable=False
        )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    if context.get_x_argument(as_dictionary=True).get("sqlite", None):
        with op.batch_alter_table("workspace") as batch_op:
            batch_op.alter_column("user_id", existing_type=sa.INTEGER(), nullable=True)
    else:
        op.alter_column(
            "workspace", "user_id", existing_type=sa.INTEGER(), nullable=True
        )
    # ### end Alembic commands ###
