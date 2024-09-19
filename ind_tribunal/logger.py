import logging

class Logger:
    def __init__(self, log_file='app.log'):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)

    def log_success(self, message):
        self.logger.info(f"SUCCESS: {message}")

    def log_error(self, message):
        self.logger.error(f"ERROR: {message}")

    def log_debug(self, message):
        self.logger.debug(f"DEBUG: {message}")