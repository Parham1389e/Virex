"""Add receipt metadata, rejection reason, and delivery state."""
from alembic import op
import sqlalchemy as sa
revision="0003_receipt_and_decision_metadata"; down_revision="0002_production_schema"; branch_labels=None; depends_on=None
def upgrade():
    op.add_column("topups", sa.Column("receipt_size", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("topups", sa.Column("rejection_reason", sa.String(500), nullable=True))
def downgrade():
    op.drop_column("topups", "rejection_reason"); op.drop_column("topups", "receipt_size")
