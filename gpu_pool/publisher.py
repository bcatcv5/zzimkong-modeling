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
        "arch": {"type": "CustomModel", "args": {"num_classes": 11}},
        "data_loader": {
            "type": "CustomDataLoader",
            "args": {"batch_size": 3, "shuffle": False, "num_workers": 2},
        },
        "dataset": {
            "type": "CustomDataset",
            "args": {
                "annotation": "../dataset/train.json",
                "data_dir": "../dataset",
                "resize": 1024,
            },
        },
        "trainer": {
            "type": "CustomTrainer",
            "args": {
                "epochs": 2,
                "save_path": "/data/ephemeral/home/level2-objectdetection-cv-05/live/checkpoints/faster_rcnn_torchvision_checkpoints.pth",
            },
        },
    }
    threading.Thread(target=sender, args=(config,)).start()


def sender(config: dict):
    sleep(SLEEP_TIME)
    manager.push_message(config)


if __name__ == "__main__":
    run_queue()
    logger.info("큐에 메세지를 적재 완료했습니다.")
