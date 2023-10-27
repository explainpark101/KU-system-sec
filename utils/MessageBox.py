import ctypes
_MessageBox = ctypes.windll.user32.MessageBoxW

def alert(message, title="tracker.py"):
    return _MessageBox(None, message, title, 0x00)
def confirm(message, title="tracker.py"):
    return _MessageBox(None, message, title, 0x01)