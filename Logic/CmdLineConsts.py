from enum import Enum
# Command line arguments
CMD_ARG_ACTION		= "action"
CMD_ARG_CONFIG_FILE	= "configfile"

# Actions
class Actions(Enum):
	full = 1
	init_dir = 2
	scan_dir = 3
