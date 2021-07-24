import re
from typing import Any
from dateutil import parser


def date_type_validator(v: Any) -> str:
    s = re.sub(r'[^\d-]', ' ', v)
    try:
        dt = parser.parse(s)
        return f'{dt.year}-{dt.month}-{dt.day}'
    except Exception:
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


def confirm_type_validator(v: Any) -> str:
    # replace with simple pos-neg NL model
    pos_presets = ['ok', 'yes', '응', '예', '네', '좋아', '좋아요', '그래']
    neg_presets = ['no', '아니', '아니오', '싫어', '싫어요', '취소']
    if v in pos_presets:
        return True
    elif v in neg_presets:
        return False
    else:
        return None
