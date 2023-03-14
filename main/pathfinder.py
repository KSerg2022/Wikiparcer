"""Main module."""
import re
from time import sleep, time

from settings import wiki_link
from utils.calc_time import calc_delay
from main.parser import WikiParser
from db.dbconnection import DBConnection


class PathFinder:
    """"""
    time_data_1 = set()
    time_data_2 = set()

    def __init__(self, start_article, finish_article, requests_per_minute, links_per_page):
        self.db = DBConnection()
        self.parser = WikiParser()
        self.start_article = start_article
        self.finish_article = finish_article
        self.requests_per_minute = requests_per_minute
        self.links_per_page = links_per_page

    def get_page_by_link(self, links: list[str], to_article: str) -> tuple | bool:
        """
        Find link to article with title - in variable 'finish_article'
        :param links: list of links for queries,
        :param to_article: title of article on which is stopping finding,
        :return: True if result found, False if result not found.
        """
        for link_from in links:
            current_time = time()
            delay = calc_delay(self.requests_per_minute, current_time)
            sleep(delay)

            link_to, links_and_title = self.find_article_name_on_page(link_from[0], to_article=to_article)
            if link_to:
                self.db.add_links_to_db(link_to)

                id_start_link = self.db.get_id_for_link(link_from)
                id_links = self.db.get_id_for_link(link_to)

                data_for_table_link_to_link = list(zip(id_start_link * len(id_links), id_links))
                self.db.add_link_to_link(data_for_table_link_to_link)
                return link_to
        return False

    @staticmethod
    def find_finish_article(links: list[str], finish_article: str) -> str:
        """
        Find link in line where which contain text according to regular expression with variable 'finish_article'
        :param links: list of links (tag <a>),
        :param finish_article: title of article link to find,
        :return: link (tag <a>) which contain regular expression, or empty string.
        """
        for link in links:
            pattern = re.compile(f'{finish_article}')
            result = pattern.findall(str(link[1]))
            if result:
                return link
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
        links = self.parser.get_links(from_url)

        link_to_article = self.find_finish_article(links, to_article)
        if link_to_article:
            return link_to_article, links
        else:
            return False, links

    def find_result(self, from_article, to_article):
        """
        Are looking for the titles of articles by moving on which you can get from the start article to the finish.
        :param from_article: title of article from which start find,
        :param to_article: title of article on which is stopping finding,
        :return: If found - True, if not found - False.
        """
        from_url = f'{wiki_link}{from_article}'
        link, links_and_title = self.find_article_name_on_page(from_url, to_article)
        self.add_data_to_db(from_article, from_url, links_and_title)
        if link:
            return link
        else:
            links = self.db.get_urls_from_start_url(from_url)
            link = self.get_page_by_link(links, to_article=to_article)
            if link:
                return link
        return False

    def add_data_to_db(self, start_article: str, start_url: str, links: list[tuple]):
        """
        Adding data to database.
        :param start_article: title of article from which start find,
        :param start_url: link to article from which are start find,
        :param links: list of links (tag <a>)
         """
        self.db.add_links_to_db((start_url, start_article))
        self.db.add_links_to_db(links)

        try:
            id_start_link = self.db.get_id_for_title_article(start_article)
        except TypeError:
            id_start_link = self.db.get_id_for_link(start_url)

        id_links = self.db.get_id_for_link(links)
        data_for_table_link_to_link = list(zip(id_start_link * len(id_links), id_links))
        self.db.add_link_to_link(data_for_table_link_to_link)

    def get_result_from_db(self, from_article: str, to_article: str) -> bool | list[str]:
        """
        Get result from start_article to finish_article in database, and is there a transition path.
        :param from_article: title of article from which start find,
        :param to_article: title of article on which is stopping finding,
        :return: if found - list of title articles from start to end, if not found - False.
        """
        path_from_to = []
        from_title_article = self.db.get_title_article(from_article)
        to_title_article = self.db.get_title_article(to_article)
        if not from_title_article or not to_title_article:
            return False

        path_from_to.append(to_title_article[0])
        path_from_to_article = self.get_path_from_start_to_finish_article(path_from_to)
        if path_from_to_article:
            return path_from_to_article
        return False

    def get_path_from_start_to_finish_article(self, path_from_to):
        """
        :param path_from_to:
        :return:
        """
        while True:

            parent_title_articles = self.db.get_check_parent_title_article(path_from_to[-len(path_from_to)])
            if not parent_title_articles:
                return False

            if self.start_article in parent_title_articles:
                path_from_to.insert(0, self.start_article)
                return path_from_to
            else:
                for article in parent_title_articles:
                    if article in path_from_to or article in self.time_data_1:
                        continue

                    self.time_data_1.add(article)
                    path_from_to.insert(0, article)

                    parent_articles = self.db.get_check_parent_title_article(path_from_to[-len(path_from_to)])
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
                    else:
                        path_from_to.pop(0)

    def find_path_to_finish_article(self, from_article, to_article):
        """
        Find way from start_article to finish_article.
        :param from_article: title of article from which find way
        :param to_article: title of article on which is stopping finding,
        :return: ! add comment.
        """
        title_articles = [(f'{wiki_link}{from_article}', from_article)]
        title_articles.extend(self.db.get_urls_from_start_url(article=from_article))
        for title_article in title_articles[:self.links_per_page]:
            if title_article in self.time_data_2:
                continue

            total_result = self.find_result(title_article[1], to_article)
            if total_result:
                return total_result

            self.time_data_2.add(title_article)

        for title_article in title_articles:
            total_result = self.find_path_to_finish_article(title_article[1], to_article)
            if total_result:
                return total_result
        return []

    def main(self):
        """Main controller."""
        if path_from_to := self.get_result_from_db(self.start_article, self.finish_article):
            return path_from_to

        else:
            path_from_to = self.find_path_to_finish_article(self.start_article, self.finish_article)
            if path_from_to:
                path_from_to = self.get_result_from_db(self.start_article, self.finish_article)
                return path_from_to
            return []
