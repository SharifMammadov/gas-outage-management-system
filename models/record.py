"""
Bağlantı modeli
"""
from models.database import Database
import logging
import sqlite3

logger = logging.getLogger('database')

class Record:
    """Bağlantı sinfi"""

    def __init__(self, id=None, rayon=None, küçə=None, reason=None,
                 abonent_count=0, category=None, pipe_mm=None,
                 closed_at=None, opened_at=None, status='Bağlı'):
        self.id = id
        self.rayon = rayon
        self.küçə = küçə
        self.reason = reason
        self.abonent_count = abonent_count if abonent_count is not None else 0
        self.category = category
        self.pipe_mm = pipe_mm
        self.closed_at = closed_at if closed_at is not None else ""
        self.opened_at = opened_at if opened_at is not None else ""
        self.status = status if status is not None else "Bağlı"

    @classmethod
    def from_row(cls, row):
        """Verilənlər bazası sətirindən Record obyekti yarat"""
        if not row:
            return None
        return cls(
            id=row[0],
            rayon=row[1],
            küçə=row[2],
            reason=row[3],
            abonent_count=row[4],
            category=row[5],
            pipe_mm=row[6],
            closed_at=row[7],
            opened_at=row[8],
            status=row[9]
        )

    def save(self):
        """Record-u verilənlər bazasına yaz"""
        db = Database()

        try:
            if self.id:
                # Update
                query = """
                    UPDATE records SET 
                        rayon=?, küçə=?, reason=?, abonent_count=?,
                        category=?, pipe_mm=?, status=?, closed_at=?, opened_at=?
                    WHERE id=?
                """
                params = (
                    self.rayon, self.küçə, self.reason, self.abonent_count,
                    self.category, self.pipe_mm, self.status,
                    self.closed_at, self.opened_at, self.id
                )
                db.execute(query, params)
                logger.info(f"Record yeniləndi: {self.id}")

            else:
                # Insert
                query = """
                    INSERT INTO records 
                        (rayon, küçə, reason, abonent_count, category, pipe_mm, 
                         closed_at, opened_at, status)
                    VALUES (?,?,?,?,?,?,?,?,?)
                """
                params = (
                    self.rayon, self.küçə, self.reason, self.abonent_count,
                    self.category, self.pipe_mm, self.closed_at,
                    self.opened_at, self.status
                )

                # Xüsusi olaraq lastrowid almaq üçün connection yaradaq
                conn = db.get_connection()
                c = conn.cursor()
                c.execute(query, params)
                conn.commit()

                # Yeni ID-ni əldə et
                self.id = c.lastrowid
                conn.close()

                logger.info(f"Yeni record yaradıldı: ID {self.id}")

            return self

        except Exception as e:
            logger.error(f"Record save xətası: {e}")
            raise

    def delete(self):
        """Record-u sil"""
        if self.id:
            db = Database()
            db.execute("DELETE FROM records WHERE id=?", (self.id,))
            logger.info(f"Record silindi: {self.id}")

    @classmethod
    def get_by_id(cls, id):
        """ID-ə görə record tap"""
        db = Database()
        row = db.execute(
            "SELECT * FROM records WHERE id=?",
            (id,),
            fetchone=True
        )
        return cls.from_row(row) if row else None

    @classmethod
    def get_all(cls, rayon_filter=None, status_filter=None):
        """Bütün record-ları yüklə"""
        db = Database()
        query = "SELECT * FROM records WHERE 1=1"
        params = []

        if rayon_filter:
            query += " AND LOWER(rayon) LIKE ?"
            params.append(f"%{rayon_filter.lower()}%")

        if status_filter and status_filter != "Hamısı":
            query += " AND status = ?"
            params.append(status_filter)

        query += " ORDER BY id DESC"

        rows = db.execute(query, params, fetchall=True)
        return [cls.from_row(row) for row in rows]

    def __repr__(self):
        """Record-un string təsviri"""
        return f"<Record id={self.id} rayon={self.rayon} status={self.status}>"