import threading
from loguru import logger

from Qndxx import Qndxx


def schedule_start():
    laravel_session = ""
    qndxx = Qndxx(laravel_session)
    qndxx.login()
    qndxx.confirm()


def func():
    logger.info("schedule start")
    schedule_start()
    timer = threading.Timer(86400,func)
    timer.start()

timer = threading.Timer(0,func)
timer.start()