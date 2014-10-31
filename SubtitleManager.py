import json
import os.path

# My Files
from SubDB import SubDB
from EpisodeData import EpisodeData
from SubDownloader import SubDownloader
from OpenSubtitles import OpenSubtitles

class SubtitleManager:
	def __init__(self, configData):
		self.configData = configData
		self.langauges = self.configData["SubtitleLanguages"]
		#self.downloaders = [OpenSubtitles(), SubDB()]
		self.downloaders = [OpenSubtitles()]
		
	def DownloadTVSubtitles(self, epData: EpisodeData):
		print('------ Attempting to download subtitles')
		langs = list(self.langauges)
		# If no langauges configured skipping this phase
		if langs == []:
			print('------ No subtitle language configured.')
			return True

		# Iterate over all downloaders until all subtitles in all languages are aquired.
		foundLangs = []
		for downloader in self.downloaders:
			if isinstance(downloader, SubDownloader):
				for lang in langs:
					# If exists already a subtitle file for this language - we skip it.
					subPath = downloader.GetSubtitleFilePath(epData, lang)
					if (os.path.exists(subPath)):
						foundLangs.append(lang)
						epData.AddAssociatedFile(subPath)
						continue

					# Attempt downloading subtitle for language
					res = downloader.DownloadSubs(epData, lang)
					if res == True:
						foundLangs.append(lang)

				# Remove found langs from langs
				langs = list(set(langs) - set(foundLangs))
				foundLangs = []

		# Only if there are no remaining languages we return True
		if langs == []:
			result = True
			print("------ Successfully downloaded subtitles")
		else:
			result = False
			print("------ Did not find subtitles for " + ','.join(map(str, langs)))

		return result