"""partition login history

Revision ID: 7f83b7a43830
Revises: 7741ef2bb6cc
Create Date: 2025-02-08 18:31:55.906405

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '7f83b7a43830'
down_revision: Union[str, None] = '7741ef2bb6cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE login_history_january PARTITION OF auth.login_history
            FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
        """
    )
    op.execute(
        """
        CREATE TABLE login_history_february PARTITION OF auth.login_history
            FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
        """
    )
    op.execute(
        """
        CREATE TABLE login_history_march PARTITION OF auth.login_history
            FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');
        """
    )
    op.execute(
        """
        CREATE TABLE login_history_april PARTITION OF auth.login_history
            FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');
        """
    )


def downgrade() -> None:
    op.execute('DROP TABLE login_history_january')
    op.execute('DROP TABLE login_history_february')
    op.execute('DROP TABLE login_history_march')
    op.execute('DROP TABLE login_history_april')
