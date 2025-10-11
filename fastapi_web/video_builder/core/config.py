from dotenv import load_dotenv
import logging
from pathlib import Path
import os
from datetime import datetime

# Load environment variables - ye images ko online search kerne ke liye change kiya gaya hay 2025-09-03 13:30:24
load_dotenv()

# Setup logging to file and console
def base_dir():
    """
    Get the base directory of the project.
    returns: Path object of the base directory
    """
    return Path(__file__).resolve().parent.parent

def make_dir(addresses: list) -> Path:
    """
    Create directories based on the provided list of addresses.
    requires: list of directory names (str)
    returns: Path object of the created directory
    """
    full_path = base_dir() / Path(*addresses)
    full_path.mkdir(parents=True, exist_ok=True)
    return full_path

def gen_user_base_logs(user_name) -> Path:
    """
    Generate a base logs directory for a specific user.
    requires: user_name (str)
    returns: Path object of the user's logs directory
    """
    path = make_dir(['logs', user_name])
    return path

def create_file_name(user_name: str = None, file_name: str = None, address: str = None, ext: str = None) -> Path:
    """
    Create a file name with the given parameters.
    requires: file_name (str), address (str), ext (str, required)
    returns: Path object of the created file name
    """
    if user_name is None or user_name.strip() == '':
        raise ValueError("User name 'user_name' is required.")
    if ext is None or ext.strip() == '':
        raise ValueError("File extension 'ext' is required.")
    if not file_name:
        file_name = datetime.now().strftime('%Y_%b').lower()
    if not address:
        address = base_dir() / 'outputs'
    else:
        address = base_dir() / address
    address.mkdir(parents=True, exist_ok=True)
    return address / f"{file_name}.{ext}"

class LoggerConfig:
    def __init__(self, user_name='custom_name', log_user='bilal'):
        self.logger = logging.getLogger(__name__)
        self.logger.propagate = False  # Prevent duplicate logs if root logger is configured elsewhere

        log_file = create_file_name(user_name=user_name, address=gen_user_base_logs(log_user), ext='log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)

        # Avoid adding handlers multiple times
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def set_debug(self):
        self.logger.setLevel(logging.DEBUG)

    def set_info(self):
        self.logger.setLevel(logging.INFO)

    def set_warning(self):
        self.logger.setLevel(logging.WARNING)

    def set_error(self):
        self.logger.setLevel(logging.ERROR)

    def set_warn(self):
        self.logger.setLevel(logging.WARN)

    def get_logger(self):
        return self.logger
    

