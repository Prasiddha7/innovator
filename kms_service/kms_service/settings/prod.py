# kms_service/settings/prod.py
from .base import *
import os

DEBUG = False
# load hosts and strip out blanks; if nothing is provided fall back to localhost
_raw_allowed = os.getenv("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h for h in _raw_allowed.split(",") if h]
if not ALLOWED_HOSTS:
    #환경에서 설정되지 않은 경우 기본으로 localhost를 허용합니다.
    ALLOWED_HOSTS = ["localhost"]
