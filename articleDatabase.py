import sqlite3
from models import Article


class ArticleDatabase:
    def __init__(self):
        # CONNECT TO DATABASE "articles.db" using SQLITE3

        # create table "articles" if it does not exist
        # id (auto generate), title, abstract, url

        # create table "article_tags" if it does not exist
        # id (auto generate), article_id, tag_name

        # create table "article_authors" if it does not exist
        # id (auto generate), article_id, author_name

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
