"""remove_amount_from_payments

Revision ID: af4050b89401
Revises: a2db01140c1f
Create Date: 2026-05-14 15:57:18.737881

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "af4050b89401"
down_revision: Union[str, Sequence[str], None] = "a2db01140c1f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Remove amount column from payments table."""
    op.drop_column("payments", "amount")


def downgrade() -> None:
    """Downgrade schema: Add amount column back to payments table."""
    op.add_column(
        "payments",
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
    )
