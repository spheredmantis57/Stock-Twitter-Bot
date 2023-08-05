"""Module for custom logging
Uses the normal logging file but with filename and line number"""
from inspect import currentframe
import logging

def basic_config(file_name):
    """
    Wrapper for logging.basicConfig, where it is set up in the format I want
    while still allowing you to change the logging file

    Arguments:
    file_name (str): the name of the file to use for logging
    """
    logging.basicConfig(
        level=logging.INFO,
        format='\n%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=file_name,
        filemode='a'
    )

def custom_log(message):
    """custom logging that includes file name and line number"""
    current_frame = currentframe().f_back
    file_path = current_frame.f_code.co_filename
    line_number = current_frame.f_lineno

    message = f"File: {file_path}, Line: {line_number}\n\t{message}"
    logging.info(message)
