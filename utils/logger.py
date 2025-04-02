import os
import logging


if not os.path.exists('logs'):
    os.makedirs('logs', exist_ok=True)
    os.makedirs('logs/submissions', exist_ok=True)
    

# Configure logging
LOG_FILE="logs/app.log"
USER_LOG_FILE="logs/submissions/users.log"
AI_LOG_FILE="logs/submissions/ai.log"


def get_logger(name:str, log_file : str):
    """
    Get a logger with the specified name.
    
    Args:
        name (str): The name of the logger.
        
    Returns:
        logging.Logger: The logger instance.
    """

    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

        stream_handler = logging.StreamHandler()
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
        logger.addHandler(stream_handler)
    return logger