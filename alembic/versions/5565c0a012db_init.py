"""init

Revision ID: 5565c0a012db
Revises: 
Create Date: 2022-01-03 23:06:11.002572

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
from sqlalchemy import ForeignKey

revision = '5565c0a012db'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'geometry_object',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('type', sa.String)
    )
    op.create_table(
        'coordinate',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('geometry_object_id', sa.Integer, ForeignKey('geometry_object.id')),
        sa.Column('x', sa.Float),
        sa.Column('y', sa.Float)
    )


def downgrade():
    op.drop_table('geometry_object')
    op.drop_table('coordinate')
