import os
import os.path
import shutil
import stat
import threading
import time
import traceback
from threading import Thread

from logic.cmd_line_consts import Actions
from logic.data.vid_file_data_factory import get_vid_file_data
from logic.logic_defs import IVideoOrganizer, workers_lock
from new_downloads_handler import NewDownloadsHandler
from notifier import Notifier
from subtitles.subtitle_manager import SubtitleManager
from utils.utilities import is_vid_file, capitalize_first_letters, unrar_videos, remove_non_video_files_from_dir


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

        try:
            # Parse the information from the file name and return an object representing it.
            vid_file_data = get_vid_file_data(directory, file_name, self.config_data)
        except TypeError:
            print('---- Could not parse and handle file %s' % file_name)
            return

        # Make sure TV file is up to format
        vid_file_data.rename_to_format()

        if is_new_download:
            # This should happen only once per video
            self.notifier.add_downloaded_file(vid_file_data)

        # Download subtitles for TV show
        result = self.subtitle_manager.download_subtitles(vid_file_data)
        if result:
            # Move files and associates to proper location
            vid_file_data.move_to_target_directory()
            # Add to Notifier as ready episode
            self.notifier.add_ready_file(vid_file_data)
        else:
            # Add to Notifier as in staging episode
            self.notifier.add_staging_file(vid_file_data)

    def scan_thread(self):
        while self.run:
            try:
                print('-- Scanner Thread: Starting loop --')
                # Lock - so both threads won't accidence work on the same file/s
                # The scan dir is a writer as it touches all files and moves them around, no new file can be handled in
                # the midst of a scan
                workers_lock.writer_acquire()

                # Scan all files in working dir and see if we can make any ready
                for _file in os.listdir(self.working_dir):
                    path = os.path.join(self.working_dir, _file)
                    if os.path.isdir(path):
                        unrar_videos(path)
                        remove_non_video_files_from_dir(path)

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

                print('-- Scanner Thread: loop ended --')
            except Exception:
                print('-- ERROR: Exception raised in scanner thread')
                traceback.print_exc()
                print('-' * 60)
            finally:
                workers_lock.writer_release()

            # Schedule the next scan
            self.scan_event.wait(timeout=self.scan_interval_sec)
            self.scan_event.clear()

    def start_fully(self):
        # Start new downloads listener
        self.new_downloads_handler.start()

        # Start Scanner Thread
        self.scan_thread_obj.start()

        while True:
            try:
                time.sleep(30)
            except Exception:
                traceback.print_exc()
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
        self.subtitle_manager = SubtitleManager(config_data)
        self.working_dir = config_data['WorkingDirectory']
        self.download_dir = config_data['DownloadDirectory']
        self.scan_interval_sec = config_data['ScanIntervalSec']
        self.notifier = Notifier(config_data)
        self.scan_event = threading.Event()
        self.scan_thread_obj = Thread(target=self.scan_thread)
        self.new_downloads_handler = NewDownloadsHandler(self, self.download_dir, self.working_dir,
                                                         self.scan_event)
        self.run = True
