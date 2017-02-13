import os
import os.path
import pickle
import shutil
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from logic.logic_defs import workers_lock
from utils.file_listener import IFileChangeRecipient, FileListener

DOWNLOAD_DIR_FILES_LIST_FILE_NAME = 'DownloadDirFiles'


class NewDownloadsHandler(IFileChangeRecipient):
    def __init__(self, organizer, download_dir, working_dir, scan_event):
        self.download_dir = download_dir
        self.working_dir = working_dir
        self.organizer = organizer
        self.file_listener = FileListener(self.download_dir, self)
        self.run = True
        self.scan_event = scan_event
        self.executor = ThreadPoolExecutor(max_workers=3)

    def start(self):
        # Start file listener
        self.file_listener.start()

        # Check if there are new files in the Download directory since last time
        self.check_for_new_files_since_last_time()

    def on_file_change(self, file_path, action):
        print('-- ' + file_path + ' ' + action)
        self.executor.submit(self.worker_thread, file_path)

    @staticmethod
    def save_download_dir_file_list(files):
        with open(os.path.join(os.getcwd(), DOWNLOAD_DIR_FILES_LIST_FILE_NAME), 'wb') as h:
            pickle.dump(files, h)

    @staticmethod
    def get_download_dir_file_list():
        try:
            with open(os.path.join(os.getcwd(), DOWNLOAD_DIR_FILES_LIST_FILE_NAME), 'rb') as h:
                return pickle.load(h)
        except Exception:
            return []

    def init_dir(self):
        print('-- Directory: ' + self.download_dir)
        files = os.listdir(self.download_dir)
        self.save_download_dir_file_list(files)
        print('-- Directory contents saved')

    def check_for_new_files_since_last_time(self):
        # Check if there are new files in the Download directory
        curr_files = os.listdir(self.download_dir)
        prev_files = self.get_download_dir_file_list()
        # Get the difference in the files image in the download directory
        diff_files = list(set(curr_files) - set(prev_files))
        for _file in diff_files:
            self.on_file_change(os.path.join(self.download_dir, _file), 'Created')
        # Save the current image of the files
        self.save_download_dir_file_list(curr_files)

    def stop(self):
        self.run = False
        self.file_listener.stop()

    def worker_thread(self, path):
        try:
            # The worker is considered a reader as it moves one file from the download dir to the workdir without
            # touching other files, therefore many worker threads can work simultaneously
            workers_lock.reader_acquire()
            if not self.run:
                return

            print('-- Worker Thread initiated --')
            # Update directory listing of files
            self.init_dir()

            if self.working_dir != self.download_dir:
                new_path = os.path.join(self.working_dir, os.path.basename(path))
                print('---- Copying ' + path + ' to ' + new_path)
                if os.path.isdir(path):
                    shutil.copytree(path, new_path)
                elif os.path.isfile(path):
                    shutil.copyfile(path, new_path)

                print('---- Notifying scanner of new file')
                self.scan_event.set()
            print('-- Worker Thread terminated --')
        except Exception:
            print('-- ERROR: Exception raised in worker thread')
            traceback.print_exc(file=sys.stdout)
            print('-' * 60)
        finally:
            workers_lock.reader_release()
