import os, os.path
import string
import stat
import shutil
from unrar import rarfile
import glob

# Known vid extensions
vidExtenstions = ['.avi', '.mkv', '.mp4']

MIN_VID_SIZE_BYTE = 2000000


def IsVidFile(file):
    ext = os.path.splitext(file)[1]
    return ext in vidExtenstions


def GetWordDelimiter(baseName):
    firstDot = baseName.find('.')
    if firstDot < 0:
        firstDot = len(baseName)

    firstSpace = baseName.find(' ')
    if firstSpace < 0:
        firstSpace = len(baseName)

    if firstDot < firstSpace:
        return '.'
    elif firstSpace < firstDot:
        return ' '
    else:
        return ''


def CaptalizeFirstLetters(dir, file):
    ext = os.path.splitext(file)[1]
    base = os.path.splitext(file)[0]

    delim = GetWordDelimiter(base)
    newBase = string.capwords(base, delim)

    src = os.path.abspath(os.path.join(dir, file))
    trgt = os.path.abspath(os.path.join(dir, newBase + ext))

    os.rename(src, trgt)

    return newBase + ext


def RemoveNonVideoFilesFromDir(path):
    remove = False
    if not os.path.isdir(path):
        if not IsVidFile(path):
            remove = True
        if os.path.getsize(path) < MIN_VID_SIZE_BYTE:
            remove = True
    else:
        files = os.listdir(path)
        for file in files:
            filePath = os.path.join(path, file)
            # Attempt removing non video files from path
            RemoveNonVideoFilesFromDir(filePath)
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
