import ctypes

hcursor = ctypes.windll.user32.GetCursor()

# ctypes.windll.user32.SetSystemCursor(hcursor, 32514) ## loading
ctypes.windll.user32.SetSystemCursor(hcursor, 32512) ## default