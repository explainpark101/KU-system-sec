import sys
import time
from pprint import pprint
from pathlib import Path
from pyuac import isUserAdmin, runAsAdmin
from .utils.MessageBox import alert, confirm
from .config.settings import DEBUG, BASE_DIR
from .config.utils import fire_and_forget, fire_and_forget_decorator
from datetime import datetime
from itertools import chain
from datetime import datetime
from .database.utils import dictfetchall, get_connection
from .database.funcs import insertFileLog_many, insertFileLog

from filetype import is_extension_supported as is_not_code
from charset_normalizer import detect
import multiprocessing
import json

def write_last_logging():
    with open(".last_log.json", "w") as last_log:
        last_log.write(json.dumps({"last_logged": datetime.now().timestamp()}))

def get_last_logging():
    if not (BASE_DIR / ".last_log.json").is_file():
        return 0
    with open(".last_log.json", "r") as last_log:
        last_log_readed = last_log.read()
        if not last_log_readed:
            return 0
        data = json.loads(last_log_readed)
        LAST_LOG:int = data.get('last_logged', 0)
    return LAST_LOG

WATCHING_INTERVAL_MS = 1

def dir_walk(mydir: Path):
    '''like os.walk, but using pathlib.Path, and with fewer options'''
    if isinstance(mydir, str): 
        mydir = Path(mydir).resolve() 
    subdirs = list(d for d in mydir.iterdir() if d.is_dir())
    files = list(f for f in mydir.iterdir() if f.is_file())
    yield mydir, subdirs, files
    for s in subdirs:
        yield from dir_walk(s)

def p_rint(*args):
    print(*args)
    if len(args) == 1: return args[0]
    return args

def get_changes(path:Path, last_modified_date:int):
    data = dir_walk(path)
    for root, dirs, files in data:
        for dir_name in dirs:
            st_mtime = (root/dir_name).stat().st_mtime
            if st_mtime > (last_modified_date):
                yield root / dir_name
        for file_name in files:
            st_mtime = (root/file_name).stat().st_mtime
            if st_mtime > (last_modified_date):
                yield root / file_name

def get_last_modified_dict(path:Path) -> dict:
    """
    returns the dict object containing filename and last modified time
    """
    data = dir_walk(path)
    return_data = dict()
    for root, dirs, files in data:
        for directory in dirs:
            directory = root / directory
            return_data[directory] = directory.stat().st_mtime
        for file in files:
            file = root / file
            return_data[file] = file.stat().st_mtime
    return return_data

def get_unique_data(old_dict:dict, new_dict:dict) -> dict:
    """
    returns the dict object that contains new files , changed files, deleted files by comparing
    two arguments that contains last modified time
    """
    return_data = {
        "changed" : [],
        "new" : [],
        "deleted" : []
    }
    if old_dict != new_dict:
        return_data["changed"] = [
            file for file in set(old_dict.keys()).intersection(set(new_dict.keys()))
            if old_dict[file] != new_dict[file]
        ]
        return_data["new"] = list(set(new_dict.keys()).difference(set(old_dict.keys())))
        return_data["deleted"] = list(set(old_dict.keys()).difference(set(new_dict.keys())))

    return return_data

def insertData_to_DB(file_path:Path):
    if file_path.is_dir():
        return (insertFileLog(file_path, None, datetime.now().timestamp(), None))
    if is_not_code(file_path):
        with open(file_path, "rb") as filebyte:
            blob = filebyte.read()
        return (insertFileLog(file_path, blob, datetime.now().timestamp(), False))
    else:
        with open(file_path, "rb") as filebyte:
            content = filebyte.read()
            try:
                encoding_detection = detect(content)
            except TypeError:
                return (insertFileLog(file_path, content, datetime.now().timestamp(), False))
        try:
            with open(file_path, "r", encoding=encoding_detection.get("encoding", "utf8")) as file_data:
                content = file_data.read()
            return (insertFileLog(file_path, content, datetime.now().timestamp(), True))
        except UnicodeDecodeError:
            # if file_path.stat().st_size > 10000:
            #     return (insertFileLog(file_path, None, datetime.now().timestamp(), False))
            return (insertFileLog(file_path, content, datetime.now().timestamp(), False))

