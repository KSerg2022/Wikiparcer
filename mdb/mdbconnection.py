""""""
from pprint import pprint

import pymongo
from bson.codec_options import CodecOptions

from settings import database_name as db_name

from mdb.data_for_testing import data, data_many


# collaction = {
#               'url': 'link',
#               'title': 'title article',
#               'url_to_article': (id),
#               'url_from_article': (id)
#               }


class MDBConnection:
    def __init__(self):
        """"""
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client[f'{db_name}']
        self.col = self.db.articles
        # self.q = CodecOptions({
        #                         '_id': {"$inc": {'score': 1}},
        #                         'url': 'link',
        #                         'title': 'title article',
        #                         'url_to_article': (),
        #                         'url_from_article': ()}
        # )
        # self.col = self.db.create_collection('articles', self.q)

    def get_server_info(self):
        return self.client.server_info()

    def get_db_list(self):
        return self.client.list_database_names()

    def get_col_list(self):
        return self.db.list_collection_names()

    def get_db_stats(self):
        return self.db.command("dbstats")

    def get_col_stats(self):
        return self.db.command("collstats", "articles")

    def get_validate(self):
        return self.db.command("validate", "articles")

    def add_article_to_db(self,
                          articles):  # {'url': 'link', 'title': 'title article', 'url_to_article': (),'url_from_article': ()}
        if not isinstance(articles, list):
            articles = [articles]
        query = [{'url': article[0], 'title': article[1], 'url_to_article': [], 'url_from_article': []}
                 for article in articles if not self.get_id(url=article[0])]

        if query:
            self.col.insert_many(query, ordered=False)
    # def add_article_to_db(self, articles):  # {'url': 'link', 'title': 'title article', 'url_to_article': (),'url_from_article': ()}
    #     if not isinstance(articles, list):
    #         articles = [articles]
    #     for article in articles:
    #         print(article)
    #         query = {'url': article[0], 'title': article[1], 'url_to_article': [], 'url_from_article': []}
    #         print(query)
    #         if not self.get_id(url=article[0]):
    #             self.col.insert_one(query)

    def add_urls_from_article(self, title_article, url_from_article):
        myquery = {"title": title_article}
        new_values = {"$set": {"url_from_article": url_from_article}}
        self.col.update_one(myquery, new_values)
        pass

    def add_urls_to_article(self, title_article, url_to_article):
        myquery = {"title": title_article}
        new_values = {"$set": {"url_from_article": url_to_article}}
        self.col.update_one(myquery, new_values)
        pass

    def get_id(self, url=None, title=None):
        id_article = None
        if url:
            id_article = self.col.find_one({"url": url}, {"address": 0, "url_to_article": 0, "url_from_article": 0})
        if title:
            id_article = self.col.find_one({"title": title}, {"address": 0, "url_to_article": 0, "url_from_article": 0})
        return id_article

    def get_urls_from_article(self, url=None, title=None):
        id_articles = None
        if url:
            id_articles = self.col.find({"url": url}, {"_id": 0, "address": 0, "url_to_article": 0})
        if title:
            id_articles = self.col.find({"title": title}, {"_id": 0, "address": 0, "url_to_article": 0})
        return id_articles

    def get_urls_to_article(self, url=None, title=None):
        id_articles = None
        if url:
            id_articles = self.col.find({"url": url}, {"_id": 0, "address": 0, "url_from_article": 0})
        if title:
            id_articles = self.col.find({"title": title}, {"_id": 0, "address": 0, "url_from_article": 0})
        return id_articles


mdb = MDBConnection()
# print(mdb.get_db_stats())
# pprint(mdb.get_db_stats())
# print(mdb.get_col_stats())

mdb.add_article_to_db(data)

mdb.add_article_to_db(data_many)
