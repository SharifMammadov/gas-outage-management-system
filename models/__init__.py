"""
Modellər paketi.

Bu versiyada əsas verilənlər bazası SQLite-dir.
PostgreSQL faylları layihədə saxlanılıb, amma avtomatik import edilmir.
"""

USE_POSTGRES = False

from models.database import Database, get_conn
from models.record import Record
