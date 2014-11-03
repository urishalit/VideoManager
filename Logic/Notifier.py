import json	
import threading

# My Files
from EmailSender import SendEmail
from EpisodeData import EpisodeData

mapsLock = threading.Lock()

STAGING_EPISODES_TITLE = 'Pending Episodes'
STAGING_EPISODES_CAPTION = 'The following episodes have been downloaded and are waiting to get subtitles'

READY_EPISODES_TITLE = 'Ready Episodes'
READY_EPISODES_CAPTION = 'The following episodes are ready to watch'

DOWNLOADED_EPISODES_TITLE = 'Newly Downloaded Episodes'
DOWNLOADED_EPISODES_CAPTION = 'The following episodes are newly downloaded'

from enum import Enum
class NotifyFileType(Enum):
	Ready = 1
	Downloaded = 2
	Staging = 3

class Notifier:
	def ClearAllLists(self):
		self.data = dict()
		for type in NotifyFileType:
			self.data[type] = []
		

	def __init__(self, configData):
		self.configData = configData
		self.emailList = configData["Emails"]
		self.data = dict()
		self.ClearAllLists()

	def AddEpisode(self, type, epData: EpisodeData):
		mapsLock.acquire()
		# First we check if this episode has already been added to this list
		found = False
		for data in self.data[type]:
			if data.GetSeriesName() == epData.GetSeriesName() and data.GetSeason() == epData.GetSeason() and data.GetEpisodeNumber() == epData.GetEpisodeNumber():
				found = True
				break

		# Only if it's the first time this episode is added to the list we add it.
		if not found:
			self.data[type].append(epData)

		mapsLock.release()

	def RemoveEpisode(self, type, epData: EpisodeData):
		mapsLock.acquire()
		try:
			self.data[type].remove(epData)
		except:
			pass
		mapsLock.release()

	def AddReadyEpisode(self, epData: EpisodeData):
		self.AddEpisode(NotifyFileType.Ready, epData)
		self.RemoveEpisode(NotifyFileType.Staging, epData)

	def AddStagingEpisode(self, epData: EpisodeData):
		self.AddEpisode(NotifyFileType.Staging, epData)

	def AddDownloadedEpisode(self, epData: EpisodeData):
		self.AddEpisode(NotifyFileType.Downloaded, epData)

	def GetEpisodes(self, type):
		return self.data[type]

	def GetTitleAndCaption(self, type):
		if type is NotifyFileType.Ready:
			return (READY_EPISODES_TITLE, READY_EPISODES_CAPTION)
		elif type is NotifyFileType.Staging:
			return (STAGING_EPISODES_TITLE, STAGING_EPISODES_CAPTION)
		elif type is NotifyFileType.Downloaded:
			return (DOWNLOADED_EPISODES_TITLE, DOWNLOADED_EPISODES_CAPTION)
		else:
			return ()

	def GenerateContent(self, type, readyEps: list):
		title, caption = self.GetTitleAndCaption(type)
		content = '<p><b>' + title + ':</b><br>' + caption + '<br>'
		for epData in readyEps:
			content += '\t' + epData.GetNotificationText() + '<br>'
		content += '</p><br><br>'
		return content

	def GetSeriesNames(self, episodes):
		s = set()
		for epData in episodes:
			s.add(epData.GetSeriesName())

		return ','.join(map(str, s))

	def SendNotification(self):
		# First we copy and clear the members list - we do this under lock so they won't be changed in the meantime.
		mapsLock.acquire()
		# If no updates to send we leave.
		if len(self.GetEpisodes(NotifyFileType.Ready)) == 0 and len(self.GetEpisodes(NotifyFileType.Downloaded)) == 0:
			self.ClearAllLists()
			mapsLock.release()
			return

		tmpData = dict()
		# Copy each list asice - so we can work on it
		for type in NotifyFileType:
			tmpData[type] = list(self.GetEpisodes(type))
		# Clear all lists - next time we will work on new data
		self.ClearAllLists()
		# Here we stop working on the members - so we can release the lock
		mapsLock.release()
		
		subject = ''
		if len(tmpData[NotifyFileType.Ready]) > 0:
			# Generate subject according to ready episodes
			subject = 'New Episodes Ready (' + self.GetSeriesNames(tmpData[NotifyFileType.Ready]) + ')'
		else:
			subject = 'New Episodes Downloaded (' + self.GetSeriesNames(tmpData[NotifyFileType.Downloaded]) + ')'

		# Contnet prefix
		content = '<html><head></head><body>'

		# generate content per type
		for type in NotifyFileType:
			if len(tmpData[type]) > 0:
				content += self.GenerateContent(type, tmpData[type])

		# Contnet suffix
		content += '</body></html>'

		for email in self.emailList:
			SendEmail(email, subject, content, 'html')
			print('---- Notification email sent to ' + email)


