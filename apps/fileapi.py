from .config.settings import BASE_DIR

import os
from pathlib import Path
import filecmp
import time
from datetime import datetime
from pprint import pprint
from .database.funcs import getattr_func, dictfetchall
from .config.utils import optionalIndex
import sqlite3


# 파일 또는 폴더 정보를 가져오는 함수
def getfile_info(item_path):
    # 입력된 경로를 절대 경로로 변환
    item_path = Path(item_path).resolve()

    # 해당 항목이 폴더인지 확인
    folder = item_path.is_dir()

    # 파일 또는 폴더의 이름과 확장자를 가져오기
    name = item_path.name
    extension = item_path.suffix

    # 파일 크기를 가져오고 폴더인 경우 크기를 0으로 표시합니다.
    if folder:
        size = 0
    else:
        size = item_path.stat().st_size

    # 최근 수정일과 생성일을 가져오기
    recent_edit = time.ctime(item_path.stat().st_mtime)
    created_date = time.ctime(item_path.stat().st_ctime)

    return {
        "is_folder": folder,
        "name": name,
        "absolute_dir": str(item_path),
        "extension": extension,
        "size": size,
        "recent_edit": recent_edit,
        "created_at": created_date
    }


# 현재 디렉토리의 파일과 폴더를 구분하여 정보를 가져오는 함수
def listfiles_folders(current_path = BASE_DIR):
    # 현재 디렉토리 내의 모든 파일과 폴더 가져오기
    items = current_path.iterdir()

    # 파일과 폴더 정보를 저장할 리스트 생성.
    file_infos = {"Files": [], "Folders": []}

    # 각 파일과 폴더에 대한 정보 얻기.
    for item in items:
        file_info = getfile_info(item)
        if file_info["is_folder"]:
            file_infos["Folders"].append(file_info)
        else:
            file_infos["Files"].append(file_info)

    return file_infos


# 두 폴더를 비교하여 공통 파일과 폴더의 정보를 가져오는 함수
def compare_folders(folder1, folder2):
    comp = filecmp.dircmp(folder1, folder2)
    common_files = comp.common_files
    common_folders = comp.common_dirs
    return {
        "Files": [getfile_info(Path(folder1) / common_file) for common_file in common_files],
        "Folders": [getfile_info(Path(folder1) / common_folder) for common_folder in common_folders],
    }
    
def changeSizeToString(size:int|float):
    if size > 1000000000:
        size /= 1000000000
        return f"{size:.2f}GB"
    if size > 1000000:
        size /= 1000000
        return f"{size:.2f}MB"
    if size > 1000:
        size /= 1000
        return f"{size:.2f}KB"
    return f"{size} Byte"

def getFileInfo_fromDB(path:Path|str):
    if isinstance(path, str):
        path = Path(path)
    
    with sqlite3.connect('FEWT.sqlite3') as conn:
        cur = conn.cursor()
        cur.execute("""
                    SELECT file_path, content, record_time, is_text, is_dir, size
                    FROM "fileContent"
                    WHERE file_path = ?
                    ORDER BY record_time DESC
                    LIMIT 1
                    """, [path.__str__()])
        result = dictfetchall(cur)
    res = optionalIndex(result, 0, {})
    return {
        "name": res.get('file_path'),
        "LastModified": datetime.fromtimestamp(res.get('st_mtime')) if res.get('st_mtime') else "None",
        "Size": changeSizeToString(res.get("size")) if res.get("size") is not None else "None"
    }
    lastModified = getattr(getattr_func(path, 'stat'), 'st_mtime', None)
    size = getattr(getattr_func(path, 'stat'), 'st_size', None)

    return {
        "name": path.name,
        "LastModified": datetime.fromtimestamp(path.stat().st_mtime) if lastModified is not None else None,
        "Size": changeSizeToString(path.stat().st_size) if size is not None else None
    }

if __name__ == "__main__":
    # 함수를 호출후 실행
    file_infos = listfiles_folders()

    # 결과를 출력합니다.
    print("Files:")
    for info in file_infos["Files"]:
        pprint(info)

    print("\nFolders:")
    for info in file_infos["Folders"]:
        pprint(info)

    # 두 폴더 비교 예시
    Folder1 = BASE_DIR / "sample01"
    Folder2 = BASE_DIR / "sample02"
    pprint(
        compare_folders(Folder1, Folder2)
    )