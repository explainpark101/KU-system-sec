from .utils import get_connection, dictfetchall, dictfetchall_lazy
from datetime import datetime, timedelta
from pathlib import Path
from ..config.settings import DEBUG, DEBUG_PRINT_FILEINPUT, DB_NAME, WATCHING_INTERVAL_MS
import sqlite3, time, traceback



def getFileLogs(filename, logged_after=None, lazy=True):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
                SELECT *
                FROM fileContent
                WHERE fileContent.file_path = %s
                    AND (
                        %s IS NULL
                        OR %s <= fileContent.record_time
                    )
                """, [filename, logged_after, logged_after])
    result = dictfetchall_lazy(cur) if lazy else dictfetchall(cur)
    conn.close()
    return result

def getFileLogs_after(timestamp:datetime|int):
    if not isinstance(timestamp, datetime):
        timestamp = datetime.fromtimestamp(timestamp)
    timestamp -= timedelta(hours=1)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
                SELECT fileContent.file_path as [file_path]
                FROM fileContent
                WHERE fileContent.record_time > ?
                ORDER BY fileContent.record_time DESC
                """, [timestamp.timestamp()])
    return dictfetchall(cur)

def insertFileLog_many(filenames:list[Path|str], contents:list[str|bytes], is_texts:list[bool], record_time:int|datetime|list[int|datetime]) -> None:
    if not hasattr(record_time, "__iter__"):
        record_time = [record_time for _ in range(len(filenames))]
    is_folder = [filename.is_dir() if isinstance(filename, Path) else Path(filename).is_dir() for filename in filenames]
    filenames = [filename.as_posix() if isinstance(filename, Path) else filename for filename in filenames]
    sizes = [filename.stat().st_size if isinstance(filename, Path) else Path(filename).stat().st_size for filename in filenames]
    values = zip(filenames, contents, record_time, is_texts, is_folder, sizes)
    conn = get_connection()
    cur = conn.cursor()
    cur.executemany("""
                INSERT INTO fileContent(
                    [id],
                    [file_path],
                    [content],
                    [record_time],
                    [is_text],
                    [is_dir],
                    [size]
                )
                VALUES (
                    NULL,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )
                """, values)
    conn.commit()
    conn.close()

def getattr_func(obj, property:str):
    try:
        return getattr(obj, property, lambda:None)()
    except:
        return None

def insertFileLog(filename:Path|str, content:str|bytes, 
                  record_time:datetime|int, is_text:bool, error=None, conn=None) -> None:
    values = filename.as_posix(), content, record_time, is_text, \
                (getattr(filename, "is_dir", lambda: Path(filename).is_dir))(), \
                getattr(getattr_func(filename, "stat"), "st_size", 0), error
    
    if conn is None:
        conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    while True:
        try:
            cur.execute("""
                        INSERT INTO fileContent(
                            [id], [file_path], [content], [record_time], [is_text], [is_dir], [size], [error_msg]
                        )
                        VALUES (
                            NULL, ?, ?, ?, ?, ?, ?, ?
                        )
                        """, values)
            conn.commit()
            break
        except sqlite3.OperationalError:
            time.sleep(WATCHING_INTERVAL_MS / 1000)
    conn.close()
    if DEBUG_PRINT_FILEINPUT: print("[inserted]: ", filename, end="\r")
    return values

def convert_file_log_data(filename:Path|str, content:str|bytes, 
                  record_time:datetime|int, is_text:bool, error=None) -> None:
    return filename.as_posix(), content, record_time, is_text, \
                (getattr(filename, "is_dir", lambda: Path(filename).is_dir))(), \
                getattr(getattr_func(filename, "stat"), "st_size", 0), error