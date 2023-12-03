import threading
from typing import Any

def fire_and_forget(func, *args ,**kwargs) -> None:
    thd = threading.Thread(target=func, args=args, kwargs=kwargs)
    thd.daemon = True
    thd.start()
    
def fire_and_forget_decorator(func):
    def wrapper(*args, **kwargs):
        return fire_and_forget(func, *args, **kwargs)
    return wrapper

def optionalIndex(_iterable, _index, _default=None) -> Any|None:
    try:
        return _iterable[_index]
    except IndexError:
        return _default
    
def process_f_string(f_string:str):
    splitted = f_string.split("\n")
    for i, line in enumerate(splitted):
        if line.strip() == '': continue
        f_string = '\n'.join(splitted[i:])
        break
    f_string = f_string.rstrip()
    first_whitespace_size = len(f_string) - len(f_string.lstrip())
    strings = [_[first_whitespace_size:].rstrip() for _ in f_string.split("\n")]
    return "\n".join(strings)