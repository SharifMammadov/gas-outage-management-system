"""
Keş mexanizmi
"""
import time
import threading


class Cache:
    """Məlumat keşi - Singleton pattern"""

    _instance = None
    _lock = threading.Lock()
    CACHE_DURATION = 300  # 5 dəqiqə

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._cache = {}
        return cls._instance

    def get(self, key):
        """Keşdən məlumat al"""
        if key in self._cache:
            timestamp, data = self._cache[key]
            if time.time() - timestamp < self.CACHE_DURATION:
                return data
            else:
                del self._cache[key]
        return None

    def set(self, key, data):
        """Məlumatı keşə yaz"""
        self._cache[key] = (time.time(), data)

    def clear(self, key=None):
        """Keşi təmizlə"""
        if key:
            self._cache.pop(key, None)
        else:
            self._cache.clear()

    def clear_record_cache(self):
        """Bağlantı ilə bağlı keşləri təmizlə"""
        keys_to_remove = []
        for key in self._cache:
            if key.startswith('records_') or key == 'report':
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del self._cache[key]