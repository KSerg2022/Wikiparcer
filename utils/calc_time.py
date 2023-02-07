"""Utils for project."""
import time
from datetime import datetime


def calc_time(func):
    """Calc execution time"""

    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        func_result = func(*args, **kwargs)
        end_time = datetime.now()
        print(f'Execution time {func.__name__}: {end_time - start_time}', end='\n\n')
        return func_result

    return wrapper


start_time = time.time()


def calc_delay(limit_per_minute, current_time):
    """
    Calculating the size of the pause between requests to the site.
    :param limit_per_minute: request per minute limit,
    :param current_time: current time doing operation,
    :return: delay in seconds.
    """
    global start_time
    base_delay = 60 / limit_per_minute

    if current_time - start_time > base_delay:
        start_time = current_time
        return 0
    else:
        current_delay = base_delay - (current_time - start_time)
        start_time = current_time
        return current_delay
