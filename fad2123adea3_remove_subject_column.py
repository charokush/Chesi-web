"""remove_subject_column

Revision ID: fad2123adea3
Revises: <previous_revision_id>
Create Date: <timestamp>

"""

from alembic import op
import sqlalchemy as sa

# Define the previous revision ID if needed
# Use this if your migration depends on a previous migration
# Example: revision depends on '123456789abc'
# revision = '123456789abc'

# This is the upgrade function that defines what changes are made to the database schema.
def upgrade():
    # Use op.drop_column() to remove the 'subject' column from the 'teacher' table
    op.drop_column('teacher', 'subject')

# This is the downgrade function that defines how to rollback the migration if needed.
def downgrade():
    # Use op.add_column() to recreate the 'subject' column in the 'teacher' table
    op.add_column('teacher', sa.Column('subject', sa.String(100), nullable=False))

