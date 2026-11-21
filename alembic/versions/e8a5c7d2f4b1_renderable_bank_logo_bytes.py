"""Align serving logo metadata with renderable content-addressed SVG bytes."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "e8a5c7d2f4b1"
down_revision = "b6f2c0a9d4e7"
branch_labels = None
depends_on = None

OLD_NATIONAL_BANK_ASSET_KEY = (
    "bank-logos/v1/26de030040a217f8038910f321c152bd1d79fa4ede662aee40b6f456fa1db8a4.svg"
)
NATIONAL_BANK_ASSET_SHA256 = "dd414f9e0ebd60e1ca6b8f36d9b2c7b6dd6ac02e12d479c33eca94c6e8fba685"
NATIONAL_BANK_ASSET_KEY = f"bank-logos/v1/{NATIONAL_BANK_ASSET_SHA256}.svg"


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE loan_serving_facts
            SET bank_logo_asset_key = CASE
                    WHEN bank_logo_asset_key = :old_national_key THEN :national_key
                    ELSE bank_logo_asset_key
                END,
                bank_logo_asset_sha256 = CASE
                    WHEN bank_logo_asset_key = :old_national_key THEN :national_sha
                    ELSE substring(bank_logo_asset_key from 'bank-logos/v1/([a-f0-9]{64})[.]svg')
                END
            WHERE bank_logo_asset_key ~ '^bank-logos/v1/[a-f0-9]{64}[.]svg$'
            """
        ).bindparams(
            old_national_key=OLD_NATIONAL_BANK_ASSET_KEY,
            national_key=NATIONAL_BANK_ASSET_KEY,
            national_sha=NATIONAL_BANK_ASSET_SHA256,
        )
    )


def downgrade() -> None:
    pass
