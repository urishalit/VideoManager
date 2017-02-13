import os.path
from VidFileData import VidFileData

SearchLanguages = ['en']


class SubDownloader:
    def GetSubtitleFilePath(self, fileData, lang):
        srtFile = os.path.join(fileData.fileDir, fileData.fileName[:fileData.fileName.rfind('.')] + "-" + lang + ".srt")
        return srtFile

    def DownloadSubs(self, fileData, lang):
        return self.GetLanguages()

    def SaveSubtitleFile(self, fileData, lang, content):
        # Construct sub file path
        subFilePath = self.GetSubtitleFilePath(fileData, lang)

        # Save subtitle to file
        subFile = open(subFilePath, 'wb')
        subFile.write(content)
        subFile.close()

        # Add to associated files
        fileData.add_associated_file(subFilePath)
