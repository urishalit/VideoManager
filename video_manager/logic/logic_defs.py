import threading

# Lock so Scan Thread and worker thread won't work together.
workersLock = threading.Lock()


class IVideoOrganizer:
    def ProcessVideo(self, dir, file, isNewDownload):
        raise NotImplementedError("Should have implemented this")
