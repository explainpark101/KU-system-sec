from .utils import get_connection, dictfetchall, dictfetchall_lazy
from datetime import datetime
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

def insertFileLog_many(filenames:list[str], contents:list[str|bytes], is_texts:list[bool], record_time:int|datetime|list[int|datetime]) -> None:
    if not hasattr(record_time, "__iter__"):
        record_time = [record_time for _ in range(len(filenames))]
    values = zip(filenames, contents, record_time, is_texts)
    with get_connection() as conn:
        cur = conn.cursor()
        cur.executemany("""
                    INSERT INTO fileContent(
                        [file_path],
                        [content],
                        [record_time],
                        [is_text]
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """, values)
        conn.commit()

def insertFileLog(filename:str, content:str|bytes, 
                  record_time:datetime|int, is_text:bool) -> None:
    values = filename, content, record_time, is_text
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
                    INSERT INTO fileContent(
                        [file_path],
                        [content],
                        [record_time],
                        [is_text]
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """, values)
        conn.commit()
    