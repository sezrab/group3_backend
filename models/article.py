
class Article:
    def __init__(self, id, title, abstract, author, tags, link):
        self._id = id
        self._title = title
        self._abstract = abstract
        self._author = author
        self._tags = tags
        self._link = link

    def __str__(self) -> str:
        return f'{self.title} by {self._author}'

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
    def author(self):
        return self._author

    @property
    def tags(self):
        return self._tags

    @property
    def link(self):
        return self._link

    @staticmethod
    def fromJSON(json):
        return Article(json['id'], json['title'], json['summary'], json['author'], json['tags'], json['link'])
