import sys
import os.path
import json
import traceback

# Add paths of scripts to paths Python looks for scripts in.
sys.path.append(os.path.abspath('Logic'))
sys.path.append(os.path.abspath(os.path.join('Logic', 'Data')))
sys.path.append(os.path.abspath('Subtitles'))
sys.path.append(os.path.abspath('Utils'))

# My files
from CmdLineParser import ParseCmdLine
from VideoOrganizer import VideoOrganizer

def main():
	try:
		# Load the Config File data
		configData = ParseCmdLine()
		if None != configData:
			# Start the Video Organizer
			vidOrganizer = VideoOrganizer(configData)
			vidOrganizer.Start()
	except Exception:
		print('Exiting due to error...')
		traceback.print_exc(file=sys.stdout)

	vidOrganizer.Stop()
	print('Exiting...')

if __name__ == "__main__":
    main()