import sys
import os
import re
import string
from EpisodeData import EpisodeData
from SubDB import SubDB

class VideoOrganizer:
	def __init__(config):
		print(config)
		
def CaptalizeFirstLetters(dir, file):
	ext = os.path.splitext(file)[1]
	base = os.path.splitext(file)[0]

	newBase = string.capwords(base, '.')

	src = os.path.abspath(os.path.join(dir, file))
	trgt = os.path.abspath(os.path.join(dir, newBase + ext))

	os.rename(src, trgt)

	return newBase + ext

def ValidateEpisodeNumber(dir, file):
	# Divide extension and file name
	ext = os.path.splitext(file)[1]
	base = os.path.splitext(file)[0]

	# Check if we can get episode information about the file
	episodeInfo = re.search(r"(?:s|season)(\d{2})(?:e|x|episode|\n)(\d{2})", base, re.I)
	if episodeInfo == None:
		print('Problem formatting episode number for ' + base)
		return file

	# Get the series name from the file
	series = base[:episodeInfo.span()[0] - 1]
	suffix = base[episodeInfo.span()[1]:]

	# Get the Episode season & episode number
	episodeInfo = re.findall(r"(?:s|season)(\d{2})(?:e|x|episode|\n)(\d{2})", base, re.I)
	season = episodeInfo[0][0]
	episode = episodeInfo[0][1]

	# Construct new file name
	newFile = series + "." + "S" + season + "E" + episode + suffix + ext;

	# Rename file
	os.rename(os.path.join(dir, file), os.path.join(dir, newFile))

	return EpisodeData(series, season, episode, dir, newFile)


def OrganizeEpisode(dir, file):
	print("OrganizeEpisode - " + file)
	if isVidFile(file):
		# Capitize First letters of every word
		file = CaptalizeFirstLetters(dir, file)
		# Parse episode data & rename file to proper format 
		epData = ValidateEpisodeNumber(dir, file)

		subGetter = SubDB()
		x = subGetter.DownloadSubs(epData)
		print("DownloadSubs From SUBDB: " + str(x))

def OrganizeEpisodes(dir):
	print("OrganizeEpisodes - " + dir)
	if not os.path.isdir(dir):
		print("No files to capatilize")
		sys.exit()

	for file in os.listdir(dir):
		OrganizeEpisode(dir, file)

def Organize(path):
	if os.path.isdir(path):
		return OrganizeEpisodes(path)
	elif os.path.isfile(path):
		return OrganizeEpisode(os.path.dirname(path), os.path.basename(path))

def main():
	if len(sys.argv) < 2:
		print('Missing directory.\n')
		print('usage: ReplaceInAllFiles.py <directoy> <look-for> <replace-with>')
		sys.exit()

	dir = sys.argv[1]

	Organize(dir)

if __name__ == "__main__":
    main()
