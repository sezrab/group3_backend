import requests
import xmltodict
from models.article import Article
from topic_classifier import tagger

def getArxivData(search_query, start=0, max_results=10, sortBy="submittedDate", CONFIDENCE_THRESH=0.15):
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
            try:
                entry['authors'] = [entry['author']['name']]
                entry['author'] = [entry['author']['name']]
            except TypeError:
                print("Some error with", entry)
                continue
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
