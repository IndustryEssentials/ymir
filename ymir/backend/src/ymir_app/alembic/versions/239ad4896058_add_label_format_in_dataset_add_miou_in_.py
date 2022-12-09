"""add miou in model, add object_type in docker_image

Revision ID: 239ad4896058
Revises: c91513775753
Create Date: 2022-10-26 11:35:59.598597

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "239ad4896058"
down_revision = "b88055a18c30"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("model", schema=None) as batch_op:
        batch_op.add_column(sa.Column("miou", sa.Float(), nullable=True))
    with op.batch_alter_table("docker_image", schema=None) as batch_op:
        batch_op.add_column(sa.Column("object_type", sa.SmallInteger(), nullable=False, server_default="1"))
        batch_op.create_index(batch_op.f("ix_docker_image_object_type"), ["object_type"], unique=False)


#    conn = op.get_bind()
#    iterations = conn.execute("UPDATE docker_image SET object_type = 1")
# ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("docker_image", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_docker_image_object_type"))
        batch_op.drop_column("object_type")
    with op.batch_alter_table("model", schema=None) as batch_op:
        batch_op.drop_column("miou")
    # ### end Alembic commands ###
