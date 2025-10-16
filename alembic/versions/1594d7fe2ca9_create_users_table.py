"""Create users table

Revision ID: 1594d7fe2ca9
Revises: 
Create Date: 2025-10-16 10:56:19.291539

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1594d7fe2ca9'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('email', sa.String, unique=True, index=True, nullable=False),
        sa.Column('password_hash', sa.String, nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'OPERATOR', 'ACCOUNTANT', 'SUPERVISOR', name='userrole'), nullable=False, server_default='OPERATOR'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS userrole')
