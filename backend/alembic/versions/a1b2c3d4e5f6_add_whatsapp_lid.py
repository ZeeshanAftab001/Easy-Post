"""add whatsapp_lid to users

Revision ID: a1b2c3d4e5f6
Revises: db8bccf93acc
Create Date: 2026-06-02

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'a1b2c3d4e5f6'
down_revision = '035f5e8e335e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('whatsapp_lid', sa.String(), nullable=True))
    op.create_unique_constraint('uq_users_whatsapp_lid', 'users', ['whatsapp_lid'])


def downgrade() -> None:
    op.drop_constraint('uq_users_whatsapp_lid', 'users', type_='unique')
    op.drop_column('users', 'whatsapp_lid')
