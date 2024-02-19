
class Article:
    def __init__(self, title, abstract, authors, tags, url, id=None):
        self._id = id
        self._title = title
        self._abstract = abstract
        self._authors = authors
        self._tags = tags
        self._url = url

    def __str__(self) -> str:
        return f'{self.title} by {', '.join(self._authors)}'

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
        return self._url

    @staticmethod
    def fromJSON(json):
        return Article(json['id'], json['title'], json['summary'], json['authors'], json['tags'], json['link'])

    def toJSON(self):
        return {
            'id': self._id,
            'title': self._title,
            'summary': self._abstract,
            'authors': self._authors,
            'tags': self._tags,
            'link': self._link
        }
