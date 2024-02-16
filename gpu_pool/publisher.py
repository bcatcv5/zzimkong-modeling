import threading
from typing import Final
from support.queue_handler import QueueHandler
from utils.time_ckecker import sleep
from logger import get_logger
from ast import literal_eval
import argparse
# import str2bool

SLEEP_TIME: Final = 1
manager = QueueHandler()
logger = get_logger("train")

CONFIG_INDEX: Final = 1
DECODE_FORMAT: Final = "utf-8"

def convert_to_dict(config) -> dict:
    # byte_config: bytes = config[CONFIG_INDEX]
    decoded_config: str = config.decode(DECODE_FORMAT)
    return literal_eval(decoded_config)


def id_counter(arg):
    if manager.exists("counter") == 0:
        counter = {
            "furniture": 0,
            "space": 0
        }
        threading.Thread(target=sender_counter, args=(counter,)).start()

    sleep(SLEEP_TIME)
    counter = manager.get("counter")
    counter = convert_to_dict(counter) # dict
    if arg == "true": #TODO: str2bool로 변경필요
        counter["furniture"] = int(counter["furniture"]) + 1
    elif arg == "false": # TODO: str2bool로 변경
        counter["space"] = int(counter["space"]) + 1
    
    threading.Thread(target=sender_counter, args=(counter,)).start()
    return counter


def run_queue(args) -> None:
    """메세지 큐에 메세지 삽입"""
    counter = id_counter(args.objectType) # 몇번째 key인지 확인

    # config = {
    #     "arch": {"type": "CustomModel", "args": {"num_classes": 11}},
    #     "data_loader": {
    #         "type": "CustomDataLoader",
    #         "args": {"batch_size": 3, "shuffle": False, "num_workers": 2},
    #     },
    #     "dataset": {
    #         "type": "CustomDataset",
    #         "args": {
    #             "annotation": "../dataset/train.json",
    #             "data_dir": "../dataset",
    #             "resize": 1024,
    #         },
    #     },
    #     "trainer": {
    #         "type": "CustomTrainer",
    #         "args": {
    #             "epochs": 2,
    #             "save_path": "/data/ephemeral/home/level2-objectdetection-cv-05/live/checkpoints/faster_rcnn_torchvision_checkpoints.pth",
    #         },
    #     },
    # }
    config = {
        "id": 2,
        "objectType": False,
        "src": "Room3.mp4"
    }

    threading.Thread(target=sender, args=(config, counter,)).start()


def sender(config: dict, counter):
    sleep(SLEEP_TIME)
    manager.push_message(config, counter)

def sender_counter(config: dict):
    sleep(SLEEP_TIME)
    manager.push_counter(config)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--objectType',
                        type=str, # TODO str2bool 변경할 것
                        help='(Required) object type. true: furniture, false:space')

    # Parse arguments
    args = parser.parse_args()
    run_queue(args)
    logger.info("큐에 메세지를 적재 완료했습니다.")
