"""create initial banking tables

Revision ID: 7f757c6bcc9e
Revises:
Create Date: 2026-10-05 14:01:10.259566

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "7f757c6bcc9e"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the initial banking database schema."""

    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True
        ),
        sa.Column(
            "username",
            sa.String(),
            nullable=True
        ),
        sa.Column(
            "password",
            sa.String(),
            nullable=True
        ),
        sa.Column(
            "balance",
            sa.Float(),
            nullable=True
        ),
        sa.UniqueConstraint(
            "username",
            name="uq_users_username"
        )
    )

    op.create_index(
        "ix_users_username",
        "users",
        ["username"],
        unique=False
    )

    op.create_table(
        "transactions",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True
        ),
        sa.Column(
            "sender_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=True
        ),
        sa.Column(
            "receiver_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False
        ),
        sa.Column(
            "amount",
            sa.Float(),
            nullable=False
        ),
        sa.Column(
            "timestamp",
            sa.String(),
            nullable=True
        )
    )


def downgrade() -> None:
    """Drop the initial banking database schema."""

    op.drop_table("transactions")

    op.drop_index(
        "ix_users_username",
        table_name="users"
    )

    op.drop_table("users")