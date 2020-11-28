from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def home():
    return "Home page"


@app.route('/treasure_hunt.json')
def check_position():
    return "Position: {}. Email: {}".format(request.args.getlist('current_location[]', None),
                                            request.args.get("email", None))


if __name__ == '__main__':
    app.run()
