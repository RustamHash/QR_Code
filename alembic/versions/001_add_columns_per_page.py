"""add columns_per_page to user_settings

Revision ID: 001_add_columns_per_page
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_add_columns_per_page'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем колонку columns_per_page с значением по умолчанию 1
    # Для SQLite сначала добавляем как nullable, затем обновляем и делаем NOT NULL
    op.add_column('user_settings', sa.Column('columns_per_page', sa.Integer(), nullable=True))
    
    # Обновляем все существующие записи, устанавливая columns_per_page = 1
    op.execute("UPDATE user_settings SET columns_per_page = 1")
    
    # Делаем колонку NOT NULL
    op.alter_column('user_settings', 'columns_per_page', nullable=False, server_default='1')


def downgrade() -> None:
    # Удаляем колонку columns_per_page
    op.drop_column('user_settings', 'columns_per_page')

