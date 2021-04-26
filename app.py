from os import path

from flask import Flask, request
from flask.views import MethodView
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, ValidationError, fields, post_load
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


class TodosView(MethodView):
    schema = TodoSchema

    def post(self):
        request_data = request.get_json()

        try:
            new_todo = self.schema().load(request_data)
        except ValidationError as error:
            return {"status": "error", "message": error.messages}, 400

        new_todo = Todo(**new_todo)
        db.session.add(new_todo)
        db.session.commit()

        return {
            "status": "success",
            "data": {"message": "Todo added successfully!", "todo": self.schema().dump(new_todo)},
        }, 201

    def get(self):
        query = Todo.query.all()
        all_todos = self.schema(many=True).dump(query)

        return {"status": "success", "data": {"todos": all_todos}}, 200


class TodoView(MethodView):
    schema = TodoSchema

    def get(self, id):
        todo = Todo.query.get(id)
        if not todo:
            return {"status": "error", "message": "Todo not found!"}, 404

        return {"status": "success", "data": {"todo": self.schema().dump(todo)}}, 200

    def delete(self, id):
        todo = Todo.query.get(id)
        if not todo:
            return {"status": "error", "message": "Todo not found!"}, 404

        db.session.delete(todo)
        db.session.commit()

        return {"status": "success", "message": "Todo deleted successfully!"}, 204


app.add_url_rule("/api/todos", view_func=TodosView.as_view("todos"))
app.add_url_rule("/api/todos/<id>", view_func=TodoView.as_view("todo"))
