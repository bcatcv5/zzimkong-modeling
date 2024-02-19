import threading
from typing import Final
from support.queue_handler import QueueHandler
from utils.time_ckecker import sleep
from logger import get_logger

SLEEP_TIME: Final = 1
manager = QueueHandler()
logger = get_logger("train")


def run_queue() -> None:
    """메세지 큐에 메세지 삽입"""

    config = {
        "id": 5,
        "objectType": False,
        "model": "nerfacto",
        "src": "https://zzimkong.ggm.kr/1708084929582.mp4"
    }

    threading.Thread(target=sender, args=(config, )).start()


def sender(config: dict):
    sleep(SLEEP_TIME)
    manager.push_message(config)


if __name__ == "__main__":
    run_queue()
    logger.info("큐에 메세지를 적재 완료했습니다.")
