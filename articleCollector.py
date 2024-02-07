import requests
import xmltodict

class Article:
	def __init__(self, title, abstract, author, tags, link):
		self._title = title
		self._abstract = abstract
		self._author = author
		self._tags = tags
		self._link = link

	@property
	def title(self):
		self._title
	
	@property
	def abstract(self):
		self._abstract

	@property
	def author(self):
		self._author

	@property
	def tags(self):
		self._tags

	@property
	def link(self):
		self._link
		 
		

def getArxivData(search_query, start=0, max_results=10):
	url = f'http://export.arxiv.org/api/query?search_query={search_query}&start={start}&max_results={max_results}'
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
