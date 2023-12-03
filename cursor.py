import ctypes

hcursor = ctypes.windll.user32.GetCursor()

if __name__ == "__main__":
    ctypes.windll.user32.SetSystemCursor(hcursor, 32512) ## default 
    