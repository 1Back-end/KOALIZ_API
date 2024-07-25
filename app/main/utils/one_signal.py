from onesignal_sdk.client import Client
from onesignal_sdk.error import OneSignalHTTPError
from app.main.core.config import Config
import requests
import json


def onesignal_notification(payload: dict, include_player_ids: list[str]) -> dict:
    try:

        header = {"Content-Type": "application/json; charset=utf-8"}
        payload["app_id"] = Config.ONESIGNAL_APP_ID
        payload["include_player_ids"] = include_player_ids

        response = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
        print(response.status_code, response.reason)
        if response.status_code in [200, 201]:
            response = response.json()

        return response

    except OneSignalHTTPError as e: # An exception is raised if response.status_code != 2xx
        print(e)
        print(e.status_code)
        print(e.http_response.json()) # You can see the details of error by parsing original response

