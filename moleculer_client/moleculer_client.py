import datetime
import enum
import json
import time
import uuid
from typing import Dict, List

from pynats import NATSClient, NATSMessage

PROTOCOL_VERSION = "4"
LOCAL_NATS = "nats://127.0.0.1:4222"

__all__ = ['MoleculerClient', 'MoleculerCommands']


class MoleculerCommands(enum.Enum):
    DISCOVER = "MOL.DISCOVER.{}"
    REQUEST = "MOL.REQ.{}"
    RESPONSE = "MOL.RES.{}"
    INFO = "MOL.INFO.{}"
    PING = "MOL.PING.{}"
    PONG = "MOL.PONG.{}"
    EVENT = "MOL.EVENT.{}"

    def format(self, node):
        return self.value.format(node)


class MoleculerClient(object):
    def __init__(self, node_id: str, moleculer_nodeID: str, url=LOCAL_NATS):
        self.nc: NATSClient
        self.node = moleculer_nodeID
        self.sender = node_id
        self.reply_messages: Dict[str, NATSMessage] = {}
        self.init_app()

    def init_app(self, url: str = LOCAL_NATS):
        self.nc = NATSClient(url=url, socket_timeout=5)
        self.nc.connect()

        def callback(message: NATSMessage):
            payload = message.payload.decode("utf-8")
            moleculerResponse = json.loads(payload)
            self.reply_messages[moleculerResponse['id']] = moleculerResponse["data"]

        self.nc.subscribe(MoleculerCommands.RESPONSE.format(self.sender), callback=callback)

    def call(self, action: str, params, meta: dict = None, timeout=5000) -> dict:
        body = {
            "ver": PROTOCOL_VERSION,
            "sender": self.sender,
            "id": str(uuid.uuid1()),
            "action": action,
            "params": params,
            "meta": meta or {},
            "timeout": timeout,
            "level": 1,
            "metrics": False,
            "tracing": None,
            "caller": None,
            "stream": False,
        }

        self.nc.publish(MoleculerCommands.REQUEST.format(self.node), payload=json.dumps(body).encode())
        self.nc.wait(count=1)
        return self.reply_messages.pop(body['id'])

    def discover(self, broadcast=False) -> dict:
        body = {
            "ver": PROTOCOL_VERSION,
            "sender": self.sender,
        }
        result = {'payload': None}

        def callback(message):
            result['payload'] = json.loads(message.payload.decode("utf-8"))

        self.nc.subscribe(MoleculerCommands.INFO.format(self.sender), callback=callback)
        if broadcast:
            self.nc.publish(MoleculerCommands.DISCOVER.value.replace(".{}", ''), payload=json.dumps(body).encode())
        else:
            self.nc.publish(MoleculerCommands.DISCOVER.format(self.node), payload=json.dumps(body).encode())
        self.nc.wait(count=1)
        return result['payload']

    def ping(self, broadcast=False) -> dict:
        body = {
            "ver": PROTOCOL_VERSION,
            "id": str(uuid.uuid1()),
            "sender": self.sender,
            "time": datetime.datetime.now().timestamp() * 1000
        }
        result = {'payload': None}

        def callback(message):
            result['payload'] = json.loads(message.payload.decode("utf-8"))

        self.nc.subscribe(MoleculerCommands.PONG.format(self.sender), callback=callback)
        if broadcast:
            self.nc.publish(MoleculerCommands.PING.value.replace(".{}", ''), payload=json.dumps(body).encode())
        else:
            self.nc.publish(MoleculerCommands.PING.format(self.node), payload=json.dumps(body).encode())
        self.nc.wait(count=1)
        result['payload'].pop('id')
        return result['payload']

    def emit(self, event: str, data: dict = {}, meta={}, groups: List[str] = [], broadcast=False, caller=None) -> None:
        body = {
            "ver": PROTOCOL_VERSION,
            "sender": self.sender,
            "id": str(uuid.uuid1()),
            "event": event,
            "data": data,
            "meta": meta,
            "groups": groups,
            "broadcast": broadcast,
            "level": 1,
            "caller": caller,
            "metrics": False,
            "tracing": None,
            "stream": False,
        }
        self.nc.publish(MoleculerCommands.EVENT.format(self.node), payload=json.dumps(body).encode())

# moleculer = MoleculerClient('Api', 'Mad')
# print(1, moleculer.call("mad.batata", {}))
# print(2, moleculer.call("mad.batata", {}))
# print(3, moleculer.call("mad.batata", {}))
# print(4, moleculer.call("mad.batata", {}))
# print(moleculer.discover())
# print(moleculer.ping())
# print(moleculer.emit('mad.updated', {"mac": "22:22:22:22:22:22:22"}))
