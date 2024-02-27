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


@app.route('/recommendation_score', methods=['GET'])
def recommendation_testing():
    adb = ArticleDatabase()

    articles = adb.get_articles(2, 0, 100, fb.interests(1))
    output = []
    for article,score in articles:
        output.append((article.toJSON(),score))
        
    return output


@app.route('/search', methods=['GET'])
def user_search():
    adb = ArticleDatabase()
    to_search = request.args.get('search')
    # matched_articles = adb.
    

if __name__ == '__main__':
    app.run()
