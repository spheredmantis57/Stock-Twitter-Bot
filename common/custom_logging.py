from inspect import currentframe
from os import path
import logging

LOG_FILE = "log.txt"

def basicConfig(file_name):
    global LOG_FILE
    LOG_FILE = file_name
    logging.basicConfig(
        level=logging.INFO,
        format='\n%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=LOG_FILE,
        filemode='a'
    )

def custom_log(message):
    current_frame = currentframe().f_back
    file_path = current_frame.f_code.co_filename
    line_number = current_frame.f_lineno

    logging.info(f"File: {file_path}, Line: {line_number}\n\t{message}")
