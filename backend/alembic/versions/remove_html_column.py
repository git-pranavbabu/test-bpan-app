"""Remove full_data_html column from bpans table

Revision ID: remove_html_column
Revises: add_new_lookup_tables
Create Date: 2026-06-09

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'remove_html_column'
down_revision: Union[str, None] = 'add_new_lookup_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('bpans', 'full_data_html')


def downgrade() -> None:
    op.add_column('bpans', sa.Column('full_data_html', sa.Text(), nullable=True))
