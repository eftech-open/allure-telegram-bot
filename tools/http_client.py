import logging
import requests
from urllib.parse import urlparse


class HTTPMethods:
    """
    Http-клиент
    """

    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.session()

    @staticmethod
    def __request_log(func, response):
        logging.debug(f'{func.upper()}[{response.status_code}]: {response.url}')

    def __format_url(self, url):
        if self.base_url in url:
            format_url = urlparse(url).path
        else:
            return url
        return format_url

    def __perform_request(self, method: str, endpoint: str, retries: int = 3, expected_code: int = None, **kwargs):
        for _ in range(retries):
            response = self.session.request(
                method=method,
                url=self.base_url + self.__format_url(endpoint),
                **kwargs
            )
            self.__request_log(method, response)

            retry_status_code_list = range(400, 505)
            if response.status_code != expected_code and response.status_code not in retry_status_code_list:
                raise AssertionError(
                    f"Ожидаемый статус-код [{expected_code}] не равен актуальному [{response.status_code}]")
            elif response.status_code in retry_status_code_list:
                if _ == retries - 1:
                    raise AssertionError(
                        f"Ожидаемый статус-код [{expected_code}] не равен актуальному [{response.status_code}]")
                continue
            return response

    def get(self, endpoint, expected_code=200, **kwargs):
        return self.__perform_request(method="get", endpoint=endpoint, expected_code=expected_code, **kwargs)

    def post(self, endpoint, expected_code=200, **kwargs):
        return self.__perform_request(method="post", endpoint=endpoint, expected_code=expected_code, **kwargs)

    def put(self, endpoint, expected_code=200, **kwargs):
        return self.__perform_request(method="put", endpoint=endpoint, expected_code=expected_code, **kwargs)

    def delete(self, endpoint, expected_code=200, **kwargs):
        return self.__perform_request(method="delete", endpoint=endpoint, expected_code=expected_code, **kwargs)


http_client = HTTPMethods
