import os

def init_db(app):
    app.config['MYSQL_HOST'] = 'mysql-....aivencloud.com'
    app.config['MYSQL_USER'] = 'avnadmin'
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
    app.config['MYSQL_DB'] = 'defaultdb'
    app.config['MYSQL_PORT'] = 14702