pool:multiprocessing.Pool = None
def insert_datas(loaded_datas):
    global pool
    pool = multiprocessing.Pool(multiprocessing.cpu_count() - 4 if multiprocessing.cpu_count() > 5 else 1)
    pool.map(insertData_to_DB, loaded_datas)
    pool.close()
    if DEBUG: print("Completed!", end='\r')
    from .gui import get_gui_app
    if get_gui_app() is None:
        sys.exit()
    return

def force_close_pool():
    global pool
    if pool is not None:
        pool.close()
        sys.exit()
    
itercount = 0
def track_change(watchdir=BASE_DIR, printing=False, timing=get_last_logging(), WATCHING_INTERVAL_MS=WATCHING_INTERVAL_MS):
    loaded_data = get_changes(watchdir, timing)
    # get data from database that has been updated
    # diff check it
    insert_datas(loaded_data)
    if printing: pprint(loaded_data)
    time.sleep(WATCHING_INTERVAL_MS)
    return watchdir, printing, datetime.now().timestamp(), WATCHING_INTERVAL_MS
    return track_change(watchdir, printing, timing=datetime.now().timestamp(), WATCHING_INTERVAL_MS=WATCHING_INTERVAL_MS)

# @fire_and_forget_decorator
def start_tracking(watchdir:str|Path=BASE_DIR, printing=False, WATCHING_INTERVAL_MS=WATCHING_INTERVAL_MS):
    print("tracking started!", flush=True)
    args = watchdir, printing, get_last_logging(), WATCHING_INTERVAL_MS
    while True:
        try:
            args = track_change(*args)
        except KeyboardInterrupt:
            exit()
    return track_change(watchdir, printing, get_last_logging(), WATCHING_INTERVAL_MS=WATCHING_INTERVAL_MS)

def tracking_alert(watchdir:str=".", printing=True, WATCHING_INTERVAL_MS=WATCHING_INTERVAL_MS):
    """
    the main method
    """
    # if not isUserAdmin():
    #     print("please run this program as admin")
    #     if confirm("""This Program is designed to be run in admin.\nDo you wish to run this as admin?""", 'Program Running Error',):
    #         runAsAdmin()
    #     return sys.exit(0)
    print(f"File-change monitor is live.\n watching: `{watchdir}` \n{printing=}\nInterval={WATCHING_INTERVAL_MS}ms")
    try:
        return track_change(watchdir, printing, get_last_logging())
    except KeyboardInterrupt:
        print("Keyboard interrupt received...")
        write_last_logging()
        sys.exit(0)
            
def list_get(l:list, index:int, default=None):
    try:
        return l[index]
    except IndexError:
        return default

def process_argv(argv:list[str]):
    global WATCHING_INTERVAL_MS
    watchdir = '.'
    printing = True
    if argv.__len__() == 0:
        return watchdir, printing
    
    if len([_ for _ in argv[1:] if _.startswith('--')]):
        if argv.index("--watchdir") + 1:
            watchdir = list_get(argv, argv.index("--watchdir") + 1, watchdir)
        if argv.index("--print") + 1:
            _printing = list_get(argv, argv.index("--print")+1, printing)
            if _printing in ["false", "f", "F"]:
                printing = False
            else: 
                printing = bool(_printing)
        if argv.index("--interval") + 1:
            WATCHING_INTERVAL_MS = int(list_get(argv, argv.index("--interval") + 1, WATCHING_INTERVAL_MS))
        elif argv.index("-i") + 1:
            WATCHING_INTERVAL_MS = int(list_get(argv, argv.index("-i") + 1, WATCHING_INTERVAL_MS))
        return watchdir, printing, WATCHING_INTERVAL_MS
    
    
    watchdir = list_get(argv, 1, watchdir)
    _printing = list_get(argv, 2, printing)
    if _printing in ["false", "f", "F"]:
        printing = False
    else: 
        printing = bool(_printing)
    return watchdir, printing
            
            
    
def main(argv):
    while True:
        try:
            tracking_alert(*process_argv(argv))
            
        except KeyboardInterrupt:
            print("Keyboard interrupt received...")
            sys.exit(0)
        
if __name__ == "__main__":
    main(sys.argv)