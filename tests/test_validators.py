"""
Validator testləri
"""
import unittest
import sys
import os

# Test qovluğunu əlavə et
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.validators import (
    validate_abonent_count,
    validate_pipe_mm,
    validate_required,
    validate_date
)


class TestValidators(unittest.TestCase):
    """Validator sinifinin testləri"""

    def test_validate_abonent_count(self):
        """Abonent sayı validasiyasını test et"""
        # Keçərli dəyərlər
        self.assertTrue(validate_abonent_count("5")[0])
        self.assertTrue(validate_abonent_count("0")[0])
        self.assertTrue(validate_abonent_count("1000")[0])
        self.assertTrue(validate_abonent_count("100000")[0])

        # Keçərsiz dəyərlər
        self.assertFalse(validate_abonent_count("-5")[0])
        self.assertFalse(validate_abonent_count("abc")[0])
        self.assertFalse(validate_abonent_count("")[0])
        self.assertFalse(validate_abonent_count("   ")[0])
        self.assertFalse(validate_abonent_count("100001")[0])  # Maksimumdan çox

    def test_validate_pipe_mm(self):
        """Boru diametri validasiyasını test et"""
        # Keçərli dəyərlər
        self.assertTrue(validate_pipe_mm("")[0])  # Boş ola bilər
        self.assertTrue(validate_pipe_mm("50")[0])
        self.assertTrue(validate_pipe_mm("0")[0])
        self.assertTrue(validate_pipe_mm("1000")[0])

        # Keçərsiz dəyərlər
        self.assertFalse(validate_pipe_mm("-10")[0])
        self.assertFalse(validate_pipe_mm("abc")[0])
        self.assertFalse(validate_pipe_mm("1001")[0])  # Maksimumdan çox

    def test_validate_required(self):
        """Məcburi sahə validasiyasını test et"""
        field_name = "Test sahə"

        # Keçərli dəyərlər
        self.assertTrue(validate_required("dəyər", field_name)[0])
        self.assertTrue(validate_required("  dəyər  ", field_name)[0])

        # Keçərsiz dəyərlər
        self.assertFalse(validate_required("", field_name)[0])
        self.assertFalse(validate_required("   ", field_name)[0])
        self.assertFalse(validate_required(None, field_name)[0])

    def test_validate_date(self):
        """Tarix validasiyasını test et"""
        # Keçərli tarixlər
        self.assertTrue(validate_date("15.03.2024")[0])
        self.assertTrue(validate_date("01.01.2023")[0])
        self.assertTrue(validate_date("31.12.2025")[0])

        # Keçərsiz tarixlər
        self.assertFalse(validate_date("32.01.2024")[0])  # Yanlış gün
        self.assertFalse(validate_date("15.13.2024")[0])  # Yanlış ay
        self.assertFalse(validate_date("2024-03-15")[0])  # Yanlış format
        self.assertFalse(validate_date("15/03/2024")[0])  # Yanlış format
        self.assertFalse(validate_date("")[0])  # Boş
        self.assertFalse(validate_date("   ")[0])  # Boşluq


if __name__ == '__main__':
    unittest.main()