"""Module with data for database."""
link = '''CREATE TABLE links (
            id INT GENERATED ALWAYS AS IDENTITY,
            title_article TEXT NOT NULL,
            link TEXT NOT NULL,
            PRIMARY KEY(id),
            UNIQUE (link),
            UNIQUE (title_article)
            );'''

link_to_link = '''CREATE TABLE link_to_link (
                    link_left int NOT NULL,
                    link_right int NOT NULL,
                    PRIMARY KEY (link_left, link_right),
                    CONSTRAINT fk_link_left FOREIGN KEY (link_left) REFERENCES links (id) ON UPDATE CASCADE,
                    CONSTRAINT fk_link_right FOREIGN KEY (link_right) REFERENCES links (id) ON UPDATE CASCADE,
                    CHECK (link_right != link_left)
                    ); '''

tables = [link, link_to_link]

queries = {
    'most_popular_articles': 'SELECT id, title_article, qty, link FROM links JOIN '
                             '(SELECT link_right, count(link_right) as qty FROM link_to_link '
                             'GROUP BY link_right ORDER BY qty DESC LIMIT 5) ce '
                             'ON links.id = link_right;',
    'articles_with_most_links': 'SELECT id, title_article, qty, link FROM links JOIN '
                                '(SELECT count(link_left) as qty, link_left FROM link_to_link '
                                'GROUP BY link_left ORDER BY qty desc LIMIT 5) ce '
                                'ON links.id = link_left;',
   }
