
import datetime


class Article:
    def __init__(self, title, abstract, authors, tags, published, url, source, id=None):
        self._id = id
        self._title = title
        self._abstract = abstract
        self._authors = authors
        self._tags = tags
        self._published = published
        self._url = url
        self.source = source

    def __str__(self) -> str:
        return self.title + " by " + ', '.join(self._authors)

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @property
    def abstract(self):
        return self._abstract

    @property
    def authors(self):
        return self._authors

    @property
    def tags(self):
        return self._tags

    @property
    def tags_noscore(self):
        return [tag[0] for tag in self._tags]

    @property
    def url(self):
        if not self._url.startswith('http'):
            self._url = 'https://' + self._url
        return self._url
    
    @property
    def source(self):
        return self._source

    @property
    def published(self):
        return self._published

    @staticmethod
    def fromJSON(json):
        return Article(title=json['title'], abstract=json['summary'], authors=json['authors'], tags=json['tags'], url=json['url'], source=json['source'], published=datetime.datetime.strptime(json['published'], "%Y-%m-%dT%H:%M:%SZ") if json['published'] else None)

    def toJSON(self):
        return {
            'id': self._id,
            'title': self._title,
            'summary': self._abstract,
            'authors': self._authors,
            'tags': self.tags_noscore,
            'published': self._published.isoformat() if self._published else None,
            'url': self._url,
            'source': self._source
        }
