from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
alarm_status = Table('alarm_status', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('attribute', String(length=64)),
    Column('value', String(length=64)),
)

settings = Table('settings', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('attribute', String(length=64)),
    Column('value', String(length=64)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['alarm_status'].create()
    post_meta.tables['settings'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['alarm_status'].drop()
    post_meta.tables['settings'].drop()
