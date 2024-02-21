import flask
from flask import request, jsonify
from firebase_manager import FirebaseManager
from article_database import ArticleDatabase
app = flask.Flask(__name__)

fb = FirebaseManager()


@app.route('/getFeed', methods=['GET'])
def get_articles():
    adb = ArticleDatabase()
    # userid = request.args.get('user_id')
    # Using user ID, get the user's interests from FIREBASE
    # Use some algorithm to curate a feed.

    sortby = request.args.get('sort_by')

    # interests = fb.interests(userid)
    articles = adb.list_all_articles()
    # articles = adb.get_articles(sortby, 0, 10, interests)
    output = []
    for article in articles:
        output.append(article.toJSON())

    response = jsonify(output)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == '__main__':
    app.run()
