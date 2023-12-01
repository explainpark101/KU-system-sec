import os, sys
from apps.init import init_all
from apps.tracker import write_last_logging, start_tracking
from apps.config.settings import BASE_DIR

try:
    from apps.gui import runGUI
except ImportError:
    from apps.init import check_dependencies
    from apps.utils.MessageBox import alert
    check_dependencies()
    alert("Please Restart the program.")
    sys.exit(0)

    

def main(argv):
    if len(argv) > 1 and argv[1] == 'flush':
        if (BASE_DIR / "FEWT.sqlite3").is_file(): os.remove(BASE_DIR / "FEWT.sqlite3")
        if (BASE_DIR / ".last_log.json").is_file(): os.remove(BASE_DIR / ".last_log.json")
    init_all()
    runGUI()
    start_tracking()
    # os.system("python manage.py gui")
    # write_last_logging()
    

if __name__ == "__main__":
    main(sys.argv)