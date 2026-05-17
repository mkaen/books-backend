"""created_at & updated_at timestamp modification

Revision ID: d35b2dc64274
Revises: 14c486aa33ae
Create Date: 2026-04-03 23:11:28.876800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'd35b2dc64274'
down_revision: Union[str, Sequence[str], None] = '14c486aa33ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CURRENT_UTC_TIMESTAMP = 'now()'


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('books', 'created_at',
                    existing_type=postgresql.TIMESTAMP(timezone=True),
                    server_default=sa.text(CURRENT_UTC_TIMESTAMP),
                    existing_nullable=False)

    op.alter_column('books', 'updated_at',
                    existing_type=postgresql.TIMESTAMP(timezone=True),
                    server_default=sa.text(CURRENT_UTC_TIMESTAMP),
                    existing_nullable=False)

    op.alter_column('users', 'created_at',
                    existing_type=postgresql.TIMESTAMP(timezone=True),
                    server_default=sa.text(CURRENT_UTC_TIMESTAMP),
                    existing_nullable=False)

    op.alter_column('users', 'updated_at',
                    existing_type=postgresql.TIMESTAMP(timezone=True),
                    server_default=sa.text(CURRENT_UTC_TIMESTAMP),
                    existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('users', 'updated_at',
                    existing_type=postgresql.TIMESTAMP(timezone=True),
                    server_default=None,
                    existing_nullable=False)

    op.alter_column('users', 'created_at',
                    existing_type=postgresql.TIMESTAMP(timezone=True),
                    server_default=None,
                    existing_nullable=False)

    op.alter_column('books', 'updated_at',
                    existing_type=postgresql.TIMESTAMP(timezone=True),
                    server_default=None,
                    existing_nullable=False)

    op.alter_column('books', 'created_at',
                    existing_type=postgresql.TIMESTAMP(timezone=True),
                    server_default=None,
                    existing_nullable=False)
