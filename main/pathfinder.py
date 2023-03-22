"""Module where find path from one article to other article in internet."""
import re
from time import sleep, time

from settings import wiki_url
from utils.calc_time import calc_delay
from main.parser import WikiParser
from mdb.mdbconnection import MDBConnection


class PathFinder:
    time_data_1 = set()
    time_data_2 = set()
    time_data_3 = set()

    def __init__(self, start_article, finish_article, requests_per_minute, urls_per_page):
        self.db = MDBConnection()
        self.parser = WikiParser()
        self.start_article = start_article
        self.finish_article = finish_article
        self.requests_per_minute = requests_per_minute
        self.urls_per_page = urls_per_page

    def get_page_by_link(self, urls: list[str], to_article: str) -> tuple | bool:
        """
        Find link to article with title - in variable 'to_article'
        :param urls: list of links for queries,
        :param to_article: title of article on which is stopping finding,
        :return: True if result found, False if result not found.
        """
        for url_from in urls:
            current_time = time()
            delay = calc_delay(self.requests_per_minute, current_time)
            sleep(delay)

            url_to, urls_and_titles = self.find_article_name_on_page(url_from[0], to_article=to_article)
            if url_to:
                self.add_data_to_db(from_url=url_from[0], from_article=url_from[1], urls=url_to)
                return url_to
        return False

    @staticmethod
    def find_finish_article(urls: list[str], finish_article: str) -> str:
        """
        Find link in line where which contain text according to regular expression with variable 'finish_article'
        :param urls: list of links (tag <a>),
        :param finish_article: title of article link to find,
        :return: link (tag <a>) which contain regular expression, or empty string.
        """
        for url in urls:
            pattern = re.compile(f'{finish_article}')
            result = pattern.findall(str(url[1]))
            if result:
                return url
        return ''

    def find_article_name_on_page(self, from_url: str, to_article: str) -> tuple[str, list[str]] | tuple[bool, list[str]]:
        """
        Find link which to go to finish article.
        :param from_url: link to article from which are start find,
        :param to_article: title of article on which is stopping finding,
        :return: If found - link (tag <a>) and False, if not found - False and list of links (tag <a>).
        """
        if isinstance(from_url, tuple):
            from_url = list(from_url)[0]

        if from_url in self.time_data_3:
            return False, []
        urls = self.parser.get_urls(from_url)
        self.time_data_3.add(from_url)

        url_to_article = self.find_finish_article(urls, to_article)
        if url_to_article:
            return url_to_article, urls
        else:
            return False, urls

    def find_result(self, from_article: str, to_article: str) -> bool | str:
        """
        Are looking for the titles of articles by moving on which you can get from the start article to the finish.
        :param from_article: title of article from which start find,
        :param to_article: title of article on which is stopping finding,
        :return: If found - True, if not found - False.
        """
        from_url = f'{wiki_url}{from_article}'
        url, urls_and_titles = self.find_article_name_on_page(from_url, to_article)
        self.add_data_to_db(from_url, from_article, urls_and_titles)
        if url:
            return url
        else:
            urls = self.db.get_urls_from_article(title=from_article)

            url = self.get_page_by_link(urls, to_article=to_article)
            if url:
                return url
        return False

    def add_data_to_db(self, from_url: str, from_article: str, urls: list[tuple]):
        """
        Adding data to database.
        :param from_article: title of article from which start find,
        :param from_url: link to article from which are start find,
        :param urls: list of urls.
         """
        self.db.add_article_to_db((from_url, from_article))
        self.db.add_article_to_db(urls)

        id_urls = self.db.get_ids(urls)
        self.db.add_from_article(from_article, id_urls)
        self.db.add_to_article(from_article, id_urls)

    def get_result_from_db(self, from_article: str, to_article: str) -> bool | list[str]:
        """
        Get result from start_article to finish_article in database, and is there a transition path.
        :param from_article: title of article from which start find,
        :param to_article: title of article on which is stopping finding,
        :return: List title articles through which can get from start_article to finish_article, if not found - False.
        """
        path_from_to = []
        from_title_article = self.db.get_title(from_article)
        to_title_article = self.db.get_title(to_article)
        if not from_title_article or not to_title_article:
            return False

        path_from_to.append(to_title_article[0])
        path_from_to_article = self.get_path_from_start_to_finish_article(path_from_to)
        if path_from_to_article:
            return path_from_to_article
        return False

    def get_path_from_start_to_finish_article(self, path_from_to: list[str]) -> bool | list[str]:
        """
        Finding articles through which can get from start_article to finish_article.
        :param path_from_to: List title articles.  There is only the title finish_article at start,
        :return: List title articles through which can get from start_article to finish_article, if not found - False.
        """
        while True:
            parent_title_articles = self.db.get_urls_to_article(title=path_from_to[-len(path_from_to)])
            if not parent_title_articles:
                return False

            if self.start_article in parent_title_articles:
                path_from_to.insert(0, self.start_article)
                return path_from_to
            else:
                for article in parent_title_articles:
                    if article in path_from_to or article in self.time_data_1:
                        if article in path_from_to and len(parent_title_articles) == 1:
                            return False
                        continue

                    self.time_data_1.add(article)
                    path_from_to.insert(0, article)

                    parent_articles = self.db.get_urls_to_article(title=path_from_to[-len(path_from_to)])
                    if not parent_articles:
                        continue
                    if self.start_article in parent_articles:
                        path_from_to.insert(0, self.start_article)
                        return path_from_to

                    path_from_to.pop(0)

                for article in parent_title_articles:
                    if article in path_from_to:
                        continue

                    path_from_to.insert(0, article)
                    path_from_to_article = self.get_path_from_start_to_finish_article(path_from_to)
                    if path_from_to_article:
                        return path_from_to
                    path_from_to.pop(0)
                return False

    def find_path_to_finish_article(self, from_article, to_article):
        """
        Find way from start_article to finish_article.
        :param from_article: title of article from which find way
        :param to_article: title of article on which is stopping finding,
        :return: ! add comment.
        """
        title_articles = [(f'{wiki_url}{from_article}', from_article)]
        title_articles.extend(self.db.get_urls_from_article(title=from_article))
        for title_article in title_articles[:self.urls_per_page]:
            if title_article in self.time_data_2:
                continue

            path_from_to = self.find_result(title_article[1], to_article)
            if path_from_to:
                return path_from_to

            self.time_data_2.add(title_article)

        for title_article in title_articles:
            path_from_to = self.find_path_to_finish_article(title_article[1], to_article)
            if path_from_to:
                return path_from_to
        return []

    def main(self):
        """Main controller."""
        if path_from_to := self.get_result_from_db(self.start_article, self.finish_article):
        # if path_from_to := False:
            return path_from_to

        else:
            path_from_to = self.find_path_to_finish_article(self.start_article, self.finish_article)
            if path_from_to:
                path_from_to = self.get_result_from_db(self.start_article, self.finish_article)
                return path_from_to
            return []
