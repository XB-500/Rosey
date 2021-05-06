import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '../src'))
sys.path.insert(1, os.path.join(sys.path[0], 'src'))
from internals.adapters.google import SecretsManagerAdapter, SecretsManagerSecretModel


def test_secrets_manager_stub():
    """ make sure SM stubbing works """
    os.environ['STUB_SECRETS_MANAGER'] = "True"
    os.environ['SECRET'] = "STUBBED"

    secret = SecretsManagerAdapter.retrieve_secret(
            SecretsManagerSecretModel(
                project="",
                secret_id="SECRET"
            )
    )
    assert secret == "STUBBED"


if __name__ == "__main__":
    test_secrets_manager_stub()

    print("all tests complete")