import requests
from typing import Optional
from pydantic import BaseModel  # type:ignore
import ujson as json  # type:ignore


class SlackNotificationModel(BaseModel):
    slack_token: str
    channel: str
    text: str
    icon_url: Optional[str]
    username: Optional[str]
    blocks: Optional[dict]


class SlackAdapter:
    @staticmethod
    def notify(notification_model: SlackNotificationModel):
        return requests.post(
            "https://slack.com/api/chat.postMessage",
            {
                "token": notification_model.slack_token,
                "channel": notification_model.channel,
                "text": notification_model.text,
                "icon_url": notification_model.icon_url
                if notification_model.icon_url
                else None,
                "username": notification_model.username
                if notification_model.username
                else None,
                "blocks": json.dumps(notification_model.blocks)
                if notification_model.blocks
                else None,
            },
        ).json()
