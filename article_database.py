import sqlite3
from models.article import Article
import datetime


class ArticleDatabase:
    def __init__(self):
        # CONNECT TO DATABASE "articles.db" using SQLITE3
        con = sqlite3.connect("data/articles.db")
        cur = con.cursor()
        # create table "articles" if it does not exist
        # id (auto generate), title, abstract, url
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS articles(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                title TEXT UNIQUE NOT NULL, 
                abstract TEXT NOT NULL, 
                url TEXT NOT NULL,
                source TEXT NOT NULL,
                published TEXT NOT NULL
                )
                """
        )

        # create table "article_tags" if it does not exist
        # id (auto generate), article_id, tag_name
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS article_tags(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                article_id INTEGER NOT NULL, 
                tag_name TEXT NOT NULL,
                score REAL NOT NULL,
                FOREIGN KEY(article_id) REFERENCES articles(id)
                )
                """
        )

        # create table "article_authors" if it does not exist
        # id (auto generate), article_id, author_name
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS article_authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                article_id INTEGER NOT NULL, 
                author_name TEXT NOT NULL, 
                FOREIGN KEY(article_id) REFERENCES articles(id))
                """
        )
        self._con = con
        self._cur = cur

    def list_sources(self):
        return [
            source[0]
            for source in self._cur.execute(
                "SELECT DISTINCT source FROM articles"
            ).fetchall()
        ]

    def add_article(self, article, auto_commit=True):
        datestring = article.published.strftime("%d%m%y")
        # insert the article's title, abstract, and url into the "articles" table
        try:
            article_id = self._cur.execute(
                "INSERT INTO articles (title, abstract, url, source, published) VALUES (?, ?, ?, ?, ?)",
                (
                    article.title,
                    article.abstract,
                    article.url,
                    article.source,
                    datestring,
                ),
            ).lastrowid
        except sqlite3.IntegrityError:
            # abort, the article already exists in the db
            return
        # insert authors into the "article_authors" table
        if article.authors is None:
            return
        for author in article.authors:
            self._cur.execute(
                "INSERT INTO article_authors (article_id, author_name) VALUES (?, ?)",
                (article_id, author),
            )
        # insert tags into the "article_tags" table
        for tag in article.tags:
            self._cur.execute(
                "INSERT INTO article_tags (article_id, tag_name, score) VALUES (?, ?, ?)",
                (article_id, tag[0], tag[1]),
            )
        if auto_commit:
            self._con.commit()

    def commit(self):
        self._con.commit()

    def remove_article(self, article):
        # delete the row which matches the article's title
        pass

    def get_relevant_articles(
        self,
        interests,
        sources,
        random_sample=True,
        num_articles=100,
    ):
        sources_string = ", ".join(["?"] * len(sources))
        interests_string = ", ".join(["?"] * len(interests))
        # use sql for efficiency
        # return num_articles (random) articles from the database where the article's tags match the user's interests and the article's source matches the user's selected sources
        query = """
            SELECT id FROM articles 
            WHERE source IN ({})
            AND id IN (
                SELECT article_id FROM article_tags 
                WHERE tag_name IN ({})
            )
        """.format(
            sources_string, interests_string
        )

        params = sources + [interest[0] for interest in interests]

        if random_sample:
            query += " ORDER BY RANDOM() LIMIT ?"
            params.append(num_articles)

        self._cur.execute(query, params)
        article_ids = [result[0] for result in self._cur.fetchall()]
        # print(article_ids)

        articles = self.get_article_by_ids(article_ids)
        print(len(articles))
        return articles

    # recommendation algorithm :)
    def get_articles(
        self,
        interests,
        sources=[],
        ignore_interests=False,
        start_date=None,
        stop_date=None,
    ):
        thresh = 0.25
        articles_ranked = []

        if ignore_interests:
            articleList = self.list_all_articles(
                date_start=start_date, date_end=stop_date
            )
        else:
            articleList = self.get_relevant_articles(
                interests=interests, sources=sources, random_sample=True
            )

        for article in articleList:
            # print(article)
            if start_date:
                if article.published < start_date:
                    continue
            if stop_date:
                if article.published > stop_date:
                    continue
            if ignore_interests:
                articles_ranked.append((article, 1))
                continue
            # if sources != [] and article.source not in sources:
            #     continue
            total = 0
            for interest, interest_score in interests:
                for topic, topic_score in article.tags:
                    if interest == topic:
                        total += interest_score * topic_score
            # print(total)
            if total > thresh:
                articles_ranked.append((article, total))

        return sorted(articles_ranked, key=lambda x: x[1], reverse=True)

    def list_all_articles(self, date_start=None, date_end=None):
        # get articles, corresponding authors, and tags from the database
        if date_start and date_end:
            articles = self._cur.execute(
                "SELECT * FROM articles WHERE published >= ? AND published <= ?",
                (date_start.strftime("%d%m%y"), date_end.strftime("%d%m%y")),
            ).fetchall()
        else:
            articles = self._cur.execute("SELECT * FROM articles").fetchall()

        objects = []
        for id, title, abstract, url, source, published in articles:
            authors = self._cur.execute(
                "SELECT author_name FROM article_authors WHERE article_id = ?", (id,)
            ).fetchall()
            for i, author in enumerate(authors):
                authors[i] = author[0]
            tags = self._cur.execute(
                "SELECT tag_name,score FROM article_tags WHERE article_id = ?", (id,)
            ).fetchall()

            a = Article(
                id=id,
                title=title,
                abstract=abstract,
                authors=authors,
                tags=tags,
                url=url,
                source=source,
                published=datetime.datetime.strptime(published, "%d%m%y"),
            )
            objects.append(a)
        return objects

    def search_articles(self, to_search):
        # get articles which match in some way with the user's search input in the title, abstract, authors, or tags
        # get the first 100 articles which match the search input
        from_articles = self._cur.execute(
            "SELECT id FROM articles WHERE abstract LIKE ? OR title LIKE ? LIMIT 100;",
            (f"%{to_search}%", f"%{to_search}%"),
        ).fetchall()
        from_authors = self._cur.execute(
            "SELECT article_id, author_name FROM article_authors WHERE author_name LIKE ? LIMIT 100;",
            (f"%{to_search}%",),
        ).fetchall()

        from_tags = self._cur.execute(
            "SELECT article_id, tag_name FROM article_tags WHERE tag_name LIKE ? LIMIT 100;",
            (f"%{to_search}%",),
        ).fetchall()

        fetch_ids = [x[0] for x in set(from_articles + from_authors + from_tags)]
        # get articles, corresponding authors, and tags from the database
        articles = self.get_article_by_ids(fetch_ids)

        return articles

    def get_article_by_ids(self, ids):
        if type(ids) == int:
            ids = [ids]

        objects = []

        for id in ids:
            id, title, abstract, url, source, published = self._cur.execute(
                "SELECT * FROM articles WHERE id = ?", (id,)
            ).fetchone()

            authors = self._cur.execute(
                "SELECT author_name FROM article_authors WHERE article_id = ?", (id,)
            ).fetchall()
            for i, author in enumerate(authors):
                authors[i] = author[0]
            tags = self._cur.execute(
                "SELECT tag_name,score FROM article_tags WHERE article_id = ?", (id,)
            ).fetchall()

            a = Article(
                id=id,
                title=title,
                abstract=abstract,
                authors=authors,
                tags=tags,
                url=url,
                source=source,
                published=datetime.datetime.strptime(published, "%d%m%y"),
            )
            objects.append(a)
        return objects


if __name__ == "__main__":
    adb = ArticleDatabase()
    # insert some dummy data
    article = Article(
        title="Title",
        abstract="Abstract",
        url="URL",
        authors=["Author1", "Author2"],
        tags=["tag1", "tag2"],
    )
    try:
        adb.add_article(article)
    except:
        pass
