"""Run module."""
from settings import (tasks,
                      requests_per_minute,
                      links_per_page)
from main.main import main as start


def main(start_article, finish_article,  requests_per_minute=None, links_per_page=None):
    """Main controller"""
    total_result = start(start_article, finish_article, requests_per_minute, links_per_page)
    return total_result


if __name__ == '__main__':
    for articles in tasks:
        main(*articles, requests_per_minute=requests_per_minute, links_per_page=links_per_page)
