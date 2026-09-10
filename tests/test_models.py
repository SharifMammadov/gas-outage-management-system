"""
Model testləri
"""
import unittest
import sys
import os
import tempfile
import shutil

# Test qovluğunu əlavə et
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.database import Database
from models.record import Record
from models.cache import Cache
import config


class TestModels(unittest.TestCase):
    """Model siniflərinin testləri"""

    @classmethod
    def setUpClass(cls):
        """Testlərdən əvvəl işə düşür"""
        # Test üçün müvəqqəti qovluq yarat
        cls.test_dir = tempfile.mkdtemp()
        cls.original_db_path = config.Config.DB_PATH
        config.Config.DB_PATH = os.path.join(cls.test_dir, "test.db")

        # Test bazasını yarat
        cls.db = Database()

    @classmethod
    def tearDownClass(cls):
        """Testlərdən sonra işə düşür"""
        # Orijinal yolu bərpa et
        config.Config.DB_PATH = cls.original_db_path
        # Test qovluğunu sil
        shutil.rmtree(cls.test_dir)

    def setUp(self):
        """Hər testdən əvvəl işə düşür"""
        # Test məlumatlarını təmizlə
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM records")
        c.execute("DELETE FROM rayons WHERE name LIKE 'Test%'")
        c.execute("DELETE FROM reasons WHERE name LIKE 'Test%'")
        conn.commit()
        conn.close()

        # Keşi təmizlə
        Cache().clear()

    def test_create_record(self):
        """Record yaratma testi"""
        record = Record(
            rayon="Test Rayon",
            küçə="Test Küçə 5",
            reason="Test səbəb",
            abonent_count=10,
            category="Təmir-telefonoqramma",
            pipe_mm=50,
            closed_at="15.03.2024 10:00",
            status="Bağlı"
        )

        record.save()

        # ID-nin yaradıldığını yoxla
        self.assertIsNotNone(record.id)

        # Bazadan oxu
        saved = Record.get_by_id(record.id)
        self.assertIsNotNone(saved)
        self.assertEqual(saved.rayon, "Test Rayon")
        self.assertEqual(saved.abonent_count, 10)

    def test_update_record(self):
        """Record yeniləmə testi"""
        # Yarat
        record = Record(rayon="Köhnə ad", küçə="Test küçə")
        record.save()

        # Yenilə
        record.rayon = "Yeni ad"
        record.abonent_count = 25
        record.save()

        # Yoxla
        updated = Record.get_by_id(record.id)
        self.assertEqual(updated.rayon, "Yeni ad")
        self.assertEqual(updated.abonent_count, 25)

    def test_delete_record(self):
        """Record silmə testi"""
        # Yarat
        record = Record(rayon="Silinəcək", küçə="Test")
        record.save()
        record_id = record.id

        # Sil
        record.delete()

        # Yoxla
        deleted = Record.get_by_id(record_id)
        self.assertIsNone(deleted)

    def test_get_all_records(self):
        """Bütün recordları yükləmə testi"""
        # 3 record yarat
        for i in range(3):
            record = Record(
                rayon=f"Test Rayon {i}",
                küçə=f"Test Küçə {i}"
            )
            record.save()

        # Hamısını yüklə
        records = Record.get_all()
        self.assertGreaterEqual(len(records), 3)

    def test_filter_records(self):
        """Record filter testi"""
        # Müxtəlif statuslu recordlar yarat
        record1 = Record(rayon="Rayon A", küçə="Küçə 1", status="Bağlı")
        record1.save()

        record2 = Record(rayon="Rayon B", küçə="Küçə 2", status="Açıq")
        record2.save()

        record3 = Record(rayon="Rayon C", küçə="Küçə 3", status="Stop")
        record3.save()

        # Statusa görə filter
        closed = Record.get_all(status_filter="Bağlı")
        self.assertEqual(len(closed), 1)
        self.assertEqual(closed[0].status, "Bağlı")

        # Rayona görə filter
        rayon_a = Record.get_all(rayon_filter="Rayon A")
        self.assertEqual(len(rayon_a), 1)
        self.assertEqual(rayon_a[0].rayon, "Rayon A")

    def test_cache(self):
        """Keş testi"""
        cache = Cache()

        # Məlumat yaz
        cache.set("test_key", "test_value")

        # Məlumat oxu
        value = cache.get("test_key")
        self.assertEqual(value, "test_value")

        # Təmizlə
        cache.clear("test_key")
        value = cache.get("test_key")
        self.assertIsNone(value)

        # Hamısını təmizlə
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()

        self.assertIsNone(cache.get("key1"))
        self.assertIsNone(cache.get("key2"))


if __name__ == '__main__':
    unittest.main()