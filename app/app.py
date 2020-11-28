import re
from flask import Flask, request, abort, jsonify
from math import cos, asin, pi, sqrt

app = Flask(__name__)
treasure_location = (50.051227, 19.945704)


@app.route('/')
def home():
    return "Home page"


@app.route('/treasure_hunt.json')
def check_position():
    position = request.args.getlist('current_location[]', type=float)
    email = request.args.get("email", type=str)
    validate_position(position)
    validate_email(email)
    return jsonify(status="ok", distance=calculate_distance(position, treasure_location))


@app.errorhandler(404)
def page_not_found(error):
    return jsonify(status="error", distance=-1, error=error.description), 404


def validate_position(position):
    if position is None:
        abort(404, description="Position is missing")
    elif len(position) < 2:
        abort(404, description="Position uncompleted or wrong type")


def validate_email(email):
    if email is None:
        abort(404, description="Email is missing")
    if not re.search(r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$", email):
        abort(404, description="Invalid email")


def calculate_distance(point_1, point_2):
    p = pi / 180
    a = 0.5 - cos((point_2[0] - point_1[0]) * p) / 2 \
        + cos(point_1[0] * p) * cos(point_2[0] * p) * (1 - cos((point_2[1] - point_1[1]) * p)) / 2
    return 2 * 6371 * asin(sqrt(a)) * 1000


if __name__ == '__main__':
    app.run()
