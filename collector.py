import sqlite3
import requests
import xmltodict
from models.article import Article
from topic_classifier import tagger
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
            data['author'] = [].extend([entry['name']
                                        for entry in entry['author']])
        except TypeError:

            data['author'] = [entry['author']['name']]

        entry['tags'] = tagger.tag_abstract(
            entry['summary'], thresh=CONFIDENCE_THRESH, data_folder="topic_classifier/data/")

        articles.append(Article.fromJSON(entry))

    return articles


# def initArchiveDB():
#     # make a article table
#     # make a "last_update" table
#     # make a trigger to update the last_update table
#     conn = sqlite3.connect('archive.db')
#     c = conn.cursor()
#     c.execute('''
#     CREATE TABLE IF NOT EXISTS articles (
#         id INTEGER PRIMARY KEY,
#         title TEXT,
#         summary TEXT,
#         published TEXT,
#         updated TEXT,
#         authors TEXT,
#         tags TEXT
#     )
#     ''')
#     c.execute('''
#     CREATE TABLE IF NOT EXISTS last_update (
#         id INTEGER PRIMARY KEY,
#         last_update TEXT
#     )
#     ''')
#     c.execute('''
#     CREATE TRIGGER IF NOT EXISTS update_last_update
#     AFTER INSERT ON articles
#     BEGIN
#         DELETE FROM last_update;
#         INSERT INTO last_update (last_update) VALUES (datetime('now'));
#     END
#     ''')
#     conn.commit()
#     return conn


if __name__ == "__main__":
    # conn = initArchiveDB()

    arcs = getArxivData("natural language processing",
                        max_results=100, sortBy="submittedDate")
    for a in arcs:
        print(a.title)
        print(a.tags)
