import os
import win32file
import win32con
import time
import sys

from threading import Thread

FILE_ACTIONS = {
	1 : "Created",
	2 : "Deleted",
	3 : "Updated",
	4 : "Renamed from something",
	5 : "Renamed to something"
}

FILE_LIST_DIRECTORY = 0x0001

class IFileChangeRecipient:
	def OnFileChange(self, filePath, action):
		raise NotImplementedError("Should have implemented this")

class FileListener:
	def __init__(self, pathToWatch, sink: IFileChangeRecipient):
		self.pathToWatch = pathToWatch
		self.sink = sink
		if not os.path.isdir(self.pathToWatch):
			print('-- ERROR: Download Directory does not exist (' + self.pathToWatch + ')')
			raise

	def ListenerThread(self):
		hDir = win32file.CreateFile(self.pathToWatch,
									FILE_LIST_DIRECTORY,
									win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
									None,
									win32con.OPEN_EXISTING,
									win32con.FILE_FLAG_BACKUP_SEMANTICS,
									None)

		while 1:
			# wait for change (blocking)
			results = win32file.ReadDirectoryChangesW(hDir,
													  1024,
													  True,
													  win32con.FILE_NOTIFY_CHANGE_FILE_NAME | win32con.FILE_NOTIFY_CHANGE_DIR_NAME | win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES | win32con.FILE_NOTIFY_CHANGE_SIZE | win32con.FILE_NOTIFY_CHANGE_LAST_WRITE | win32con.FILE_NOTIFY_CHANGE_SECURITY,
													  None,
													  None)


			for action, file in results:
				if action == 1:
					filePath = os.path.join(self.pathToWatch, file)
					# TODO - Change to real logic!
					time.sleep(1)
					self.sink.OnFileChange(filePath, FILE_ACTIONS.get (action, "Unknown"))

	def Start(self):
		self.listenerThread = Thread(target = self.ListenerThread)
		self.listenerThread.start()

def main():
	path = r'C:\Users\Uri\Downloads\Torrents\Completed\Siboni\Test'
	FileListener(path).Start()

if __name__ == "__main__":
    main()

