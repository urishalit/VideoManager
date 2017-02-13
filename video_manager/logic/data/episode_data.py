import os.path
import os

from vid_file_data import VidFileData
from vid_file_data import VideoType


class EpisodeData(VidFileData):
    def __init__(self, config_data, series, season, episode, file_dir, file_name, suffix):
        super(EpisodeData, self).__init__(config_data, file_dir, file_name, suffix)
        self.series = str(series)
        self.season = '%02d' % season
        self.episode = '%02d' % episode
        self.type = VideoType.tvShow
        self.initiate_target_directory(config_data['TVShows']['TargetDirectory'])

    def get_series_name(self):
        return self.series.replace('.', ' ')

    def get_season(self):
        return str(int(self.season))

    def get_episode_number(self):
        return str(int(self.episode))

    def get_notification_text(self):
        return self.get_series_name() + ' - S' + self.season + 'E' + self.episode

    def get_notification_title(self):
        return self.get_series_name()

    def rename_to_format(self):
        # Construct new file name
        new_file = '{series_name}.S{season}E{episode}{suffix}{extension}'.format(
            series_name=self.series.replace(' ', '.'), season=self.season,
            episode=self.episode, suffix=self.suffix, extension=self.get_vid_extension())

        self.rename_file(self.file_dir, new_file)

    def move_to_target_directory(self):
        # Construct Target Dir - RootDir\Series\Season X
        target_path = os.path.join(self.target_root_dir, self.get_series_name(), 'Season %s' % self.get_season())

        self.move_to_dir(target_path)
