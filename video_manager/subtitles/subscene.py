import os
import urllib2
import zipfile

from logic import context
from logic.data.episode_data import EpisodeData
from logic.data.vid_file_data import VidFileData
from logic.data.vid_file_data_factory import get_vid_file_data
from subscene_api import Subscene
from subtitles.sub_downloader import SubDownloader


LANGUAGE_MAP = {
    'eng': 'English',
    'heb': 'Hebrew',
}


class SubSceneWrapper(SubDownloader):
    def download_subs(self, file_data, lang):
        api = Subscene()

        results = api.search(file_data.file_name)
        subtitles = [x for x in results.subtitles if x.language == LANGUAGE_MAP[lang]]
        subtitle = self._find_best_match(subtitles, file_data)
        if subtitle is None:
            return False

        content = self._download_subtitle(subtitle)

        self.save_subtitle_file(file_data, lang, content)

        return True

    @staticmethod
    def _download_subtitle(subtitle):
        zip_link = subtitle.get_zip_link()
        req = urllib2.Request(
            zip_link,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )

        zip_content = urllib2.urlopen(req).read()
        zip_file = os.path.join(context.config['WorkingDirectory'], subtitle.title + '.zip')
        with open(zip_file, 'wb') as f:
            f.write(zip_content)

        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            if len(zip_ref.namelist()) != 1:
                content = None
            else:
                content = zip_ref.read(zip_ref.namelist()[0])

        os.remove(zip_file)

        return content

    @classmethod
    def _find_best_match(cls, subtitles, file_data):
        max_score = 0
        best_match = None
        for subtitle in subtitles:
            vid_file_data = get_vid_file_data('', file_data.file_name + file_data.suffix, None)
            sub_file_data = get_vid_file_data('', subtitle.title, None)
            if type(vid_file_data) != type(sub_file_data):
                continue

            if isinstance(vid_file_data, EpisodeData):
                score = cls._compare_episodes(vid_file_data, sub_file_data)
            else:
                score = cls._compare_movies(vid_file_data, sub_file_data)

            if score > max_score:
                max_score = score
                best_match = subtitle

        return best_match

    @classmethod
    def _compare_episodes(cls, vid_file_data, sub_file_data):
        if vid_file_data.series != sub_file_data.series or vid_file_data.season != sub_file_data.season or \
                        vid_file_data.episode != sub_file_data.episode:
            return -1

        if vid_file_data.suffix.lower() != sub_file_data.suffix.lower():
            if vid_file_data.suffix.lower().find(sub_file_data.suffix.lower()) >= 0:
                return 3

            if sub_file_data.suffix.lower().find(vid_file_data.suffix.lower()) >= 0:
                return 3

            if cls._get_last_suffix_word(vid_file_data.suffix.lower()) != \
                    cls._get_last_suffix_word(sub_file_data.suffix.lower()):
                return 1
            else:
                return 2

        return 4

    @classmethod
    def _compare_movies(cls, vid_file_data, sub_file_data):
        if vid_file_data.title != sub_file_data.title:
            return -1

        if vid_file_data.year != sub_file_data.year:
            return 1

        return 2

    @staticmethod
    def _get_last_suffix_word(suffix):
        last_dot = suffix.rfind('.')
        if last_dot < 0:
            return ''
        return suffix[:last_dot]

if __name__ == '__main__':
    s = SubSceneWrapper()
    s.download_subs(
        VidFileData({'WorkingDirectory': ''}, r'F:\Downloads\test\tv\Kevin Can Wait\Season 1', 'Kevin.Can.Wait.S01E01', '.Hdtv.X264-killers'),
        'eng')
