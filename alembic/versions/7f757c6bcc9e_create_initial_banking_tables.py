"""create initial banking tables

Revision ID: 7f757c6bcc9e
Revises:
Create Date: 2026-10-05 14:01:10.259566

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "7f757c6bcc9e"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Mark the existing database schema as the initial baseline."""
    pass


def downgrade() -> None:
    """No schema changes to reverse for the initial baseline."""
    pass