from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
rfid = Table('rfid', post_meta,
    Column('identifier', String(length=50), primary_key=True, nullable=False),
    Column('pretty_name', String(length=50)),
    Column('device_type', String(length=50), default=ColumnDefault('rfid')),
    Column('description', Text),
    Column('door_identifier', String),
    Column('active', Boolean, default=ColumnDefault(True)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['rfid'].columns['door_identifier'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['rfid'].columns['door_identifier'].drop()
