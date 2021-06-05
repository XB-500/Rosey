# read logs between two dates, with a filter


# google-cloud-logging
# pydantic

import datetime
from mabel.logging.create_logger import LEVELS  # type:ignore
from pydantic import BaseModel  # type:ignore
from typing import Union, Optional

from internals.errors.missing_dependency_error import MissingDependencyError

try:  # pragma: no cover
    from google.cloud import logging as stackdriver  # type:ignore
    from google.cloud.logging import DESCENDING, TextEntry, StructEntry  # type:ignore
except ImportError:
    stackdriver = None  # type:ignore

LOG_NAME = "MABEL"

LEVELS_TO_STRING = {
    LEVELS.DEBUG: "DEBUG",
    LEVELS.INFO: "INFO",
    LEVELS.WARNING: "WARNING",
    LEVELS.ERROR: "ERROR",
    LEVELS.AUDIT: "AUDIT",
    LEVELS.ALERT: "ALERT",
}


class EventModel(BaseModel):
    message: Union[str, dict]
    system: Optional[str] = None
    severity: Optional[int] = LEVELS.DEBUG


class EventFilterModel(BaseModel):
    events_since: Optional[datetime.datetime] = None
    events_before: Optional[datetime.datetime] = None
    severity: Optional[int] = None
    system: Optional[str] = None


class StackDriverAdapter:
    @staticmethod
    def write_event(event: EventModel):

        if not stackdriver:
            MissingDependencyError(
                "`google-cloud-logging` is missing, please install or include in requirements.txt"
            )

        client = stackdriver.Client()
        logger = client.logger(LOG_NAME)

        labels = {}
        if event.system:
            labels["system"] = event.system

        if isinstance(event.message, dict):
            logger.log_struct(
                info=event.message,
                severity=LEVELS_TO_STRING[event.severity],
                labels=labels,
            )
        else:
            logger.log_text(
                text=f"{event.message}",
                severity=LEVELS_TO_STRING[event.severity],
                labels=labels,
            )

    @staticmethod
    def search_events(filters=EventFilterModel):

        if not stackdriver:
            MissingDependencyError(
                "`google-cloud-logging` is missing, please install or include in requirements.txt"
            )

        client = stackdriver.Client()
        logger = client.logger(LOG_NAME)

        formatted_filters = []

        # default to midnight this morning
        if filters.events_since:
            formatted_filters.append(
                f"timestamp >= \"{filters.events_since.strftime('%Y-%m-%dT%H:%M:%SZ')}\""
            )
        else:
            formatted_filters.append(
                f"timestamp >= \"{datetime.datetime.now().strftime('%Y-%m-%dT00:00:00Z')}\""
            )

        # default to now
        if filters.events_before:
            formatted_filters.append(
                f"timestamp <= \"{filters.events_before.strftime('%Y-%m-%dT%H:%M:%SZ')}\""
            )

        if filters.severity:
            formatted_filters.append(f"severity = {LEVELS_TO_STRING[filters.severity]}")

        if filters.system:
            formatted_filters.append(f"labels.system = {filters.system}")

        for entry in logger.list_entries(
            filter_=" AND ".join(formatted_filters), order_by=DESCENDING
        ):  # API call(s)
            result = {}

            result["log:labels"] = entry.labels
            result["log:severity"] = entry.severity
            result["log:timestamp"] = entry.timestamp

            if isinstance(entry, TextEntry):
                result["log:message"] = entry.payload
            elif isinstance(entry, StructEntry):
                result = {**result, **entry.payload}
            yield result
