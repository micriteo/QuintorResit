import time
import os

import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from src.base_application import api_server_ip
from src.base_application.utils import check_mt940_file, parse_mt940_file


def parse_file(file):
    """Parse the selected MT940 files and save the results as JSON files."""
    # Check MT940 file
    if check_mt940_file(file):
        # Save to NoSQL DB
        url = api_server_ip + '/api/mt940'
        json_data = parse_mt940_file(file)
        print(json_data)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=json_data, headers=headers)
        # Save to SQL DB
        url = api_server_ip + '/api/insertmtsql'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=json_data, headers=headers)


print("Running folder listener")


class FolderListener(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.processed_files = set()

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            if file_path not in self.processed_files:
                self.processed_files.add(file_path)
                print(f"New file created: {file_path}")
                parse_file(file_path)


if __name__ == "__main__":
    folder_path = "../listener_folder"
    event_handler = FolderListener()

    # Initial scan of the folder
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_path not in event_handler.processed_files:
                event_handler.processed_files.add(file_path)
                print(f"Existing file found: {file_path}")
                parse_file(file_path)

    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
