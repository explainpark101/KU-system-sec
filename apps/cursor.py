import ctypes
from typing import Literal
from .config.settings import DEBUG

hcursor = ctypes.windll.user32.GetCursor()

# ctypes.windll.user32.SetSystemCursor(hcursor, 32514) ## loading
# ctypes.windll.user32.SetSystemCursor(hcursor, 32512) ## default

def change_cursor(type:Literal["loading", 'default']='default'):
    if type == 'default':
        ctypes.windll.user32.SetSystemCursor(hcursor, 32512) ## default
        if DEBUG:
            print("Cursor set to default")
        
    elif type == 'loading':
        ctypes.windll.user32.SetSystemCursor(hcursor, 32514)
        if DEBUG:
            print("Cursor set to loading")
    else:
        raise Exception("Not valid Cursor type")