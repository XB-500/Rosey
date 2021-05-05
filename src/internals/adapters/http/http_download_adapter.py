"""
HTTP Download Adapter

Requirements
    urllib
"""
from urllib.request import urlopen


class HttpDownloadAdapter():

    @staticmethod
    def simple_download(url: str):

        if not url.startswith('https://') and not url.startswith("http://"):
            raise ValueError(F"`{url}` is not a valid HTTP end-point, HTTP Download Adapter can only be used for HTTP end-points.")

        body = urlopen(url)  # nosec
        return body.read().decode('utf8', errors='backslashreplace')
