import os.path
import os

class EpisodeData:
	def __init__(self, series, season, episode, fileDir, fileName, suffix):
		self.series = series
		self.season = season
		self.episode = episode
		self.fileDir = fileDir
		self.fileName = fileName
		self.suffix = suffix
		self.associatedFiles = []
		self.associatedFiles.insert(0, self.GetFilePath())
		self.baseFileName = os.path.basename(self.fileName)

	def GetSeriesName(self):
		return self.series.replace(".", " ")

	def GetSeason(self):
		return str(int(self.season))

	def GetEpisodeNumber(self):
		return str(int(self.episode))
		
	def GetFilePath(self):
		return os.path.abspath(os.path.join(self.fileDir, self.fileName))

	def GetVidExtension(self):
		return os.path.splitext(self.fileName)[1]

	def AddAssociatedFile(self, path):
		self.associatedFiles.append(path)

	def RenameFile(self, dir, file):
		# Current path
		currPath = self.GetFilePath()

		# Remove current path from list of associated files
		self.associatedFiles = list(set(self.associatedFiles) - set([currPath]))

		# Update dir & file name
		self.fileDir = dir
		self.fileName = file

		# Add file to associated files list
		self.AddAssociatedFile(self.GetFilePath())

		# Rename file
		os.rename(currPath, self.GetFilePath())

	def AddSuffixToFiles(self, suffix):
		newAssociatedFileList = []
		newBaseName = os.path.splitext(self.baseFileName)[0] + str(suffix)

		currBaseName = os.path.splitext(os.path.basename(self.fileName))[0]
		for file in self.associatedFiles:
			newFile = file.replace(currBaseName, newBaseName)
			newAssociatedFileList.append(newFile)

		self.fileName = newBaseName + os.path.splitext(os.path.basename(self.fileName))[1]
		self.associatedFiles = newAssociatedFileList