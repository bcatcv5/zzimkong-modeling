from .queue_data_source import QueueDataSource
import json
from typing import Final
DECODE_FORMAT: Final = "utf-8"

class QueueHandler:
    """redis 메시지 큐 적재, 추출 핸들러"""

    def __init__(self) -> None:
        self.conn = QueueDataSource().getConnection()

    def exists(self, str):
        return self.conn.exists(str)

    def get(self, str):
        return self.conn.get(str)

    def pop_message(self) -> dict:
        # return self.conn.blpop("config", timeout=0)
        # return self.conn.get("config")
        confs = self.conn.keys("*")[-5:]
        return confs
    
    def push_counter(self, config):
        # self.conn.rpush("config", json.dumps(config))
        self.conn.set("counter", json.dumps(config))

    def push_message(self, config, counter):
        # self.conn.rpush("config", json.dumps(config))

        if config["objectType"]:
            n = counter["furniture"]
            self.conn.set(f"furniture{n}", json.dumps(config))
        else:
            n = counter["space"]
            self.conn.set(f"space{n}", json.dumps(config))
