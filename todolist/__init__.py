import sqlite3

from flask import Flask
from .views import views
from .variables import db_path

def create_app(testing=False):
    app = Flask(__name__)
    app.secret_key = 'dev'

    if testing:
        app.testing = True
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS credentials (
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
        );
        """)
        if testing:
            conn.execute("""
                DELETE FROM credentials
            """)
    app.register_blueprint(views)
    return app