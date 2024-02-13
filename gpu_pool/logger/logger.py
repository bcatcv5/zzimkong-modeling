import logging
import logging.config
from pathlib import Path
import json
from collections import OrderedDict


def get_logger(name: str) -> logging:
    """로거를 반환한다.

    Args:
        name (_type_): 로거 이름

    Returns:
        _type_: 셋팅 완료한 로거
    """
    setup_logging()
    logger = logging.getLogger(name)

    return logger


def setup_logging(log_config="logger/logger_config.json", default_level=logging.INFO):
    """로거 셋업

    Args:
        log_config (str, optional): _description_. 셋팅 json 경로".
        default_level (_type_, optional): _description_. Default 레벨
    """

    log_config = Path(log_config)
    if log_config.is_file():
        config = read_json(log_config)
        logging.config.dictConfig(config)
    else:
        print("config 파일을 찾을 수 없습니다. {}.".format(log_config))
        logging.basicConfig(level=default_level)


def read_json(cfg_fname: str):
    fname = Path(cfg_fname)
    with fname.open("rt") as handle:
        return json.load(handle, object_hook=OrderedDict)
