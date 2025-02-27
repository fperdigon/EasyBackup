# ============================================================
#
#  Easy backup
#  Logger
#
#  author: Francisco Perdigon Romero
#  email: fperdigon88@gmail.com
#  github id: fperdigon
#
# ===========================================================

import logging
from pathlib import Path
import os
import datetime

# Create the logs path
logs_path = f"{Path(__file__).parent.parent}/logs/"
if os.path.exists(logs_path) and os.path.isdir(logs_path):
    pass
else:
    os.makedirs(logs_path)

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the base logging level

# Create a file handler
date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
file_handler = logging.FileHandler(f"{logs_path}/{date_str}_easybackup_app.log", mode="a")  # Log to a file in append mode
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")  # Include %(asctime)s
file_handler.setFormatter(file_formatter)

# Create a console handler
console_handler = logging.StreamHandler()  # Log to the console
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")  # Include %(asctime)s
console_handler.setFormatter(console_formatter)

# Add handler to the logger (avoid duplicate handlers)
if not logger.hasHandlers():
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)