import sys
import os.path
import json

# Add paths of scripts to paths Python looks for scripts in.
sys.path.append(os.path.abspath('Logic'))
sys.path.append(os.path.abspath('Subtitles'))
sys.path.append(os.path.abspath('Utils'))

# My files
from VideoOrganizer import VideoOrganizer

CONFIGURATION_FILE_NAME = "config.json"

ACTION_FULL = "full"
ACTION_INIT_DIR = "init_dir"

def GetParameterValue(argName, defaultValue = "", prefix='-', suffix='='):
	argToFind = prefix + argName + suffix
	for arg in sys.argv:
		index = arg.find(argToFind) 
		if index > -1:
			return arg[index + len(argToFind):]

	return defaultValue


def GetDefaultConfigFilePath():
	dir = os.path.dirname(sys.argv[0])
	if dir == '':
		dir = os.getcwd()

	return os.path.join(dir, CONFIGURATION_FILE_NAME)

def LoadConfigFile(configFile):
	# if no config file - display error and exit
	if not os.path.isfile(configFile):
		print(configFile + " does not exist.")
		sys.exit()

	# Read config file data
	hFile = open(configFile, 'r')
	configStr = hFile.read()
	hFile.close()

	# Parse config data
	try:
		configData = json.loads(configStr)
	except:
		print('Invalid config data - error parsing. ')
		print(sys.exc_info()[0])
		sys.exit()

	return configData

def main():
	try:
		# If given a config file path in command line - use it - otherwise look for it in the same directory
		configFile = GetParameterValue("configFile", GetDefaultConfigFilePath())

		# Load the Config File data
		configData = LoadConfigFile(configFile)

		# Get the action requested	
		action = GetParameterValue("action", ACTION_FULL)

		# Start the Video Organizer
		vidOrganizer = VideoOrganizer(configData)

		if action.lower() == ACTION_INIT_DIR:
			# Initiate Directory
			vidOrganizer.InitDir()
		elif action.lower() == ACTION_FULL:
			# Start the Video Manager
			vidOrganizer.StartFully()
		else:
			print('ERROR: Unknown action (' + action + ')')
	except:
		print('Exiting due to error...')
		traceback.print_exc(file=sys.stdout)

if __name__ == "__main__":
    main()