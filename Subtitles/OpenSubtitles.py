from VidFileData import VidFileData
import os.path
import hashlib
import os
import struct
from SubDownloader import SubDownloader
import xmlrpclib
import math
import base64
import gzip
import traceback
import sys

OpenSubtitlesUrl_Download = 'http://api.opensubtitles.org/xml-rpc'

OpenSubtitlesUrl_UserName = "VidMngr"
OpenSubtitlesUrl_Password = "Mov!esAndShows"

#MyUserAgent = "OS Test User Agent"
OpenSubtitlesUrl_UserAgent = "VidMngr"

class OpenSubtitles(SubDownloader):
	#this hash function receives the name of the file and returns the hash code
	def get_hash(self, name):
		try:
			longlongformat = 'q'  # long long 
			bytesize = struct.calcsize(longlongformat)
			f = open(name, "rb")
			filesize = os.path.getsize(name)
			hash = filesize
			if filesize < 65536 * 2:
				return "SizeError"

			for x in range(int(65536/bytesize)):
				buffer = f.read(bytesize)
				(l_value,)= struct.unpack(longlongformat, buffer)
				hash += l_value
				hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number

			f.seek(max(0,filesize-65536),0)
			for x in range(int(65536/bytesize)):
				buffer = f.read(bytesize)
				(l_value,)= struct.unpack(longlongformat, buffer)
				hash += l_value
				hash = hash & 0xFFFFFFFFFFFFFFFF

			f.close()
			returnedhash =  "%016x" % hash
			return returnedhash

		except(IOError):
			return "IOError"

	def Connect(self):
		# Connect to open subtitles server
		self.osProxy = xmlrpclib.ServerProxy(OpenSubtitlesUrl_Download)
		if self.osProxy is None:
			raise Exception('Failed connecting to Open Subtitles')

	def LogIn(self):
		# Log in to server
		loginData = self.osProxy.LogIn(OpenSubtitlesUrl_UserName, OpenSubtitlesUrl_Password, "eng", OpenSubtitlesUrl_UserAgent)

		# Check status
		status = loginData['status']
		if status != '200 OK':
			raise

		self.token = loginData['token']

	def LogOut(self):
		try:
			self.osProxy.LogOut(self.token)
		except:
			pass


	def SearchSubs(self, fileData, lang):
		# Get episode hash
		epHash = self.get_hash(fileData.GetFilePath())

		# Get file byte size
		fileSizeBytes = os.path.getsize(fileData.GetFilePath())
		#strfileSizeBytes = str(fileSizeBytes)
		
		searchResults = self.osProxy.SearchSubtitles(self.token, [{'moviehash': epHash, 'moviebytesize': str(fileSizeBytes), 'sublanguageid' :lang}])
		if not isinstance(searchResults, dict):
			print('------ ERROR: Open Subtitles bad response.')
			return None

		# Check status
		status = searchResults['status']
		if status != '200 OK':
			return None

		# If the search succeeded but there are no results the data is returned as false
		data = searchResults['data']
		if data == False:
			return None

		return data

	def DownloadSubtitle(self, fileData, lang, searchResults):
		for searchResult in searchResults:
			# Verify we have the correct series name
			#episodeName = searchResult['MovieName']
			#seriesName = episodeName[1:episodeName.rfind('"')]
			#epData.series = seriesName

			# Get the subtitle Id
			IDSubtitleFile = searchResult['IDSubtitleFile']

			# Download the subtitle itself
			downloadResult = self.osProxy.DownloadSubtitles(self.token, [IDSubtitleFile])

			# Check status
			status = downloadResult['status']
			if status != '200 OK':
				continue;

			# Update teh video file with the IMDB Id
			fileData.imdbTitleId = searchResult['IDMovieImdb']
			
			# The data is returned in base64 format
			base64Data = ''
			if len(downloadResult['data']) > 0:
				base64Data = downloadResult['data'][0]['data']

			# Decode the data from base64 - we then get gzip data.
			gzipData = base64.standard_b64decode(base64Data)

			# We write the gzip data to a file
			tmpFile = os.path.join(fileData.fileDir, os.path.basename(fileData.fileName) + '.srt.gzip')
			fh = open(tmpFile, "wb")
			fh.write(gzipData)
			fh.close()

			# We then read the gzip data from the file with the gzip library
			fh = gzip.open(tmpFile, "rb")
			subData = fh.read()
			fh.close()

			# Delete the temp file
			os.remove(tmpFile)

			# And finally we have the raw data of the subtitle and save it to a subtitle file
			self.SaveSubtitleFile(fileData, lang, subData)

			return True

		return False


	def DownloadSubs(self, fileData, lang):
		try:		
			# Connect
			self.Connect()
			# Login to Open Subtitles
			self.LogIn()
		except:
			print("------ ERROR: Exception raised while connecting to Open Subtitles")
			traceback.print_exc(file=sys.stdout)
			print('-' * 60)
			return False

		try:	
			# Search subtitles for the movie/show
			searchResults = self.SearchSubs(fileData, lang)

			# If no subtitles found we exit
			if searchResults == None:
				self.LogOut()
				return False

			if len(searchResults) == 0:
				print("------ ERROR: Unexpected error - no subtitles although it suceeded " + fileData.fileName)
				self.LogOut()
				return False

			# Download the subtitle
			result = self.DownloadSubtitle(fileData, lang, searchResults)
			if False == result:
				print("------ ERROR: Failed to download subtitles for " + fileData.fileName)
				self.LogOut()
				return False			

			self.LogOut()
			return True
		except:
			print("------ ERROR: Exception raised while downloading from Open Subtitles (" + fileData.fileName + ")")
			traceback.print_exc(file=sys.stdout)
			print('-' * 60)
			self.LogOut()
			return False						

