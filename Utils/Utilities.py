import os, os.path
import string

# Known vid extensions
vidExtenstions = ['.avi','.mkv','.mp4']

def IsVidFile(file):
	ext = os.path.splitext(file)[1]
	return ext in vidExtenstions

def GetWordDelimiter(baseName):
	firstDot = baseName.find('.')
	if firstDot < 0:
		firstDot = len(baseName)

	firstSpace = baseName.find(' ')
	if firstSpace < 0:
		firstSpace = len(baseName)

	if firstDot < firstSpace:
		return '.'
	elif firstSpace < firstDot:
		return ' '
	else:
		return ''

def CaptalizeFirstLetters(dir, file):
	ext = os.path.splitext(file)[1]
	base = os.path.splitext(file)[0]

	delim = GetWordDelimiter(base)
	newBase = string.capwords(base, delim)

	src = os.path.abspath(os.path.join(dir, file))
	trgt = os.path.abspath(os.path.join(dir, newBase + ext))

	os.rename(src, trgt)

	return newBase + ext
