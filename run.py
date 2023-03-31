"""Run module."""
from settings import (tasks,
                      requests_per_minute,
                      urls_per_page)
from main.pathfinder import PathFinder
from utils.calc_time import calc_time


class WikiRacer:
    @calc_time
    def find_path(self, start_article: str, finish_article: str, requests_per_minute, urls_per_page):
        path = PathFinder(start_article=start_article,
                          finish_article=finish_article,
                          requests_per_minute=requests_per_minute,
                          urls_per_page=urls_per_page)
        path_from_to = path.main()
        if not path_from_to:
            print('Can not find result.', path_from_to)
            return path_from_to
        print(path_from_to)
        return path_from_to


if __name__ == '__main__':
    for articles in tasks:
        path = WikiRacer()
        path.find_path(*articles, requests_per_minute=requests_per_minute, urls_per_page=urls_per_page)
