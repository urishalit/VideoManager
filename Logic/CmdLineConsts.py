from enum import Enum
# ---------------------------------------------------------
# Command line arguments
# ---------------------------------------------------------

# General
CMD_ARG_ACTION			= "action"
CMD_ARG_CONFIG_FILE		= "configfile"

# Folders
CMD_ARG_FOLDER			= "folder"
CMD_ARG_DOWNLOAD_DIR	= "downloaddir"
CMD_ARG_WORKING_DIR		= "workingdir"
CMD_ARG_SHOWS_DIR		= "showsdir"

# Email
CMD_ARG_NO_EMAIL		= "noemail"
CMD_ARG_EMAILS			= "emails"

# Actions
class Actions(Enum):
	full = 1
	init_dir = 2
	scan_dir = 3
