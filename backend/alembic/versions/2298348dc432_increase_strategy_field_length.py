"""increase strategy field length

Revision ID: 2298348dc432
Revises: 98ded3f2100f
Create Date: 2025-11-06 21:44:21.341870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2298348dc432'
down_revision: Union[str, None] = '98ded3f2100f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Increase strategy column length from 20 to 50
    op.alter_column('usage_records', 'strategy',
                    existing_type=sa.String(length=20),
                    type_=sa.String(length=50),
                    existing_nullable=False)


def downgrade() -> None:
    # Revert strategy column length from 50 to 20
    op.alter_column('usage_records', 'strategy',
                    existing_type=sa.String(length=50),
                    type_=sa.String(length=20),
                    existing_nullable=False)
