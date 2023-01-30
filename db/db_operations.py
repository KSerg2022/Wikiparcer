""" Module for working with database """
from psycopg2 import Error

from db.db_postgres import connect_to_db
from db.data import queries


def get_id_for_link(links: list[tuple] | tuple | str) -> list:
    """
    Searching id in database for link or links from list.
    :param links: list of links or a link to search for their id in the database,
    :return: list of id for link or links from list.
    """
    id_for_link = []
    if not isinstance(links, list):
        links = [links]
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        for link in links:
            if isinstance(link, tuple):
                link = link[0]
            try:
                query = f"SELECT id FROM links WHERE link = '{link}'"
                cursor.execute(query)
            except (Exception, Error) as error:
                print(f'When searching for data {link} in PostgresSQ {error}')
            else:
                id_link = cursor.fetchone()
                if not id_link:
                    continue
                else:
                    id_for_link.append(id_link[0])

        cursor.close()
    connection.close()
    return id_for_link


def get_id_for_title_article(title: str) -> list[str]:
    """
    Searching article's id in database by his title.
    :param title: title to search for their id in the database,
    :return: list of id for article with title.
    """
    id_article = []
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            query = f"SELECT id FROM links WHERE title_article = '{title}'"
            cursor.execute(query)
        except (Exception, Error) as error:
            print(f'When searching for data {title} in PostgresSQ {error}')
        else:
            id_result = cursor.fetchone()
            id_article.append(id_result[0])

        cursor.close()
    connection.close()
    return id_article


def get_urls_from_start_url(start_url: list[str] | str = None, article: bool = False) -> list[str]:
    """
    Get a list of link's id, first-level descendants.
    :param start_url: initial link,
    :param article: If True - function return list of articles? if False - list of links,
    :return: list of ids for links, which are first-level descendants.
    """
    id_for_start_url = 0
    try:
        id_for_start_url = get_id_for_link(start_url)[0]
    except IndexError:
        pass
    urls = []
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            if start_url:
                query = f"SELECT link FROM links " \
                        f"WHERE links.id IN (SELECT link_right FROM link_to_link" \
                        f" WHERE link_left = {id_for_start_url})"

            if article:
                query = f"SELECT title_article FROM links " \
                        f"WHERE links.id IN (SELECT link_right FROM link_to_link" \
                        f" WHERE link_left = {id_for_start_url})"

            cursor.execute(query)
        except (Exception, Error) as error:
            print(f'When searching for data in  PostgresSQ {error}')
        else:
            for url in cursor.fetchall():
                urls.append(list(url)[0])

        cursor.close()
    connection.close()
    return urls


def get_mean_value_of_second_level_descendants(title_article: str) -> list[str]:
    """
    Get the number of second-level descendants for the article
    :param title_article: title_article,
    :return: list from two elements: title article and number of second-level descendants for her.
    """
    id_url = get_id_for_title_article(title_article)
    mean_value_of_second_level_descendants = []
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            query = f"SELECT link_left, link_right, count(link_left)" \
                    f" FROM link_to_link WHERE link_left IN " \
                    f"(SELECT link_right FROM link_to_link WHERE link_left = {id_url[0]})" \
                    f" GROUP BY link_left, link_right"
            cursor.execute(query)
        except (Exception, Error) as error:
            print(f'When searching for data in PostgresSQ {error}')
        else:
            for url in cursor.fetchall():
                mean_value_of_second_level_descendants.append(list(url))
            mean_value_of_second_level_descendants = [title_article, len(mean_value_of_second_level_descendants)]
        cursor.close()
    connection.close()
    return mean_value_of_second_level_descendants


def get_query(query: str) -> list[list]:
    """
    Get data according to query.
    :param query: key for query in dict from 'queries' from 'data.py'.
    :return: data according to query.
    """
    query_to_find = queries[query]
    articles_with_most_links = []
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            query = query_to_find
            cursor.execute(query)
        except (Exception, Error) as error:
            print(f'When searching for data in PostgresSQ {error}')
        else:
            for url in cursor.fetchall():
                articles_with_most_links.append(list(url))

        cursor.close()
    connection.close()
    return articles_with_most_links


def get_title_article(url: str | tuple) -> list[str]:
    """
    Get title for the article in database by url.
    :param url:  link to article in internet,
    :return: title for the article in database according url.
    """
    title_article = []
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            query = f"SELECT title_article FROM links WHERE link = '{url}'"
            cursor.execute(query)
        except (Exception, Error) as error:
            print(f'When searching for data in PostgresSQ {error}')
        else:
            title = cursor.fetchone()
            title_article.append(title[0])

        cursor.close()
    connection.close()
    return title_article


def get_check_title_article(url: str) -> list[str] | bool:
    """
    Checking if is article in database by url.
    :param url: link to article in internet,
    :return: if is - title for the article in database according url, if not is - False.
    """
    title_article = []
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            query = f"SELECT title_article FROM links WHERE title_article = '{url}'"
            cursor.execute(query)
        except (Exception, Error) as error:
            print(f'When searching for data in PostgresSQ {error}')
        else:
            title = cursor.fetchone()
            try:
                title_article.append(title[0])
            except Exception:
                return False

        cursor.close()
    connection.close()
    return title_article


def get_check_parent_title_article(title: str) -> list[str] | bool:
    """
    Checking if is article in database by title.
    :param title: title to article which myst find in internet,
    :return:  if is - title for the article in database according url, if not is - False.
    """
    title_article = []
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            query = f"SELECT title_article FROM link_to_link, links " \
                    f"WHERE link_right = (SELECT id link FROM links " \
                    f"WHERE title_article = '{title}') " \
                    f"AND id = link_left"
            cursor.execute(query)
        except (Exception, Error) as error:
            print(f'When searching for data in PostgresSQ {error}')
        else:
            title = cursor.fetchall()
            try:
                for value in title:
                    title_article.append(value[0])
            except Exception:
                pass

        cursor.close()
    connection.close()
    return title_article
