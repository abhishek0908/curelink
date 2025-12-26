"""updated schema fdfd

Revision ID: 9a41d62f6306
Revises: 20d7f9c82d43
Create Date: 2025-12-26 03:23:40.767527

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a41d62f6306'
down_revision: Union[str, Sequence[str], None] = '20d7f9c82d43'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
