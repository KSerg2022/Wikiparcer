""""""
from pprint import pprint

import pymongo
from pymongo import errors
from pymongo.errors import DuplicateKeyError, BulkWriteError
from bson.codec_options import CodecOptions

from settings import database_name as db_name

from mdb.data_for_testing import (data, data_many,
                                  data_1, data_2, data_3, data_4
                                  )


class MDBConnection:
    def __init__(self):
        """"""
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client[f'{db_name}']
        self.col = self.db.articles
        self.col.create_index([('title', pymongo.ASCENDING)], unique=True)

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

    def get_index(self):
        return self.col.index_information()

    def add_article_to_db(self, articles: tuple | list[tuple]):
        """"""

        if not isinstance(articles, list):
            articles = [articles]
        else:
            articles = list(set(articles))
        query = [{'url': article[0], 'title': article[1]}
                 for article in articles]
        if query:
            try:
                self.col.insert_many(query, ordered=False)
            except (TypeError, DuplicateKeyError, BulkWriteError):
                pass

    def add_from_article(self, title_article, ids_from_article):
        myquery = {"title": title_article}
        new_values = {"$addToSet": {"from_article": {"$each": ids_from_article}}}
        self.col.update_one(myquery, new_values)

    def add_to_article(self, title_article, ids_to_article):
        id_title_article = self.get_id(title=title_article)
        for id_to_article in ids_to_article:
            myquery = {"_id": id_to_article}
            new_values = {"$addToSet": {"to_article": id_title_article}}
            self.col.update_one(myquery, new_values)

    def get_id(self, url=None, title=None):
        id_article = None
        if url:
            id_article = self.col.find_one({"url": url}, {"_id": 1})
        if title:
            id_article = self.col.find_one({"title": title}, {"_id": 1})

        if not id_article:
            return id_article
        return id_article['_id']

    def get_ids(self, urls):
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

    def get_title(self, title_article):
        title = self.col.find_one({"title": title_article}, {"_id": 0, "title": 1})
        if not title:
            return None
        return [title["title"]]

    def get_urls_from_article(self, url=None, title=None):
        urls_from_article = []
        id_articles = None
        if url:
            id_articles = self.col.find_one({"url": url}, {"from_article": 1})
        if title:
            id_articles = self.col.find_one({"title": title}, {"from_article": 1})

        try:
            id_articles = id_articles['from_article']
        except (TypeError, KeyError):
            return []

        for id_article in id_articles:
            url = self.col.find_one({"_id": id_article}, {"_id": 0, "url": 1})["url"]
            title = self.col.find_one({"_id": id_article}, {"_id": 0, "title": 1})["title"]
            urls_from_article.append((url, title))
        return urls_from_article

    def get_urls_to_article(self, url=None, title=None):
        urls_to_article = []
        id_articles = None
        if url:
            id_articles = self.col.find_one({"url": url}, {"to_article": 1})
        if title:
            id_articles = self.col.find_one({"title": title}, {"to_article": 1})

        try:
            id_articles = id_articles['to_article']
        except (TypeError, KeyError):
            return None

        for id_article in id_articles:
            urls_to_article.append(self.col.find_one({"_id": id_article}, {"_id": 0, "title": 1})["title"])
        return urls_to_article

    def get_urls(self, title):
        urls_to_article = []
        # id_articles = self.col.find_one({"title": title}, {"to_article": 1})
        id_articles = self.col.aggregate([
            {'$match': {'title': title}},
            {'$unwind': "$to_article"},
            {'$group': {
                '_id': {'article': '$title'},
                'urls': {'$push': '$to_article'}
                # 'urls': {'$push': {
                #                     'url': '$url',
                #                     'title': '$title'}}
             }}
        ])
        for i in id_articles:
            print(i)

        id_articles = self.col.aggregate([
            {'$match': {'title': title}},
            {'$unwind': "$to_article"},
            {'$project': {
                '_id': 0,
                'title': 1,
                'to_article': 1}}
        ])
        for i in id_articles:
            print(i)
        print(self.col.find_one({'title': title}, {'url': 1, 'title': 1, 'to_article': 1}))

if __name__ == '__main__':
    mdb = MDBConnection()
    mdb.get_urls('Дружба')
    # print(mdb.get_db_stats())
    # pprint(mdb.get_db_stats())
    # pprint(mdb.get_col_stats())

    # mdb.add_article_to_db(data)
    #
    # mdb.add_article_to_db(data_many)

    # print(mdb.get_index())
    # print(mdb.get_ids(data_many))
    # print(mdb.get_title(data[1]))
    #
    # mdb.add_from_article(data_1[0], data_1[1])
    # mdb.add_from_article(data_2[0], data_2[1])
    # mdb.add_from_article(data_3[0], data_3[1])
    # mdb.add_from_article(data_4[0], data_4[1])
    #
    # mdb.add_from_article(data_1[0], data_1[1])
    # mdb.add_from_article(data_2[0], data_2[1])
    # mdb.add_from_article(data_3[0], data_3[1])
    # mdb.add_from_article(data_4[0], data_4[1])

    # print(mdb.get_urls_from_article(url=data[0]))
    # print(mdb.get_urls_from_article(url=data_many[0][0]))
    # print(mdb.get_urls_from_article(url=data_many[3][0]))
    #
    # print(mdb.get_urls_to_article(url=data[0]))
    # print(mdb.get_urls_to_article(url=data_many[0][0]))

    # print('~' * 50)
    # [pprint(q) for q in mdb.col.find()]
