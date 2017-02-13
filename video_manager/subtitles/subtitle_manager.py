import os.path

from open_subtitles import OpenSubtitles
from sub_downloader import SubDownloader


class SubtitleManager(object):
    def __init__(self, config_data):
        self.config_data = config_data
        self.languages = self.config_data['SubtitleLanguages']
        self.downloaders = [OpenSubtitles()]

    def download_subtitles(self, file_data):
        print('------ Attempting to download subtitles')
        languages = list(self.languages)
        # If no languages configured skipping this phase
        if not languages:
            print('------ No subtitle language configured.')
            return True

        # Iterate over all downloaders until all subtitles in all languages are acquired.
        found_languages = []
        for downloader in self.downloaders:
            if isinstance(downloader, SubDownloader):
                for lang in languages:
                    # If exists already a subtitle file for this language - we skip it.
                    sub_path = downloader.get_subtitle_file_path(file_data, lang)
                    if os.path.exists(sub_path):
                        found_languages.append(lang)
                        file_data.add_associated_file(sub_path)
                        continue

                    # Attempt downloading subtitle for language
                    res = downloader.download_subs(file_data, lang)
                    if res:
                        found_languages.append(lang)

                # Remove found languages from languages
                languages = list(set(languages) - set(found_languages))
                found_languages = []

        # Only if there are no remaining languages we return True
        if not languages:
            result = True
            print('------ Successfully downloaded subtitles')
        else:
            result = False
            print('------ Did not find subtitles for ' + ','.join(map(str, languages)))

        return result
