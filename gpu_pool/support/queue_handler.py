from .queue_data_source import QueueDataSource
import json


class QueueHandler:
    """redis 메시지 큐 적재, 추출 핸들러"""

    def __init__(self) -> None:
        self.conn = QueueDataSource().getConnection()

    def pop_message(self) -> dict:
        return self.conn.blpop("config", timeout=0)

    def push_message(self, config):
        self.conn.rpush("config", json.dumps(config))
