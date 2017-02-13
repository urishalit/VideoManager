import os.path
from abc import ABCMeta, abstractmethod

SearchLanguages = ['en']

sub_downloaders = []


def register_sub_downloader(downloader):
    sub_downloaders.append(downloader)
    return downloader


class SubDownloader(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def download_subs(self, file_data, lang):
        pass

    @classmethod
    def get_subtitle_file_path(cls, file_data, lang):
        return os.path.join(file_data.file_dir, file_data.file_name[:file_data.file_name.rfind('.')] + '-' + lang +
                            '.srt')

    def save_subtitle_file(self, file_data, lang, content):
        # Construct sub file path
        sub_file_path = self.get_subtitle_file_path(file_data, lang)

        # Save subtitle to file
        sub_file = open(sub_file_path, 'wb')
        sub_file.write(content)
        sub_file.close()

        # Add to associated files
        file_data.add_associated_file(sub_file_path)
