import os, sys
from apps.init import init_all
from apps.tracker import start_tracking
from apps.config.settings import BASE_DIR
import traceback
from apps.config.settings import DEBUG
from apps.cursor import change_cursor
from apps.utils.MessageBox import alert, confirm
import ctypes
from pyuac import main_requires_admin
import pathlib

try:
    from apps.gui import runGUI
except ImportError:
    from apps.init import check_dependencies
    from apps.utils.MessageBox import alert
    check_dependencies()
    if DEBUG:
        alert(traceback.format_exc())
    else:
        alert("Please Restart the program.")
    sys.exit(0)
    
# @main_requires_admin
def main(argv):
    change_cursor("default")
    watch_path:pathlib.Path = pathlib.Path(os.path.expanduser("~"))
    if len(argv) > 1:
        if argv[1] in ['--flush', '-f']:
            if (BASE_DIR / "FEWT.sqlite3").is_file(): os.remove(BASE_DIR / "FEWT.sqlite3")
            if (BASE_DIR / ".last_log.json").is_file(): os.remove(BASE_DIR / ".last_log.json")
            if len(argv) > 2:
                watch_path = pathlib.Path(os.path.expanduser(argv[2]))
        else:
            watch_path = pathlib.Path(argv[1])
            if len(argv) > 2 and argv[2] == 'flush':
                if (BASE_DIR / "FEWT.sqlite3").is_file(): os.remove(BASE_DIR / "FEWT.sqlite3")
                if (BASE_DIR / ".last_log.json").is_file(): os.remove(BASE_DIR / ".last_log.json")
    init_all()
    runGUI()

    if DEBUG:
        print("watching: ", watch_path.__str__())
    start_tracking(watch_path)
    # os.system("python manage.py gui")
    # write_last_logging()
    

if __name__ == "__main__":
    main(sys.argv)