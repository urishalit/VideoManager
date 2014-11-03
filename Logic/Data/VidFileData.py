import os.path
import os
import shutil
import stat

from enum import Enum

class VideoType(Enum):
	tvShow = 1
	movie = 2

class VidFileData:
	def __init__(self, configData, fileDir, fileName, suffix):
		self.configData = configData
		self.fileDir = fileDir
		self.fileName = fileName
		self.suffix = suffix
		self.associatedFiles = []
		self.associatedFiles.insert(0, self.GetFilePath())
		self.baseFileName = os.path.basename(self.fileName)
		self.workingDir = configData["WorkingDirectory"]
		self.targetRootDir = ''
		self.imdbTitleId = ''

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

	def IsMovie(self):
		return VideoType.movie == self.type

	def IsTvShow(self):
		return VideoType.tvShow == self.type

	def GetType(self):
		return self.type

	def GetNotificationText(self):
		raise NotImplemented

	def GetNotificationTitle(self):
		raise NotImplemented

	def RenameToFormat(self):
		return

	def MoveToTargetDirectory(self):
		self.MoveToDir(self.targetRootDir)

	def InitiateTargetDirectory(self, path):
		self.targetRootDir = path
		if os.path.exists(self.targetRootDir):
			if not os.path.isdir(self.targetRootDir):
				self.targetRootDir = ''
		else:
			os.makedirs(self.targetRootDir)
			if not os.path.isdir(self.targetRootDir):
				self.targetRootDir = ''

		if len(self.targetRootDir) == 0:
			self.moveFiles = False
		else: 
			# If the shows dir is the same as the working directory - we do not move the files
			self.moveFiles = self.targetRootDir != self.workingDir

	def MoveToDir(self, targetPath):
		if not self.moveFiles:
			return

		# Verify target dir exists
		if not os.path.exists(targetPath):
			os.makedirs(targetPath)

		moveFiles = True
		# Check if file with same name already exists
		targetVidPath = os.path.join(targetPath, self.fileName)
		counter = 0
		while os.path.exists(targetVidPath) and counter < 10:
			# If a file with that name already exists and it has the same size we do nothing.
			if os.path.getsize(targetVidPath) == os.path.getsize(os.path.join(self.fileDir, self.fileName)):
				print('------ File already exists in target directory: ' + targetPath)				
				moveFiles = False
				break
			else:
				self.AddSuffixToFiles(counter)
				counter = counter + 1
				targetVidPath = os.path.join(targetPath, self.fileName)

		if moveFiles:
			print('------ Moving to ' + targetPath)
		
		for file in self.associatedFiles:
			targetFilePath = os.path.join(targetPath, os.path.basename(file))
			# If the file is marked as read-only we remove the read-only flag and then move it.
			if not os.access(file, os.W_OK):
				os.chmod(file, stat.S_IWUSR)

			if moveFiles:
				shutil.move(file, targetFilePath)
			else:
				os.remove(file)

	def Equals(self, otherFileData):
		return self.fileDir == otherFileData.fileDir and self.fileName == otherFileData.fileName

