import json
import os.path
import sys
from copy import deepcopy

from cmd_line_consts import *
from config import CONFIG

CONFIGURATION_FILE_NAME = 'config.py'


def get_parameter_value(arg_name, default_value=None, prefix='-', suffix='='):
    arg_to_find = prefix + arg_name + suffix
    for arg in sys.argv:
        index = arg.find(arg_to_find)
        if index > -1:
            value = arg[index + len(arg_to_find):]
            if len(value) == 0:
                return True
            else:
                return value

    return default_value


def display_help():
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
    print('	    \t        them. If action is not given this will be the default')
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
    print('   -folder=\t\tThe folder to scan & work in. If \'showsdir\' is not')
    print('           \t\tdefined the files will not be moved at all.')
    print('')
    print('   -downloaddir=\tThe folder to scan for new downloaded files')
    print('')
    print('   -workingdir=\t\tThe folder to copy files to where they will be renamed.')
    print('          \t\tThis folder is used mainly if you do not want to change')
    print('          \t\tthe download directory as it is still seeding.')
    print('          \t\tDownloaded files that don\'t have subtitles yet will stay')
    print('          \t\tin this directory until they are ready with subs - and')
    print('          \t\tthen moved to the matching directory')
    print('')
    print('   -showsdir=\t\tThe root folder to place episodes that are ready to')
    print('          \t\twatch (renamed and with subtitles).')
    print('')
    print('   -moviesdir=\t\tThe root folder to place movies that are ready to')
    print('          \t\twatch (renamed and with subtitles).')
    print('')
    print('   -noemails=\t\tSet no emails to be set. If there is a config file')
    print('          \t\tpresent with emails - this will override it.')
    print('')
    print('   -emails=\t\tA comma seperated list of emails to send notifications')
    print('          \t\tto. If there is a config filepresent with emails - this')
    print('          \t\twill override it.')
    print('')


def display_config_help():
    print('ConfigHelp: TBD')


def display_help_if_needed():
    # First check if the general is help was asked for
    isHelp = get_parameter_value('help', False, '-', '')
    if isHelp:
        display_help()
        return True

    # Then check if the config help was asked for
    isConfigHelp = get_parameter_value('confighelp', False, '-', '')
    if isConfigHelp:
        display_config_help()
        return True

    return False


def get_default_config_file_path():
    dir = os.path.dirname(sys.argv[0])
    if dir == '':
        dir = os.getcwd()

    return os.path.join(dir, CONFIGURATION_FILE_NAME)


def load_config_file(config_file):
    # if no config file - display error and exit
    if not os.path.isfile(config_file):
        print(config_file + ' does not exist.')
        sys.exit()

    # Read config file data
    h_file = open(config_file, 'r')
    config_str = h_file.read()
    h_file.close()

    # Parse config data
    try:
        config_data = json.loads(config_str)
    except:
        print('Invalid config data - error parsing. ')
        raise

    return config_data


def parse_cmd_line():
    # If we display the help we return without parsing further the command line. As the program should exit.
    if display_help_if_needed():
        return None

    try:
        action_name = get_parameter_value(CMD_ARG_ACTION, Actions.full.name)
        # Get the action requested
        action = Actions[action_name]
    except Exception:
        print('ERROR: Unknown action: ' + action_name)
        return None

    # Get the configuration data
    config_data = deepcopy(CONFIG)
    # Add the action to the configData
    config_data['action'] = action

    # Initiate directories to blank
    download_dir = ''
    working_dir = ''
    shows_dir = ''
    movies_dir = ''

    # Given the folder argument all directories will be set by default to this folder
    folder = get_parameter_value(CMD_ARG_FOLDER)
    if len(folder) > 0:
        download_dir = folder
        working_dir = folder
        shows_dir = folder
        movies_dir = folder

    # Check if there is a download directory to override the one in the config file
    download_dir = get_parameter_value(CMD_ARG_DOWNLOAD_DIR, download_dir)
    if len(download_dir) > 0:
        config_data['DownloadDirectory'] = download_dir

    # Check if there is a working directory to override the one in the config file
    working_dir = get_parameter_value(CMD_ARG_WORKING_DIR, working_dir)
    if len(working_dir) > 0:
        config_data['WorkingDirectory'] = working_dir

    # Check if there is a shows target directory to override the one in the config file
    shows_dir = get_parameter_value(CMD_ARG_SHOWS_DIR, shows_dir)
    if len(shows_dir) > 0:
        config_data['TVShows']['TargetDirectory'] = shows_dir

    # Check if there is a shows target directory to override the one in the config file
    movies_dir = get_parameter_value(CMD_ARG_MOVIES_DIR, movies_dir)
    if len(movies_dir) > 0:
        config_data['Movies']['TargetDirectory'] = movies_dir

    no_emails = get_parameter_value(CMD_ARG_NO_EMAIL, False, '-', '')
    emails = get_parameter_value(CMD_ARG_EMAILS)

    if no_emails and len(emails) > 0:
        print('ERROR: Cannot use no emails flags with the emails flag - Contracdiction!')
        return None

    # If user defined not to send emails - we override the email list by an empty list
    if no_emails:
        config_data['Emails'] = []

    # If user defined emails to send to - we override the email list given in the config file
    if len(emails) > 0:
        # Parse the emails list string to a list
        if emails.find(','):
            emails = emails.split(',')
        else:
            emails = [emails]

        config_data['Emails'] = emails

    return config_data
