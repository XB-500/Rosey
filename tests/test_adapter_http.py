import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], "../src"))
sys.path.insert(1, os.path.join(sys.path[0], "src"))
from internals.adapters.http import HttpAdapter, GetRequestModel, PostRequestModel
from mabel.utils.entropy import random_string
import pytest


def test_get():

    test_payload = random_string()
    response = HttpAdapter.get(
        GetRequestModel(
            url="https://httpbin.org/headers", headers={"test": test_payload}
        )
    )

    assert isinstance(response, tuple)
    assert response[0] == 200, "Status Code unexpected"
    assert test_payload in response[2].decode("utf-8"), "Not reading body correctly"


def test_post():

    test_payload = random_string()
    response = HttpAdapter.post(
        PostRequestModel(url="https://httpbin.org/post", data={"test": test_payload})
    )

    assert isinstance(response, tuple)
    assert response[0] == 200, "Status Code unexpected"
    assert test_payload in response[2].decode("utf-8"), "Not reading body correctly"


def test_non_http():

    with pytest.raises(ValueError):
        HttpAdapter.post(PostRequestModel(url="file://"))

    with pytest.raises(ValueError):
        HttpAdapter.get(GetRequestModel(url="file://"))


if __name__ == "__main__":
    test_get()
    test_post()
    test_non_http()

    print("all tests complete")
