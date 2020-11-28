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
    email = request.args.get("email", None)
    if position is None or email is None:
        abort(404, description="error description")
    return jsonify(status="ok", distance=calculate_distance(position, treasure_location))


@app.errorhandler(404)
def page_not_found(error):
    return jsonify(status="error", distance=-1, error=error.description), 404


def calculate_distance(point_1, point_2):
    p = pi / 180
    a = 0.5 - cos((point_2[0] - point_1[0]) * p) / 2 \
        + cos(point_1[0] * p) * cos(point_2[0] * p) * (1 - cos((point_2[1] - point_1[1]) * p)) / 2 * 1000
    return 2 * 6371 * asin(sqrt(a))


if __name__ == '__main__':
    app.run()
