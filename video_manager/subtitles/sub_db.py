import hashlib
import os
import os.path

from httplib2 import Http

from sub_downloader import SubDownloader

SubDBUrl_Search = "http://api.thesubdb.com/?action=search&hash=HASH_ALIAS"
SubDBUrl_Download = "http://api.thesubdb.com/?action=download&hash=HASH_ALIAS&language=LANGUAGE_ALIAS"

MyUserAgent = "SubDB/1.0 (Shalit/0.1; http://none)"


class SubDB(SubDownloader):
    # this hash function receives the name of the file and returns the hash code
    @staticmethod
    def get_hash(name):
        read_size = 64 * 1024
        with open(name, 'rb') as f:
            data = f.read(read_size)
            f.seek(-read_size, os.SEEK_END)
            data += f.read(read_size)
        return hashlib.md5(data).hexdigest()

    def download_subs(self, file_data, lang):
        # Start an http object
        h = Http()

        # Get episode hash
        ep_hash = self.get_hash(file_data.get_file_path())

        # Construct Url
        url = SubDBUrl_Search.replace('HASH_ALIAS', ep_hash)

        # Search for subs
        resp, content = h.request(url, "GET", headers={'user-agent': MyUserAgent})
        if resp.status != 200:
            return False

        # Get supported languages that actually interest us.
        langs_found = str(content)[2:-1].split(',')
        if lang not in langs_found:
            return False

        # Download subtitles for all languages
        # Construct Url
        url = SubDBUrl_Download.replace('HASH_ALIAS', ep_hash)
        # Replace language alias in url
        url = url.replace('LANGUAGE_ALIAS', lang)
        # Download subtitle
        resp, content = h.request(url, "GET", headers={'user-agent': MyUserAgent})
        if resp.status != 200:
            return False

        # Save the subtitle file
        self.save_subtitle_file(file_data, lang, content)

        return True
