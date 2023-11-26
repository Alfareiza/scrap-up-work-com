from datetime import datetime
from functools import wraps
from time import time

from settings import log


def logtime(tag):
    def decorator(func):
        @wraps(func)
        def wrapper(*fargs, **fkwargs):
            start = time()
            log.debug(format(datetime.now(), '%D %T'), f'Executing {func.__name__!r}')
            value = func(*fargs, **fkwargs)
            title = ''
            log.debug(format(datetime.now(), '%D %T'),
                      f"{title or tag}{func.__name__!r} took {format(time() - start, '.4f')}s.")
            return value

        return wrapper

    return decorator
