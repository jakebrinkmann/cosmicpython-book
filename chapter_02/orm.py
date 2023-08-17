import sqlalchemy as sa
from sqlalchemy.orm import mapper, relationship

# ORM imports/depends on/knows about the domain model
import model

metadata = sa.MetaData()
tbl_order_lines = sa.Table(
    "order_lines",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("sku", sa.String(255)),
    sa.Column("qty", sa.Integer, nullable=False),
    sa.Column("orderid", sa.String(255)),
)


# TODO: replace mapper() with registry.map_imperatively()
# https://docs.sqlalchemy.org/en/14/orm/mapping_styles.html?highlight=sqlalchemy#orm-imperative-mapping
def start_mappers():
    lines_mapper = mapper(model.OrderLine, tbl_order_lines)
