from typing import Callable, Dict

import json
import requests
import time

from threading import Thread

import websocket
from websocket._app import WebSocketApp
from websocket._exceptions import WebSocketConnectionClosedException

from .enumerations import ProductCode, Channel, PublicChannel
from .responses import Ticker


class BitFlyer:
    URL = 'https://api.bitflyer.com/v1'

    def get_ticker(self, product_code: ProductCode) -> Ticker:
        response = requests.get(f'{self.URL}/ticker', params={'product_code': product_code.name})
        response.raise_for_status()
        return Ticker.from_dict(response.json())


class BitFlyerRealTime:
    ENDPOINT = 'wss://ws.lightstream.bitflyer.com/json-rpc'

    def __init__(self) -> None:
        websocket.enableTrace(True)
        self._ws_app = websocket.WebSocketApp(
            self.ENDPOINT,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

        self._message_handler_of: Dict[str, Callable] = {}

    def start(self) -> None:
        def run(ws: WebSocketApp) -> None:
            while True:
                ws.run_forever(ping_interval=30, ping_timeout=10)
                time.sleep(1)

        t = Thread(target=run, args=(self._ws_app, ))
        t.start()

    def subscribe(self, channel: Channel, product_code: ProductCode, handler: Callable) -> None:
        channel_name = f'{channel.name}_{product_code.name}'
        self._message_handler_of[channel_name] = handler
        try:
            self._subscribe(channel_name)
        except WebSocketConnectionClosedException:
            pass

    def _subscribe(self, channel: str) -> None:
        self._ws_app.send(json.dumps({
            'method': 'subscribe',
            'params': {'channel': channel},
        }))

    def _on_message(self, _: WebSocketApp, json_str: str) -> None:
        msg = json.loads(json_str)
        params = msg['params']
        channel: str = params['channel']
        message = params['message']
        handler = self._message_handler_of[channel]

        if channel.startswith(PublicChannel.lightning_ticker.name):
            handler(Ticker.from_dict(message))

    def _on_error(self, ws: WebSocketApp, error) -> None:
        print(error)

    def _on_close(self, ws: WebSocketApp, close_status_code, close_msg) -> None:
        print("### closed ###")

    def _on_open(self, _: WebSocketApp):
        for c in self._message_handler_of.keys():
            self._subscribe(c)
