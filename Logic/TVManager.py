import os.path
import re
import shutil

# My Files
from EpisodeData import EpisodeData
from CmdLineConsts import *

class TVManager:
	def __init__(self, configData):
		self.configData = configData
		# Shows Root Directory
		self.showsRootDir = configData["TVShows"]["TargetDirectory"]
		if os.path.exists(self.showsRootDir):
			if not os.path.isdir(self.showsRootDir):
				self.showsRootDir = ''
		else:
			os.makedirs(self.showsRootDir)
			if not os.path.isdir(self.showsRootDir):
				self.showsRootDir = ''

		if Actions.init_dir != configData['action']:
			print('-- Shows Root Directory is ' + self.showsRootDir)

		#TODO Add format in config data

	def IsTVEpisode(self, dir, file):
		# Divide extension and file name
		ext = os.path.splitext(file)[1]
		base = os.path.splitext(file)[0]

		# Check if we can get episode information about the file
		episodeInfo = re.search(r"(?:s|season)(\d{2})(?:e|x|episode|\n)(\d{2})", base, re.I)
		if episodeInfo == None:
			print('------ Problem formatting episode number for ' + base)
			return None

		# Get the series name from the file
		series = base[:episodeInfo.span()[0] - 1]
		suffix = base[episodeInfo.span()[1]:]

		# Get the Episode season & episode number
		episodeInfo = re.findall(r"(?:s|season)(\d{2})(?:e|x|episode|\n)(\d{2})", base, re.I)
		season = episodeInfo[0][0]
		episode = episodeInfo[0][1]

		return EpisodeData(series, season, episode, dir, file, suffix)

	def RenameToFormat(self, epData : EpisodeData):
		# Construct new file name
		newFile = epData.series + "." + "S" + epData.season + "E" + epData.episode + epData.suffix + epData.GetVidExtension();

		epData.RenameFile(epData.fileDir, newFile)

	
	def MoveToShowsDirectory(self, epData : EpisodeData):
		targetRootPath = self.showsRootDir

		# Construct Target Dir - RootDir\Series\Season X
		targetPath = os.path.join(targetRootPath, epData.GetSeriesName(), "Season " + epData.GetSeason())

		# Verify target dir exists
		if not os.path.exists(targetPath):
			os.makedirs(targetPath)

		moveFiles = True
		# Check if file with same name already exists
		targetVidPath = os.path.join(targetPath, epData.fileName)
		counter = 0
		while os.path.exists(targetVidPath) and counter < 10:
			# If a file with that name already exists and it has the same size we do nothing.
			if os.path.getsize(targetVidPath) == os.path.getsize(os.path.join(epData.fileDir, epData.fileName)):
				print('------ File already exists in target directory: ' + targetPath)				
				moveFiles = False
				break
			else:
				epData.AddSuffixToFiles(counter)
				counter = counter + 1
				targetVidPath = os.path.join(targetPath, epData.fileName)

		if moveFiles:
			print('------ Moving to ' + targetPath)
		
		for file in epData.associatedFiles:
			targetFilePath = os.path.join(targetPath, os.path.basename(file))
			if moveFiles:
				os.rename(file, targetFilePath)
			else:
				os.remove(file)

