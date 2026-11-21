"""Correct recorded SHA-256 values for verified controlled bank-logo files."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "b6f2c0a9d4e7"
down_revision = "c90f0d6e1a2b"
branch_labels = None
depends_on = None

LOGO_ASSETS = (
    ("بانک اقتصاد نوین", "bank-logos/v1/3902883cfd7325451774fc5d9f99a4cb6fcf776f5077a8e4d2f3ad3293c2c787.svg", "e1e2eb891e8588e60cc470943f9afb843f9c228c2782a1ebf649d703b5f7c2bb"),
    ("بانک ایران و ونزوئلا", "bank-logos/v1/25629dd9f7828634048062f74b3411cb65b459893f36691cb4de945bc91cb020.svg", "b42d7f1ea6ca7bda36e1d4ecc3f8ae7b91c0c61491a11a200f1e9c998c113253"),
    ("بانک تجارت", "bank-logos/v1/06343e1bf69ad493df88299d266c255b549458a2ab0ea23744a5e83306694ec8.svg", "412fbc97dc743486de63e5f5114faaf924aa2632a3f0d37177b9abb55020c593"),
    ("بانک توسعه تعاون", "bank-logos/v1/809e9a337d769c8dfd84c01d2ffc4c059dd0a3a1008295e8e6c261fe4b4026a3.svg", "f71a1cfc388fd5c6068b2e0ed6cd2736144b6d31cd9024710fe734bc87699d2d"),
    ("بانک توسعه صادرات", "bank-logos/v1/71e86e80d234b77ac1bfd2bcdbbfa7595ec079ef7d29ac438818806c6507ea8b.svg", "bb616fd1df5bc8a09104ad069fff7c379311ea995d75ba784e34150035242491"),
    ("بانک خاورمیانه", "bank-logos/v1/63accc8957cb9792f9c8606da653e3121f8865fb195ad956b654f6f05be6f877.svg", "6e182f3caca0f083f198a098071bf01b2329add640d8f12cfab871378f541094"),
    ("بانک دی", "bank-logos/v1/307d5809e9779273624971b5f2c2f971176e45a664b46eb024f2b696534201d6.svg", "d81b5ce8df02c952060214607a0f5c37343d684985f35a0b7a6c0c7286d6726f"),
    ("بانک رفاه کارگران", "bank-logos/v1/fb0c72cbf0549753cb6fc56b9177da71b176ccb81d923966708721c1246b04be.svg", "72ac6309523d98946272affd1fb8750b4b596d81cd824c87af4a8ca8f966e555"),
    ("بانک سامان", "bank-logos/v1/b3887cd34509f69de042d6a68585cffc24d0134cfc867d8e13971a61484916ee.svg", "3eb83749f02ee16fb4109b3f35413f0a5550c05c062d6a02d41a2a361f892b1c"),
    ("بانک سرمایه", "bank-logos/v1/25589d05bbebfa9c662fbdb41d34cc48c83a6544f0b0abe0d948c38298dd01b3.svg", "e0f1fa0aae9b5509d16079831ee19446b1d48441a09becac1c33b5fafb80fd7f"),
    ("بانک سپه", "bank-logos/v1/aaf2b4f22b7a3020226d62c3fc9903f2f73312cef38f05d1e1308d33cc041d52.svg", "7a7860993a4cdaf6a944b2f345d8d807a61497f8dc82ead180a4db52624b729c"),
    ("بانک سینا", "bank-logos/v1/bd66c103eb19164ba177a839c4c5597cee6e6537dd150a6bcf5c547bc6b87bab.svg", "aa72c4c24da7b708caffbd6a4e70b6d38fc8f702a710aab453f4fd78484330d5"),
    ("بانک شهر", "bank-logos/v1/5f60ef318751ac950a91bbf8e6876353a08b7ff1553eb56f5268b2f7b7053956.svg", "445b011241f14b41ce960a382c4fcd1a89c6df620a79146a7a44a94ce64c4015"),
    ("بانک صادرات", "bank-logos/v1/fd529cd2dd90e30540c95bc1fb172ae8149c3bdf8cadb41c978cd5d99502c5da.svg", "211a0641e286742e12d862302ada6b72abb753973846c25fb77985ec59a11c5d"),
    ("بانک صنعت و معدن", "bank-logos/v1/d4d7d3b1ece8f2f073c72477cf8c536cb485d9bf50bdd63d3443ce98e06c6433.svg", "1d9d883a9a5777707492fcd92129e42dee35fdc6fc7bae4c46e38ca8a800199e"),
    ("بانک مرکزی", "bank-logos/v1/03ad836481c3be3b7a9035cfef5b845bf682756b4e2c8ae13c53af8cf0d2ab28.svg", "a2daf183daa24da74d8d4cac69c3fb257646ece44d6f1fd0d8845287c768c129"),
    ("بانک مسکن", "bank-logos/v1/5f6460cc5694c70c17e91cfeabeee3d0cb118b95500b69f0644aacb9c4d8f65a.svg", "44d1905104e207392f4a2167786549702bef4c3b71db36a06b99b664a0e863a7"),
    ("بانک ملت", "bank-logos/v1/8be1383361651e9a37b9d520af2ef84a88d0292d356cec614e0a42cc95a0b3c1.svg", "24cbb08c3b252800418c3794538a98f4bf12f5399b3bf613563ccc17f6346b10"),
    ("بانک ملی", "bank-logos/v1/26de030040a217f8038910f321c152bd1d79fa4ede662aee40b6f456fa1db8a4.svg", "5b8f3a011f44e4d3adcbb04d65222e5538bf81c413e31abbd575933ec3ee2a8d"),
    ("بانک پارسیان", "bank-logos/v1/32e51777852c839d410c25d14597ff33ecd4695ea28498ccfa2914b1ea689d38.svg", "ecc454a2b93f029d6042e0fbc0e04abe08820b1552a625b8ad128786d6633d7f"),
    ("بانک پاسارگاد", "bank-logos/v1/efe915505c7ac04536736e740032fe409e8b37540f6ae98bf33d980228ce8fc6.svg", "e94dcddf5e3a1a39270aaaec6020b51f279e2c7ac78a90b958798d2047715edc"),
    ("بانک کارآفرین", "bank-logos/v1/76f272f56539bbb31c6c6733522255deb7692a8866d9b5adc4cdd6098ab0f00c.svg", "50717059bbead192e220323de16c7cbdcaf4c72e5b8515eaac149cf793bab20c"),
    ("بانک کشاورزی", "bank-logos/v1/495efbb48ad9eac086c40e7e938ac06b636b07e1800f195d8062687f998d1df1.svg", "18b723e9fc986b0203489b63ee10ccb566aae7a3a6d6c944747f28e408bcbeec"),
    ("بانک گردشگری", "bank-logos/v1/26f5ac22e4bb3e1f79bc5572b659569caf96aec63596ccccfa11466d7e3dd8c8.svg", "9c6782ad57ed5201d8a4d130482e4612ecc0459cc69d72dc960f669919dfc811"),
    ("موسسه اعتباری ملل", "bank-logos/v1/7f0efbcaa554b71a22e084a9cb5a71efbf4abaf82f8b602ceeb57242849ff0fd.svg", "a4c22f756a113e0c59ca18e30177f9b00a6669b5683b99fbe9960877f7fd85fa"),
    ("پست بانک", "bank-logos/v1/f211749dd2d992500af2ab69b73c62b44710f55681aaf3f59d03675020375f40.svg", "37b5bf5608e38acc33221ac0a20b5cb66ababd63bdd936d85dc3f939bc92cdf3"),
)


def upgrade() -> None:
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
    pass
