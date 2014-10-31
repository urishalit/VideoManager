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
from TVManager import TVManager
from Notifier import Notifier

# Known vid extensions
vidExtenstions = ['.avi','.mkv','.mp4']

# Lock so Scan Thread and worker thread won't work together.
workersLock = threading.Lock()


class VideoOrganizer:

	def isVidFile(self, file):
		ext = os.path.splitext(file)[1]
		return ext in vidExtenstions

	def CaptalizeFirstLetters(self, dir, file):
		ext = os.path.splitext(file)[1]
		base = os.path.splitext(file)[0]

		newBase = string.capwords(base, '.')

		src = os.path.abspath(os.path.join(dir, file))
		trgt = os.path.abspath(os.path.join(dir, newBase + ext))

		os.rename(src, trgt)

		return newBase + ext

	def OrganizeVideo(self, dir, file, isNewDownload):
		print("---- Working on " + file)
		if self.isVidFile(file):
			# Capitize First letters of every word
			file = self.CaptalizeFirstLetters(dir, file)
			# Parse episode data & rename file to proper format 
			epData = self.tvManager.IsTVEpisode(dir, file)
			if epData != None:
				# Make sure TV file is up to format
				self.tvManager.RenameToFormat(epData)

				if isNewDownload:
					# This should happen only once per video
					self.notifier.AddDownloadedEpisode(epData)

				# Download subtitles for TV show
				result = self.subtitleManager.DownloadTVSubtitles(epData)
				if result == True:
					# Move files and associates to proper location
					self.tvManager.MoveToShowsDirectory(epData)
					# Add to Notifier as ready episode
					self.notifier.AddReadyEpisode(epData)
				else:
					# Add to Notifier as in staging episode
					self.notifier.AddStagingEpisode(epData)

			else:
				print("---- Not supporting movie files yet: " + file)
				return


	def OrganizeVideos(self, dir, isNewDownload):
		if not os.path.isdir(dir):
			return

		for file in os.listdir(dir):
			self.OrganizeVideo(dir, file, isNewDownload)

	def Start(self, path, isNewDownload=False):
		if os.path.isdir(path):
			self.OrganizeVideos(path, isNewDownload)
			shutil.rmtree(path)
		else:
			self.OrganizeVideo(os.path.dirname(path), os.path.basename(path), isNewDownload)

	def WorkerThread(self, path):
		try:
			print('-- Worker Thread initiated --')
			workersLock.acquire()
			newPath = os.path.join(self.workingDir, os.path.basename(path))
			print('---- Copying ' + path + ' to ' + newPath)
			if os.path.isdir(path):
				shutil.copytree(path, newPath)
			elif os.path.isfile(path):
				shutil.copyfile(path, newPath)	

			self.Start(newPath, True)
			workersLock.release()
			print('-- Worker Thread terminated --')
		except:
			print("-- ERROR: Exception raised in worker thread")
			traceback.print_exc(file=sys.stdout)
			print('-' * 60)

	def Organize(self, path):
		thread = Thread(target = self.WorkerThread, args = (path, ))
		thread.start()

	def ScanThread(self):
		try:
			print('-- Scanner Thread initiated --')
			# Lock - so both threads won't accidetnly work on the same file/s
			workersLock.acquire()

			# Scan all files in working dir and see if we can make any ready
			for file in os.listdir(self.workingDir):
				self.Start(os.path.join(self.workingDir, file))

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

	def __init__(self, configData):
		self.configData = configData
		self.subtitleManager = SubtitleManager(configData)
		self.tvManager = TVManager(configData)
		self.workingDir = configData["WorkingDirectory"]
		self.downloadDir = configData["DownloadDirectory"]
		self.scanIntervalSec = configData["ScanIntervalSec"]
		self.scanThread = Thread(target = self.ScanThread)
		self.scanThread.start()
		self.notifier = Notifier(configData)
