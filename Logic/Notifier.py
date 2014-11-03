import json	
import threading

# My Files
from EmailSender import SendEmail
from VidFileData import VidFileData
from VidFileData import VideoType

mapsLock = threading.Lock()

STAGING_TITLE = 'Pending VIDEOS'
STAGING_CAPTION = 'The following VIDEOS have been downloaded and are waiting to get subtitles'

READY_TITLE = 'Ready VIDEOS'
READY_CAPTION = 'The following VIDEOS are ready to watch'

DOWNLOADED_TITLE = 'Newly Downloaded VIDEOS'
DOWNLOADED_CAPTION = 'The following VIDEOS are newly downloaded'

from enum import Enum
class NotifyFileType(Enum):
	Ready = 1
	Downloaded = 2
	Staging = 3

class Notifier:
	def __init__(self, configData):
		self.configData = configData
		self.emailList = configData["Emails"]
		self.maps = dict()
		self.maps[VideoType.tvShow] = dict()
		self.maps[VideoType.movie] = dict()
		self.ClearAllLists()

	def ClearAllLists(self):
		for vidType in VideoType:
			self.ClearLists(vidType)
		
	def ClearLists(self, vidType : VideoType):
		for notifyType in NotifyFileType:
			self.maps[vidType][notifyType] = []

	def AddFile(self, notifyType: NotifyFileType, fileData: VidFileData):
		mapsLock.acquire()
		# First we check if this video has already been added to this list
		found = False
		for data in self.maps[fileData.GetType()][notifyType]:
			if fileData.Equals(data):
				found = True
				break

		# Only if it's the first time this video is added to the list we add it.
		if not found:
			self.maps[fileData.GetType()][notifyType].append(fileData)

		mapsLock.release()

	def RemoveFile(self, notifyType: NotifyFileType,fileData: VidFileData):
		mapsLock.acquire()
		try:
			self.maps[fileData.GetType()][notifyType].remove(fileData)
		except:
			pass
		mapsLock.release()

	def AddReadyFile(self, fileData: VidFileData):
		self.AddFile(NotifyFileType.Ready, fileData)
		# In case the file is also in the staging list we remove it - as it is ready
		self.RemoveFile(NotifyFileType.Staging, fileData)

	def AddStagingFile(self, fileData: VidFileData):
		self.AddFile(NotifyFileType.Staging, fileData)

	def AddDownloadedFile(self, fileData: VidFileData):
		self.AddFile(NotifyFileType.Downloaded, fileData)

	def GetVids(self, vidType : VideoType, notifyType: NotifyFileType):
		return self.maps[vidType][notifyType]

	def GetTitleAndCaption(self, vidType : VideoType, notifyType: NotifyFileType):
		title = ''
		caption = ''
		if notifyType is NotifyFileType.Ready:
			title = READY_TITLE
			caption = READY_CAPTION
		elif notifyType is NotifyFileType.Staging:
			title = STAGING_TITLE
			caption = STAGING_CAPTION
		elif notifyType is NotifyFileType.Downloaded:
			title = DOWNLOADED_TITLE
			caption = DOWNLOADED_CAPTION
		else:
			raise

		vidTypeDesc = self.GetVideoTypeDescription(vidType)
		title = title.replace("VIDEOS", vidTypeDesc)
		caption = caption.replace("VIDEOS", vidTypeDesc)

		return (title, caption)

	def GenerateContent(self, vidType : VideoType, notifyType: NotifyFileType, vids: list):
		title, caption = self.GetTitleAndCaption(vidType, notifyType)
		content = '<p><b>' + title + ':</b><br>' + caption + '<br>'
		for fileData in vids:
			content += '\t' + fileData.GetNotificationText() + '<br>'
		content += '</p><br><br>'
		return content

	def GetVidTitles(self, vids):
		s = set()
		for fileData in vids:
			s.add(fileData.GetNotificationTitle())

		return ','.join(map(str, s))

	def GetVideoTypeDescription(self, vidType : VideoType):
		if VideoType.tvShow == vidType:
			return "Episodes"
		elif VideoType.movie == vidType:
			return "Movies"
		else:
			return "Videos"

	def SendNotification(self, vidType : VideoType):
		# First we copy and clear the members list - we do this under lock so they won't be changed in the meantime.
		mapsLock.acquire()
		# If no updates to send we leave.
		if len(self.GetVids(vidType, NotifyFileType.Ready)) == 0 and len(self.GetVids(vidType, NotifyFileType.Downloaded)) == 0:
			self.ClearAllLists()
			mapsLock.release()
			return

		tmpData = dict()
		# Copy each list asice - so we can work on it
		for notifyType in NotifyFileType:
			tmpData[notifyType] = list(self.GetVids(vidType, notifyType))

		# Clear all lists - next time we will work on new data
		self.ClearLists(vidType)
		# Here we stop working on the members - so we can release the lock
		mapsLock.release()
		
		subject = ''
		vidTypeDesc = self.GetVideoTypeDescription(vidType)
		if len(tmpData[NotifyFileType.Ready]) > 0:
			# Generate subject according to ready video
			subject = 'New ' + vidTypeDesc + ' Ready (' + self.GetVidTitles(tmpData[NotifyFileType.Ready]) + ')'
		else:
			subject = 'New ' + vidTypeDesc + ' Downloaded (' + self.GetVidTitles(tmpData[NotifyFileType.Downloaded]) + ')'

		# Contnet prefix
		content = '<html><head></head><body>'

		# generate content per type
		for notifyType in NotifyFileType:
			if len(tmpData[notifyType]) > 0:
				content += self.GenerateContent(vidType, notifyType, tmpData[notifyType])

		# Contnet suffix
		content += '</body></html>'

		for email in self.emailList:
			SendEmail(email, subject, content, 'html')
			print('---- ' + vidTypeDesc + ' notification email sent to ' + email)

	def SendNotifications(self):
		self.SendNotification(VideoType.tvShow)
		self.SendNotification(VideoType.movie)


