import flask
from flask import request, jsonify
from firebase_manager import FirebaseManager
from article_database import ArticleDatabase
app = flask.Flask(__name__)

fb = FirebaseManager()
adb = ArticleDatabase()


@app.route('/getFeed', methods=['GET'])
def get_articles():
    userid = request.args.get('user_id')
    sortby = request.args.get('sort_by')
    interests = fb.interests(userid)
    articles = adb.get_articles(sortby, 0, 10, interests)
    return jsonify()
