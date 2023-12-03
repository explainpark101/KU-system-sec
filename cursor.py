import ctypes

hcursor = ctypes.windll.user32.GetCursor()

# ctypes.windll.user32.SetSystemCursor(hcursor, 32514) ## loading

if __name__ == "__main__":
    ctypes.windll.user32.SetSystemCursor(hcursor, 32512) ## default 
    