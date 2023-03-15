""""""
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from db.data import tables
from settings import database_name as db_name


class DBConnection:
    def __init__(self):
        """"""
        CreateDB()
        self.conn = psycopg2.connect(host='127.0.0.1',
                                     user='postgres',
                                     database=f'{db_name}',
                                     password='1qa2ws3ed',
                                     port='5432')
        self.cursor = self.conn.cursor()
        self.cursor.execute(tables[0])
        self.cursor.execute(tables[1])

    def add_urls_to_db(self, urls: list[tuple] | tuple):
        """"""
        if not isinstance(urls, list):
            urls = [urls]
        for url in urls:
            try:
                insert_query = f"INSERT INTO links(link, title_article) VALUES {url};"
                self.cursor.execute(insert_query)
                self.conn.commit()
            except Error:
                self.conn.rollback()
                update_query = f"UPDATE links SET link = '{list(url)[0]}' WHERE title_article = '{list(url)[1]}'" \
                               f"AND NOT EXISTS (SELECT link FROM links WHERE link = '{list(url)[0]}')"
                self.cursor.execute(update_query)
                self.conn.commit()

    def add_url_to_url(self, id_urls: list[tuple] | tuple):
        """"""
        for url in id_urls:
            try:
                insert_query = f'INSERT INTO link_to_link(link_left, link_right) VALUES {url}'
                self.cursor.execute(insert_query)
                self.conn.commit()
            except Error:
                self.conn.rollback()

    def get_id_for_url(self, urls: list[tuple] | tuple | str) -> list:
        """
        Searching id in database for link or links from list.
        :param urls: list of links or a link to search for their id in the database,
        :return: list of id for link or links from list.
        """
        id_for_url = []
        if not isinstance(urls, list):
            urls = [urls]
        for url in urls:
            if isinstance(url, tuple):
                url = url[0]
            try:
                query = f"SELECT id FROM links WHERE link = '{url}'"
                self.cursor.execute(query)
            except Error as error:
                print(f'When searching for data {url} in PostgresSQ {error}')
                self.conn.rollback()
            else:
                id_url = self.cursor.fetchone()
                if not id_url:
                    continue
                else:
                    id_for_url.append(id_url[0])
        return id_for_url

    def get_id_for_title_article(self, title: str) -> list[str]:
        """
        Searching article's id in database by his title.
        :param title: title to search for their id in the database,
        :return: list of id for article with title.
        """
        id_article = []
        try:
            query = f"SELECT id FROM links WHERE title_article = '{title}'"
            self.cursor.execute(query)
        except Error:
            self.conn.rollback()
        else:
            id_result = self.cursor.fetchone()
            try:
                id_article.append(id_result[0])
            except TypeError:
                return []
        return id_article

    def get_urls_from_start_url(self, from_url: list[str] | str = None, article: str = None) -> list[str]:
        """
        Get a list of link's id, first-level descendants.
        :param from_url: initial link,
        :param article: If True - function return list of articles? if False - list of links,
        :return: list of ids for links, which are first-level descendants.
        """
        id_for_from_url = 0
        try:
            id_for_from_url = self.get_id_for_url(from_url)[0]
        except IndexError:
            pass
        try:
            id_for_from_url = self.get_id_for_title_article(article)[0]
        except IndexError:
            pass

        urls = []
        query = f"SELECT link, title_article FROM links " \
                f"WHERE links.id IN (SELECT link_right FROM link_to_link" \
                f" WHERE link_left = {id_for_from_url})"
        try:
            self.cursor.execute(query)
        except Error:
            self.conn.rollback()
        else:
            urls = self.cursor.fetchall()
        return urls

    def get_title_article(self, title: str = None, url: str = None) -> list[str] | bool:
        """
        Get title for the article in database by url.
        :param url:  link to article in internet,
        :param title:
        :return: title for the article in database according url.
        """
        title_article = []
        query = f"SELECT title_article FROM links WHERE title_article = '{title}'"
        if url:
            query = f"SELECT title_article FROM links WHERE link = '{url}'"

        try:
            self.cursor.execute(query)
        except Error:
            self.conn.rollback()
        else:
            title = self.cursor.fetchone()
            try:
                title_article.append(title[0])
            except TypeError:
                return False

        return title_article

    def get_check_parent_title_article(self, title: str) -> list[str] | bool:
        """
        Checking if is article in database by title.
        :param title: title to article which myst find in internet,
        :return:  if is - title for the article in database according url, if not is - False.
        """
        title_article = []
        try:
            query = f"SELECT title_article FROM link_to_link, links " \
                    f"WHERE link_right = (SELECT id link FROM links " \
                    f"WHERE title_article = '{title}') " \
                    f"AND id = link_left"
            self.cursor.execute(query)
        except Error:
            self.conn.rollback()
        else:
            title = self.cursor.fetchall()
            try:
                for value in title:
                    title_article.append(value[0])
            except Error:
                pass

        return title_article

    def __del__(self):
        """"""
        self.conn.close()


class CreateDB:
    """"""
    def __init__(self):
        self.conn = psycopg2.connect(host='127.0.0.1',
                                     user='postgres',
                                     password='1qa2ws3ed',
                                     port='5432')
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = self.conn.cursor()
        self.create_db()

    def create_db(self) -> bool:
        """
        Create database with given name.
         :return: if database was created - True, if not - False.
        """
        if not self.check_db_exist():
            try:
                self.cursor.execute(f"CREATE DATABASE {db_name}")

            except (Exception, Error) as error:
                print(f'PostgresSQL: {error}')
                self.conn.rollback()

            return True
        return False

    def check_db_exist(self) -> bool:
        """
        Check if is there database with given name.
        :return: if database with given name exist - True, if not - False.
        """
        self.cursor.execute(f"SELECT datname FROM pg_database;")
        db_names = self.cursor.fetchall()

        db_names = [list(dbname)[0] for dbname in db_names]
        if db_name in db_names:
            return True
        return False

    def __del__(self):
        """"""
        self.conn.close()
