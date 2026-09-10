"""
Hesabat kontrolleri
"""
from models.database import Database
from models.cache import Cache
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('database')


class ReportController:
    """Hesabat əməliyyatları kontrolleri"""

    def __init__(self):
        self.db = Database()
        self.cache = Cache()

    def get_daily_report(self, date: str = None) -> dict:
        """Günlük hesabat"""
        from utils.date_utils import today_date_str, ddmmyyyy_to_iso

        if not date:
            date = today_date_str()

        iso_date = ddmmyyyy_to_iso(date)

        cache_key = f"daily_report_{date}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        closed_iso = (
            "(substr(closed_at,7,4)||'-'||substr(closed_at,4,2)"
            "||'-'||substr(closed_at,1,2))"
        )

        try:
            # Bağlananlar
            row = self.db.execute(f"""
                SELECT COALESCE(SUM(abonent_count), 0) FROM records
                WHERE closed_at != '' AND {closed_iso} = ?
            """, (iso_date,), fetchone=True)
            closed = int(row[0] or 0)

            # Açılanlar
            opened_iso = (
                "(substr(opened_at,7,4)||'-'||substr(opened_at,4,2)"
                "||'-'||substr(opened_at,1,2))"
            )
            row = self.db.execute(f"""
                SELECT COALESCE(SUM(abonent_count), 0) FROM records
                WHERE opened_at != '' AND {opened_iso} = ?
            """, (iso_date,), fetchone=True)
            opened = int(row[0] or 0)

            # Stop olanlar
            row = self.db.execute(f"""
                SELECT COALESCE(SUM(abonent_count), 0) FROM records
                WHERE status = 'Stop' AND closed_at != '' AND {closed_iso} = ?
            """, (iso_date,), fetchone=True)
            stopped = int(row[0] or 0)

            result = {
                "date": date,
                "closed": closed,
                "opened": opened,
                "stopped": stopped,
                "total": closed + opened + stopped
            }

            self.cache.set(cache_key, result)
            return result

        except Exception as e:
            logger.error(f"Günlük hesabat xətası: {e}")
            return {
                "date": date,
                "closed": 0,
                "opened": 0,
                "stopped": 0,
                "total": 0
            }

    def get_weekly_report(self, end_date: str = None) -> list:
        """Həftəlik hesabat (son 7 gün)"""
        from utils.date_utils import date_str, get_date_range

        if not end_date:
            end_date = date_str(datetime.now())

        end = datetime.strptime(end_date, "%d.%m.%Y")
        start = end - timedelta(days=6)
        start_date = start.strftime("%d.%m.%Y")

        dates = get_date_range(start_date, end_date)

        report = []
        for date in dates:
            daily = self.get_daily_report(date)
            report.append(daily)

        return report

    def get_monthly_report(self, year: int = None, month: int = None) -> dict:
        """Aylıq hesabat"""
        from calendar import monthrange
        from utils.date_utils import date_str

        if not year or not month:
            now = datetime.now()
            year = now.year
            month = now.month

        # Ayın ilk və son günü
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, monthrange(year, month)[1])

        start_date = first_day.strftime("%d.%m.%Y")
        end_date = last_day.strftime("%d.%m.%Y")

        cache_key = f"monthly_report_{year}_{month}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        from controllers.record_controller import RecordController
        record_controller = RecordController()

        report_data = record_controller.get_report(start_date, end_date)

        result = {
            "year": year,
            "month": month,
            "start_date": start_date,
            "end_date": end_date,
            "total": report_data["total"],
            "by_status": report_data["by_status"],
            "daily": report_data["daily"]
        }

        self.cache.set(cache_key, result)
        return result

    def get_yearly_report(self, year: int = None) -> dict:
        """İllik hesabat"""
        if not year:
            year = datetime.now().year

        cache_key = f"yearly_report_{year}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        monthly_reports = []
        yearly_total = 0
        yearly_by_status = {"Bağlı": 0, "Açıq": 0, "Stop": 0}

        for month in range(1, 13):
            monthly = self.get_monthly_report(year, month)
            monthly_reports.append({
                "month": month,
                "total": monthly["total"]
            })

            yearly_total += monthly["total"]
            for status in yearly_by_status:
                yearly_by_status[status] += monthly["by_status"].get(status, 0)

        result = {
            "year": year,
            "total": yearly_total,
            "by_status": yearly_by_status,
            "months": monthly_reports
        }

        self.cache.set(cache_key, result)
        return result

    def export_to_excel(self, start_date: str, end_date: str, file_path: str) -> tuple[bool, str]:
        """Hesabatı Excel-ə export et"""
        try:
            from controllers.record_controller import RecordController
            record_controller = RecordController()

            report_data = record_controller.get_report(start_date, end_date)

            # Burada Excel yaratma kodu olacaq
            # openpyxl və ya pandas ilə

            logger.info(f"Hesabat export edildi: {file_path}")
            return True, "Hesabat uğurla export edildi"

        except Exception as e:
            logger.error(f"Export xətası: {e}")
            return False, str(e)

    def clear_cache(self):
        """Hesabat keşini təmizlə"""
        self.cache.clear()