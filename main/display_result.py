"""Module for display the result."""
from prettytable import PrettyTable


def create_result_table(result: list[str]):
    """Print - the path from the initial article to the final one."""
    result_table = PrettyTable()
    result_table.title = 'The path from the initial article to the final one.'

    step = 1
    if len(result) == 2:
        result_table.field_names = ['Start article', 'Finish article']
    elif len(result) == 3:
        result_table.field_names = ['Start article', 'Intermediate article', 'Finish article']
    elif len(result) > 3:
        intermediate_article = []
        for _ in result[1:-1]:
            intermediate_article.append(f'Intermediate article {step}')
            step += 1
        result_table.field_names = ['Start article', *intermediate_article, 'Finish article']
    else:
        print('Result is empty')

    result_table.add_row(result)
    print(result_table)


def create_table_most_popular_articles(results: list[list]):
    """Print - top 5 most popular articles (those with the most links to themselves)."""
    table_most_popular_articles = PrettyTable()
    table_most_popular_articles.title = 'Top 5 most popular articles (those with the most links to themselves).'
    table_most_popular_articles.field_names = ['ID',
                                               'Title article',
                                               'Quantity of links to the article',
                                               'Link to article']
    table_most_popular_articles.align['Link to article'] = 'l'

    for result in results:
        table_most_popular_articles.add_row(result)
        table_most_popular_articles.add_row('    ')
    print(table_most_popular_articles)


def create_table_articles_with_most_links(results: list[list]):
    """Print - top 5 articles with the most links to other articles."""
    table_articles_with_most_links = PrettyTable()
    table_articles_with_most_links.title = 'Top 5 articles with the most links to other articles.'
    table_articles_with_most_links.field_names = ['ID',
                                                  'Title article',
                                                  'Quantity of links to other articles',
                                                  'Link to article']
    table_articles_with_most_links.align['Link to article'] = 'l'

    for result in results:
        table_articles_with_most_links.add_row(result)
        table_articles_with_most_links.add_row('    ')
    print(table_articles_with_most_links)


def create_table_mean_value_of_second_level_descendants(result: list):
    """Print - number of second-level descendants for the article."""
    table_mean_value_of_second_level_descendants = PrettyTable()
    table_mean_value_of_second_level_descendants.title = 'The number of second-level descendants for the article.'
    table_mean_value_of_second_level_descendants.field_names = ['Title article',
                                                                'Quantity of links to other articles']

    table_mean_value_of_second_level_descendants.add_row(result)
    print(table_mean_value_of_second_level_descendants)


def maim(result: list[str],
         most_popular_articles: list[list],
         articles_with_most_links: list[list],
         mean_value_of_second_level_descendants: list):
    """Main controller for printing results"""
    create_result_table(result)
    create_table_mean_value_of_second_level_descendants(mean_value_of_second_level_descendants)
    create_table_most_popular_articles(most_popular_articles)
    create_table_articles_with_most_links(articles_with_most_links)
