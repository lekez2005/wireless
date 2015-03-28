from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', post_meta,
    Column('identifier', String, primary_key=True, nullable=False),
    Column('token', String, nullable=False),
    Column('name', String),
    Column('authorized', Boolean, default=ColumnDefault(False)),
    Column('gcm_id', String),
)

user_alarm = Table('user_alarm', post_meta,
    Column('alarm_id', String),
    Column('user_id', String),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].create()
    post_meta.tables['user_alarm'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].drop()
    post_meta.tables['user_alarm'].drop()
