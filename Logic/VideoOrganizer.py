import os
import os.path
import json
import string
import shutil
import time
from threading import Thread
from threading import Timer
import threading


# My Files
from EpisodeData import EpisodeData
from SubtitleManager import SubtitleManager
from Notifier import Notifier
from FileListener import *
from CmdLineConsts import *
from VidFileDataFactory import GetVidFileData

# Known vid extensions
vidExtenstions = ['.avi','.mkv','.mp4']

# Lock so Scan Thread and worker thread won't work together.
workersLock = threading.Lock()


class VideoOrganizer(IFileChangeRecipient):
	def isVidFile(self, file):
		ext = os.path.splitext(file)[1]
		return ext in vidExtenstions

	def GetWordDelimiter(self, baseName):
		firstDot = baseName.find('.')
		if firstDot < 0:
			firstDot = len(baseName)

		firstSpace = baseName.find(' ')
		if firstSpace < 0:
			firstSpace = len(baseName)

		if firstDot < firstSpace:
			return '.'
		elif firstSpace < firstDot:
			return ' '
		else:
			return ''

	def CaptalizeFirstLetters(self, dir, file):
		ext = os.path.splitext(file)[1]
		base = os.path.splitext(file)[0]

		delim = self.GetWordDelimiter(base)
		newBase = string.capwords(base, delim)

		src = os.path.abspath(os.path.join(dir, file))
		trgt = os.path.abspath(os.path.join(dir, newBase + ext))

		os.rename(src, trgt)

		return newBase + ext

	def ProcessVideo(self, dir, file, isNewDownload):
		print("---- Working on " + file)
		# First check if this is actually a video file
		if not self.isVidFile(file):
			print("---- Not supporting movie files yet: " + file)
			return

		# Capitize First letters of every word
		file = self.CaptalizeFirstLetters(dir, file)

		# Parse the infomrmation from the file name and return an object representing it.
		vidFileData = GetVidFileData(dir, file, self.configData)

		# Make sure TV file is up to format
		vidFileData.RenameToFormat()

		#if isNewDownload:
			# This should happen only once per video
			#self.notifier.AddDownloadedEpisode(vidFileData)

		# Download subtitles for TV show
		result = self.subtitleManager.DownloadSubtitles(vidFileData)
		if result == True:
			# Move files and associates to proper location
			vidFileData.MoveToTargetDirectory()
			# Add to Notifier as ready episode
			#self.notifier.AddReadyEpisode(vidFileData)
		#else:
			# Add to Notifier as in staging episode
			#self.notifier.AddStagingEpisode(vidFileData)


	def Process(self, path, isNewDownload=False, removeDir=True):
		if os.path.isdir(path):
			for file in os.listdir(path):
				self.Process(os.path.join(path, file), isNewDownload, False)
			
			if removeDir:
				# Only if the working driectory is different then the target directory we attempt to
				# we attempt to remove the folder as it should be emppty after processed
				if self.workingDir != self.configData["TVShows"]["TargetDirectory"]:
					if os.path.exists(path):
						try:
							shutil.rmtree(path)			
						except:
							print('---- Failed removing directory ' + path)
		else:
			self.ProcessVideo(os.path.dirname(path), os.path.basename(path), isNewDownload)

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

			self.Process(newPath, True)
			workersLock.release()
			print('-- Worker Thread terminated --')
		except:
			print("-- ERROR: Exception raised in worker thread")
			traceback.print_exc(file=sys.stdout)
			print('-' * 60)

	def OnFileChange(self, filePath, action):
		print("-- " + filePath + " " + action)
		thread = Thread(target = self.WorkerThread, args = (filePath, ))
		thread.start()

	def ScanThread(self):
		try:
			print('-- Scanner Thread initiated --')
			# Lock - so both threads won't accidetnly work on the same file/s
			workersLock.acquire()

			# Scan all files in working dir and see if we can make any ready
			for file in os.listdir(self.workingDir):
				self.Process(os.path.join(self.workingDir, file))

			# Send Notification (email) if there is any new news to update
			self.notifier.SendNotification()
			
			# Schedule the next scan
			self.scanThread = Timer(self.scanIntervalSec, self.ScanThread)
			self.scanThread.start()

			# Release the lock - so the worker can work if it needs to
			workersLock.release()
			print('-- Scanner Thread terminated --')
		except:
			print("-- ERROR: Exception raised in scanner thread")
			traceback.print_exc(file=sys.stdout)
			print('-' * 60)

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
		currFiles = os.listdir(self.downloadDir)
		prevFiles = self.GetDownloadDirFileList()
		# Get the difference in the files image in the download directory
		diffFiles = list(set(currFiles) - set(prevFiles))
		for file in diffFiles:
			self.OnFileChange(os.path.join(self.downloadDir, file), "Created")
		# Save the current image of the files
		self.SaveDownloadDirFileList(currFiles)

	def InitDir(self):
		print('-- Directory: ' + self.downloadDir)
		files = os.listdir(self.downloadDir)
		self.SaveDownloadDirFileList(files)
		print('-- Directory contenets saved')

	def StartFully(self):
		# Start file listener
		self.fileListener.Start()

		# Start Scanner Thread
		self.scanThread.start()

		# Check if there are new files in the Download directory since last time
		self.CheckForNewFilesSinceLastTime()

	def ScanDir(self):
		print('-- Scanning Directory ' + self.workingDir)
		self.Process(self.workingDir)
		self.notifier.SendNotification()
		print('-- Scan completed.')

	def Start(self):
		action = self.configData['action']

		if Actions.full == action:
			self.StartFully()
		elif Actions.init_dir == action:
			self.InitDir()
		elif Actions.scan_dir == action:
			self.ScanDir()
		else:
			print('ERROR: Unknown action: Should never get here')

	def __init__(self, configData):
		self.configData = configData
		self.subtitleManager = SubtitleManager(configData)
		self.workingDir = configData["TVShows"]["WorkingDirectory"]
		self.downloadDir = configData["DownloadDirectory"]
		self.scanIntervalSec = configData["ScanIntervalSec"]
		self.notifier = Notifier(configData)
		self.scanThread = Thread(target = self.ScanThread)
		self.fileListener = FileListener(self.downloadDir, self)

		