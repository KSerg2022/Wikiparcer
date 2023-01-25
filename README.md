# Wikiparcer
Two article titles are given. You need to find transitions from one article to another.

A function has been written that accepts two article names as parameters and returns a list of page names through which you can get to it, or an empty list if such a path could not be found.
Example:
('Friendship', 'Rome') -> ['Friendship', 'Jacopo Pontormo', 'Rome']

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
