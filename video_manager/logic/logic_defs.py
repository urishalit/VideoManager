# Lock so Scan Thread and worker thread won't work together.
from abc import ABCMeta, abstractmethod

from utils.rw_lock import RWLock

workers_lock = RWLock()


class IVideoOrganizer(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def process_video(self, directory, file_name, is_new_download):
        pass
