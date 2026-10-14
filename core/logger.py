import os

PRODUCTION = False

def debug_print(*args, **kwargs):
    if not PRODUCTION:
        print(*args, **kwargs, flush=True)