from httplib2 import Http
from VidFileData import VidFileData
import os.path
import hashlib
import os
from SubDownloader import SubDownloader

SubDBUrl_Search = "http://api.thesubdb.com/?action=search&hash=HASH_ALIAS"
SubDBUrl_Download = "http://api.thesubdb.com/?action=download&hash=HASH_ALIAS&language=LANGUAGE_ALIAS"

MyUserAgent = "SubDB/1.0 (Shalit/0.1; http://none)"

class SubDB(SubDownloader):
	#this hash function receives the name of the file and returns the hash code
	def get_hash(self, name):
	    readsize = 64 * 1024
	    with open(name, 'rb') as f:
	        size = os.path.getsize(name)
	        data = f.read(readsize)
	        f.seek(-readsize, os.SEEK_END)
	        data += f.read(readsize)
	    return hashlib.md5(data).hexdigest()

	def DownloadSubs(self, fileData, lang):
		# Start an http object
		h = Http()

		# Get episode hash
		epHash = self.get_hash(fileData.GetFilePath())

		# Construct Url
		url = SubDBUrl_Search.replace('HASH_ALIAS', epHash)

		# Search for subs
		resp, content = h.request(url, "GET", headers={'user-agent': MyUserAgent})
		if (resp.status != 200):
			return False

		# Get supported languages that actually interest us.
		langsFound = str(content)[2:-1].split(',')
		if lang not in langsFound:
			return False

		# Download subtitles for all languages
		# Construct Url
		url = SubDBUrl_Download.replace('HASH_ALIAS', epHash)
		# Replace language alias in url
		url = url.replace('LANGUAGE_ALIAS', lang)
		# Download subtitle
		resp, content = h.request(url, "GET", headers={'user-agent': MyUserAgent})
		if (resp.status != 200):
			return False

		# Save the subtitle file
		self.SaveSubtitleFile(fileData, lang, content)

		return True

