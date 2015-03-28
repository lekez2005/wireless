from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
door = Table('door', pre_meta,
    Column('identifier', VARCHAR, primary_key=True, nullable=False),
    Column('pretty_name', VARCHAR(length=50)),
    Column('device_type', VARCHAR(length=50)),
    Column('description', TEXT),
    Column('active', BOOLEAN),
    Column('dd', TEXT),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['door'].columns['dd'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['door'].columns['dd'].create()
