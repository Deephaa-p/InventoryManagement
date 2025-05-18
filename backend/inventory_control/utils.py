import os
from django.core.exceptions import ImproperlyConfigured
import random
import string


def load_env():
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

def get_env(key):
    try:
        return os.environ[key]
    except KeyError:
        raise ImproperlyConfigured(f"Set the {key} environment variable.")
