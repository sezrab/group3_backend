class User:
    def __init__(self, id, email, bookmarks, interests, settings):
        self._id = id  # int
        self._email = email  # string
        self._bookmarks = bookmarks  # list of strings
        self._interests = interests  # list of strings
        self._settings = settings  # dictionary

    @property
    def id(self):
        return self._id

    @property
    def email(self):
        return self._email

    @property
    def bookmarks(self):
        return self._bookmarks

    @property
    def interests(self):
        return self._interests

    @property
    def settings(self):
        return self._settings
