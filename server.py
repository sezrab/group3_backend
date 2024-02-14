import flask
from flask import request, jsonify

app = flask.Flask(__name__)


@app.route('/userFeed', methods=['GET'])
def get_articles():
    # do something with the posted user data
    id = request.args.get('id')
    # access the firebase, get interests and any other relevant info
    # do some processing
    # return the articles
    return jsonify()
