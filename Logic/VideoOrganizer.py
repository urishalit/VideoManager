import os
import os.path
import json
import string
import shutil
import time
import traceback
import sys
from threading import Thread
from threading import Timer

# My Files
from VidFileData import VidFileData
from VidFileData import VideoType
from SubtitleManager import SubtitleManager
from Notifier import Notifier
from CmdLineConsts import *
from VidFileDataFactory import GetVidFileData
from Utilities import *
from LogicDefs import *
from NewDownloadsHandler import NewDownloadsHandler

class VideoOrganizer(IVideoOrganizer):

	def Process(self, path, isNewDownload=False):
		if os.path.isdir(path):
			for file in os.listdir(path):
				self.Process(os.path.join(path, file), isNewDownload)
		else:
			self.ProcessVideo(os.path.dirname(path), os.path.basename(path), isNewDownload)

	def ProcessVideo(self, dir, file, isNewDownload):
		print("---- Working on " + file)
		# First check if this is actually a video file
		if not IsVidFile(file):
			print("---- Not supporting movie files yet: " + file)
			return

		# Capitize First letters of every word
		file = CaptalizeFirstLetters(dir, file)

		# Parse the infomrmation from the file name and return an object representing it.
		vidFileData = GetVidFileData(dir, file, self.configData)

		# Make sure TV file is up to format
		vidFileData.RenameToFormat()

		if isNewDownload:
			# This should happen only once per video
			self.notifier.AddDownloadedFile(vidFileData)

		# Download subtitles for TV show
		result = self.subtitleManager.DownloadSubtitles(vidFileData)
		if result == True:
			# Move files and associates to proper location
			vidFileData.MoveToTargetDirectory()
			# Add to Notifier as ready episode
			self.notifier.AddReadyFile(vidFileData)
		else:
			# Add to Notifier as in staging episode
			self.notifier.AddStagingFile(vidFileData)

	def ScanThread(self):
		try:
			print('-- Scanner Thread initiated --')
			# Lock - so both threads won't accidetnly work on the same file/s
			workersLock.acquire()

			# Scan all files in working dir and see if we can make any ready
			for file in os.listdir(self.workingDir):
				self.Process(os.path.join(self.workingDir, file))

			# Send Notification (email) if there is any new news to update
			self.notifier.SendNotifications()
			
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

	
	def StartFully(self):
		# Start new downloads listener
		self.newDownloadsHandler.Start()

		# Start Scanner Thread
		self.scanThread.start()

	def ScanDir(self):
		print('-- Scanning Directory ' + self.workingDir)
		self.Process(self.workingDir)
		self.notifier.SendNotifications()
		print('-- Scan completed.')

	def Start(self):
		action = self.configData['action']

		if Actions.full == action:
			self.StartFully()
		elif Actions.init_dir == action:
			self.newDownloadsHandler.InitDir()
		elif Actions.scan_dir == action:
			self.ScanDir()
		else:
			print('ERROR: Unknown action: Should never get here')

	def __init__(self, configData):
		self.configData = configData
		self.subtitleManager = SubtitleManager(configData)
		self.workingDir = configData["WorkingDirectory"]
		self.downloadDir = configData["DownloadDirectory"]
		self.scanIntervalSec = configData["ScanIntervalSec"]
		self.notifier = Notifier(configData)
		self.scanThread = Thread(target = self.ScanThread)
		self.newDownloadsHandler = NewDownloadsHandler(self, self.downloadDir, self.workingDir)

		