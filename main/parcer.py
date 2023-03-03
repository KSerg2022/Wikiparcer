"""Module for receiving data from the Internet, parsing the received data, and data normalization"""
import requests
import re
from bs4 import BeautifulSoup

from settings import key_words


def get_links(start_url):
    text_page = get_page(start_url)
    links = parse_page(text_page)
    return links


def get_page(url: str):
    """Request a page by url on the Internet and save the result"""
    global page
    try:
        page = requests.get(f'{url}')
    except requests.exceptions.RequestException:
        pass
    return page


def parse_page(text_page):
    """
    Parse the received data from the page on the Internet.
    1. Select the <div> tag with ID="bodyContent".
    2. Select all <а> tags from point 1.
    """
    soup_to_body_content = BeautifulSoup(text_page.content, 'html.parser')
    a_tags = soup_to_body_content.find('div', {'id': 'bodyContent'}).\
        find_all('a', href=re.compile('^(/wiki/)((?!:).)*$'))

    links = []
    for a_tag in a_tags:
        if 'href' in a_tag.attrs and 'title' in a_tag.attrs:
            link = 'https://uk.wikipedia.org' + a_tag.attrs['href']
            title = re.sub(r"\'", '"', a_tag.attrs['title'])
            links.append((link, title))
    return links


def clean_data_teg_a(data: list[str]) -> list[str]:
    """Delete lines that do not contain a word - 'title'."""
    pattern = re.compile('title')
    results = []
    for row in data:
        result = pattern.search(str(row))
        if result:
            results.append(row)
    results = clean_data_teg_a_additional(results)
    return results


def clean_data_teg_a_additional(data: list[str]) -> list[str]:
    """
    Delete lines that contain a word from -  'key_words'.
    :param data:
    :return:
    """
    results = data.copy()
    for word in key_words:
        pattern = re.compile(f'{word}')
        for row in data:
            result = pattern.search(str(row))
            if result:
                try:
                    results.remove(row)
                except ValueError:
                    pass
    return results
