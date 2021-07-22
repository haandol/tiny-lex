import re
from typing import Any
from dateutil import parser

def date_type_validator(v: Any) -> str:
    s = re.sub(r'[^\d-]', ' ', v)
    try:
        dt = parser.parse(s)
        return f'{dt.year}-{dt.month}-{dt.day}'
    except:
        return None

def time_type_validator(v: Any) -> str:
    s = re.sub(r'[^\d]', ' ', v)
    hour = None
    minutes = None
    for el in map(int, filter(None, s.split(' '))):
        if hour is None and 0 <= el < 24:
            hour = el
            continue
        if minutes is None and 0 <= el < 60:
            minutes = el
    if hour and minutes:
        return f'{hour}:{minutes}'
    else:
        return None