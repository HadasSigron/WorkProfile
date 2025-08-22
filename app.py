from flask import Flask, render_template, request, Response, jsonify
from os import environ
from dbcontext import db_data, db_delete, db_add, health_check
from person import Person
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
log_handler = logging.StreamHandler()
log_handler.setLevel(logging.INFO)
app.logger.addHandler(log_handler)

host_name = environ.get("HOSTNAME","unknown")
db_host = environ.get('DB_HOST')
backend = environ.get('BACKEND') or "http://localhost"

@app.route("/")
def main():
    app.logger.info("Entering main  route")
    data = db_data()
    return render_template("index.html.jinja", host_name=host_name, db_host=db_host, data=data, backend=backend)

@app.route("/delete/<int:id>", methods=["DELETE"])
def delete(id: int):
    app.logger.info("Request to delete person with id: %s", id)
    return db_delete(id)

@app.route("/add", methods=["POST","PUT"])
def add():
    body = request.json
    if body is not None:
        app.logger.info("Request to add person with body: %s", body)
        person = Person(0, body["firstName"], body["lastName"], body["age"], body["address"], body["workplace"])
        return db_add(person)
    app.logger.error("Request body is ggggempty")
    return Response(status=404)

@app.route("/health")
def health():
    try:
        app.logger.info("Application is running")
        status = {
            "status": "healthy",
            "components": {
                "application": "running"
            }
        }
        return jsonify(status), 200
    except Exception as e:
        status = {
            "status": "unhealthy",
            "error": str(e)
        }
        return jsonify(status), 503


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
