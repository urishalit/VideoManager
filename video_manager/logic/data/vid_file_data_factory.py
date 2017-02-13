import os
import os.path

from guessit import guess_file_info

from episode_data import EpisodeData
from movie_data import MovieData


def get_vid_file_data(dir, file, config_data):
    file_dir = dir
    file_name = file

    # 3rd party function to guess according to the file name if movie or tv show
    file_info = guess_file_info(file_name)
    if None == file_info:
        return None

    # According to the guessed type we create the object
    vid_type = file_info.get('type', '')

    vid_file_data = None
    if 'episode' == vid_type:
        # Get Episode information
        series = file_info.get('series', '')
        season = file_info.get('season', '')
        episode_number = file_info.get('episodeNumber', '')

        # Get episode suffix
        format = file_info.get('format', '')
        basename = os.path.splitext(file_name)[0]
        suffix = basename[basename.lower().find(format.lower()) - 1:]

        # Create Episode Data Object
        vid_file_data = EpisodeData(config_data, series, season, episode_number, file_dir, file_name, suffix)
    elif 'movie' == vid_type:
        # Get Movie information
        title = file_info.get('title', '')
        year = file_info.get('year', '')

        # Create Movie Data Object
        vid_file_data = MovieData(config_data, title, year, file_dir, file_name)

    return vid_file_data
