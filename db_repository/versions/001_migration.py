from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
alarm = Table('alarm', post_meta,
    Column('identifier', String(length=50), primary_key=True, nullable=False),
    Column('pretty_name', String(length=50)),
    Column('device_type', String(length=50), default=ColumnDefault('alarm')),
    Column('description', Text),
    Column('active', Boolean, default=ColumnDefault(True)),
)

card = Table('card', post_meta,
    Column('identifier', String(length=50), primary_key=True, nullable=False),
    Column('pretty_name', String(length=50)),
    Column('valid', Boolean, default=ColumnDefault(True)),
    Column('description', Text),
    Column('rfid_identifier', String),
)

detector = Table('detector', post_meta,
    Column('identifier', String(length=50), primary_key=True, nullable=False),
    Column('pretty_name', String(length=50)),
    Column('device_type', String(length=50), default=ColumnDefault('detector')),
    Column('description', Text),
    Column('active', Boolean, default=ColumnDefault(True)),
)

detector_alarm = Table('detector_alarm', post_meta,
    Column('alarm_id', String),
    Column('detector_id', String),
)

rfid = Table('rfid', post_meta,
    Column('identifier', String(length=50), primary_key=True, nullable=False),
    Column('pretty_name', String(length=50)),
    Column('device_type', String(length=50), default=ColumnDefault('rfid')),
    Column('description', Text),
    Column('active', Boolean, default=ColumnDefault(True)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['alarm'].create()
    post_meta.tables['card'].create()
    post_meta.tables['detector'].create()
    post_meta.tables['detector_alarm'].create()
    post_meta.tables['rfid'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['alarm'].drop()
    post_meta.tables['card'].drop()
    post_meta.tables['detector'].drop()
    post_meta.tables['detector_alarm'].drop()
    post_meta.tables['rfid'].drop()
