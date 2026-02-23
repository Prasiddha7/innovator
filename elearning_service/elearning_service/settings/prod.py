# elearning_service/settings/prod.py
from .base import *
import os

DEBUG = False
_raw_allowed = os.getenv("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h for h in _raw_allowed.split(",") if h]
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost"]
