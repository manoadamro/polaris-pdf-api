"""filename lookup

Revision ID: 2344c8a35859
Revises: 
Create Date: 2019-03-05 12:06:24.620045

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2344c8a35859"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "filename_lookup",
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("created_by_", sa.String(), nullable=False),
        sa.Column("modified", sa.DateTime(), nullable=False),
        sa.Column("modified_by_", sa.String(), nullable=False),
        sa.Column("encounter_uuid", sa.String(), nullable=False),
        sa.Column("file_name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("encounter_uuid"),
    )


def downgrade():
    op.drop_table("filename_lookup")
