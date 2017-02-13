import os
import os.path
import shutil
import stat
import sys
import time
import traceback
from threading import Thread
from threading import Timer

from logic.cmd_line_consts import Actions
from logic.data.vid_file_data_factory import get_vid_file_data
from logic.logic_defs import IVideoOrganizer, workers_lock
from new_downloads_handler import NewDownloadsHandler
from notifier import Notifier
from subtitles.subtitle_manager import SubtitleManager
from utils.utilities import is_vid_file, capitalize_first_letters


class VideoOrganizer(IVideoOrganizer):
    def process(self, path, is_new_download=False):
        if os.path.isdir(path):
            for _file in os.listdir(path):
                self.process(os.path.join(path, _file), is_new_download)
        else:
            self.process_video(os.path.dirname(path), os.path.basename(path), is_new_download)

    def process_video(self, directory, file_name, is_new_download):
        print('---- Working on ' + file_name)
        # First check if this is actually a video file
        if not is_vid_file(file_name):
            print('---- Not supporting movie files yet: ' + file_name)
            return

        # Capitalize First letters of every word
        file_name = capitalize_first_letters(directory, file_name)

        # Parse the information from the file name and return an object representing it.
        vid_file_data = get_vid_file_data(directory, file_name, self.config_data)

        # Make sure TV file is up to format
        vid_file_data.rename_to_format()

        if is_new_download:
            # This should happen only once per video
            self.notifier.add_downloaded_file(vid_file_data)

        # Download subtitles for TV show
        result = self.subtitleManager.download_subtitles(vid_file_data)
        if result:
            # Move files and associates to proper location
            vid_file_data.move_to_target_directory()
            # Add to Notifier as ready episode
            self.notifier.add_ready_file(vid_file_data)
        else:
            # Add to Notifier as in staging episode
            self.notifier.add_staging_file(vid_file_data)

    def scan_thread(self):
        if not self.run:
            return
        try:
            print('-- Scanner Thread initiated --')
            # Lock - so both threads won't accidetnly work on the same file/s
            workers_lock.acquire()

            # Scan all files in working dir and see if we can make any ready
            for _file in os.listdir(self.working_dir):
                path = os.path.join(self.working_dir, _file)
                if os.path.isdir(path):
                    # If it is a directory we check if it is empty - if it is - we delete it.
                    if len(os.listdir(path)) == 0:
                        # If the file is read only we remove the read only flag as we are about to delete it
                        if not os.access(path, os.W_OK):
                            os.chmod(path, stat.S_IWUSR)
                        # Remove it
                        shutil.rmtree(path)
                # Process the file/directory
                self.process(os.path.join(self.working_dir, _file))

            # Send Notification (email) if there is any new news to update
            self.notifier.send_notifications()

            # Schedule the next scan
            self.scanThread = Timer(self.scanIntervalSec, self.scan_thread)
            self.scanThread.start()

            # Release the lock - so the worker can work if it needs to
            workers_lock.release()
            print('-- Scanner Thread terminated --')
        except Exception:
            print('-- ERROR: Exception raised in scanner thread')
            traceback.print_exc(file=sys.stdout)
            print('-' * 60)

    def start_fully(self):
        # Start new downloads listener
        self.new_downloads_handler.start()

        # Start Scanner Thread
        self.scanThread.start()

        while True:
            try:
                time.sleep(30)
            except Exception:
                self.stop()
                break

    def scan_dir(self):
        print('-- Scanning Directory ' + self.working_dir)
        self.process(self.working_dir)
        self.notifier.send_notifications()
        print('-- Scan completed.')

    def start(self):
        action = self.config_data['action']

        action_map = {
            Actions.full.name: self.start_fully,
            Actions.init_dir.name: self.new_downloads_handler.init_dir,
            Actions.scan_dir.name: self.scan_dir,
        }

        action_func = action_map[action]
        action_func()

    def stop(self):
        self.run = False
        self.new_downloads_handler.stop()

    def __init__(self, config_data):
        self.config_data = config_data
        self.subtitleManager = SubtitleManager(config_data)
        self.working_dir = config_data['WorkingDirectory']
        self.downloadDir = config_data['DownloadDirectory']
        self.scanIntervalSec = config_data['ScanIntervalSec']
        self.notifier = Notifier(config_data)
        self.scanThread = Thread(target=self.scan_thread)
        self.new_downloads_handler = NewDownloadsHandler(self, self.downloadDir, self.working_dir)
        self.run = True
