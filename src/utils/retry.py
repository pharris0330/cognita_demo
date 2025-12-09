"""Retry with exponential backoff."""
import time
import random
from functools import wraps

def exponential_backoff(max_retries=5, base_delay=0.1, max_delay=30.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt >= max_retries - 1:
                        raise
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    delay += random.uniform(0, delay * 0.1)
                    time.sleep(delay)
        return wrapper
    return decorator
