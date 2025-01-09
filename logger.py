import logging
import os
from datetime import datetime

# Define the log directory
log_directory = '/home/admin/plc_monitoring/log'

# Create the log directory if it doesn't exist
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Get the current date and time
logging.getLogger('pika').setLevel(logging.CRITICAL)
current_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

# Define the log file name with date and time
log_file = os.path.join(log_directory, f'log {current_time}.txt')

# Log format to include date, time, log level, module, line number, and message
FORMAT = '%(asctime)s [%(levelname)s] %(module)-15s:%(lineno)-8s  %(message)s'

# Set up the logging configuration, ensuring handlers are only added once
log = logging.getLogger()
log.setLevel(logging.INFO)

# Check if the log already has handlers, to prevent double logging
if not log.hasHandlers():
    # Create the file handler with the dynamically named log file
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(FORMAT))
    log.addHandler(file_handler)

    # Create a stream handler for terminal output
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(FORMAT))
    log.addHandler(stream_handler)

# Test the logging configuration
log.info("Logger initialized successfully!")
