from typing import List

import run
from settings import requests_per_minute, links_per_page


class WikiRacer:

    def find_path(self, start: str, finish: str) -> List[str]:
        # implementation goes here
        result = run.main(start,
                          finish,
                          requests_per_minute=requests_per_minute,
                          links_per_page=links_per_page)
        return result

