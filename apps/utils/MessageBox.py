import ctypes
_MessageBox = ctypes.windll.user32.MessageBoxW

def alert(message, title="FEWT: File Explorer With Tracker"):
    return _MessageBox(None, message, title, 0x00)
def confirm(message, title="FEWT: File Explorer With Tracker"):
    return _MessageBox(None, message, title, 0x01) == 1