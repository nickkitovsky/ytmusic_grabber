import json
import logging
import time
from datetime import datetime
from functools import wraps
from typing import Iterable

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


def write_json(filename: str, filedata: dict | list):
    """Write dict or list object to file

    Args:
        filename (str): File for dump data
        filedata (dict | list): Data for writing
    """
    with open(filename, "w") as fs:
        json.dump(filedata, fs)


def read_json(filemane: str) -> dict:
    """Read json object from file

    Args:
        filemane (str): File for load data

    Returns:
        dict: Json object(dict)
    """
    with open(filemane, encoding="utf-8") as fs:
        return json.load(fs)


def extract_chain(data: dict | list, chain: Iterable | None = None):
    '''
    Extract chain keys from dict or list, skipping signle nested element (len==1)
    '''
    if chain:
        for item in chain:
            while len(data) == 1:
                match data:
                    case list(data):
                        data = data[0]
                    case dict(data) if item in data.keys():
                        break
                    case dict(data):
                        data = list(data.values())[0]
            data = data[item]
        return data
    else:
        while len(data) == 1:
            match data:
                case list(data):
                    data = data[0]
                case dict(data):
                    data = list(data.values())[0]
        return data


def fields_to_str(fields_parrent: list, separator: str = " "):
    '''
    Join list's fields in response to str
    '''
    return f"{separator}".join([field["text"] for field in fields_parrent])


def dump_exception(
    dump_data: list | dict,
    error_message: str,
    exception_type: type,
):
    '''
    Raise exception and dump data to `data/errors` dir with file name %Y-%M-%DT%H_%M_%S'
    '''
    now = datetime.now().isoformat(timespec='seconds').replace(':', '_')
    dump_filename = f'data/errors/{now}.json'
    write_json(dump_filename, dump_data)
    raise exception_type(f'{error_message}.\nDump file saved to {dump_filename}')
