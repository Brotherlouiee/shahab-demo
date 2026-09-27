"""Persist controlled bank-logo asset references for published serving facts."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "c90f0d6e1a2b"
down_revision = "a62c0b5b005b"
branch_labels = None
depends_on = None

LOGO_ASSETS = (
    ("بانک اقتصاد نوین", "bank-logos/بانک اقتصاد نوین.svg", "3902883cfd7325451774fc5d9f99a4cb6fcf776f5077a8e4d2f3ad3293c2c787"),
    ("بانک ایران و ونزوئلا", "bank-logos/بانک ایران ونزوئلا.svg", "25629dd9f7828634048062f74b3411cb65b459893f36691cb4de945bc91cb020"),
    ("بانک تجارت", "bank-logos/بانک تجارت.svg", "06343e1bf69ad493df88299d266c255b549458a2ab0ea23744a5e83306694ec8"),
    ("بانک توسعه تعاون", "bank-logos/بانک توسعه تعاون.svg", "809e9a337d769c8dfd84c01d2ffc4c059dd0a3a1008295e8e6c261fe4b4026a3"),
    ("بانک توسعه صادرات", "bank-logos/بانک توسعه صادرات.svg", "71e86e80d234b77ac1bfd2bcdbbfa7595ec079ef7d29ac438818806c6507ea8b"),
    ("بانک خاورمیانه", "bank-logos/بانک خاورمیانه.svg", "63accc8957cb9792f9c8606da653e3121f8865fb195ad956b654f6f05be6f877"),
    ("بانک دی", "bank-logos/بانک دی.svg", "307d5809e9779273624971b5f2c2f971176e45a664b46eb024f2b696534201d6"),
    ("بانک رفاه کارگران", "bank-logos/بانک رفاه کارگران.svg", "fb0c72cbf0549753cb6fc56b9177da71b176ccb81d923966708721c1246b04be"),
    ("بانک سامان", "bank-logos/بانک سامان.svg", "b3887cd34509f69de042d6a68585cffc24d0134cfc867d8e13971a61484916ee"),
    ("بانک سرمایه", "bank-logos/بانک سرمایه.svg", "25589d05bbebfa9c662fbdb41d34cc48c83a6544f0b0abe0d948c38298dd01b3"),
    ("بانک سپه", "bank-logos/بانک سپه.svg", "aaf2b4f22b7a3020226d62c3fc9903f2f73312cef38f05d1e1308d33cc041d52"),
    ("بانک سینا", "bank-logos/بانک سینا.svg", "bd66c103eb19164ba177a839c4c5597cee6e6537dd150a6bcf5c547bc6b87bab"),
    ("بانک شهر", "bank-logos/بانک شهر.svg", "5f60ef318751ac950a91bbf8e6876353a08b7ff1553eb56f5268b2f7b7053956"),
    ("بانک صادرات", "bank-logos/بانک صادرات.svg", "fd529cd2dd90e30540c95bc1fb172ae8149c3bdf8cadb41c978cd5d99502c5da"),
    ("بانک صنعت و معدن", "bank-logos/بانک صنعت و معدن.svg", "d4d7d3b1ece8f2f073c72477cf8c536cb485d9bf50bdd63d3443ce98e06c6433"),
    ("بانک مرکزی", "bank-logos/بانک مرکزی.svg", "03ad836481c3be3b7a9035cfef5b845bf682756b4e2c8ae13c53af8cf0d2ab28"),
    ("بانک مسکن", "bank-logos/بانک مسکن.svg", "5f6460cc5694c70c17e91cfeabeee3d0cb118b95500b69f0644aacb9c4d8f65a"),
    ("بانک ملت", "bank-logos/بانک ملت.svg", "8be1383361651e9a37b9d520af2ef84a88d0292d356cec614e0a42cc95a0b3c1"),
    ("بانک ملی", "bank-logos/بانک ملی.svg", "26de030040a217f8038910f321c152bd1d79fa4ede662aee40b6f456fa1db8a4"),
    ("بانک پارسیان", "bank-logos/بانک پارسیان.svg", "32e51777852c839d410c25d14597ff33ecd4695ea28498ccfa2914b1ea689d38"),
    ("بانک پاسارگاد", "bank-logos/بانک پاسارگاد.svg", "efe915505c7ac04536736e740032fe409e8b37540f6ae98bf33d980228ce8fc6"),
    ("بانک کارآفرین", "bank-logos/بانک کارآفرین.svg", "76f272f56539bbb31c6c6733522255deb7692a8866d9b5adc4cdd6098ab0f00c"),
    ("بانک کشاورزی", "bank-logos/بانک کشاورزی.svg", "495efbb48ad9eac086c40e7e938ac06b636b07e1800f195d8062687f998d1df1"),
    ("بانک گردشگری", "bank-logos/بانک گردشگری.svg", "26f5ac22e4bb3e1f79bc5572b659569caf96aec63596ccccfa11466d7e3dd8c8"),
    ("موسسه اعتباری ملل", "bank-logos/موسسه اعتباری ملل.svg", "7f0efbcaa554b71a22e084a9cb5a71efbf4abaf82f8b602ceeb57242849ff0fd"),
    ("پست بانک", "bank-logos/پست بانک.svg", "f211749dd2d992500af2ab69b73c62b44710f55681aaf3f59d03675020375f40"),
)


def upgrade() -> None:
    op.add_column("loan_serving_facts", sa.Column("bank_logo_asset_key", sa.String(length=512), nullable=True))
    op.add_column("loan_serving_facts", sa.Column("bank_logo_asset_sha256", sa.String(length=64), nullable=True))

    facts = sa.table(
        "loan_serving_facts",
        sa.column("loan_product_version_id"),
        sa.column("bank_logo_asset_key"),
        sa.column("bank_logo_asset_sha256"),
    )
    versions = sa.table("loan_product_versions", sa.column("loan_product_version_id"), sa.column("loan_product_id"))
    products = sa.table("loan_products", sa.column("loan_product_id"), sa.column("lender_id"))
    lenders = sa.table("lenders", sa.column("lender_id"), sa.column("canonical_name"))
    for lender_name, asset_key, asset_sha256 in LOGO_ASSETS:
        version_ids = (
            sa.select(versions.c.loan_product_version_id)
            .select_from(
                versions.join(products, versions.c.loan_product_id == products.c.loan_product_id).join(
                    lenders, products.c.lender_id == lenders.c.lender_id
                )
            )
            .where(lenders.c.canonical_name == lender_name)
        )
        op.execute(
            sa.update(facts)
            .where(facts.c.loan_product_version_id.in_(version_ids))
            .values(bank_logo_asset_key=asset_key, bank_logo_asset_sha256=asset_sha256)
        )


def downgrade() -> None:
    op.drop_column("loan_serving_facts", "bank_logo_asset_sha256")
    op.drop_column("loan_serving_facts", "bank_logo_asset_key")
