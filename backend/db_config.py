def init_db(app):
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'pri'  # apna password
    app.config['MYSQL_DB'] = 'sales_db'