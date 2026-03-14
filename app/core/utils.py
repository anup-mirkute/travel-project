import secrets
from datetime import datetime
from zoneinfo import ZoneInfo


def generate_otp():
    return f"{secrets.randbelow(10000):04}"

def current_dtts():
    DEFAULT_TZ = ZoneInfo("Asia/Kolkata")
    return datetime.now(DEFAULT_TZ)