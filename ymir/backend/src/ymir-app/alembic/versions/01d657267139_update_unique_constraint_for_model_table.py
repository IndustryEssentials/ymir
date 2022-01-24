"""update unique constraint for model table

Revision ID: 01d657267139
Revises: 98423cdb01df
Create Date: 2021-11-29 14:04:31.788923

"""
import sqlalchemy as sa

from alembic import context, op

# revision identifiers, used by Alembic.
revision = "01d657267139"
down_revision = "98423cdb01df"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    if context.get_x_argument(as_dictionary=True).get("sqlite", None):
        with op.batch_alter_table("model") as batch_op:
            batch_op.drop_index("ix_model_hash")
            batch_op.create_index(op.f("ix_model_hash"), ["hash"], unique=False)
            batch_op.create_unique_constraint("uniq_user_hash", ["user_id", "hash"])
    else:
        op.drop_index("ix_model_hash", table_name="model")
        op.create_index(op.f("ix_model_hash"), "model", ["hash"], unique=False)
        op.create_unique_constraint("uniq_user_hash", "model", ["user_id", "hash"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    if context.get_x_argument(as_dictionary=True).get("sqlite", None):
        with op.batch_alter_table("model") as batch_op:
            batch_op.drop_constraint("uniq_user_hash", type_="unique")
            batch_op.drop_index(op.f("ix_model_hash"))
            batch_op.create_index("ix_model_hash", ["hash"], unique=False)
    else:
        op.drop_constraint("uniq_user_hash", "model", type_="unique")
        op.drop_index(op.f("ix_model_hash"), table_name="model")
        op.create_index("ix_model_hash", "model", ["hash"], unique=False)
    # ### end Alembic commands ###
