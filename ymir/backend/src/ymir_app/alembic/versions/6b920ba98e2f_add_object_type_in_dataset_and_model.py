"""add object_type in dataset and model tables

Revision ID: 6b920ba98e2f
Revises: 27ae716547a2
Create Date: 2023-05-19 10:31:17.765125

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6b920ba98e2f"
down_revision = "27ae716547a2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.add_column(sa.Column("object_type", sa.SmallInteger(), nullable=True))

    conn = op.get_bind()
    if conn.engine.name != "sqlite":
        with op.batch_alter_table("dataset", schema=None) as batch_op:
            update_sql = """
                UPDATE dataset
                SET object_type = (
                    SELECT object_type
                    FROM project
                    WHERE dataset.project_id = project.id
                )
            """
            conn.execute(update_sql)
            op.alter_column("dataset", "object_type", existing_type=sa.SmallInteger(), nullable=False)
            batch_op.create_index(batch_op.f("ix_dataset_object_type"), ["object_type"], unique=False)

    with op.batch_alter_table("model", schema=None) as batch_op:
        batch_op.add_column(sa.Column("object_type", sa.SmallInteger(), nullable=True))

    if conn.engine.name != "sqlite":
        with op.batch_alter_table("model", schema=None) as batch_op:
            update_sql = """
                UPDATE model
                SET object_type = (
                    SELECT object_type
                    FROM project
                    WHERE model.project_id = project.id
                )
            """
            conn.execute(update_sql)
            op.alter_column("model", "object_type", existing_type=sa.SmallInteger(), nullable=False)
            batch_op.create_index(batch_op.f("ix_model_object_type"), ["object_type"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("model", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_model_object_type"))
        batch_op.drop_column("object_type")

    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_dataset_object_type"))
        batch_op.drop_column("object_type")
