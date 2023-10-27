import subprocess, os, pathlib
from .config.settings import BASE_DIR, DB_NAME
from .database.utils import dictfetchall
from urllib import request
import sys, json
import io
import sqlite3
from .utils.MessageBox import confirm, alert

    

def _get_file(Url):
    with request.urlopen(Url) as Response:
        Length = Response.getheader('content-length')
        BlockSize = 1000000  # default value
        if Length:
            Length = int(Length)
            BlockSize = max(4096, Length // 20)
        BufferAll = io.BytesIO()
        Size = 0
        while True:
            BufferNow = Response.read(BlockSize)
            if not BufferNow:
                break
            BufferAll.write(BufferNow)
            Size += len(BufferNow)
            if Length:
                Percent = int((Size / Length)*100)
                print(f"download: {Percent}% {Url}", end='\r')
        print()
    return BufferAll.getbuffer()


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
                    [content] BLOB,
                    [record_time] INT,
                    [is_text] BOOLEAN
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
    is_64bit = sys.maxsize > 2**32
    binFolder = BASE_DIR / 'bin'
    if not (binFolder / "mpv.exe").is_file():
        try:
            import py7zr
        except ImportError:
            if confirm("py7zr is not installed. Do you want to install it?"):
                os.system("pip install py7zr -q")
                import py7zr
            else:
                alert("Program installation has been canceled.", "FEWT Error")
                sys.exit(0)
        
        data = json.loads(request.urlopen("https://github.com/ScoopInstaller/Extras/raw/master/bucket/mpv.json").read())
        url = data.get("architecture").get("64bit" if is_64bit else "32bit").get("url")
        with open(BASE_DIR / 'bin' / 'mpv.7z', 'wb') as f:
            f.write(_get_file(url))
        with py7zr.SevenZipFile(BASE_DIR / 'bin' / 'mpv.7z', 'r') as archive:
            archive.extract(BASE_DIR / "bin", targets=['mpv.exe'])
        os.remove(BASE_DIR / 'bin' / 'mpv.7z')
        print("mpv setup Complete!")


    
if __name__ == "__main__":
    init_all()
    
    os.system("python file_grid.py")