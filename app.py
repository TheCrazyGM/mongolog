import csv
import logging
from io import StringIO

from flask import Flask, jsonify, make_response, render_template, request
from flask_paginate import Pagination, get_page_parameter

from config import MongoHandler, collection

app = Flask("mongolog")

# Set up logging
mongo_uri = "mongodb://localhost:27017/"
mongo_db = "logs"
mongo_collection = "logs"
logger = logging.getLogger("mongolog")
logger.setLevel(logging.DEBUG)
handler = MongoHandler(mongo_uri, mongo_db, mongo_collection)
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
logger.addHandler(handler)
logger.info("Starting the application...")

per_page = 100


# Define routes
@app.route("/")
@app.route("/level/<level>")
def index(level=None):
    page = request.args.get(get_page_parameter(), type=int, default=1)
    page = request.args.get("page", 1, type=int)
    total_logs = collection.count_documents({})
    pagination = Pagination(
        page=page, total=total_logs, per_page=per_page, css_framework="bootstrap4"
    )

    query = {"log_level": {"$exists": True, "$ne": ""}}
    if level:
        query["log_level"] = level.upper()

    if query_str := request.args.get("query", ""):
        query["$or"] = [
            {"message": {"$regex": query_str, "$options": "i"}},
            {"app_name": {"$regex": query_str, "$options": "i"}},
        ]

    logs = (
        collection.find(query)
        .sort("timestamp", -1)
        .skip((page - 1) * per_page)
        .limit(per_page)
    )

    header = f"{level.upper()} Logs" if level else "All Logs"
    return render_template("logs.html", logs=logs, pagination=pagination, header=header)


@app.route("/export/csv")
def export_csv():
    # Retrieve the logs from the database
    logs = collection.find()

    # Create a StringIO object to write the CSV data to
    csv_output = StringIO()

    # Create a CSV writer object
    csv_writer = csv.writer(csv_output)

    # Write the header row
    csv_writer.writerow(["timestamp", "log_level", "app_name", "message"])

    # Write each log entry to the CSV file
    for log in logs:
        csv_writer.writerow(
            [log["timestamp"], log["log_level"], log["app_name"], log["message"]]
        )

    # Create a Flask response object with the CSV data
    response = make_response(csv_output.getvalue())

    # Set the response headers to indicate that this is a CSV file
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = "attachment; filename=logs.csv"

    return response


@app.route("/export/json")
def export_json():
    # Retrieve the logs from the database
    logs = collection.find()

    logs_list = [
        {
            "timestamp": str(log["timestamp"]),
            "log_level": str(log["log_level"]),
            "app_name": str(log["app_name"]),
            "message": str(log["message"]),
        }
        for log in logs
    ]
    return jsonify(logs_list)


if __name__ == "__main__":
    app.run(debug=True)
