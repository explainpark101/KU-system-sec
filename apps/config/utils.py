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