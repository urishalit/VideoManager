import win32api
import win32security

import ntsecuritycon as con


def AddFullAccessToFile(path):
    everyone, domain, type = win32security.LookupAccountName("", "Everyone")
    admins, domain, type = win32security.LookupAccountName("", "Administrators")
    user, domain, type = win32security.LookupAccountName("", win32api.GetUserName())
    sd = win32security.GetFileSecurity(path, win32security.DACL_SECURITY_INFORMATION)

    dacl = win32security.ACL()
    dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_GENERIC_READ | con.FILE_GENERIC_WRITE, everyone)
    dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, admins)
    dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, user)

    sd.SetSecurityDescriptorDacl(1, dacl, 0)
    win32security.SetFileSecurity(path, win32security.DACL_SECURITY_INFORMATION, sd)


if __name__ == "__main__":
    path = r"C:\Users\Uri\Downloads\Torrents\LocalMovies\Redirected.2014.1080p.Bluray.X264.Dts-rarbg.mkv"
    AddFullAccessToFile(path)
