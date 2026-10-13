import os

PRODUCTION = True

def debug_print(*args, **kwargs):
    if not PRODUCTION:
        print(*args, **kwargs, flush=True)