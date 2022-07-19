"""rename column

Revision ID: 7b19ac1c5b8e
Revises: 2344c8a35859
Create Date: 2020-05-28 10:23:32.782296

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "7b19ac1c5b8e"
down_revision = "2344c8a35859"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("filename_lookup", "encounter_uuid", new_column_name="lookup_uuid")
    op.drop_constraint(
        "filename_lookup_encounter_uuid_key", "filename_lookup", type_="unique"
    )
    op.create_unique_constraint(None, "filename_lookup", ["lookup_uuid"])


def downgrade():
    op.alter_column("filename_lookup", "lookup_uuid", new_column_name="encounter_uuid")
    op.drop_constraint(
        "filename_lookup_lookup_uuid_key", "filename_lookup", type_="unique"
    )
    op.create_unique_constraint(None, "filename_lookup", ["encounter_uuid"])
