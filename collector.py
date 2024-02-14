import random
import os
import json
import sqlite3
import requests
import xmltodict
from models.article import Article
from topic_classifier import tagger, utils
CONFIDENCE_THRESH = 0.16


def getArxivData(search_query, start=0, max_results=10, sortBy="submittedDate"):
    # https://info.arxiv.org/help/api/user-manual.html#_calling_the_api
    # parameters:   search_query : string
    #               start : int
    #               max_results : int
    #               sortBy : relevance, submittedDate, lastUpdatedDate
    #               sortOrder : ascending, descending

    url = f'http://export.arxiv.org/api/query?sortBy={sortBy}&search_query={
        search_query}&start={start}&max_results={max_results}'
    data = requests.get(url)
    data = xmltodict.parse(data.text)

    articles = []

    for entry in data['feed']['entry']:
        try:
            entry['author'] = [].extend([entry['name']
                                        for entry in entry['author']])
        except TypeError:

            entry['author'] = [entry['author']['name']]

        tags = tagger.tag_abstract(
            entry['summary'], thresh=CONFIDENCE_THRESH, data_folder="topic_classifier/data/")

        entry['tags'] = tags

        articles.append(Article.fromJSON(entry))

    return articles


topicData = utils.load_topic_vector_file("topic_classifier/data/")
topics = list(topicData.keys())

# choose five random topics
topics = random.sample(topics, 5)


if __name__ == "__main__":
    # conn = initArchiveDB()
    import datetime
    date = datetime.datetime.now().strftime("%d%m%y")

    todayArchive = f"archive_{date}.json"

    if not os.path.exists(todayArchive):
        print("Archive does not exist")
        arcs = getArxivData("natural language processing",
                            max_results=100, sortBy="submittedDate")
        out = []
        for arc in arcs:
            out.append(arc.toJSON())

        json.dump(out, open(todayArchive, 'w'))
    else:
        print("Archive already exists")
        arcs = json.load(open(todayArchive, 'r'))
        for i in range(len(arcs)):
            arcs[i] = Article.fromJSON(arcs[i])

    print(f"Found {len(arcs)} articles")
    print(f"My interests: {topics}")
    print()
    for arc in arcs:
        # get intersection of topics and tags
        matches = list(set(arc.tags_noscore) & set(topics))
        if len(matches) > 0:
            print(arc.title, len(matches))
            print()
