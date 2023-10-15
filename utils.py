from pathlib import Path

def path_to_str(path:Path) -> str:
    return "\\".join(path.parts)