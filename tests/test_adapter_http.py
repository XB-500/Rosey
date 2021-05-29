import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '../src'))
sys.path.insert(1, os.path.join(sys.path[0], 'src'))
from internals.adapters.http import HttpAdapter, GetRequestModel, PostRequestModel
from mabel.utils.entropy import random_string


def test_get():

    test_payload = random_string()
    response = HttpAdapter.get(
        GetRequestModel(
            url="https://httpbin.org/headers",
            headers={"test":test_payload}
        )
    )

    assert isinstance(response, tuple)
    assert response[0] == 200, "Status Code unexpected"
    assert test_payload in response[2].decode('utf-8'), "Not reading body correctly"


def test_post():

    test_payload = random_string()
    response = HttpAdapter.post(
        PostRequestModel(
            url="https://httpbin.org/post",
            data={"test":test_payload}
        )
    )

    assert isinstance(response, tuple)
    assert response[0] == 200, "Status Code unexpected"
    assert test_payload in response[2].decode('utf-8'), "Not reading body correctly"


if __name__ == "__main__":
    test_get()
    test_post()

    print("all tests complete")