import os.path
import os

#My Files
from VidFileData import VidFileData
from VidFileData import VideoType

class MovieData(VidFileData):
	def __init__(self, configData, title, year, fileDir, fileName):
		VidFileData.__init__(self, configData, fileDir, fileName, '')
		self.title = title
		self.year = str(year)
		self.type = VideoType.movie
		self.InitiateTargetDirectory(configData["Movies"]["TargetDirectory"])

	def GetMovieTitle(self):
		return self.title
	
	def GetMovieYear(self):
		return self.year

	def GetNotificationText(self):
		if len(self.imdbTitleId) > 0:
			return self.GenerateLinkText()
		else:
			return self.GeneratePlainText()

	def GenerateLinkText(self):
		text = '<a href=\"http://www.imdb.com/title/tt'
		text += str(self.imdbTitleId)
		text += '\" target=\"_blank\">'
		text += self.GeneratePlainText()
		text += '</a>'

		return text

	def GeneratePlainText(self):
		text = self.title
		if len(self.year) > 0:
			text += ' (' + self.year + ')'
		
		return text

	def GetNotificationTitle(self):
		return self.GetMovieTitle()