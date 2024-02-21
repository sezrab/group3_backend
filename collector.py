import datetime
import random
import os
import json
import sqlite3
import requests
import xmltodict
from models.article import Article
from topic_classifier import tagger, utils
CONFIDENCE_THRESH = 0.11


def getArxivData(search_query, start=0, max_results=10, sortBy="submittedDate"):
    # https://info.arxiv.org/help/api/user-manual.html#_calling_the_api
    # parameters:   search_query : string
    #               start : int
    #               max_results : int
    #               sortBy : relevance, submittedDate, lastUpdatedDate
    #               sortOrder : ascending, descending

    url = f'http://export.arxiv.org/api/query?sortBy={sortBy}&search_query={search_query}&start={start}&max_results={max_results}'
    data = requests.get(url)
    try:
        entries = xmltodict.parse(data.text)['feed']['entry']
    except KeyError:
        return []
    articles = []

    for entry in entries:
        try:
            entry['authors'] = [].extend([entry['name']
                                          for entry in entry['author']])
        except TypeError:
            entry['authors'] = [entry['author']['name']]
        if entry['authors'] == []:
            print(entry)
            exit()

        for url in entry['link']:
            if url.get("@title") == "pdf":
                entry['url'] = url["@href"]
                break
            else:
                entry['url'] = entry['link'][0]["@href"]

        tags = tagger.tag_abstract(
            entry['summary'], thresh=CONFIDENCE_THRESH, data_folder="topic_classifier/data/")

        entry['tags'] = tags
        a = Article.fromJSON(entry)
        print(a)
        articles.append(a)

    return articles


if __name__ == "__main__":
    COLLECTION_INTERVAL = 1  # in days
    # read or create a collector_data.json file
    if os.path.exists("collector_data.json"):
        cdata = json.load(open("collector_data.json", 'r'))
        # get "last_updated" from the file as a datetime object
        last_updated = cdata['last_updated']
        last_updated = datetime.datetime.strptime(last_updated, "%d%m%y")
        # if it's been more than N days, update the data
        today = datetime.datetime.now()
        number_of_days = (today - last_updated).days
        if number_of_days < COLLECTION_INTERVAL:
            print(
                f"Data was last collected {number_of_days} days ago. Skipping collection.")
            exit()
    else:
        last_updated = datetime.datetime.now(
        ) - datetime.timedelta(days=COLLECTION_INTERVAL*10)

    json.dump({"last_updated": datetime.datetime.now().strftime(
        "%d%m%y")}, open("collector_data.json", 'w'))

    import article_database
    db = article_database.ArticleDatabase()

    start = 0
    inDateRange = True
    while inDateRange:
        results = getArxivData("natural language processing", start=start, max_results=100,
                               sortBy="submittedDate")
        start += 100
        if len(results) == 0:
            inDateRange = False
            break
        for result in results:
            if result.published > last_updated:
                print(f"Adding {result.title}")
                db.add_article(result, auto_commit=False)
            else:
                inDateRange = False
                break
    db.commit()
