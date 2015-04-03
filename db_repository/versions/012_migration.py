from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
detector = Table('detector', post_meta,
    Column('identifier', String(length=50), primary_key=True, nullable=False),
    Column('pretty_name', String(length=50)),
    Column('device_type', String(length=50), default=ColumnDefault('detector')),
    Column('description', Text),
    Column('active', Boolean, default=ColumnDefault(True)),
    Column('alarm_message', Text),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['detector'].columns['alarm_message'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['detector'].columns['alarm_message'].drop()
