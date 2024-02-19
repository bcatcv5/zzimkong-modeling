from typing import Final
from support.queue_handler import QueueHandler
from utils.subprocessor import *
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
SUCCESS_CODE: Final = 0


def handle_receive_process() -> None:
    """메세지 큐를 이용한 모델 학습 반복"""

    while True:
        logger.info("메세지를 대기하는 중입니다.")
        select_process()
        sleep(SLEEP_TIME)


def select_process(): # TODO: 서버마다 담당한 프로세스만 수행 (이외는 주석 처리할 것)
    # TODO GPU 가용 공간 체크하고 train process 수행할지

    # for gcp server
    train_space_process()

    # for 4090 server
    # train_furniture_process()


def getErrorMessage(log):
    return log.stderr.read().decode()


def train_space_process() -> None:
    """큐에서 메세지를 추출하여 공간 모델 학습 수행"""
    # TODO config 받았다는 메시지 수신 시 웹 서버로 전송 api1
    # r = request.post => r.status_code 201일 때만 학습 진행
    # TODO 201 이외의 경우 예외 처리 어떻게 할지 (aistage 사용 시 문제가 될 수 있음)
    config: bytes = handler.pop_message_space()

    if config is not None:
        command = construct_config(config, env.TRAIN_SPACE_PATH)
        logger.info("학습 중 입니다.")
        # git_synchronize()

        # train_log = train(command)
        train_log = handle_setup(command)
        
        if train_log.returncode != SUCCESS_CODE:
            logger.error(getErrorMessage(train_log))
            logger.info("학습 중 에러 발생 log를 확인하세요.")
            # TODO 에러 발생 시 status, 해당 config를 웹 서버에 전달 api2
            # status => status, status_message
            # 1. OOM => docker 쓰는 서버는 docker안에서 consumer 여러개 돌림
            # 2. no output file => 추론 서버 용량 부족, 서버 다운
            # NOTE 입력 데이터 오류
            # TODO ply 전송 실패 예외 처리
            # api 호출 코드
        else:
            logger.info(getErrorMessage(train_log))
            logger.info("학습 완료입니다.")
            # TODO status, status_message 웹 서버에 전달


def train_furniture_process() -> None:
    """큐에서 메세지를 추출하여 가구 모델 학습 수행"""
    config: bytes = handler.pop_message_furniture()

    if config is not None:
        command = construct_config(config, env.TRAIN_FURNITURE_PATH)

        logger.info("학습 중 입니다.")
        # git_synchronize()

        # train_log = train(command)
        train_log = handle_setup(command)
        
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


if __name__ == "__main__":
    handle_receive_process()