import logging
import os


class LoggerClass:
    """
    Logger class to log to a file and console output
    """

    def setup(self, path_save, stage="training"):
        """
        Create a log file to record the experiment's logs


        returns:
            logger (obj): logger that record logs
        """
        # check if the file exist
        self.log_file = os.path.join(path_save, f"{stage}.log")

        # set logging format
        console_logging_format = "%(message)s"
        file_logging_format = "%(asctime)s: %(levelname)s: %(message)s"

        # configure logger
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger()

        # Reset the logger.handlers if it already exists.
        if logger.handlers:
            logger.handlers = []

        handler = self.file_log(file_logging_format)
        logger.addHandler(handler)

        consoleHandler = self.console_log(console_logging_format)
        logger.addHandler(consoleHandler)
        return logger

    def file_log(self, logging_format, level=logging.DEBUG):
        # create a file log
        handler = logging.FileHandler(filename=self.log_file)
        handler.setLevel(level)
        formatter = logging.Formatter(logging_format)
        handler.setFormatter(formatter)
        return handler

    def console_log(self, logging_format, level=logging.INFO):
        # console log
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(level)
        formatter = logging.Formatter(logging_format)
        consoleHandler.setFormatter(formatter)
        return consoleHandler

    def __call__(self, path_save, stage="training"):
        return self.setup(path_save, stage=stage)
