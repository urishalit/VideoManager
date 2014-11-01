
import os.path
from EpisodeData import EpisodeData

SearchLanguages = ['en']

class SubDownloader:
	def GetSubtitleFilePath(self, epData: EpisodeData, lang):
		srtFile = os.path.join(epData.fileDir, epData.fileName[:epData.fileName.rfind('.')] + "-" + lang + ".srt")
		return srtFile

	def DownloadSubs(self, epData: EpisodeData, lang):
		return self.GetLanguages()

	def SaveSubtitleFile(self, epData: EpisodeData, lang, content):
		# Construct sub file path
		subFilePath = self.GetSubtitleFilePath(epData, lang)

		# Save subtitle to file
		subFile = open(subFilePath, 'wb')
		subFile.write(content)
		subFile.close()

		# Add to associated files
		epData.AddAssociatedFile(subFilePath)