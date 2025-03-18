from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from src import config

migrate = Migrate()
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    migrate.init_app(app, db, render_as_batch=True)

    from . import models
    from src.views import main

    app.register_blueprint(main.bp)

    return app
