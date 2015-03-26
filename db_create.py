__author__ = 'lekez2005'

from migrate.versioning import api
import os

from app import db
from app import app

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = app.config['SQLALCHEMY_DATABASE_URI']
print SQLALCHEMY_DATABASE_URI
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

db.create_all()
print db.metadata.tables.keys()

if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))

