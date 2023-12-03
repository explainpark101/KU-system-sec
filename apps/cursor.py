import ctypes
from typing import Literal
from .config.settings import DEBUG

_CURSOR_MAP = {
    'default': 32512,
    'loading': 32650
}
def change_cursor(_type:Literal["loading", 'default']='default'):
    hcursor = ctypes.windll.user32.GetCursor()
    
    ctypes.windll.user32.SetSystemCursor(hcursor, (_CURSOR_MAP[_type])) ## default
    if DEBUG:
        print(f"Cursor set to {_type}")