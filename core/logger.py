import os

PRODUCTION = False

def debug_print(*args, **kwargs):
    if not PRODUCTION:
        kwargs.setdefault("flush", True)
        print(*args, **kwargs)