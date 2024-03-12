import datetime
import random
import os
import json
import sqlite3
import requests
import xmltodict
from models.article import Article
from topic_classifier import tagger
from wrappers import arxiv_wrapper, semantic_wrapper
import time
CONFIDENCE_THRESH = 0.17

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
        relevant = arxiv_wrapper.getArxivData(
            "natural language processing", max_results=100, sortBy="relevance", CONFIDENCE_THRESH=CONFIDENCE_THRESH)
        for a in relevant:
            db.add_article(a, auto_commit=False)

    json.dump({"last_updated": datetime.datetime.now().strftime(
        "%d%m%y")}, open("collector_data.json", 'w'))

    start = 0
    inDateRange = True
    retries = 0
    start_date = last_updated
    while inDateRange:
        print(f"Getting articles {start} to {start+100}")
        results_arxiv = arxiv_wrapper.getArxivData("natural language processing", start=start, max_results=100,
                               sortBy="submittedDate", CONFIDENCE_THRESH=CONFIDENCE_THRESH)
        results_semantic = semantic_wrapper.getSemanticData("natural language processing", start_date=start_date + datetime.timedelta(days=1), sort="publicationDate:asc", CONFIDENCE_THRESH=CONFIDENCE_THRESH)
        results = results_arxiv + results_semantic
        start += 100
        if len(results) == 0:
            print("Stopped by arxiv API. No more results.")
            if retries >= 2:
                inDateRange = False
                break
            time.sleep(5)
            retries += 1
        for result in results:
            if result.published > last_updated:
                if result.published > start_date:
                    start_date = result.published
                retries = 0
                # print(f"Adding {result.title}")
                db.add_article(result, auto_commit=False)
            else:
                inDateRange = False
                break
    db.commit()
