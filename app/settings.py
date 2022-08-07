import os

# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost/studb2'
SQLALCHEMY_DATABASE_URI = os.environ.get('JAWSDB_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
secret_key = "login"


