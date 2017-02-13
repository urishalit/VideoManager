import os
import os.path
import shutil
import stat

from enum import Enum

from utils.file_security import add_full_access_to_file


class VideoType(Enum):
    tv_show = 1
    movie = 2


class VidFileData(object):
    def __init__(self, config_data, file_dir, file_name, suffix):
        self.config_data = config_data
        self.file_dir = file_dir
        self.file_name = file_name
        self.suffix = suffix
        self.associated_files = []
        self.associated_files.insert(0, self.get_file_path())
        self.base_file_name = os.path.basename(self.file_name)
        self.working_dir = config_data['WorkingDirectory']
        self.target_root_dir = ''
        self.imdb_title_id = ''
        self.move_files = False
        self.type = None

    def get_file_path(self):
        return os.path.abspath(os.path.join(self.file_dir, self.file_name))

    def get_vid_extension(self):
        return os.path.splitext(self.file_name)[1]

    def add_associated_file(self, path):
        self.associated_files.append(path)

    def rename_file(self, dir, file):
        # Current path
        curr_path = self.get_file_path()

        # Remove current path from list of associated files
        self.associated_files = list(set(self.associated_files) - {curr_path})

        # Update dir & file name
        self.file_dir = dir
        self.file_name = file

        # Add file to associated files list
        self.add_associated_file(self.get_file_path())

        # Rename file
        new_path = self.get_file_path()
        if new_path == curr_path:
            return

        if new_path.lower() == curr_path.lower():
            # For some reason when all we do is change case of letters it fails, so we move through a temp file
            tmp_path = curr_path + '.tmp'
            os.rename(curr_path, tmp_path)
            curr_path = tmp_path

        os.rename(curr_path, self.get_file_path())

    def add_suffix_to_files(self, suffix):
        new_associated_file_list = []
        new_base_name = os.path.splitext(self.base_file_name)[0] + str(suffix)

        curr_base_name = os.path.splitext(os.path.basename(self.file_name))[0]
        for _file in self.associated_files:
            new_file = _file.replace(curr_base_name, new_base_name)
            new_associated_file_list.append(new_file)

        self.file_name = new_base_name + os.path.splitext(os.path.basename(self.file_name))[1]
        self.associated_files = new_associated_file_list

    def is_movie(self):
        return VideoType.movie == self.type

    def is_tv_show(self):
        return VideoType.tv_show == self.type

    def get_type(self):
        return self.type

    def get_notification_text(self):
        raise NotImplemented

    def get_notification_title(self):
        raise NotImplemented

    def rename_to_format(self):
        return

    def move_to_target_directory(self):
        self.move_to_dir(self.target_root_dir)

    def initiate_target_directory(self, path):
        self.target_root_dir = path
        if os.path.exists(self.target_root_dir):
            if not os.path.isdir(self.target_root_dir):
                self.target_root_dir = ''
        else:
            os.makedirs(self.target_root_dir)
            if not os.path.isdir(self.target_root_dir):
                self.target_root_dir = ''

        if len(self.target_root_dir) == 0:
            self.move_files = False
        else:
            # If the shows dir is the same as the working directory - we do not move the files
            self.move_files = self.target_root_dir != self.working_dir

    def move_to_dir(self, target_path):
        if not self.move_files:
            return

        # Verify target dir exists
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        move_files = True
        # Check if file with same name already exists
        target_vid_path = os.path.join(target_path, self.file_name)
        counter = 0
        while os.path.exists(target_vid_path) and counter < 10:
            # If a file with that name already exists and it has the same size we do nothing.
            if os.path.getsize(target_vid_path) == os.path.getsize(os.path.join(self.file_dir, self.file_name)):
                print('------ File already exists in target directory: ' + target_path)
                move_files = False
                break
            else:
                self.add_suffix_to_files(counter)
                counter += 1
                target_vid_path = os.path.join(target_path, self.file_name)

        if move_files:
            print('------ Moving to ' + target_path)

        for file in self.associated_files:
            target_file_path = os.path.join(target_path, os.path.basename(file))
            # If the file is marked as read-only we remove the read-only flag and then move it.
            if not os.access(file, os.W_OK):
                os.chmod(file, stat.S_IWUSR)

            if move_files:
                shutil.move(file, target_file_path)
                add_full_access_to_file(target_file_path)
            else:
                os.remove(file)

    def equals(self, other_file_data):
        return self.file_dir == other_file_data.file_dir and self.file_name == other_file_data.file_name

    def __eq__(self, other):
        return self.equals(other)
