import base64
import gzip
import os
import os.path
import struct
import sys
import traceback
import xmlrpclib

from sub_downloader import SubDownloader

OpenSubtitlesUrl_Download = 'http://api.opensubtitles.org/xml-rpc'

OpenSubtitlesUrl_UserName = 'VidMngr'
OpenSubtitlesUrl_Password = 'Mov!esAndShows'

OpenSubtitlesUrl_UserAgent = 'VidMngr'


class OpenSubtitles(SubDownloader):
    def __init__(self):
        self.os_proxy = None
        self.token = None

    @staticmethod
    def get_hash(name):
        '''
        This hash function receives the name of the file and returns the hash code
        '''
        try:
            long_long_format = 'q'  # long long
            byte_size = struct.calcsize(long_long_format)
            f = open(name, 'rb')
            file_size = os.path.getsize(name)
            hash = file_size
            if file_size < 65536 * 2:
                return 'SizeError'

            for x in range(int(65536 / byte_size)):
                _buffer = f.read(byte_size)
                (l_value,) = struct.unpack(long_long_format, _buffer)
                hash += l_value
                hash &= 0xFFFFFFFFFFFFFFFF  # to remain as 64bit number

            f.seek(max(0, file_size - 65536), 0)
            for x in range(int(65536 / byte_size)):
                _buffer = f.read(byte_size)
                (l_value,) = struct.unpack(long_long_format, _buffer)
                hash += l_value
                hash &= 0xFFFFFFFFFFFFFFFF

            f.close()
            return '%016x' % hash

        except IOError:
            return 'IOError'

    def connect(self):
        # Connect to open subtitles server
        self.os_proxy = xmlrpclib.ServerProxy(OpenSubtitlesUrl_Download)
        if self.os_proxy is None:
            raise Exception('Failed connecting to Open subtitles')

    def login(self):
        # Log in to server
        login_data = self.os_proxy.login(OpenSubtitlesUrl_UserName, OpenSubtitlesUrl_Password, 'eng',
                                         OpenSubtitlesUrl_UserAgent)

        # Check status
        status = login_data['status']
        if status != '200 OK':
            raise

        self.token = login_data['token']

    def logout(self):
        try:
            self.os_proxy.logout(self.token)
        except Exception:
            pass

    def search_subs(self, file_data, lang):
        # Get episode hash
        ep_hash = self.get_hash(file_data.get_file_path())

        # Get file byte size
        file_size_bytes = os.path.getsize(file_data.get_file_path())

        search_results = self.os_proxy.SearchSubtitles(self.token, [
            {'moviehash': ep_hash, 'moviebytesize': str(file_size_bytes), 'sublanguageid': lang}])
        if not isinstance(search_results, dict):
            print('------ ERROR: Open subtitles bad response.')
            return None

        # Check status
        status = search_results['status']
        if status != '200 OK':
            return None

        # If the search succeeded but there are no results the data is returned as false
        data = search_results['data']
        if not data:
            return None

        return data

    def download_subtitle(self, file_data, lang, search_results):
        for searchResult in search_results:
            # Verify we have the correct series name
            # episodeName = searchResult['MovieName']
            # seriesName = episodeName[1:episodeName.rfind(''')]
            # epData.series = seriesName

            # Get the subtitle Id
            id_subtitle_file = searchResult['IDSubtitleFile']

            # Download the subtitle itself
            download_result = self.os_proxy.download_subtitles(self.token, [id_subtitle_file])

            # Check status
            status = download_result['status']
            if status != '200 OK':
                continue

            # Update teh video file with the IMDB Id
            file_data.imdb_title_id = searchResult['IDMovieImdb']

            # The data is returned in base64 format
            base64_data = ''
            if len(download_result['data']) > 0:
                base64_data = download_result['data'][0]['data']

            # Decode the data from base64 - we then get gzip data.
            gzip_data = base64.standard_b64decode(base64_data)

            # We write the gzip data to a file
            tmp_file = os.path.join(file_data.fileDir, os.path.basename(file_data.fileName) + '.srt.gzip')
            fh = open(tmp_file, 'wb')
            fh.write(gzip_data)
            fh.close()

            # We then read the gzip data from the file with the gzip library
            fh = gzip.open(tmp_file, 'rb')
            sub_data = fh.read()
            fh.close()

            # Delete the temp file
            os.remove(tmp_file)

            # And finally we have the raw data of the subtitle and save it to a subtitle file
            self.save_subtitle_file(file_data, lang, sub_data)

            return True

        return False

    def download_subs(self, file_data, lang):
        try:
            # Connect
            self.connect()
            # Login to Open subtitles
            self.login()
        except Exception:
            print('------ ERROR: Exception raised while connecting to Open subtitles')
            traceback.print_exc(file=sys.stdout)
            print('-' * 60)
            return False

        try:
            # Search subtitles for the movie/show
            search_results = self.search_subs(file_data, lang)

            # If no subtitles found we exit
            if search_results is None:
                self.logout()
                return False

            if len(search_results) == 0:
                print('------ ERROR: Unexpected error - no subtitles although it succeeded ' + file_data.fileName)
                self.logout()
                return False

            # Download the subtitle
            result = self.download_subtitle(file_data, lang, search_results)
            if not result:
                print('------ ERROR: Failed to download subtitles for ' + file_data.fileName)
                self.logout()
                return False

            self.logout()
            return True
        except Exception:
            print('------ ERROR: Exception raised while downloading from Open subtitles (' + file_data.fileName + ')')
            traceback.print_exc(file=sys.stdout)
            print('-' * 60)
            self.logout()
            return False
