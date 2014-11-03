import os
import os.path
import pickle
import shutil
import traceback
from threading import Thread

# My Files
from VidFileData import VidFileData
from FileListener import IFileChangeRecipient
from FileListener import FileListener
from LogicDefs import *

# Name of file to save image of files in Download directory
DOWNLOAD_DIR_DILES_LIST_FILE_NAME = 'DownloadDirFiles'

class NewDownloadsHandler(IFileChangeRecipient):
	def __init__(self, organizer: IVideoOrganizer, downloadDir, workingDir):
		self.downloadDir = downloadDir
		self.workingDir = workingDir
		self.organizer = organizer
		self.fileListener = FileListener(self.downloadDir, self)

	def Start(self):
		# Start file listener
		self.fileListener.Start()

		# Check if there are new files in the Download directory since last time
		self.CheckForNewFilesSinceLastTime()


	def OnFileChange(self, filePath, action):
		print("-- " + filePath + " " + action)
		thread = Thread(target = self.WorkerThread, args = (filePath, ))
		thread.start()

	def SaveDownloadDirFileList(self, files):
		with open(os.path.join(os.getcwd(), DOWNLOAD_DIR_DILES_LIST_FILE_NAME), 'wb') as h:
			pickle.dump(files, h)

	def GetDownloadDirFileList(self):
		try:
			with open(os.path.join(os.getcwd(), DOWNLOAD_DIR_DILES_LIST_FILE_NAME), 'rb') as h:
				return pickle.load(h)
		except:
			return []

	def InitDir(self):
		print('-- Directory: ' + self.downloadDir)
		files = os.listdir(self.downloadDir)
		self.SaveDownloadDirFileList(files)
		print('-- Directory contenets saved')

	def CheckForNewFilesSinceLastTime(self):
		# Check if there are new files in the Download directory
		currFiles = os.listdir(self.downloadDir)
		prevFiles = self.GetDownloadDirFileList()
		# Get the difference in the files image in the download directory
		diffFiles = list(set(currFiles) - set(prevFiles))
		for file in diffFiles:
			self.OnFileChange(os.path.join(self.downloadDir, file), "Created")
		# Save the current image of the files
		self.SaveDownloadDirFileList(currFiles)

	def WorkerThread(self, path):
		try:
			print('-- Worker Thread initiated --')
			workersLock.acquire()

			if self.workingDir != self.downloadDir:
				newPath = os.path.join(self.workingDir, os.path.basename(path))
				print('---- Copying ' + path + ' to ' + newPath)
				if os.path.isdir(path):
					shutil.copytree(path, newPath)
				elif os.path.isfile(path):
					shutil.copyfile(path, newPath)	
			else:
				newPath = path

			self.organizer.Process(newPath, True)
			workersLock.release()
			print('-- Worker Thread terminated --')
		except:
			print("-- ERROR: Exception raised in worker thread")
			traceback.print_exc(file=sys.stdout)
			print('-' * 60)