"""Main module."""
import re
from time import sleep

from utils.time import calc_time
from db.db_postgres import (main as init_db,
                            insert_data_in_table_link,
                            insert_data_in_table_link_to_link, )
from db.db_operations import (get_id_for_link,
                              get_id_for_title_article,
                              get_urls_from_start_url,
                              get_query,
                              get_mean_value_of_second_level_descendants,
                              get_title_article,
                              get_check_title_article,
                              get_check_parent_title_article)
from main.parcer import (get_page, parse_page, normalize_link_to_http, parse_title,
                         normalize_link, normalize_title, clean_data_teg_a)
from main.display_result import maim as print_results
from settings import wiki_link


def get_page_by_link(links: list[str],
                     total_result: list,
                     limit_per_minute: int,
                     finish_article: str) -> bool:
    """
    Find link to article with title - in variable 'finish_article'
    :param links: list of links for queries,
    :param total_result: variable to store the result,
    :param limit_per_minute: request per minute limit,
    :param finish_article: title of article on which is stopping finding,
    :return: True if result found, False if result not found.
    """
    timeout = 60 / limit_per_minute
    if len(links) < 200:
        timeout = 0
    for link in links:
        text_page = get_page(link)

        link_name, uniq_data_teg_a = find_article_name_on_page(text_page, finish_article=finish_article)
        if link_name:
            link_to_article = find_links(link_name)
            add_article_to_result(get_title_article(link), total_result)
            add_article_to_result(link_to_article[1], total_result)

            insert_data_in_table_link((link, check_found_link(link)))
            insert_data_in_table_link(link_to_article)
            id_start_link = get_id_for_link(link)
            id_links = get_id_for_link(link_to_article)
            data_for_table_link_to_link = list(zip(id_start_link * len(id_links), id_links))
            insert_data_in_table_link_to_link(data_for_table_link_to_link)
            return True

        sleep(timeout)
    return False


def find_links(links: list[str] | str) -> list[tuple] | tuple:
    """
    Get links and titles according to regular expression.
    :return: tuple(link, title) or list of tuples.
    """
    pattern_link = re.compile('(href="[^\s#]+")')
    pattern_title = re.compile('(title="[\w\s\\S]+">)')

    if len(links) == 1:
        url = pattern_link.findall(str(links))
        url = normalize_link(url.pop())
        url = normalize_link_to_http(url)

        title = pattern_title.findall(str(links))
        title = normalize_title(str(title.pop()))
        title = re.sub(r"\'", "", title)
        return tuple((url.pop(), title))
    else:
        results = []
        for link in links:
            url = pattern_link.findall(str(link))
            title = pattern_title.findall(str(link))
            if not url or not title:
                continue
            url = normalize_link(url.pop())
            url = normalize_link_to_http(url)
            title = normalize_title(str(title.pop()))
            title = re.sub(r"\'", "", title)
            results.append((url.pop(), title))
    return results


def find_name_article_in_title(data_links: list[str], finish_article: str) -> str:
    """
    Find link in line where which contain text according to regular expression with variable 'finish_article'
    :param data_links: list of links (tag <a>),
    :param finish_article: title of article link to find,
    :return: link (tag <a>) which contain regular expression, or empty string.
    """
    for link in data_links:
        pattern = re.compile(f'title="{finish_article}"')
        result = pattern.findall(str(link))
        if result:
            return link
    return ''


def check_found_link(link: list[str] | str) -> str:
    """
    Find the title of the article by the link.
    :param link: link to the finish article which are looking for,
    :return: title of article.
    """
    if not isinstance(link, list):
        link = [link]
    text_page = get_page(link[0])
    title = parse_title(text_page)
    return title


def find_article_name_on_page(start_url: str, finish_article: str) -> tuple[str, list[str]] | tuple[bool, list[str]]:
    """
    Find link which to go to finish article.
    :param start_url: link to article from which are start find,
    :param finish_article: title of article on which is stopping finding,
    :return: If found - link (tag <a>) and False, if not found - False and list of links (tag <a>).
    """
    text_page = get_page(start_url)
    data_teg_a = parse_page(text_page)
    uniq_data_teg_a = list(set(data_teg_a))
    clean_uniq_data_teg_a = clean_data_teg_a(uniq_data_teg_a)

    link = find_name_article_in_title(clean_uniq_data_teg_a, finish_article)
    if link:
        return link, clean_uniq_data_teg_a
    else:
        return False, clean_uniq_data_teg_a


