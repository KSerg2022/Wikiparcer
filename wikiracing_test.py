import unittest

from wikiracing import WikiRacer


class WikiRacerTest(unittest.TestCase):
    racer = WikiRacer()

    def test_1(self):
        path = self.racer.find_path('Дружба', 'Рим')
        self.assertEqual(path, ['Дружба', 'Якопо Понтормо', 'Рим'])

    def test_2(self):
        path = self.racer.find_path('Мітохондріальна ДНК', 'Вітамін K')
        self.assertEqual(path, ['Мітохондріальна ДНК', 'Бактерії', 'Вітамін K'])

    def test_3(self):
        path = self.racer.find_path('Марка (грошова одиниця)', 'Китайський календар')
        self.assertIn('Марка (грошова одиниця)', path)
        self.assertIn('19', path[1])
        self.assertIn('Китайський календар', path)

    def test_4(self):
        path = self.racer.find_path('Фестиваль', 'Пілястра')
        self.assertEqual(path, ['Фестиваль', 'Бароко', 'Пілястра'])

    def test_5(self):
        path = self.racer.find_path('Дружина (військо)', '6 жовтня')
        self.assertIn('Дружина (військо)', path)
        self.assertIn('світова війна', path[1])
        self.assertIn('6 жовтня', path)


if __name__ == '__main__':
    unittest.main()
