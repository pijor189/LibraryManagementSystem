import logging


#  create a logger
logger = logging.getLogger("Library Logger")
logger.setLevel(logging.INFO)
# create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
# set the log format
log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(log_format)
# adding a handler to the logger
if not logger.handlers:
    logger.addHandler(console_handler)
