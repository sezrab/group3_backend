class FirebaseManager:
    def __init__(self):
        # CONNECT TO FIREBASE DATABASE
        pass

    def bookmarks(self, user_id):
        # get all the bookmarks of a user
        return [5, 1, 25, 32]

    def interests(self, user_id):
        # get all the interests of a user
        return [('Stemming', 0.6), ('Lemmatization', 0.2), ('Stop Words Removal', 0.2)]

    def settings(self, user_id):
        # get all the settings of a user
        return {
            "dark_mode": True,
            "font_size": "small",
            "notifications": False
        }
