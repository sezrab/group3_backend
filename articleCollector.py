import requests
import xmltodict


def getArxivData(search_query, start=0, max_results=10):
    url = f'http://export.arxiv.org/api/query?search_query={
        search_query}&start={start}&max_results={max_results}'
    data = requests.get(url)
    data = xmltodict.parse(data.text)
    for entry in data['feed']['entry']:
        try:
            data['author'] = [].extend([entry['name']
                                       for entry in entry['author']])
        except TypeError:
            data['author'] = [entry['author']['name']]
    return data


print(getArxivData("natural language processing"))
