from google.cloud import firestore
import datetime
# Replace 'path/to/serviceAccountKey.json' with the path to your key file
# Replace 'your-project-id' with your Google Cloud project ID


class FirebaseManager:
    def __init__(self):
        self._db = firestore.Client.from_service_account_json(
            'nlpress-ef983d7da653.json', project='nlpress')

    def bookmarks(self, user_id):
        # get all the bookmarks of a user
        return [5, 1, 25, 32]
    def get_read_articles(self, user_id):
        try:
            return self._db.collection(u'users').document(str(user_id)).get().to_dict()['readArticles']
        except:
            return {}
        
    def get_all_user_id(self):
        try:
            return self._db.collection(u'users').get()
        except:
            return{}
    def interests(self, user_id):
        # get all the interests of a user
        doc_ref = self._db.collection(u'users').document(str(user_id))
        doc = doc_ref.get()
        if doc.exists:
            return [(i, 1) for i in doc.to_dict()['interests']]

    def user(self, user_id):
        # get all the settings of a user
        doc_ref = self._db.collection(u'users').document(str(user_id))
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()


class FirebaseUser:
    def __init__(self, user_id):
        self._fb = FirebaseManager()
        self._user_id = user_id
        self._user = self._fb.user(user_id)

    def refresh(self):
        self._user = self._fb.user(self._user_id)

    @property
    def interests(self):
        return [(i, 1) for i in self._user['interests']]

    @property
    def newsletter_period(self):
        if 'newsletterPeriod' not in self._user:
            return 7
        return self._user['newsletterPeriod']

    @property
    def name(self):
        return self._user['name']

    @property
    def email(self):
        return self._user.get('newsletterAddress', None)
