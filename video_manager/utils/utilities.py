import glob
import os
import os.path
import shutil
import stat
import string

from unrar import rarfile

# Known vid extensions
vid_extensions = ['.avi', '.mkv', '.mp4']

MIN_VID_SIZE_BYTE = 2000000


def is_vid_file(file_path):
    ext = os.path.splitext(file_path)[1]
    return ext in vid_extensions


def get_word_delimiter(base_name):
    first_dot = base_name.find('.')
    if first_dot < 0:
        first_dot = len(base_name)

    first_space = base_name.find(' ')
    if first_space < 0:
        first_space = len(base_name)

    if first_dot < first_space:
        return '.'
    elif first_space < first_dot:
        return ' '
    else:
        return ''


def capitalize_first_letters(directory, file_name):
    ext = os.path.splitext(file_name)[1]
    base = os.path.splitext(file_name)[0]

    delimiter = get_word_delimiter(base)
    new_base = string.capwords(base, delimiter)

    src = os.path.abspath(os.path.join(directory, file_name))
    target = os.path.abspath(os.path.join(directory, new_base + ext))

    os.rename(src, target)

    return new_base + ext


def remove_non_video_files_from_dir(path):
    remove = False
    if not os.path.isdir(path):
        if not is_vid_file(path):
            remove = True
        if os.path.getsize(path) < MIN_VID_SIZE_BYTE:
            remove = True
    else:
        files = os.listdir(path)
        for _file in files:
            file_path = os.path.join(path, _file)
            # Attempt removing non video files from path
            remove_non_video_files_from_dir(file_path)
        # If the directory is empty we remove it
        if len(os.listdir(path)) == 0:
            remove = True

    if remove:
        # If the file is read only we remove the read only flag as we are about to delete it
        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWUSR)
        # Remove it
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def unrar_videos(path):
    rar_files = glob.glob(os.path.join(path, '*.rar'))
    for rar in rar_files:
        base_name = os.path.splitext(rar)[0]
        if os.path.isfile(base_name + '.r00') and os.path.isfile(base_name + '.r01'):
            rar_archive = rarfile.RarFile(rar)
            rar_archive.extractall(path)
