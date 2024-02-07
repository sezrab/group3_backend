import requests
import xmltodict
url = 'http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=10'
data = requests.get(url)
data = xmltodict.parse(data.text)

for entry in data['feed']['entry']:
    try:
        print("-"*50)
        print(entry['title'])
        print("-"*50)
        print("     " + entry['summary'][:50]+"...")
        print("     " + " ,".join([entry["name"]
                                   for entry in entry['author']]))
        print("     "+entry['published'])
        print()
    except:
        pass
