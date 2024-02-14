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
            id int AUTO_INCREMENT PRIMARY KEY, 
            title varchar UNIQUE NOT NULL, 
            abstract varchar NOT NULL, 
            url varchar NOT NULL
            )
            """)
        
        # create table "article_tags" if it does not exist
        # id (auto generate), article_id, tag_name
        cur.execute("""
        CREATE TABLE IF NOT EXISTS article_tags(
            id int AUTO_INCREMENT PRIMARY KEY, 
            article_id int NOT NULL, 
            tag_name varchar NOT NULL,
            FOREIGN KEY(article_id) REFERENCES articles(id)
            )
            """)
        
        # create table "article_authors" if it does not exist
        # id (auto generate), article_id, author_name
        cur.execute("""
        CREATE TABLE IF NOT EXISTS article_authors (
            id int AUTO_INCREMENT PRIMARY KEY, 
            article_id int NOT NULL, 
            author_name varchar NOT NULL, 
            FOREIGN KEY(article_id) REFERENCES articles(id))
            """)
        
        con.close()
        pass

    def add_article(self, article):
        # "article" is an object of class Article (From models.article)
        # add it to the database's "articles" table
        pass

    def remove_article(self, article):
        # delete the row which matches the article's title
        pass

    def get_articles(self, sort, start_at, max_results, topics):
        return []
