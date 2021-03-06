import re
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from math import cos, asin, pi, sqrt

app = Flask(__name__)
treasure_location = (50.051227, 19.945704)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '@gmail.com'
app.config['MAIL_PASSWORD'] = '****'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:password@localhost:5432/treasure_hunt"
db = SQLAlchemy(app)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True, nullable=False)
    found_treasure = db.Column(db.Boolean)

    def __repr__(self):
        return '<Player %r>' % self.email


@app.route('/')
def home():
    return "Home page"


@app.route('/treasure_hunt.json')
def check_position():
    position = request.args.getlist('current_location[]', type=float)
    email = request.args.get("email", type=str)
    validate_position(position)
    validate_email(email)
    distance = calculate_distance(position, treasure_location)
    if distance <= 5:
        send_email(email)
    return jsonify(status="ok", distance=distance)


@app.errorhandler(404)
def page_not_found(error):
    return jsonify(status="error", distance=-1, error=error.description), 404


def get_found_treasure(email):
    players = Player.query.filter(Player.email == email).all()
    return len(players) > 0 and players[0].found_treasure is True


def add_player(email):
    if len(db.session.query(Player).filter(Player.email == email).all()) == 0:
        player = Player(email=email, found_treasure=False)
        db.session.add(player)
        db.session.commit()


def set_found_treasure(email):
    add_player(email)
    db.session.query(Player).filter(Player.email == email).update({Player.found_treasure: True},
                                                                  synchronize_session=False)
    db.session.commit()


def get_players_count():
    return len(db.session.query(Player).filter(Player.found_treasure == 'true').all())


def send_email(email):
    if get_found_treasure(email):
        return
    msg = Message('Congratulations!', sender='@gmail.com', recipients=[email])
    msg.body = "Hey, you’ve found a treasure, congratulations! You are {} treasure hunter who has found the treasure." \
               "\nTreasure position is: {}"\
        .format(get_players_count() + 1, treasure_location)
    mail.send(msg)
    set_found_treasure(email)


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
    db.create_all()
    app.run()
