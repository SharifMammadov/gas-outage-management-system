"""
Tarix əməliyyatları üçün köməkçi funksiyalar
"""
from datetime import datetime, timedelta
import re


def today_date_str() -> str:
    """Bugünkü tarixi qaytar (gg.aa.iiii)"""
    return datetime.now().strftime("%d.%m.%Y")


def default_time_str() -> str:
    """Default vaxtı qaytar (09:00)"""
    return "09:00"


def date_str(date: datetime) -> str:
    """Datetime obyektini formatla (gg.aa.iiii)"""
    return date.strftime("%d.%m.%Y")


def datetime_str(dt: datetime) -> str:
    """Datetime obyektini formatla (gg.aa.iiii ss:dd)"""
    return dt.strftime("%d.%m.%Y %H:%M")


def make_dt_str(date_part: str, time_part: str) -> str:
    """Tarix və saatı birləşdir"""
    return f"{date_part} {time_part}"


def is_valid_date_ddmmyyyy(date_str: str) -> bool:
    """Tarix formatını yoxla (gg.aa.iiii)"""
    if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', date_str):
        return False

    try:
        datetime.strptime(date_str, "%d.%m.%Y")
        return True
    except ValueError:
        return False


def ddmmyyyy_to_iso(date_str: str) -> str:
    """gg.aa.iiii -> iiii-aa-gg formatına çevir"""
    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return date_str


def iso_to_ddmmyyyy(iso_str: str) -> str:
    """iiii-aa-gg -> gg.aa.iiii formatına çevir"""
    try:
        if ' ' in iso_str:
            iso_str = iso_str.split()[0]
        dt = datetime.strptime(iso_str, "%Y-%m-%d")
        return dt.strftime("%d.%m.%Y")
    except ValueError:
        return iso_str


def fmt_int(value: int) -> str:
    """Rəqəmi formatla (əgər 0-dırsa '0' qaytar)"""
    if value == 0:
        return "0"
    return f"{value:,}".replace(",", " ")


def time_choices(interval_minutes: int = 5) -> list:
    """Vaxt seçimləri yarat (00:00 - 23:55)"""
    choices = []
    for hour in range(24):
        for minute in range(0, 60, interval_minutes):
            choices.append(f"{hour:02d}:{minute:02d}")
    return choices


def get_date_range(start_date: str, end_date: str) -> list:
    """Tarix aralığındakı bütün günləri qaytar"""
    try:
        start = datetime.strptime(start_date, "%d.%m.%Y")
        end = datetime.strptime(end_date, "%d.%m.%Y")

        dates = []
        current = start
        while current <= end:
            dates.append(current.strftime("%d.%m.%Y"))
            current += timedelta(days=1)

        return dates
    except ValueError:
        return []


def get_current_datetime() -> str:
    """Hazırki tarix və vaxtı qaytar"""
    return datetime.now().strftime("%d.%m.%Y %H:%M")


def parse_datetime(dt_str: str) -> datetime | None:
    """Tarix-saat mətnini parse et"""
    try:
        return datetime.strptime(dt_str, "%d.%m.%Y %H:%M")
    except ValueError:
        try:
            return datetime.strptime(dt_str, "%d.%m.%Y")
        except ValueError:
            return None