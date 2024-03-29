import sqlite3
from models.article import Article


class ArticleDatabase:
    def __init__(self):
        # CONNECT TO DATABASE "articles.db" using SQLITE3
        con = sqlite3.connect("articles.db")
        cur = con.cursor()
        # create table "articles" if it does not exist
        # id (auto generate), title, abstract, url
        cur.execute("""
            CREATE TABLE IF NOT EXISTS articles(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                title TEXT UNIQUE NOT NULL, 
                abstract TEXT NOT NULL, 
                url TEXT NOT NULL,
                published TEXT NOT NULL
                )
                """)

        # create table "article_tags" if it does not exist
        # id (auto generate), article_id, tag_name
        cur.execute("""
            CREATE TABLE IF NOT EXISTS article_tags(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                article_id INTEGER NOT NULL, 
                tag_name TEXT NOT NULL,
                score REAL NOT NULL,
                FOREIGN KEY(article_id) REFERENCES articles(id)
                )
                """)

        # create table "article_authors" if it does not exist
        # id (auto generate), article_id, author_name
        cur.execute("""
            CREATE TABLE IF NOT EXISTS article_authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                article_id INTEGER NOT NULL, 
                author_name TEXT NOT NULL, 
                FOREIGN KEY(article_id) REFERENCES articles(id))
                """)
        self._con = con
        self._cur = cur

    def add_article(self, article, auto_commit=True):
        datestring = article.published.strftime("%d%m%y")
        # insert the article's title, abstract, and url into the "articles" table
        try:
            article_id = self._cur.execute("INSERT INTO articles (title, abstract, url, published) VALUES (?, ?, ?, ?)", (
                article.title, article.abstract, article.url, datestring)).lastrowid
        except sqlite3.IntegrityError:
            # abort, the article already exists in the db
            return
        # insert authors into the "article_authors" table
        if article.authors is None:
            return
        for author in article.authors:
            self._cur.execute(
                "INSERT INTO article_authors (article_id, author_name) VALUES (?, ?)", (article_id, author))
        # insert tags into the "article_tags" table
        for tag in article.tags:
            self._cur.execute(
                "INSERT INTO article_tags (article_id, tag_name, score) VALUES (?, ?, ?)", (article_id, tag[0], tag[1]))
        if auto_commit:
            self._con.commit()

    def commit(self):
        self._con.commit()

    def remove_article(self, article):
        # delete the row which matches the article's title
        pass

    # recommendation algorithm :)
    def get_articles(self, sort, interests, ignore_interests=False, start_date=None, stop_date=None):
        thresh = 0.25
        articles_ranked = []

        for article in self.list_all_articles():
            if start_date:
                if article.published < start_date:
                    continue
            if stop_date:
                if article.published > stop_date:
                    continue
            if ignore_interests:
                articles_ranked.append((article, 1))
                continue
            total = 0
            for interest, interest_score in interests:
                for topic, topic_score in article.tags:
                    if (interest == topic):
                        total += interest_score * topic_score
            # print(total)
            if total > thresh:
                articles_ranked.append((article, total))

        return sorted(articles_ranked, key=lambda x: x[1], reverse=True)

    def list_all_articles(self):
        # get articles, corresponding authors, and tags from the database
        articles = self._cur.execute(
            "SELECT * FROM articles").fetchall()
        objects = []
        for id, title, abstract, url, published in articles:
            authors = self._cur.execute(
                "SELECT author_name FROM article_authors WHERE article_id = ?", (id,)).fetchall()
            for i, author in enumerate(authors):
                authors[i] = author[0]
            tags = self._cur.execute(
                "SELECT tag_name,score FROM article_tags WHERE article_id = ?", (id,)).fetchall()
            import datetime
            a = Article(id=id, title=title, abstract=abstract, authors=authors,
                        tags=tags, url=url, published=datetime.datetime.strptime(published, "%d%m%y"))
            objects.append(a)
        return objects

    def search_articles(self, to_search):
        # get articles which match in some way with the user's search input in the title, abstract, authors, or tags

        from_articles = self._cur.execute(
            "SELECT id FROM articles WHERE abstract LIKE ? OR title LIKE ?;", (f'%{to_search}%', f'%{to_search}%')).fetchall()
        from_authors = self._cur.execute(
            "SELECT article_id, author_name FROM article_authors WHERE author_name LIKE ?;", (f'%{to_search}%',)).fetchall()

        from_tags = self._cur.execute(
            "SELECT article_id, tag_name FROM article_tags WHERE tag_name LIKE ?;", (f'%{to_search}%',)).fetchall()

        fetch_ids = [x[0]
                     for x in set(from_articles + from_authors + from_tags)]
        # get articles, corresponding authors, and tags from the database
        articles = [article for article in self.list_all_articles()
                    if article.id in fetch_ids]

        return articles


if __name__ == "__main__":
    adb = ArticleDatabase()
    # insert some dummy data
    article = Article(title="Title", abstract="Abstract", url="URL", authors=[
        "Author1", "Author2"], tags=["tag1", "tag2"])
    try:
        adb.add_article(article)
    except:
        pass
