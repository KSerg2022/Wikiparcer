"""Run module."""
from settings import (tasks,
                      requests_per_minute,
                      urls_per_page)
from main.pathfinder import PathFinder
from utils.calc_time import calc_time


@calc_time
def main(start_article, finish_article, requests_per_minute, urls_per_page):
    """Main controller"""
    path = PathFinder(start_article, finish_article, requests_per_minute, urls_per_page)
    path_from_to = path.main()
    if not path_from_to:
        print('Can not find result.', path_from_to)
    print(path_from_to)


if __name__ == '__main__':
    for articles in tasks:
        main(*articles, requests_per_minute=requests_per_minute, urls_per_page=urls_per_page)
