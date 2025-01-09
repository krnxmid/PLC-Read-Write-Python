"""This is logging file"""
import os
import logging
from logging.handlers import TimedRotatingFileHandler

log_level = logging.INFO

# FORMAT = '%(asctime)-15s %(levelname)-8s %(m
log = logging.getLogger()

# checking and creating logs directory here
if not os.path.isdir("./logs"):
    log.info("[-] logs directory doesn't exists")
    try:
        os.mkdir("./logs")
        log.info("[+] Created logs dir successfully")
    except Exception as e:
        log.error(f"[-] Can't create dir logs Error: {e}")

# fileHandler = TimedRotatingFileHandler(os.path.join(dir_name, f'logs/app_log'),
#                                        when='midnight', interval=1)
# fileHandler.setFormatter(logFormatter)
# fileHandler.suffix = "%Y-%m-%d.log"
# log.addHandler(fileHandler)

# consoleHandler = logging.StreamHandler()
# consoleHandler.setFormatter(logFormatter)
# log.addHandler(consoleHandler)
# log.setLevel(log_level)