def add_article_to_result(title_articles: str | list[str] | tuple, total_result: list[str]):
    """
    Add title article to variable 'total_result' to store result.
    :param title_articles: title article to store in result,
    :param total_result: variable to store the result,
    """
    if not isinstance(title_articles, list):
        title_articles = [title_articles]
    for title_article in title_articles:
        total_result.append(title_article)


def print_results_for_task(title_articles: list[str]):
    """
    Output results according to task.
    :param title_articles: Title of articles - start, intermediate, finish article,
    """
    most_popular_articles = get_query('most_popular_articles')
    articles_with_most_links = get_query('articles_with_most_links')
    mean_value_of_second_level_descendants = get_mean_value_of_second_level_descendants(title_articles[0])
    print_results(title_articles,
                  most_popular_articles,
                  articles_with_most_links,
                  mean_value_of_second_level_descendants)


def find_result(start_article, finish_article, requests_per_minute, links_per_page):
    """
    Are looking for the titles of articles by moving on which you can get from the start article to the finish.
    :param start_article: title of article from which start find,
    :param finish_article: title of article on which is stopping finding,
    :param requests_per_minute: request per minute limit,
    :param links_per_page: maximum number of links that are taken from the page,
    :return: If found - True, if not found - False.
    """
    total_result = []
    start_url = f'{wiki_link}{start_article}'
    add_article_to_result(start_article, total_result)

    link, uniq_data_teg_a = find_article_name_on_page(start_url, finish_article)
    if link:
        add_data_to_db(start_article, start_url, uniq_data_teg_a, links_per_page)

        link = find_links(link)
        add_article_to_result(get_title_article(link[0]), total_result)
        return total_result

    if uniq_data_teg_a:
        add_data_to_db(start_article, start_url, uniq_data_teg_a, links_per_page)

        links = get_urls_from_start_url(start_url)
        status = get_page_by_link(links, total_result,
                                  limit_per_minute=requests_per_minute, finish_article=finish_article)
        if status:
            return total_result
    return False


def add_data_to_db(start_article: str, start_url: str, uniq_data_teg_a: list[str], links_per_page: int):
    """
    Adding data to database.
    :param start_article: title of article from which start find,
    :param start_url: link to article from which are start find,
    :param uniq_data_teg_a: list of links (tag <a>)
    :param links_per_page: maximum number of links that are taken from the page,
     """
    insert_data_in_table_link((start_url, start_article))
    data_links = find_links(uniq_data_teg_a)
    insert_data_in_table_link(data_links)

    links_for_requests = data_links[:links_per_page]
    try:
        id_start_link = get_id_for_title_article(start_article)
    except TypeError:
        id_start_link = get_id_for_link(start_url)
    id_links = get_id_for_link(links_for_requests)
    data_for_table_link_to_link = list(zip(id_start_link * len(id_links), id_links))
    insert_data_in_table_link_to_link(data_for_table_link_to_link)


def check_article_in_db(start_article, finish_article):
    """
    Check if there is start_article, finish_article in database, and is there a transition path.
    :param start_article: title of article from which start find,
    :param finish_article: title of article on which is stopping finding,
    :return: if found - list of title articles from start to end, if not found - False.
    """

    total_result = []
    start_title_article = get_check_title_article(start_article)
    if start_title_article:
        finish_title_article = get_check_title_article(finish_article)

        if not finish_title_article:
            return False
        total_result.append(start_title_article[0])
        total_result.append(finish_title_article[0])

        position_in_total_result = -1
        while True:
            parent_title_article = get_check_parent_title_article(total_result[position_in_total_result])
            if not parent_title_article:
                return False
            total_result.insert(position_in_total_result, parent_title_article[0])
            position_in_total_result -= 1
            if total_result[0] != parent_title_article[0]:
                return total_result
    return False


@calc_time
def main(start_article, finish_article, requests_per_minute=None, links_per_page=None):
    """Main controller."""
    init_db()

    total_result = check_article_in_db(start_article, finish_article)
    if total_result:
        print_results_for_task(total_result)
        return total_result

    else:
        total_result = find_result(start_article, finish_article, requests_per_minute, links_per_page)
        if total_result:
            print_results_for_task(total_result)
            return total_result
        else:
            start_url = f'{wiki_link}{start_article}'
            links = get_urls_from_start_url(start_url)
            for link in links:
                total_result = find_result(link, finish_article, requests_per_minute, links_per_page)
                if total_result:
                    print_results_for_task(total_result)
                    return total_result
                return print('Can not find by 3 step')