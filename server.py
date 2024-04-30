import flask
from flask import request, jsonify
from firebase_manager import FirebaseManager
from article_database import ArticleDatabase

app = flask.Flask(__name__)

fb = FirebaseManager()


@app.route("/getFeed", methods=["GET"])
def get_articles():
    adb = ArticleDatabase()
    userid = request.args.get("user_id")

    # Using user ID, get the user's interests from FIREBASE
    # Use some algorithm to curate a feed.

    sortby = request.args.get("sort_by")

    interests = fb.interests(userid)

    sources = fb.get_selected_sources(userid, default=adb.list_sources())

    articles = [a[0] for a in adb.get_articles(interests=interests, sources=sources)]

    output = []
    for article in articles:
        output.append(article.toJSON())

    response = jsonify(output)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/listSources", methods=["GET"])
def list_sources():
    adb = ArticleDatabase()
    sources = adb.list_sources()
    response = jsonify(sources)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/getArticlesFromIDs", methods=["GET"])
def get_articles_from_ids():
    adb = ArticleDatabase()
    ids = request.args.get("ids").split(",")
    intIds = []
    for id in ids:
        try:
            intIds.append(int(id))
        except:
            pass
    articles = adb.get_article_by_ids(intIds)
    output = []
    for article in articles:
        output.append(article.toJSON())

    response = jsonify(output)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/allTopics", methods=["GET"])
def get_all_topics():
    with open("topics.txt") as f:
        topics = f.readlines()
    topics = [x.strip() for x in topics]
    response = jsonify(topics)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/search", methods=["GET"])
def user_search():
    adb = ArticleDatabase()
    to_search = request.args.get("q")
    if to_search == None:
        return []
    matched_articles = adb.search_articles(to_search)

    output = []
    for article in matched_articles:
        output.append(article.toJSON())

    response = jsonify(output)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0")
