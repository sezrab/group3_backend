import datetime
import random
import os
import json
import sqlite3
import requests
import xmltodict
from models.article import Article
from topic_classifier import tagger, utils
import time
CONFIDENCE_THRESH = 0.15


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
    try:
        entries = xmltodict.parse(' '.join(data.text.replace("\n", " ").split()))[
            'feed']['entry']
    except KeyError:
        return []
    articles = []

    for entry in entries:
        try:
            author_names = [author['name'] for author in entry['author']]
            entry['author'] = author_names
            entry['authors'] = author_names
        except TypeError:
            entry['authors'] = [entry['author']['name']]
            entry['author'] = [entry['author']['name']]
        # print(entry['author'])
        if entry['authors'] == []:
            print("NO AUTHORS", entry)
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
        articles.append(a)

    return articles


if __name__ == "__main__":
    COLLECTION_INTERVAL = 1  # in days
    import article_database
    db = article_database.ArticleDatabase()
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
        ) - datetime.timedelta(days=COLLECTION_INTERVAL*100)
        # add the 100 most relevant
        relevant = getArxivData(
            "natural language processing", max_results=100, sortBy="relevance")
        for a in relevant:
            db.add_article(a, auto_commit=False)

    json.dump({"last_updated": datetime.datetime.now().strftime(
        "%d%m%y")}, open("collector_data.json", 'w'))

    start = 0
    inDateRange = True
    retries = 0
    while inDateRange:
        print(f"Getting articles {start} to {start+100}")
        results = getArxivData("natural language processing", start=start, max_results=100,
                               sortBy="submittedDate")
        start += 100
        if len(results) == 0:
            print("Stopped by arxiv API. No more results.")
            if retries > 3:
                inDateRange = False
                break
            time.sleep(5)
            retries += 1
        for result in results:
            if result.published > last_updated:
                retries = 0
                # print(f"Adding {result.title}")
                db.add_article(result, auto_commit=False)
            else:
                inDateRange = False
                break
    db.commit()
