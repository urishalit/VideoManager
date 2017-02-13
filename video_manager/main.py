import traceback

from logic.cmd_line_parser import parse_cmd_line
from logic.video_organizer import VideoOrganizer


def main():
    vid_organizer = None
    try:
        # Load the Config File data
        config_data = parse_cmd_line()
        if config_data is not None:
            # Start the Video Organizer
            vid_organizer = VideoOrganizer(config_data)
            vid_organizer.start()
    except Exception:
        print('Exiting due to error...')
        traceback.print_exc()

    if vid_organizer is not None:
        vid_organizer.stop()
    print('Exiting...')


if __name__ == "__main__":
    main()
