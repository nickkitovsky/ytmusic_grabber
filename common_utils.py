import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


logger.setLevel(logging.ERROR)
handler = logging.StreamHandler()
handler.setLevel(logging.ERROR)
logger.addHandler(handler)


def retry(attempts_number: int, retry_sleep_sec: int):
    '''
    Retry help decorator.
    '''

    def decarator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(attempts_number):
                try:
                    return func(*args, **kwargs)
                except Exception as err:
                    logger.error(err)
                    time.sleep(retry_sleep_sec)
                logger.error('Trying attempt %s of %s', attempt + 1, attempts_number)
            logger.error('func %s retry failed', func)
            raise Exception(f'Exceed max retry num: {attempts_number} failed')

        return wrapper

    return decarator
