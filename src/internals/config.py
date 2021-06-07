import os
from typing import Optional
from functools import lru_cache
from mabel.logging import get_logger  # type:ignore

PRODUCTION_PROJECT = "mabeldev"
DEVELOPMENT_PROJECT = os.environ.get("PROJECT_NAME", "DEVELOPMENT")

PRODUCTION_CONTROLLER = "https://controller-cuvdwt7kra-uc.a.run.app"
DEVELOPMENT_CONTROLLER = os.environ.get("CONTROLLER_URL")

PRODUCTION_VALUES = {
    "<project>": PRODUCTION_PROJECT,
    "<bucket:raw>": "mabel_data/RAW",
    "<bucket:logs>": "mabel_logs",
    "<bucket:processed>": "mabel_data/PROCESSED",
    "<bucket:flows>": "mabel_flows",
}

DEVELOPMENT_VALUES = {
    "<project>": DEVELOPMENT_PROJECT,
    "<bucket:raw>": os.environ.get("BUCKET_NAME", "TEST") + "/RAW",
    "<bucket:logs>": os.environ.get("BUCKET_NAME", "TEST"),
    "<bucket:processed>": os.environ.get("BUCKET_NAME", "TEST") + "/PROCESSED",
    "<bucket:flows>": os.environ.get("BUCKET_NAME", "TEST"),
}


@lru_cache(1)
def _get_env() -> str:
    environment = os.environ.get("ENVIRONMENT", "DEVELOPMENT")
    if environment in ("DEVELOPMENT", "LAB"):
        get_logger().debug(
            f"Environment is `{environment}`, ensure you set the PROJECT_NAME, BUCKET_NAME and CONTROLLER_URL info in your .env or environment"
        )
    else:
        get_logger().debug(f"Environment is `{environment}`")
    return environment


@lru_cache(1)
def _get_env_set() -> dict:
    env_set = {}
    if _is_production():
        env_set = PRODUCTION_VALUES
    else:
        env_set = DEVELOPMENT_VALUES  # type:ignore
    get_logger().debug(env_set)
    return env_set


def _is_production() -> bool:
    return _get_env() == "PRODUCTION"


def project_name() -> str:
    if _is_production():
        return PRODUCTION_PROJECT
    return DEVELOPMENT_PROJECT


def set_environment_value(raw: str) -> str:
    for k, v in _get_env_set().items():
        if k in raw:
            return raw.replace(k, v)
    return raw


def controller_url() -> Optional[str]:
    if _is_production():
        return PRODUCTION_CONTROLLER
    return DEVELOPMENT_CONTROLLER
