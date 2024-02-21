from typing import Final
from support.queue_handler import QueueHandler
from utils.subprocessor import *
from utils.time_ckecker import sleep
import env
from logger import get_logger
import git
import sys
import requests
import json

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

def id(config):
    url = "https://zzimkong.ggm.kr/inference/recived"
    data = {"id": config["id"]}
    r = requests.post(url, data=data, verify=False)
    return r.status_code


def status(status, message, id):
    url = "https://zzimkong.ggm.kr/inference/status"
    data = {"status": status, "statusMessage": message, "id": id}
    r = requests.post(url, data=data, verify=False)


def select_process(): # NOTE: 서버마다 담당한 프로세스만 수행 (이외는 주석 처리할 것)
    # TODO GPU 가용 공간 체크하고 train process 수행할지

    # for gcp server
    train_space_process()

    # for 4090 server
    # train_furniture_process()

    # else: # NOTE 이외의 경우 예외 처리 어떻게 할지 (aistage 사용 시 문제가 될 수 있음)


def getErrorMessage(log):
    return log.stderr.read()


def train_space_process() -> None:
    """큐에서 메세지를 추출하여 공간 모델 학습 수행"""
    config: bytes = handler.pop_message_space()

    if config is not None:
        command = construct_config(config, env.TRAIN_SPACE_PATH)
        logger.info("학습 중 입니다.")
        # git_synchronize()

        # command -dc to config: str to dict
        # command: (str) python nerfstudio/pipe.py -dc '{"id":6,"objectType":false,"model":"nerfacto","src":"1708417256111.mov"}'
        # config: (dict) {"id":6,"objectType":false,"model":"nerfacto","src":"1708417256111.mov"}
        config = json.loads(command.split(' \'')[1][:-1])

        print(id(config))
        if id(config) == 201: # 웹 서버와 정상 통신
            # train_log = train(command)
            train_log = handle_setup(command)
            
            if train_log.returncode != SUCCESS_CODE:
                logger.error(getErrorMessage(train_log))
                logger.info("학습 중 에러 발생 log를 확인하세요.")
            else:
                logger.info(getErrorMessage(train_log))
                logger.info("학습 완료입니다.")
                status("success", "기다려주셔서 감사합니다. 재구성 결과를 확인해보세요 :)", config["id"])


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