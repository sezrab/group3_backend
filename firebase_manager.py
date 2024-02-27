from google.cloud import firestore

# Replace 'path/to/serviceAccountKey.json' with the path to your key file
# Replace 'your-project-id' with your Google Cloud project ID


class FirebaseManager:
    def __init__(self):
        self._db = firestore.Client.from_service_account_json(
            'nlpress-ef983d7da653.json', project='nlpress')

    def bookmarks(self, user_id):
        # get all the bookmarks of a user
        return [5, 1, 25, 32]

    def interests(self, user_id):
        # get all the interests of a user
        doc_ref = self._db.collection(u'users').document(str(user_id))
        doc = doc_ref.get()
        if doc.exists:
            return [(i, 1) for i in doc.to_dict()['interests']]

    def settings(self, user_id):
        # get all the settings of a user
        return {
            "dark_mode": True,
            "font_size": "small",
            "notifications": False
        }
