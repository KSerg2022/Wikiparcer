import unittest

from run import WikiRacer
from settings import requests_per_minute, urls_per_page


class WikiRacerTest(unittest.TestCase):
    racer = WikiRacer()

    def test_1(self):
        path = self.racer.find_path('Дружба', 'Рим', requests_per_minute, urls_per_page)
        self.assertEqual(path, ['Дружба', 'Якопо Понтормо', 'Рим'])

    def test_2(self):
        path = self.racer.find_path('Мітохондріальна ДНК', 'Вітамін K', requests_per_minute, urls_per_page)
        self.assertEqual(path, ['Мітохондріальна ДНК', 'Бактерії', 'Вітамін K'])

    def test_3(self):
        path = self.racer.find_path('Марка (грошова одиниця)', 'Китайський календар', requests_per_minute, urls_per_page)
        self.assertEqual(path, ['Марка (грошова одиниця)', '2017', 'Китайський календар'])

    def test_4(self):
        path = self.racer.find_path('Фестиваль', 'Пілястра', requests_per_minute, urls_per_page)
        self.assertEqual(path, ['Фестиваль', 'Бароко', 'Пілястра'])

    def test_5(self):
        path = self.racer.find_path('Дружина (військо)', '6 жовтня', requests_per_minute, urls_per_page)
        self.assertEqual(path, ['Дружина (військо)', 'Перша світова війна', '6 жовтня'])

    def test_6(self):
        path = self.racer.find_path('Україна', 'Азовсталь', requests_per_minute, urls_per_page)
        self.assertEqual(path, ['Україна', 'Маріуполь', 'Азовсталь'])


if __name__ == '__main__':
    unittest.main()
