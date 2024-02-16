from typing import Final
from support.queue_handler import QueueHandler
from utils.subprocessor import train
from utils.time_ckecker import sleep
import env
from logger import get_logger
import git
import sys

SLEEP_TIME: Final = 0.5
CONFIG_INDEX: Final = 1
DECODE_FORMAT: Final = "utf-8"
WORKING_BRANCH_NAME: Final = "test"
handler = QueueHandler()
logger = get_logger("train")


def handle_receive_process() -> None:
    """메세지 큐를 이용한 모델 학습 반복"""

    while True:
        logger.info("메세지를 대기하는 중입니다.")
        listen_message()
        sleep(SLEEP_TIME)

def listen_message():
    confs = handler.pop_message()

    for c in confs[::-1]:
        c = c.decode(DECODE_FORMAT) # str
        if "space" in c:                    # NOTE 4090
            config = handler.get(c)
            return train_space_process(config)
        if "furniture" in c:                # NOTE: 4090 이외 서버, 4090은 space 우선 furniture 다음으로 수정할 것
            config = handler.get(c)
            return train_furniture_process(config)

def train_space_process(config) -> None:
    """큐에서 메세지를 추출하여 공간 모델 학습 수행"""
    # config: bytes = handler.pop_message()
    # print(config)

    if config is not None:
        command = construct_config(config, env.TRAIN_SPACE_PATH)
        # logger.info("학습 중 입니다.")
        # git_synchronize()

        train_log = train(command)
        print(train_log)
        sys.exit(1)
        # if train_log.stderr:
        #     logger.info("학습 중 에러 발생 log를 확인하세요.")
        #     logger.error(train_log.stderr)
        #     logger.info(train_log.stdout)
        # else:
        #     logger.info("학습 완료입니다.")


def train_furniture_process(config) -> None:
    """큐에서 메세지를 추출하여 가구 모델 학습 수행"""

    if config is not None:
        command = construct_config(config, env.TRAIN_FURNITURE_PATH)

        # logger.info("학습 중 입니다.")
        # # git_synchronize()

        # train_log = train(command)
        # if train_log.stderr:
        #     logger.info("학습 중 에러 발생 log를 확인하세요.")
        #     logger.error(train_log.stderr)
        #     logger.info(train_log.stdout)
        # else:
        #     logger.info("학습 완료입니다.")


# def git_synchronize():
#     """원격에 배포된 코드 동기화"""
#     repo = git.Repo.init(path=env.ROOT_PATH)
#     repo.git.checkout(WORKING_BRANCH_NAME)
#     repo.remotes.origin.pull()


def convert_to_string(config) -> str:
    # byte_config: bytes = config[CONFIG_INDEX]
    # decoded_config: str = byte_config.decode(DECODE_FORMAT)
    decoded_config: str = config.decode(DECODE_FORMAT)
    return decoded_config


def construct_config(config, train_path) -> str:
    """메세지 추출 후 모델 학습 포멧에 맞게 조정

    Args:
        config (_type_): 큐에서 추출한 메세지

    Returns:
        _type_: 모델 학습 sub process 포멧
    """
    decoded_config = convert_to_string(config)

    print(f"python {train_path} -dc '{decoded_config}'")
    return f"python {train_path} -dc '{decoded_config}'"

    # python train.py -dc '{"input": "input.txt"}' 

if __name__ == "__main__":
    handle_receive_process()
