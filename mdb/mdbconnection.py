""""""
import pymongo

from pymongo.errors import DuplicateKeyError, BulkWriteError
from settings import database_name as db_name


class MDBConnection:
    def __init__(self):
        # """"""
        self.client = pymongo.MongoClient("mongodb://mongo:mongo@localhost:27017")
        # self.client = pymongo.MongoClient("mongodb://localhost:27017")
        self.db = self.client[f'{db_name}']
        self.col = self.db.articles
        self.col.create_index([('title', pymongo.ASCENDING)], unique=True)

    def add_article_to_db(self, articles: tuple | list[tuple]):
        """"""
        if not isinstance(articles, list):
            articles = [articles]
        query = [{'url': article[0], 'title': article[1]}
                 for article in articles]
        if query:
            try:
                self.col.insert_many(query, ordered=False)
            except (TypeError, DuplicateKeyError, BulkWriteError):
                pass

    def add_from_article(self, title_article: str, ids_from_article: list[int]):
        """"""
        myquery = {"title": title_article}
        new_values = {"$addToSet": {"from_article": {"$each": ids_from_article}}}
        self.col.update_one(myquery, new_values)

    def add_to_article(self, title_article: str, ids_to_article: list[int]):
        """"""
        id_title_article = self.get_id(title=title_article)
        for id_to_article in ids_to_article:
            myquery = {"_id": id_to_article}
            new_values = {"$addToSet": {"to_article": id_title_article}}
            self.col.update_one(myquery, new_values)

    def get_id(self, title: str) -> int:
        """"""
        id_article = self.col.find_one({"title": title}, {"_id": 1})
        if not id_article:
            return id_article
        return id_article['_id']

    def get_ids(self, urls: tuple | list[tuple]) -> list[int]:
        """"""
        id_articles = []
        if not isinstance(urls, list):
            urls = [urls]
        for url in urls:
            try:
                id_article = self.col.find_one({"url": url[0]}, {"_id": 1})["_id"]
            except TypeError:
                try:
                    id_article = self.col.find_one({"title": url[1]}, {"_id": 1})["_id"]
                except TypeError:
                    id_article = None

            id_articles.append(id_article)
        return id_articles

    def get_title(self, title_article: str) -> list[str] | None:
        """"""
        title = self.col.find_one({"title": title_article}, {"_id": 0, "title": 1})
        if not title:
            return None
        return [title["title"]]

    def get_urls_from_article(self, title: str) -> list[tuple]:
        """"""
        try:
            id_articles = self.col.find_one({"title": title}, {"_id": 0, "from_article": 1})['from_article']
        except (TypeError, KeyError):
            return []
        urls_from_article = [(url_from_article['url'], url_from_article['title'])
                             for url_from_article in self.col.find({"_id": {"$in": id_articles}})]
        return urls_from_article

    def get_urls_to_article(self, title: str) -> list[str] | None:
        """"""
        try:
            id_articles = self.col.find_one({"title": title}, {"to_article": 1})['to_article']
        except (TypeError, KeyError):
            return []
        urls_to_article = [url_to_article['title'] for url_to_article in self.col.find({"_id": {"$in": id_articles}})]
        return urls_to_article
