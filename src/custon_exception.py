import traceback
import sys

class CustomException(Exception):
    def __init__(self, error_message: Exception, error_details: sys):
        self.error_message = error_message
        self.error_details = error_details

    def __str__(self):
        return self.error_message
    
    @staticmethod
    def get_detailed_error_message(error_message: Exception, error_details: sys) -> str:
        _, _, exc_tb = error_details.exc_info()
        line_number = exc_tb.tb_lineno
        file_name = exc_tb.tb_frame.f_code.co_filename
        error_message = f"Error occurred in script: [{file_name}] at line number: [{line_number}] error message: [{error_message}]"
        return error_message
