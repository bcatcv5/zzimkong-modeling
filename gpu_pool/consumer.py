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
from mysql.connector import Error
import mysql
from datetime import datetime

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

# def id(config):
#     url = "https://zzimkong.ggm.kr/inference/recived"
#     data = {"id": config["id"],
#             "server": env.SERVER_IP}
#     headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWRtaW4iLCJpYXQiOjE3MDkwMTE5NDIsImV4cCI6MTcxNzY1MTk0Mn0.GDqzeLFwWziLvFzRPNJ0AsJiy4l2UwzAy74Cg27wY5A"}
#     r = requests.post(url, headers=headers, data=data, verify=False)
#     return r.status_code


def changeStatus(status, message, id, store_file_url = None, thumbnail_file_url = None, infer_start_time = None, infer_end_time = None):
    connection = None
    
    try:
        connection = mysql.connector.connect(
            host='34.64.80.157',
            database='ZZIMKONG',
            user='root',
            password='NewSt@rt!70'
        )

        if connection.is_connected():
            if(store_file_url == None and thumbnail_file_url == None):
                insert_query = f"UPDATE space_model_result SET status_code = '{status}', status_message = '{message}' WHERE message_id = {id};"
            elif(store_file_url != None):
                insert_query = f"UPDATE space_model_result SET status_code = '{status}', status_message = '{message}', store_file_url = '{store_file_url}' WHERE message_id = {id};"
            elif(thumbnail_file_url != None):
                insert_query = f"UPDATE space_model_result SET thumbnail_file_url = '{thumbnail_file_url}' WHERE message_id = {id};"
            elif(infer_start_time != None):
                insert_query = f"UPDATE space_model_result SET learned_date = '{infer_start_time}' WHERE message_id = {id};"
            elif(infer_end_time != None):
                insert_query = f"UPDATE space_model_result SET finished_date = '{infer_end_time}' WHERE message_id = {id};"
                
            cursor = connection.cursor()
            cursor.execute(insert_query)
            connection.commit()
            print("space_model_result 테이블에 메시지를 입력하였습니다.")

    except Error as e:
        print("MySQL에 연결되지 않았습니다.", e)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL 연결을 끊었습니다.")


def select_process(): # NOTE: 서버마다 담당한 프로세스만 수행 (이외는 주석 처리할 것)
    # TODO GPU 가용 공간 체크하고 train process 수행할지

    # for gcp server
    train_space_process()

    # for 4090 server
    # train_furniture_process()


def getErrorMessage(log):
    return log.stderr.read()


def train_space_process() -> None:
    """큐에서 메세지를 추출하여 공간 모델 학습 수행"""
    config: bytes = handler.pop_message_space()

    if config is not None:
        command = construct_config(config, env.TRAIN_SPACE_PATH)
        logger.info("학습 중 입니다.")
        # git_synchronize()

        config = json.loads(command.split(' \'')[1][:-1])

        # print(id(config))
        # if id(config) == 201: # 웹 서버와 정상 통신
        #     # train_log = train(command)
        #     train_log = handle_setup(command)
            
        #     if train_log.returncode != SUCCESS_CODE:
        #         logger.error(getErrorMessage(train_log))
        #         logger.info("학습 중 에러 발생 log를 확인하세요.", config["id"], infer_end_time=str(datetime.now()))
        #     else:
        #         logger.info(getErrorMessage(train_log))
        #         logger.info("학습 완료입니다.")
        #         changeStatus("FINISH", "기다려주셔서 감사합니다. 재구성 결과를 확인해보세요 :)", config["id"], infer_end_time=str(datetime.now()))
        train_log = handle_setup(command)
        
        if train_log.returncode != SUCCESS_CODE:
            logger.error(getErrorMessage(train_log))
            logger.info("학습 중 에러 발생 log를 확인하세요.", config["id"], infer_end_time=str(datetime.now()))
        else:
            logger.info(getErrorMessage(train_log))
            logger.info("학습 완료입니다.")
            changeStatus("FINISH", "기다려주셔서 감사합니다. 재구성 결과를 확인해보세요 :)", config["id"], infer_end_time=str(datetime.now()))



def train_furniture_process() -> None:
    """큐에서 메세지를 추출하여 가구 모델 학습 수행"""
    config: bytes = handler.pop_message_furniture()

    if config is not None:
        command = construct_config(config, env.TRAIN_FURNITURE_PATH)

        logger.info("학습 중 입니다.")
        # git_synchronize()

        # print(id(config))
        # if id(config) == 201: # 웹 서버와 정상 통신
        #     # train_log = train(command)
        #     train_log = handle_setup(command)
            
        #     if train_log.returncode != SUCCESS_CODE:
        #         logger.error(getErrorMessage(train_log))
        #         logger.info("학습 중 에러 발생 log를 확인하세요.", config["id"], infer_end_time=str(datetime.now()))
        #     else:
        #         logger.info(getErrorMessage(train_log))
        #         logger.info("학습 완료입니다.")
        #         changeStatus("FINISH", "기다려주셔서 감사합니다. 재구성 결과를 확인해보세요 :)", config["id"], infer_end_time=str(datetime.now()))
        train_log = handle_setup(command)
        
        if train_log.returncode != SUCCESS_CODE:
            logger.error(getErrorMessage(train_log))
            logger.info("학습 중 에러 발생 log를 확인하세요.")
        else:
            logger.info(getErrorMessage(train_log))
            logger.info("학습 완료입니다.")
            changeStatus("FINISH", "기다려주셔서 감사합니다. 재구성 결과를 확인해보세요 :)", config["id"], infer_end_time=str(datetime.now()))


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
