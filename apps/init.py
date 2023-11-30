import subprocess, os, pathlib
from .config.settings import BASE_DIR, DB_NAME
from .database.utils import dictfetchall
from urllib import request
import sys, json
import io
import sqlite3
from .utils.MessageBox import confirm, alert

    

def _create_database():
    conn = sqlite3.connect(DB_NAME)
    CHECK_DB_EXISTS = """SELECT name FROM sqlite_master WHERE type='table' AND name='fileContent';"""
    cur = conn.cursor()
    cur.execute(CHECK_DB_EXISTS)
    tables = dictfetchall(cur)
    if len([_ for _ in tables if _.get('name') == 'fileContent']):
        return 
    
    cur.execute("""
                CREATE TABLE fileContent (
                    [file_path] VARCHAR(1024),
                    [content] BLOB NULL,
                    [record_time] INT,
                    [is_text] BOOLEAN NULL,
                    [is_dir] BOOLEAN,
                    [size] INT NULL
                );
                """)
    conn.commit()
    print("Database Setup Complete!")
    return 
    
def check_dependencies():
    from pip._internal.operations.freeze import freeze
    with open(BASE_DIR / "requirements.txt", "r") as req:
        requirements = set((_.split("==")[0] for _ in req.readlines()))
    installed = set(freeze())
    uninstalled = requirements - installed
    if uninstalled.__len__():
        message = "Do you want to install packages below?\n\n" + "\n".join(uninstalled)
        if confirm(message, "FEWT: Installation"):
            os.system("pip install -r requirements.txt -q")
        else:
            alert("Program installation has been canceled.", "FEWT Error")
            sys.exit(0)
        

def init_all():
    _create_database()

if __name__ == "__main__":
    init_all()
    os.system("python file_grid.py")