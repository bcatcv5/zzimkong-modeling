from typing import Final
from support.queue_handler import QueueHandler
from utils.subprocessor import train
from utils.time_ckecker import sleep
import env
from logger import get_logger
import git

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
        train_process()
        sleep(SLEEP_TIME)


def train_process() -> None:
    """큐에서 메세지를 추출하여 모델 학습 수행"""
    config: bytes = handler.pop_message()

    if config is not None:
        command = construct_config(config)

        logger.info("학습 중 입니다.")
        git_synchronize()

        train_log = train(command)
        if train_log.stderr:
            logger.info("학습 중 에러 발생 log를 확인하세요.")
            logger.error(train_log.stderr)
            logger.info(train_log.stdout)
        else:
            logger.info("학습 완료입니다.")


def git_synchronize():
    """원격에 배포된 코드 동기화"""
    repo = git.Repo.init(path=env.ROOT_PATH)
    repo.git.checkout(WORKING_BRANCH_NAME)
    repo.remotes.origin.pull()


def convert_to_string(config) -> str:
    byte_config: bytes = config[CONFIG_INDEX]
    decoded_config: str = byte_config.decode(DECODE_FORMAT)
    return decoded_config


def construct_config(config) -> str:
    """메세지 추출 후 모델 학습 포멧에 맞게 조정

    Args:
        config (_type_): 큐에서 추출한 메세지

    Returns:
        _type_: 모델 학습 sub process 포멧
    """
    decoded_config = convert_to_string(config)
    return f"python {env.ROOT_PATH}/{env.TRAIN_PATH} -dc '{decoded_config}'"


if __name__ == "__main__":
    handle_receive_process()
