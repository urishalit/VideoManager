import sys
import os
import os.path
from FileManipulations import ReplaceInAllFileNames
import glob

if len(sys.argv) < 2:
	print('Missing directory')
	sys.exit()

dir = sys.argv[1]

if len(glob.glob(dir)) == 0:
	print(dir + " has no files")
	sys.exit()

filter = os.path.join(dir, '*.srt')

ReplaceInAllFileNames(filter, "-heb", "")
ReplaceInAllFileNames(filter, "-eng", "")


