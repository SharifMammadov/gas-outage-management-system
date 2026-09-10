"""
Testləri işə sal
"""
import unittest
import sys
import os

if __name__ == "__main__":
    # Test qovluğunu əlavə et
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    # Testləri tap və işə sal
    loader = unittest.TestLoader()
    tests = loader.discover('tests')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(tests)

    # Nəticəyə görə çıxış kodu
    sys.exit(not result.wasSuccessful())