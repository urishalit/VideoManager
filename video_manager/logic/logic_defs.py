import threading

# Lock so Scan Thread and worker thread won't work together.
from abc import ABCMeta, abstractmethod

workers_lock = threading.Lock()


class IVideoOrganizer(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def process_video(self, directory, file_name, is_new_download):
        pass
