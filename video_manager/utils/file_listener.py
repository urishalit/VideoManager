import os
import os.path
import time
import win32file
from abc import ABCMeta, abstractmethod
from threading import Thread

import win32con

FILE_ACTIONS = {
    1: 'Created',
    2: 'Deleted',
    3: 'Updated',
    4: 'Renamed from something',
    5: 'Renamed to something'
}

FILE_LIST_DIRECTORY = 0x0001
STOP_FILE = 'STOP_LISTENER_FILE'


class IFileChangeRecipient(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def on_file_change(self, file_path, action):
        pass


class FileListener(object):
    def __init__(self, path_to_watch, sink=None):
        self.run = True
        self.path_to_watch = path_to_watch
        self.sink = sink
        self.listener_thread = None
        if not os.path.isdir(self.path_to_watch):
            msg = '-- ERROR: Download Directory does not exist (' + self.path_to_watch + ')'
            raise Exception(msg)

    def listener_thread(self):
        hDir = win32file.CreateFile(self.path_to_watch,
                                    FILE_LIST_DIRECTORY,
                                    win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
                                    None,
                                    win32con.OPEN_EXISTING,
                                    win32con.FILE_FLAG_BACKUP_SEMANTICS,
                                    None)

        while self.run:
            # wait for change (blocking)
            results = win32file.ReadDirectoryChangesW(hDir,
                                                      1024,
                                                      True,
                                                      win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                                                      win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                                                      win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                                                      win32con.FILE_NOTIFY_CHANGE_SIZE |
                                                      win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                                                      win32con.FILE_NOTIFY_CHANGE_SECURITY,
                                                      None,
                                                      None)

            for action, file in results:
                if file == STOP_FILE:
                    break
                if action == 1:
                    file_path = os.path.join(self.path_to_watch, file)
                    # TODO - Change to real logic!
                    time.sleep(1)
                    self.sink.on_file_change(file_path, FILE_ACTIONS.get(action, 'Unknown'))

    def start(self):
        self.listener_thread = Thread(target=self.listener_thread)
        self.listener_thread.start()

    def stop(self):
        self.run = False
        stop_file = os.path.join(self.path_to_watch, STOP_FILE)
        with open(stop_file, 'w') as f:
            f.write('stop')

        os.remove(stop_file)


if __name__ == '__main__':
    path = r'C:\Users\Uri\Downloads\Torrents\Completed\Siboni\Test'
    FileListener(path).start()
