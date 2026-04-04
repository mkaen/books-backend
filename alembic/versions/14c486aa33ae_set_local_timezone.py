"""Set local timezone

Revision ID: 14c486aa33ae
Revises: dc3d7f76c90e
Create Date: 2026-03-10 23:30:53.626139

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14c486aa33ae'
down_revision: Union[str, Sequence[str], None] = 'dc3d7f76c90e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        ALTER TABLE books 
        ALTER COLUMN created_at SET DEFAULT timezone('Europe/Tallinn', NOW()),
        ALTER COLUMN updated_at SET DEFAULT timezone('Europe/Tallinn', NOW())
    """)

    op.execute("""
        ALTER TABLE users 
        ALTER COLUMN created_at SET DEFAULT timezone('Europe/Tallinn', NOW()),
        ALTER COLUMN updated_at SET DEFAULT timezone('Europe/Tallinn', NOW())
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        ALTER TABLE books 
        ALTER COLUMN created_at SET DEFAULT NOW(),
        ALTER COLUMN updated_at SET DEFAULT NOW()
    """)

    op.execute("""
        ALTER TABLE users 
        ALTER COLUMN created_at SET DEFAULT NOW(),
        ALTER COLUMN updated_at SET DEFAULT NOW()
    """)
