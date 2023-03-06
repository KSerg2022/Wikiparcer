"""Module initialization database and adding data to db."""
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from db.data import tables
from settings import database_name


def init_db():
    """
    First connection to create database.
    :return: If connected - connection, if not connected - exit from program.
    """
    connection = None
    try:
        connection = psycopg2.connect(host='127.0.0.1', user='postgres', password='1qa2ws3ed', port='5432')
    except Exception as error:
        print(error)
        exit(0)

    if connection is not None:
        return connection
    else:
        print('Connection not established to Postgres')
        exit()


def create_db(db_name: str) -> bool:
    """
    Create database with given name.
    param db_name: name of database
    :return: if database was created - True, if not - False.
    """
    connection = init_db()
    if connection:
        if not check_db_exist(connection, db_name):
            try:
                connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cursor = connection.cursor()
                sql_create_database = f"CREATE DATABASE {db_name}"
                cursor.execute(sql_create_database)
                cursor.close()
            except (Exception, Error) as error:
                connection.close()
                print(f'PostgresSQL: {error}')
            connection.close()
            return True

        connection.close()
        return False


def check_db_exist(connection, db_name: str) -> bool:
    """
    Check if is there database with given name.
    :param connection: connection with database
    :param db_name: name of database
    :return: if database with given name exist - True, if not - False.
    """
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    check_query = f"SELECT datname FROM pg_database;"
    cursor.execute(check_query)
    db_names = cursor.fetchall()

    cursor.close()
    db_names = [list(db_name)[0] for db_name in db_names]
    if db_name in db_names:
        return True
    return False


def connect_to_db():
    """
    Connecting to database for do operations.
    :return: If connected - connection, if not connected - exit from program.
    """
    connection = None
    try:
        connection = psycopg2.connect(host='127.0.0.1', user='postgres', password='1qa2ws3ed', port='5432',
                                      database='wiki')
    except Exception as error:
        print(error)
        exit(0)

    if connection is not None:
        return connection
    else:
        print('Connection not established to Postgres')
        exit()


def create_table(tables_to_add):
    """
    Create tables in database.
    param tables: tables to be created in the database
    :return: If tables created - True, if not created - error.
    """
    connection = connect_to_db()
    if connection:
        for table in tables_to_add:
            try:
                cursor = connection.cursor()
                create_table_query = table
                cursor.execute(create_table_query)
                connection.commit()
                cursor.close()
            except (Exception, Error) as error:
                connection.close()
                print(f'Table {table[:25]} в PostgresSQ {error}')

        connection.close()
        return True


def insert_data_in_table_link(links: list[tuple] | tuple) -> bool:
    """
    Adding data in database in the table 'links'.
    :param links: links and title articles
    :return: if data added in database - True, if not - error.
    """
    if not isinstance(links, list):
        links = [links]
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        for link in links:
            if not check_link_in_db(list(link)[0], cursor) and not check_title_in_db(list(link)[1], cursor):
                try:
                    insert_query = f"INSERT INTO links(link, title_article) VALUES {link};"
                    cursor.execute(insert_query)
                    connection.commit()
                except (Exception, Error) as error:
                    print(f'When adding data {link} in PostgresSQ {error}')

            else:
                if not check_link_in_db(list(link)[0], cursor) and check_title_in_db(list(link)[1], cursor):
                    try:
                        update_query = f"Update links set link = '{list(link)[0]}'" \
                                       f" where title_article = '{list(link)[1]}'"
                        cursor.execute(update_query)
                        connection.commit()
                    except (Exception, Error) as error:
                        print(f'When adding data {list(link)[0]} in PostgresSQ {error}')

        cursor.close()
    connection.close()
    return True


def check_link_in_db(link: str, cursor) -> str:
    """
    Check exist link in database.
    :param link: link which must check in database,
    :param cursor:
    :return: if link in database - True, if not - None.
    """
    get_query = f"SELECT link FROM links WHERE link = '{link}'"
    cursor.execute(get_query)
    link = cursor.fetchone()
    return link


def check_title_in_db(title_article: str, cursor) -> str:
    """
    Check exist title in database.
    param title_article: title which must check in database,
    :return: if title in database - True, if not - None.
    """
    get_query = f"SELECT title_article FROM links WHERE title_article = '{title_article}'"
    cursor.execute(get_query)
    title = cursor.fetchone()
    return title


def insert_data_in_table_link_to_link(id_links: list[tuple] | tuple):
    """
    Adding data in database in the table 'link_to_link'.
    :param id_links: pairs of id_links
    :return: if data added in database - True, if not - error.
    """
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        for link in id_links:
            if not check_link_to_link_in_db(link, cursor):
                try:
                    insert_query = f'INSERT INTO link_to_link(link_left, link_right) VALUES {link}'
                    cursor.execute(insert_query)
                    connection.commit()
                except (Exception, Error) as error:
                    print(f'When adding data {link} in PostgresSQL {error}')

        cursor.close()
    connection.close()
    return True


def check_link_to_link_in_db(link_to_link: tuple[int], cursor) -> tuple[int] | bool:
    """
    Check exist a pair of links in database.
    param link_to_link: a pair of links which must check in database,
    :return: if a pair of links in database - True, if not - None.
    """
    if link_to_link[0] == link_to_link[1]:
        return True
    get_query = f"SELECT link_left, link_right FROM link_to_link " \
                f"WHERE link_left = {link_to_link[0]} AND link_right= {link_to_link[1]}"
    cursor.execute(get_query)
    link = cursor.fetchone()
    return link


def main():
    """Controller for initialization database and create tables."""
    create_db(database_name)
    create_table(tables)
