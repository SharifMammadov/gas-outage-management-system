"""
Bağlantı kontrolleri
"""
from models.database import Database
from models.record import Record
from models.cache import Cache
from datetime import datetime
import logging

logger = logging.getLogger('database')


class RecordController:
    """Bağlantı əməliyyatları kontrolleri"""

    def __init__(self):
        self.db = Database()
        self.cache = Cache()

    def get_all_records(self, rayon_filter: str = None, status_filter: str = None) -> list:
        """Bütün bağlantıları yüklə"""
        cache_key = f"records_{rayon_filter}_{status_filter}"
        cached = self.cache.get(cache_key)

        if cached:
            return cached

        try:
            records = Record.get_all(rayon_filter, status_filter)
            self.cache.set(cache_key, records)
            return records
        except Exception as e:
            logger.error(f"Bağlantı yükləmə xətası: {e}")
            return []

    def get_record_by_id(self, record_id: int) -> Record | None:
        """ID-ə görə bağlantı tap"""
        return Record.get_by_id(record_id)

    def create_record(self, data: dict) -> tuple[bool, Record | str]:
        """Yeni bağlantı yarat"""
        try:
            record = Record(
                rayon=data["rayon"],
                küçə=data["küçə"],
                reason=data.get("reason", ""),
                abonent_count=data.get("abonent_count", 0),
                category=data.get("category", ""),
                pipe_mm=data.get("pipe_mm"),
                closed_at=data.get("closed_at", ""),
                opened_at="",
                status="Bağlı"
            )

            record.save()

            # Keşi təmizlə
            self.cache.clear_record_cache()

            logger.info(f"Yeni bağlantı yaradıldı: ID {record.id}")
            return True, record

        except Exception as e:
            logger.error(f"Bağlantı yaratma xətası: {e}")
            return False, str(e)

    def update_record(self, record_id: int, data: dict) -> tuple[bool, str]:
        """Bağlantını yenilə"""
        try:
            record = Record.get_by_id(record_id)
            if not record:
                return False, "Bağlantı tapılmadı"

            # Məlumatları yenilə
            record.rayon = data.get("rayon", record.rayon)
            record.küçə = data.get("küçə", record.küçə)
            record.reason = data.get("reason", record.reason)
            record.abonent_count = data.get("abonent_count", record.abonent_count)
            record.category = data.get("category", record.category)
            record.pipe_mm = data.get("pipe_mm", record.pipe_mm)

            record.save()

            # Keşi təmizlə
            self.cache.clear_record_cache()

            logger.info(f"Bağlantı yeniləndi: ID {record_id}")
            return True, "Məlumatlar yeniləndi"

        except Exception as e:
            logger.error(f"Bağlantı yeniləmə xətası: {e}")
            return False, str(e)

    def change_status(self, record_id: int, new_status: str, timestamp: str = "") -> tuple[bool, str]:
        """Bağlantı statusunu dəyiş"""
        try:
            record = Record.get_by_id(record_id)
            if not record:
                return False, "Bağlantı tapılmadı"

            old_status = record.status
            current_time = timestamp or datetime.now().strftime("%d.%m.%Y %H:%M")

            if new_status == "Açıq":
                record.status = "Açıq"
                record.opened_at = current_time
            elif new_status == "Bağlı":
                record.status = "Bağlı"
                record.closed_at = current_time
                record.opened_at = ""  # Açılış tarixini təmizlə
            else:  # Stop
                record.status = "Stop"
                # Stop üçün tarix saxlanmır

            record.save()

            # Keşi təmizlə
            self.cache.clear_record_cache()

            logger.info(f"Status dəyişdirildi: ID {record_id} {old_status} -> {new_status}")
            return True, f"Status '{new_status}' olaraq dəyişdirildi"

        except Exception as e:
            logger.error(f"Status dəyişmə xətası: {e}")
            return False, str(e)

    def delete_record(self, record_id: int) -> tuple[bool, str]:
        """Bağlantını sil"""
        try:
            record = Record.get_by_id(record_id)
            if not record:
                return False, "Bağlantı tapılmadı"

            record.delete()

            # Keşi təmizlə
            self.cache.clear_record_cache()

            logger.info(f"Bağlantı silindi: ID {record_id}")
            return True, "Bağlantı silindi"

        except Exception as e:
            logger.error(f"Bağlantı silmə xətası: {e}")
            return False, str(e)

    def get_report(self, start_date: str, end_date: str) -> dict:
        """Hesabat məlumatlarını hazırla"""
        from utils.date_utils import ddmmyyyy_to_iso

        iso1 = ddmmyyyy_to_iso(start_date)
        iso2 = ddmmyyyy_to_iso(end_date)

        closed_iso = (
            "(substr(closed_at,7,4)||'-'||substr(closed_at,4,2)"
            "||'-'||substr(closed_at,1,2))"
        )

        try:
            # Ümumi statistika
            row = self.db.execute(f"""
                SELECT COALESCE(SUM(abonent_count), 0) FROM records
                WHERE closed_at != '' AND {closed_iso} BETWEEN ? AND ?
            """, (iso1, iso2), fetchone=True)

            total = int(row[0] or 0)

            # Statuslara görə statistika
            rows = self.db.execute(f"""
                SELECT status, COALESCE(SUM(abonent_count), 0) FROM records
                WHERE closed_at != '' AND {closed_iso} BETWEEN ? AND ?
                GROUP BY status
            """, (iso1, iso2), fetchall=True)

            by_status = {"Bağlı": 0, "Açıq": 0, "Stop": 0}
            for status, count in rows:
                if status in by_status:
                    by_status[status] = int(count or 0)

            # Günlük statistika
            rows = self.db.execute(f"""
                SELECT substr(closed_at, 1, 10) AS tarix,
                       TRIM(status),
                       COALESCE(SUM(abonent_count), 0)
                FROM records
                WHERE closed_at != '' AND {closed_iso} BETWEEN ? AND ?
                GROUP BY tarix, TRIM(status)
                ORDER BY {closed_iso}
            """, (iso1, iso2), fetchall=True)

            daily = {}
            for tarix, status, count in rows:
                if tarix not in daily:
                    daily[tarix] = {"Bağlı": 0, "Açıq": 0, "Stop": 0}
                if status in ("Bağlı", "Açıq", "Stop"):
                    daily[tarix][status] += int(count or 0)

            return {
                "total": total,
                "by_status": by_status,
                "daily": daily
            }

        except Exception as e:
            logger.error(f"Hesabat xətası: {e}")
            return {
                "total": 0,
                "by_status": {"Bağlı": 0, "Açıq": 0, "Stop": 0},
                "daily": {}
            }