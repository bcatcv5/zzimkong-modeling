from .queue_data_source import QueueDataSource
import json
from typing import Final
DECODE_FORMAT: Final = "utf-8"

class QueueHandler:
    """redis 메시지 큐 적재, 추출 핸들러"""

    def __init__(self) -> None:
        self.conn = QueueDataSource().getConnection()

    def pop_message_furniture(self) -> dict:
        return self.conn.blpop("furniture", timeout=0)
    
    def pop_message_space(self) -> dict:
        return self.conn.blpop("space", timeout=0)

    def push_message(self, config):
        if config["objectType"]: # true
            self.conn.rpush("furniture", json.dumps(config))
        else:                    # false
            self.conn.rpush("space", json.dumps(config))
