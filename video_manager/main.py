import sys
import os.path
import traceback

# Add paths of scripts to paths Python looks for scripts in.
from logic.cmd_line_parser import parse_cmd_line

from logic import video_organizer

sys.path.append(os.path.abspath('logic'))
sys.path.append(os.path.abspath(os.path.join('logic', 'data')))
sys.path.append(os.path.abspath('subtitles'))
sys.path.append(os.path.abspath('utils'))


def main():
    vid_organizer = None
    try:
        # Load the Config File data
        configData = parse_cmd_line()
        if None != configData:
            # Start the Video Organizer
            vid_organizer = video_organizer(configData)
            vid_organizer.start()
    except Exception:
        print('Exiting due to error...')
        traceback.print_exc()

    if vid_organizer is not None:
        vid_organizer.Stop()
    print('Exiting...')


if __name__ == "__main__":
    main()
