import os.path
import os

#My Files
from VidFileData import VidFileData
from VidFileData import VideoType

class EpisodeData(VidFileData):
	def __init__(self, configData, series, season, episode, fileDir, fileName, suffix):
		VidFileData.__init__(self, configData, fileDir, fileName, suffix)
		self.series = str(series)
		self.season = "%02d" % (season,)
		self.episode = "%02d" % (episode,)
		self.type = VideoType.tvShow
		self.InitiateTargetDirectory(configData["TVShows"]["TargetDirectory"])
		
	def GetSeriesName(self):
		return self.series.replace(".", " ")

	def GetSeason(self):
		return str(int(self.season))

	def GetEpisodeNumber(self):
		return str(int(self.episode))
		
	def GetNotificationText(self):
		return self.GetSeriesName() + ' - S' + self.season + 'E' + self.episode

	def GetNotificationTitle(self):
		return self.GetSeriesName()
		
	def RenameToFormat(self):
		# Construct new file name
		newFile = self.series.replace(" ", ".") + "." + "S" + self.season + "E" + self.episode + self.suffix + self.GetVidExtension();

		self.RenameFile(self.fileDir, newFile)

	def MoveToTargetDirectory(self):
		# Construct Target Dir - RootDir\Series\Season X
		targetPath = os.path.join(self.targetRootDir, self.GetSeriesName(), "Season " + self.GetSeason())
		
		self.MoveToDir(targetPath)

