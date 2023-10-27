import subprocess, os, pathlib
from settings import BASE_DIR
from urllib import request
import sys, json
import py7zr
import io

def get_file(Url):
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


def main():
    is_64bit = sys.maxsize > 2**32
    binFolder = BASE_DIR / 'bin'
    if "mpv.exe" not in os.listdir(binFolder):
        data = json.loads(request.urlopen("https://github.com/ScoopInstaller/Extras/raw/master/bucket/mpv.json").read())
        url = data.get("architecture").get("64bit" if is_64bit else "32bit").get("url")
        with open(BASE_DIR / 'bin' / 'mpv.7z', 'wb') as f:
            f.write(get_file(url))
        with py7zr.SevenZipFile(BASE_DIR / 'bin' / 'mpv.7z', 'r') as archive:
            archive.extract(BASE_DIR / "bin", targets=['mpv.exe'])
        os.remove(BASE_DIR / 'bin' / 'mpv.7z')


    
if __name__ == "__main__":
    main()
    os.system("python file_grid.py")