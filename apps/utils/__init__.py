from pathlib import Path

def path_to_str(path:Path) -> str:
    return path.as_posix()