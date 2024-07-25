import logging
import datetime

def setup_logging(log_filename="file_log.txt"):
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_filename, filemode='a')

def log_file_completion(filename, status):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("file_log.txt", 'a') as log_file:
        log_file.write(f"Filename: {filename}, Timestamp: {timestamp}, Status: {status} , \n")
