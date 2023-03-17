"""Module for receiving data from the Internet, parsing the received data, and data normalization"""
import requests
import re
from bs4 import BeautifulSoup

from settings import key_words


class WikiParser:
    def get_urls(self, from_url):
        """
        Get urls and titles for article which are on page by 'from_url'.
        :param from_url: link to page where will get urls and title for article,
        :return: cleaned list of tuple (url, title article).
        """
        text_page = self.get_page(from_url)
        urls = self.parse_page(text_page)
        urls = self.clean_data(urls)
        return urls

    @staticmethod
    def get_page(url: str):
        """
        Request a page by url on the Internet and save the result
        :param url: link to page where will get data,
        :return: data from internet page.
        """
        page = None
        try:
            page = requests.get(f'{url}')
        except requests.exceptions.RequestException:
            pass
        return page

    @staticmethod
    def parse_page(text_page) -> list[tuple]:
        """
        Parse the received data from the page on the Internet.
        1. Select the <div> tag with ID="bodyContent".
        2. Select all <а> tags from point 1.
        :return: list of tuple (url, title article)
        """
        soup_to_body_content = BeautifulSoup(text_page.content, 'html.parser')
        a_tags = soup_to_body_content.find('div', {'id': 'bodyContent'}).\
            find_all('a', href=re.compile('^(/wiki/)((?!:).)*$'))

        urls = []
        for a_tag in a_tags:
            if 'href' in a_tag.attrs and 'title' in a_tag.attrs:
                url = 'https://uk.wikipedia.org' + a_tag.attrs['href']
                title = re.sub(r"'", '"', a_tag.attrs['title'])
                urls.append((url, title))
        return urls

    @staticmethod
    def clean_data(data: list[tuple]) -> list[tuple]:
        """
        Delete teg-a lines which contain a word from -  'key_words'.
        :param data: list of tuple (url, title article)
        :return: cleaned list of tuple (url, title article)
        """
        results = data.copy()
        for word in key_words:
            pattern = re.compile(f'{word}')
            for row in data:
                result = pattern.search(str(row[1]))
                if result:
                    try:
                        results.remove(row)
                    except ValueError:
                        pass
        return results
