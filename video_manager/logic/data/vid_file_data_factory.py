import os
import os.path

from guessit import guess_file_info

from episode_data import EpisodeData
from movie_data import MovieData


def GetVidFileData(dir, file, configData):
    fileDir = dir
    fileName = file

    # 3rd party function to guess according to the file name if movie or tv show
    fileInfo = guess_file_info(fileName)
    if None == fileInfo:
        return None

    # According to the guessed type we create the object
    vidType = fileInfo.get('type', '')

    vidFileData = None
    if 'episode' == vidType:
        # Get Episode information
        series = fileInfo.get('series', '')
        season = fileInfo.get('season', '')
        episodeNumber = fileInfo.get('episodeNumber', '')

        # Get episode suffix
        format = fileInfo.get('format', '')
        basename = os.path.splitext(fileName)[0]
        suffix = basename[basename.lower().find(format.lower()) - 1:]

        # Create Episode Data Object
        vidFileData = EpisodeData(configData, series, season, episodeNumber, fileDir, fileName, suffix)
    elif 'movie' == vidType:
        # Get Movie information
        title = fileInfo.get('title', '')
        year = fileInfo.get('year', '')

        # Creeate Movie Data Object
        vidFileData = MovieData(configData, title, year, fileDir, fileName)

    return vidFileData
