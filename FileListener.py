import os
import win32file
import win32con
import time
import pickle
import sys

# My files
from VideoOrganizer import VideoOrganizer

ACTIONS = {
	1 : "Created",
	2 : "Deleted",
	3 : "Updated",
	4 : "Renamed from something",
	5 : "Renamed to something"
}

FILE_LIST_DIRECTORY = 0x0001

# Name of file to save image of files in Download directory
DOWNLOAD_DIR_DILES_LIST_FILE_NAME = 'DownloadDirFiles'



class FileListener:
	def __init__(self, configData, start: bool):
		self.configData = configData
		self.pathToWatch = self.configData['DownloadDirectory']
		if not os.path.isdir(self.pathToWatch):
			print('-- ERROR: Download Directory does not exist')
			sys.exit()

		if start:
			self.videoOrganizer = VideoOrganizer(configData)

	def SaveDownloadDirFileList(self, files):
		with open(os.path.join(os.getcwd(), DOWNLOAD_DIR_DILES_LIST_FILE_NAME), 'wb') as h:
			pickle.dump(files, h)


	def GetDownloadDirFileList(self):
		try:
			with open(os.path.join(os.getcwd(), DOWNLOAD_DIR_DILES_LIST_FILE_NAME), 'rb') as h:
				return pickle.load(h)
		except:
			return []

	def CheckForNewFilesSinceLastTime(self):
		# Check if there are new files in the Download directory
		currFiles = os.listdir(self.pathToWatch)
		prevFiles = self.GetDownloadDirFileList()
		# Get the difference in the files image in the download directory
		diffFiles = list(set(currFiles) - set(prevFiles))
		for file in diffFiles:
			self.videoOrganizer.Organize(os.path.join(self.pathToWatch, file))
		# Save the current image of the files
		self.SaveDownloadDirFileList(currFiles)

	def Start(self):
		self.CheckForNewFilesSinceLastTime()
		
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

					print(filePath, ACTIONS.get (action, "Unknown"))
					# TODO - Change to real logic!
					time.sleep(1)

					self.videoOrganizer.Organize(filePath)

def main():
	path = r'C:\Users\Uri\Downloads\Torrents\Completed\Siboni\Test'
	FileListener(path).Start()

if __name__ == "__main__":
    main()

