from os import path

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, post_load
from sqlalchemy import func

BASE_DIR = path.dirname(path.abspath(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = "a-very-random-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{path.join(BASE_DIR, 'db.sqlite3')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Todo(db.Model):
    __tablename__ = "todos"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=func.now())


class TodoSchema(Schema):
    id = fields.Int(dump_only=True)
    content = fields.Str(required=True)
    is_completed = fields.Bool()
    timestamp = fields.DateTime(dump_only=True)

    @post_load
    def create_todo(self, data, **kwargs):
        return Todo(**data)