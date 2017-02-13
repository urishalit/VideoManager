from vid_file_data import VidFileData
from vid_file_data import VideoType


class MovieData(VidFileData):
    def __init__(self, config_data, title, year, file_dir, file_name):
        super(MovieData, self).__init__(config_data, file_dir, file_name, '')
        self.title = title
        self.year = str(year)
        self.type = VideoType.movie
        self.initiate_target_directory(config_data["Movies"]["TargetDirectory"])

    def get_movie_title(self):
        return self.title

    def get_movie_year(self):
        return self.year

    def get_notification_text(self):
        if len(self.imdb_title_id) > 0:
            return self.generate_link_text()
        else:
            return self.generate_plain_text()

    def generate_link_text(self):
        text = '<a href=\"http://www.imdb.com/title/tt'
        text += str(self.imdb_title_id)
        text += '\" target=\"_blank\">'
        text += self.generate_plain_text()
        text += '</a>'

        return text

    def generate_plain_text(self):
        text = self.title
        if len(self.year) > 0:
            text += ' (' + self.year + ')'

        return text

    def get_notification_title(self):
        return self.get_movie_title()
