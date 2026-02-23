from .base import *

DEBUG = False
_raw_allowed = os.environ.get("ALLOWED_HOSTS", "yourdomain.com")
ALLOWED_HOSTS = [h for h in _raw_allowed.split(",") if h]
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["yourdomain.com"]
