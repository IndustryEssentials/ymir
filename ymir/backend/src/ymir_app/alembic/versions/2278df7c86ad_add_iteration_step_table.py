"""add iteration_step table

Revision ID: 2278df7c86ad
Revises: 9bb7bb8b71c3
Create Date: 2022-10-11 10:48:28.244903

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2278df7c86ad"
down_revision = "9bb7bb8b71c3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "iteration_step",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("task_type", sa.Integer(), nullable=False),
        sa.Column("iteration_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=True),
        sa.Column("input_dataset_id", sa.Integer(), nullable=True),
        sa.Column("output_dataset_id", sa.Integer(), nullable=True),
        sa.Column("output_model_id", sa.Integer(), nullable=True),
        sa.Column("is_finished", sa.Boolean(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("create_datetime", sa.DateTime(), nullable=False),
        sa.Column("update_datetime", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("iteration_step", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_iteration_step_id"), ["id"], unique=False)
        batch_op.create_index(batch_op.f("ix_iteration_step_input_dataset_id"), ["input_dataset_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_iteration_step_iteration_id"), ["iteration_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_iteration_step_name"), ["name"], unique=False)
        batch_op.create_index(batch_op.f("ix_iteration_step_output_dataset_id"), ["output_dataset_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_iteration_step_output_model_id"), ["output_model_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_iteration_step_task_id"), ["task_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_iteration_step_task_type"), ["task_type"], unique=False)

    with op.batch_alter_table("visualization", schema=None) as batch_op:
        batch_op.drop_index("ix_visual_project_id")
        batch_op.drop_index("ix_visualization_tid")
        batch_op.drop_index("ix_visualization_user")

    op.drop_table("visualization")
    op.drop_table("task_visual_relationship")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "task_visual_relationship",
        sa.Column("task_id", sa.INTEGER(), nullable=False),
        sa.Column("visualization_id", sa.INTEGER(), nullable=False),
        sa.PrimaryKeyConstraint("task_id", "visualization_id"),
    )
    op.create_table(
        "visualization",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("user_id", sa.INTEGER(), nullable=False),
        sa.Column("tid", sa.VARCHAR(length=100), nullable=False),
        sa.Column("is_deleted", sa.BOOLEAN(), nullable=False),
        sa.Column("create_datetime", sa.DATETIME(), nullable=False),
        sa.Column("update_datetime", sa.DATETIME(), nullable=False),
        sa.Column("project_id", sa.INTEGER(), nullable=True),
        sa.Column("conf_thr", sa.FLOAT(), nullable=True),
        sa.Column("iou_thr", sa.FLOAT(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("visualization", schema=None) as batch_op:
        batch_op.create_index("ix_visualization_user", ["user_id"], unique=False)
        batch_op.create_index("ix_visualization_tid", ["tid"], unique=False)
        batch_op.create_index("ix_visual_project_id", ["project_id"], unique=False)

    with op.batch_alter_table("iteration_step", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_iteration_step_task_type"))
        batch_op.drop_index(batch_op.f("ix_iteration_step_task_id"))
        batch_op.drop_index(batch_op.f("ix_iteration_step_output_model_id"))
        batch_op.drop_index(batch_op.f("ix_iteration_step_output_dataset_id"))
        batch_op.drop_index(batch_op.f("ix_iteration_step_name"))
        batch_op.drop_index(batch_op.f("ix_iteration_step_iteration_id"))
        batch_op.drop_index(batch_op.f("ix_iteration_step_input_dataset_id"))
        batch_op.drop_index(batch_op.f("ix_iteration_step_id"))

    op.drop_table("iteration_step")
    # ### end Alembic commands ###
