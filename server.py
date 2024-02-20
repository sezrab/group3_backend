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
    # Using user ID, get the user's interests from FIREBASE
    # Use some algorithm to curate a feed.
    # (For now, just return all articles matching the user's interests)

    sortby = request.args.get('sort_by')

    interests = fb.interests(userid)

    articles = adb.get_articles(sortby, 0, 10, interests)
    output = []
    for article in articles:
        output.append(article.to_dict())
