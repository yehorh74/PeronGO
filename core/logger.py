import os

PRODUCTION = True

def debug_print(*args, **kwargs):
    if not PRODUCTION:
        kwargs.setdefault("flush", True)
        print(*args, **kwargs)