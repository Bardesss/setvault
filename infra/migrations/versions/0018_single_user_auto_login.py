"""single-user auto-login — system_config.single_user_auto_login

Adds the opt-in flag that lets a single-user instance skip the login page
(auto-authenticate as the sole user). Defaults false; the admin toggle is
gated to the single-user case at the API layer.

Revision ID: 0018_single_user_auto_login
Revises: 0017_7c_monitors
Create Date: 2026-06-17 12:00:00
"""
import sqlalchemy as sa
from alembic import op

revision = "0018_single_user_auto_login"
down_revision = "0017_7c_monitors"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "system_config",
        sa.Column(
            "single_user_auto_login", sa.Boolean(), nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("system_config", "single_user_auto_login")
