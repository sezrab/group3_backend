import flask
from flask import request, jsonify
from firebase_manager import FirebaseManager
from article_database import ArticleDatabase
app = flask.Flask(__name__)

fb = FirebaseManager()


@app.route('/getFeed', methods=['GET'])
def get_articles():
    adb = ArticleDatabase()
    userid = request.args.get('user_id')

    # Using user ID, get the user's interests from FIREBASE
    # Use some algorithm to curate a feed.

    sortby = request.args.get('sort_by')

    interests = fb.interests(userid)
    articles = [a[0]
                for a in adb.get_articles(sort=sortby, interests=interests)]
    output = []
    for article in articles:
        output.append(article.toJSON())

    response = jsonify(output)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/getArticlesFromIDs', methods=['GET'])
def get_articles_from_ids():
    adb = ArticleDatabase()
    ids = request.args.get('ids').split(',')
    articles = [a
                for a in adb.list_all_articles() if str(a.id) in ids] 
    print(articles)
    output = []
    for article in articles:
        output.append(article.toJSON())

    response = jsonify(output)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/allTopics', methods=['GET'])
def get_all_topics():
    with open("topics.txt") as f:
        topics = f.readlines()
    topics = [x.strip() for x in topics]
    response = jsonify(topics)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/', methods=['GET'])
def hello():
    return "Hello, World!"


@app.route('/newsletter', methods=['GET'])
def test_newsletter():
    uid = request.args.get('uid')
    fb.interests(uid)

    return "Hello, World!"


@app.route('/search', methods=['GET'])
def user_search():
    adb = ArticleDatabase()
    to_search = request.args.get('q')
    if to_search == None:
        return []
    matched_articles = adb.search_articles(to_search)

    output = []
    for article in matched_articles:
        output.append(article.toJSON())

    response = jsonify(output)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0')
