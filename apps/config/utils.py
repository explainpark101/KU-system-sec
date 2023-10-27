import threading

def fire_and_forget(func, *args ,**kwargs) -> None:
    thd = threading.Thread(target=func, args=args, kwargs=kwargs)
    thd.daemon = True
    thd.start()
    
def fire_and_forget_decorator(func):
    def wrapper(*args, **kwargs):
        return fire_and_forget(func, *args, **kwargs)
    return wrapper