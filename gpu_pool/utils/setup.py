import sys

sys.path.append("/data/ephemeral/home/level2-objectdetection-cv-05/gpu_pool/")

from subprocessor import handle_setup
from env import REDIS_SERVER_PORT, REDIS_SERVER_PASSWORD
from typing import Final
from logger import get_logger

INSTALL_REDIS_COMMAND: Final = "apt-get install redis-server && pip install redis"
SET_REDIS_CONFIG_COMMAND: Final = "redis-server /etc/redis/redis.conf"
RESTART_COMMAND: Final = """
    sudo chown redis:redis /var/log/redis/redis-server.log &&
    sudo chmod 660 /var/log/redis/redis-server.log &&
    sudo service redis-server restart
    """
SUCCESS_CODE: Final = 0
CONFIG_PATH: Final = "/etc/redis/redis.conf"

INSTALL_REDIS_FAIL_MESSAGE: Final = (
    "redis 설치 중 오류가 발생했습니다. log를 확인해 주세요, WARNING일 경우 설치 완료된 것입니다."
)
SET_CONFIG_FAIL_MESSAGE: Final = (
    "redis.conf 생성 중 오류가 발생했습니다. log를 확인해 주세요, WARNING일 경우 설치 완료된 것입니다."
)
INSTALL_REDIS_SUCCESS_MESSAGE: Final = "redis 설치 중 입니다."
MODIFY_CONFIG_MESSAGE: Final = f"""
        {CONFIG_PATH}의 92번 라인을 {REDIS_SERVER_PORT}로 수정해주세요.
        69번 라인을 bind 0.0.0.0로 수정해주세요.
        507번 라인을 {REDIS_SERVER_PASSWORD}로 수정해주세요.
        """
COMPLETE_CONFIG_MESSAGE: Final = "conf 파일을 수정한 후, 계속하려면 엔터키를 눌러주세요."
FINISH_MESSAGE: Final = "셋팅이 완료 되었습니다."
logger = get_logger("setup")


def setup():
    installQueueProcess()
    modifyConfigProcess()
    completeProcess()


def installQueueProcess():
    setup_log = handle_setup(INSTALL_REDIS_COMMAND)

    if setup_log.returncode != SUCCESS_CODE:
        logger.error(getErrorMessage(setup_log))
        logger.error(INSTALL_REDIS_FAIL_MESSAGE)
        raise Exception()
    else:
        logger.info(INSTALL_REDIS_SUCCESS_MESSAGE)


def modifyConfigProcess():
    config_log = handle_setup(SET_REDIS_CONFIG_COMMAND)

    if config_log.returncode != SUCCESS_CODE:
        logger.error(getErrorMessage(config_log))
        logger.error(SET_CONFIG_FAIL_MESSAGE)
        raise Exception()
    else:
        logger.info(MODIFY_CONFIG_MESSAGE)
        input(COMPLETE_CONFIG_MESSAGE)


def completeProcess():
    handle_setup(RESTART_COMMAND)
    logger.info(FINISH_MESSAGE)


def getErrorMessage(log):
    return log.stderr.read().decode()


if __name__ == "__main__":
    setup()
