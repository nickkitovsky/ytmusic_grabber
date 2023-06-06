import atexit
import json
import shlex
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

import httpx


class AuthData:
    def __init__(self, curl_file: str | Path) -> None:
        match curl_file:
            case str(curl_file):
                self.curl_file = Path(curl_file)
            case Path():
                self.curl_file = curl_file
            case _:
                raise ValueError('Incorrect type of `curl_file` (str or Path only)')
        if not self.curl_file.exists():
            raise FileNotFoundError('Incorrect file name or file path')
        try:
            parsed_data = self._parse_curl_file()
        except (IndexError, TypeError):
            raise ValueError(
                'Error of parsing curl file. Curl file has incorrect content'
            )
        self.cookies = parsed_data['cookies']
        self.header = parsed_data['headers']
        self.json_data = parsed_data['json_data']
        self.params = parsed_data['params']

    def _parse_curl_file(
        self,
    ) -> dict[Literal['cookies', 'headers', 'params', 'json_data'], dict]:
        with open(self.curl_file, 'r', encoding='utf-8') as fs:
            file_contents = fs.readlines()

        post_url = shlex.split(file_contents[0])[1]
        post_params_raw = urlparse(post_url).query.split('&')
        post_params = {k: v for k, v in [param.split('=') for param in post_params_raw]}
        data_raw = shlex.split(file_contents[-2])[1]
        post_data = json.loads(data_raw)
        # delete default browse id
        del post_data['browseId']
        headers_raw = [
            line.replace(' \\\n', '').replace('  -H', '')
            for line in file_contents
            if line[:4] == '  -H'
        ]
        headers = {
            line[0].replace(';', ''): ':'.join(line[1:]).strip()
            for line in [
                shlex.split(headers_line)[0].split(':') for headers_line in headers_raw
            ]
        }
        cookies_raw = headers.pop('cookie').split(';')
        cookies = {
            val[0].strip(): '='.join(val[1:]).strip()
            for val in [cookie_line.split('=') for cookie_line in cookies_raw]
        }

        return {
            'cookies': cookies,
            'headers': headers,
            'params': post_params,
            'json_data': post_data,
        }


class ApiClient:
    def __init__(self) -> None:
        self._client = self._init_client()
        atexit.register(self._close_client, self._client)

    def _init_client(self) -> httpx.Client:
        return httpx.Client()

    def _close_client(self, client: httpx.Client) -> None:
        client.close()


class YtMusic:
    def __init__(self, curl_file: str | Path) -> None:
        self.auth_data = AuthData(curl_file=curl_file)
        self.client = ApiClient()
