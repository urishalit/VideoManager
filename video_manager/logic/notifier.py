import threading
from enum import Enum

from logic.data.vid_file_data import VideoType
from utils.email_sender import send_email

maps_lock = threading.Lock()

STAGING_TITLE = 'Pending VIDEOS'
STAGING_CAPTION = 'The following VIDEOS have been downloaded and are waiting to get subtitles'

READY_TITLE = 'Ready VIDEOS'
READY_CAPTION = 'The following VIDEOS are ready to watch'

DOWNLOADED_TITLE = 'Newly Downloaded VIDEOS'
DOWNLOADED_CAPTION = 'The following VIDEOS are newly downloaded'


class NotifyFileType(Enum):
    Ready = 1
    Downloaded = 2
    Staging = 3


class Notifier:
    def __init__(self, config_data):
        self.config_data = config_data
        self.email_list = config_data["Emails"]
        self.maps = dict()
        self.maps[VideoType.tv_show] = dict()
        self.maps[VideoType.movie] = dict()
        self.clear_all_lists()

    def clear_all_lists(self):
        for vidType in VideoType:
            self.clear_lists(vidType)

    def clear_lists(self, vid_type):
        for notify_type in NotifyFileType:
            self.maps[vid_type][notify_type] = []

    def add_file(self, notify_type, file_data):
        maps_lock.acquire()
        # First we check if this video has already been added to this list
        found = False
        for data in self.maps[file_data.get_type()][notify_type]:
            if file_data.equals(data):
                found = True
                break

        # Only if it's the first time this video is added to the list we add it.
        if not found:
            self.maps[file_data.get_type()][notify_type].append(file_data)

        maps_lock.release()

    def remove_file(self, notify_type, file_data):
        maps_lock.acquire()
        try:
            self.maps[file_data.get_type()][notify_type].remove(file_data)
        except KeyError:
            pass
        maps_lock.release()

    def add_ready_file(self, file_data):
        self.add_file(NotifyFileType.Ready, file_data)
        # In case the file is also in the staging list we remove it - as it is ready
        self.remove_file(NotifyFileType.Staging, file_data)

    def add_staging_file(self, file_data):
        self.add_file(NotifyFileType.Staging, file_data)

    def add_downloaded_file(self, file_data):
        self.add_file(NotifyFileType.Downloaded, file_data)

    def get_vids(self, vid_type, notify_type):
        return self.maps[vid_type][notify_type]

    def get_title_and_caption(self, vid_type, notify_type):
        if notify_type is NotifyFileType.Ready:
            title = READY_TITLE
            caption = READY_CAPTION
        elif notify_type is NotifyFileType.Staging:
            title = STAGING_TITLE
            caption = STAGING_CAPTION
        elif notify_type is NotifyFileType.Downloaded:
            title = DOWNLOADED_TITLE
            caption = DOWNLOADED_CAPTION
        else:
            raise

        vid_type_desc = self.get_video_type_description(vid_type)
        title = title.replace("VIDEOS", vid_type_desc)
        caption = caption.replace("VIDEOS", vid_type_desc)

        return title, caption

    def generate_content(self, vid_type, notify_type, vids):
        title, caption = self.get_title_and_caption(vid_type, notify_type)
        content = '<p><b>' + title + ':</b><br>' + caption + '<br>'
        for fileData in vids:
            content += '\t' + fileData.get_notification_text() + '<br>'
        content += '</p><br><br>'
        return content

    @staticmethod
    def get_vid_titles(vids):
        s = set()
        for fileData in vids:
            s.add(fileData.get_notification_title())

        return ','.join(map(str, s))

    @staticmethod
    def get_video_type_description(vid_type):
        if VideoType.tv_show == vid_type:
            return "Episodes"
        elif VideoType.movie == vid_type:
            return "Movies"
        else:
            return "Videos"

    def send_notification(self, vid_type):
        # First we copy and clear the members list - we do this under lock so they won't be changed in the meantime.
        maps_lock.acquire()
        # If no updates to send we leave.
        if len(self.get_vids(vid_type, NotifyFileType.Ready)) == 0 and len(
                self.get_vids(vid_type, NotifyFileType.Downloaded)) == 0:
            self.clear_lists(vid_type)
            maps_lock.release()
            return

        tmp_data = dict()
        # Copy each list asice - so we can work on it
        for notifyType in NotifyFileType:
            tmp_data[notifyType] = list(self.get_vids(vid_type, notifyType))

        # Clear all lists - next time we will work on new data
        self.clear_lists(vid_type)
        # Here we stop working on the members - so we can release the lock
        maps_lock.release()

        vid_type_desc = self.get_video_type_description(vid_type)
        if len(tmp_data[NotifyFileType.Ready]) > 0:
            # Generate subject according to ready video
            subject = 'New ' + vid_type_desc + ' Ready (' + self.get_vid_titles(tmp_data[NotifyFileType.Ready]) + ')'
        else:
            subject = 'New ' + vid_type_desc + ' Downloaded (' + self.get_vid_titles(
                tmp_data[NotifyFileType.Downloaded]) + ')'

        # Content prefix
        content = '<html><head></head><body>'

        # generate content per type
        for notifyType in NotifyFileType:
            if len(tmp_data[notifyType]) > 0:
                content += self.generate_content(vid_type, notifyType, tmp_data[notifyType])

        # Content suffix
        content += '</body></html>'
        for email in self.email_list:
            send_email(email, subject, content, 'html')
            print('---- ' + vid_type_desc + ' notification email sent to ' + email)

    def send_notifications(self):
        self.send_notification(VideoType.tv_show)
        self.send_notification(VideoType.movie)
