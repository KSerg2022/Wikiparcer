# Wikiparcer
Two article titles are given. You need to find transitions from one article to another.

A function has been written that accepts two article names as parameters and returns a list of page names through which you can get to it, or an empty list if such a path could not be found.
Example:
('Дружба', 'Рим') -> ['Дружба', 'Якопо Понтормо', 'Рим']

Conditions:
Searches for articles on Ukrainian Wikipedia.

The frequency of requests is limited (200 per minute). The parameter used is the maximum number of requests per minute.
Only the first 200 links are taken on each page
The received link information from the page is stored in the postgres database.
On the next run, the connections from the database are used so that the same queries are not made twice.
On the base, which fills up after several runs, queries are executed looking for:
Top 5 most popular articles (those with the most links to themselves)
Top 5 articles with the most links to other articles
The number of descendants of the second level is found for a given article.

!
Initial data for starting the program in a file - settings.py
To run, use the file - run.py

Test data.
tasks = [
    ('Фестиваль', 'Пілястра'),
    ('Марка (грошова одиниця)', 'Китайський календар'),
    ('Мітохондріальна ДНК', 'Вітамін K'),
    ('Дружба', 'Рим'),
    ('Дружина (військо)', '6 жовтня'),
    ('Україна', 'Маріуполь'),
    ('Програмування', 'Психічний розлад'),
    ('Телепузики', 'Адольф Гітлер')
]

results= [
    ['Фестиваль', 'Бароко', 'Пілястра'],  # Execution time main: 0:00:08.989170
    ['Марка (грошова одиниця)', '1549', 'Китайський календар'),  # Execution time main: 0:00:11.533711
    ['Мітохондріальна ДНК', 'Бактерії', 'Вітамін K'],  # Execution time main: 0:00:30.752744
    ['Дружба', 'Якопо Понтормо', 'Рим'],  # Execution time main: 0:00:02.530732
    ['Дружина (військо)', 'Перша світова війна', '6 жовтня'],  # Execution time main: 0:00:06.144910
    ['Україна', 'Маріуполь'],  # Execution time main: 0:00:05.017397
    ['Програмування', 'Наука', 'Психологія', 'Психічний розлад'],  # Execution time main: 0:07:46.951540
    ['Телепузики', 'Велика Британія', 'Австрія', 'Адольф Гітлер']  # Execution time main: 0:00:21.215190
]

Note.
"Execution time" is for first launch.

