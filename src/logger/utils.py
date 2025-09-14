from datetime import datetime
import logging
from zoneinfo import ZoneInfo
from constants import TIMEZONE


def format_time(record, datefmt=None):
    dt = datetime.fromtimestamp(record.created, ZoneInfo(TIMEZONE))
    if datefmt:
        return dt.strftime(datefmt)
    return dt.isoformat()


class TimezoneFormatter(logging.Formatter):
    pass


formatter = TimezoneFormatter("[%(asctime)s] - %(name)s - %(levelname)s - %(message)s", datefmt="%d-%m-%Y %H:%M:%S")
console_formatter = TimezoneFormatter("[%(asctime)s] - %(levelname)s - %(message)s",
                                      datefmt="%d-%m-%Y %H:%M:%S")
