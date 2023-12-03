import sys
import time
from pprint import pprint
from pathlib import Path
from .utils.MessageBox import alert, confirm
from .config.settings import DEBUG, BASE_DIR
from .config.utils import fire_and_forget, fire_and_forget_decorator
from datetime import datetime
from itertools import chain
from datetime import datetime
from .database.utils import dictfetchall, get_connection
from .database.funcs import insertFileLog_many, insertFileLog
from .gui import is_gui_running, get_app2

from filetype import is_extension_supported as is_not_code
from charset_normalizer import detect

import sys
from watchfiles import watch

def insertData_to_DB(file_path:Path, status=2):
    status_map = {
        1: "created",
        2: "modified",
        3: "deleted"
    }
    if isinstance(file_path, str):
        file_path = Path(file_path)
    if file_path.is_dir():
        return (file_path, None, datetime.now().timestamp(), None)
    if file_path.name in ['FEWT.sqlite3', 'FEWT.sqlite3-journal']:
        return None
    if status == 3:
        return (file_path, None, datetime.now().timestamp(), False, 'del')

    if is_not_code(file_path):
        with open(file_path, "rb") as filebyte:
            blob = filebyte.read()
        return (file_path, blob, datetime.now().timestamp(), False, file_path.stat().st_size)
    else:
        try:
            with open(file_path, "rb") as filebyte:
                content = filebyte.read()
                try:
                    encoding_detection = detect(content)
                except TypeError:
                    return (file_path, content, datetime.now().timestamp(), False, file_path.stat().st_size)
                try:
                    if file_path.stat().st_size > 5000000:
                        return (file_path, None, datetime.now().timestamp(), False, file_path.stat().st_size)
                    with open(file_path, "r", encoding=encoding_detection.get("encoding", "utf8")) as file_data:
                        content = file_data.read()
                    return (file_path, content, datetime.now().timestamp(), True)
                except UnicodeDecodeError:
                    if file_path.stat().st_size > 5000000:
                        return (file_path, None, datetime.now().timestamp(), False, file_path.stat().st_size)
                    return (file_path, content, datetime.now().timestamp(), False, file_path.stat().st_size)
        except FileNotFoundError:
            return (file_path, None, datetime.now().timestamp(), False, "notFile")
        except PermissionError:
            print("PermissionError", file_path)
            return (file_path, None, datetime.now().timestamp(), False, "PermErr")
            
def insertDatas(file_path:Path, status:int, app2=get_app2()):
    """Function for Threading.
    
    It is concatenation of two function, {insertData_to_DB, insert_into_program_tree}

    Args:
        file_path (Path): _description_
        status (int): _description_
    """
    res = insertData_to_DB(file_path, status)
    if res is not None:
        filename, content, record_time, *is_sereis, _size = res
        app2.insert_into_program_tree({"file_path": filename, "record_time":record_time, "size":_size})
        insertFileLog(*res)
    return 

# @fire_and_forget_decorator
def start_tracking(watchdir:str|Path=BASE_DIR):
    print("tracking started!", flush=True)
    for _ in watch(watchdir, rust_timeout=100, yield_on_timeout=True):
        if not is_gui_running():
            return 
        _ = list(_)
        app2 = get_app2()
        for status, file_path in _:
            if DEBUG: print(status.name, file_path)
            fire_and_forget_decorator(insertDatas)(file_path, status, app2)
    return 


