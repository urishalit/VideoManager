import sys
import os.path
import json
import traceback

# My files
from CmdLineConsts import *

CONFIGURATION_FILE_NAME = "config.json"

def GetParameterValue(argName, defaultValue = "", prefix='-', suffix='='):
	argToFind = prefix + argName + suffix
	for arg in sys.argv:
		index = arg.find(argToFind)
		if index > -1:
			value = arg[index + len(argToFind):]
			if len(value) == 0:
				return True
			else:
				return value

	return defaultValue

def DisplayHelp():
	print('     Video Manager')
	print('  -------------------')
	print('Video Manager is a program designed to help you organize your videos (TV Shows & Movies).')
	print('')
	print('Basic Actions:')
	print('   1. Download subtitles (one language or more).')
	print('   2. Rename the files to a format.')
	print('   3. Move the files with their subs to their matching directory')
	print('   4. Send status e-mails when new files were downloaded/ready to watch.')
	print('')
	print('Command line arguments:')
	print('   -help\t\tDisplay this help section')
	print('')
	print('   -configFile=\t\tPath to a configuration file. ')
	print('')
	print('   -confighelp\t\tDisplay a detailed explanation of the config')
	print('              \t\tfile format')
	print('')
	print('   -action=\t\tThe action you want to perform. Valid values: ')
	print('     \tfull    \tFull execution: will wait for new files and process')
	print('	    \t        them.')
	print('     \t        \tand process any exisiting files that may need')
	print('     \t        \tprocessing.')
	print('     \tinit_dir\tEach time the Video Manager is executed it will look')
	print('     \t        \tfor new files added in the download directory. If it is')
	print('     \t        \tthe first time you are executing it or you want it to')
	print('     \t        \tignorethe current files in the \'Download Directory\',')
	print('     \t        \texecute it once using this action.')
	print('     \tscan_dir\tWill have the VideoManager scan and process a specific')
	print('     \t        \tfolder. According to the rest of the flags it will know')
	print('     \t        \twhat to with it.')
	print('')
	print('     \tDefault Value: full')
	print('')

def DisplayConfigHelp():
	print('ConfigHelp: TBD')

def DisplayHelpIfNeeded():
	# First check if the genereal is help was asked for
	isHelp = GetParameterValue('help', False, '-', '')
	if isHelp:
		DisplayHelp()
		return True

	# Then check if the config help was asked for
	isConfigHelp = GetParameterValue('confighelp', False, '-', '')
	if isConfigHelp:
		DisplayConfigHelp()
		return True

	return False

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
		raise

	return configData

def GetConfigData():
	try:
		# If given a config file path in command line - use it - otherwise look for it in the same directory
		configFile = GetParameterValue(CMD_ARG_CONFIG_FILE, GetDefaultConfigFilePath())
		# Load the Config File data
		configData = LoadConfigFile(configFile)
	except:
		print('-- No valid Config file given - using defaults.')
		traceback.print_exc(file=sys.stdout)
		configData = dict()

	return configData

def ParseCmdLine():
	# If we display the help we return without parsing further the command line. As the program should exit.
	if DisplayHelpIfNeeded():
		return None

	try:
		actionName = GetParameterValue(CMD_ARG_ACTION, Actions.full.name)
		# Get the action requested
		action = Actions[actionName]
	except:
		print('ERROR: Unknown action: ' + actionName)
		return None

	# Get the configuration data
	configData = GetConfigData()
	# Add the action to the configData
	configData['action'] = action
	return configData
