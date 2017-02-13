import argparse
import sys
from copy import deepcopy

from config import CONFIG

CONFIGURATION_FILE_NAME = 'config.py'
HELP = """
    Video Manager is a program designed to help you organize your videos (TV Shows & Movies).
    Basic Actions:
       1. Download subtitles (one language or more).
       2. Rename the files to a format.
       3. Move the files with their subs to their matching directory.
       4. Send status e-mails when new files were downloaded/ready to watch.
    """

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


def get_arg_parser():
    parser = argparse.ArgumentParser()
    #parser.add_help(str(HELP))
    parser.add_argument('-cf', '--config-file', help='Path to a configuration file.')
    parser.add_argument('--action', choices=['full', 'init_dir', 'scan_dir'], default='full', help="""
    Action to take:
    \tfull    \tFull execution: will wait for new files and process (this is the default)
    \tinit_dir\tEach time the Video Manager is executed it will look for new files added in the download directory. If it is the first time you are executing it or you want it to ignorethe current files in the \'Download Directory\',' execute it once using this action.'
    \tscan_dir\tWill have the VideoManager scan and process a specific folder. According to the rest of the flags it will know what to with it.'
    """)
    parser.add_argument('-f', '--folder',
                        help='The folder to scan & work in. If \'showsdir\' is not defined the files will not be moved at all.')
    parser.add_argument('-dd', '--download-dir', default=CONFIG['DownloadDirectory'],
                        help='The folder to scan for new downloaded files')
    parser.add_argument('-wd', '--working-dir', default=CONFIG['WorkingDirectory'],
                        help='The folder to copy files to where they will be renamed. This folder is used mainly if you do not want to change the download directory as it is still seeding. Downloaded files that don\'t have subtitles yet will stay in this directory until they are ready with subs - and then moved to the matching directory')
    parser.add_argument('-sd', '--shows-dir', default=CONFIG['TVShows']['TargetDirectory'],
                        help='The root folder to place episodes that are ready to watch (renamed and with subtitles).')
    parser.add_argument('-md', '--movies-dir', default=CONFIG['Movies']['TargetDirectory'],
                        help='The root folder to place movies that are ready to watch (renamed and with subtitles).')
    emails = parser.add_mutually_exclusive_group()
    emails.add_argument('-e', '--emails', nargs='+', default=CONFIG['Emails'],
                        help='A space separated list of emails to send notifications to.')
    emails.add_argument('-ne', '--no-emails', action='store_true', help='Do not send emails')

    return parser


def parse_cmd_line():
    parser = get_arg_parser()
    args = parser.parse_args()

    # Get the configuration data
    config_data = deepcopy(CONFIG)
    config_data['action'] = args.action
    config_data['DownloadDirectory'] = args.download_dir
    config_data['WorkingDirectory'] = args.working_dir
    config_data['TVShows']['TargetDirectory'] = args.shows_dir
    config_data['Movies']['TargetDirectory'] = args.movies_dir
    if args.no_emails:
        config_data['Emails'] = []
    else:
        config_data['Emails'] = args.emails

    return config_data
