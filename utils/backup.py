"""
Avtomatik backup sistemi
"""
import shutil
import threading
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from config import Config

logger = logging.getLogger('backup')


class BackupManager:
    """Backup meneceri - avtomatik backup"""

    def __init__(self):
        self.backup_dir = Config.BACKUP_DIR
        self.db_path = Config.DB_PATH
        self.running = False
        self.thread = None

    def start_auto_backup(self, interval_hours=24):
        """Avtomatik backup-ı başlat (hər 24 saatdan bir)"""
        self.running = True
        self.thread = threading.Thread(target=self._backup_loop, args=(interval_hours,), daemon=True)
        self.thread.start()
        logger.info(f"Avtomatik backup başladıldı (hər {interval_hours} saat)")

    def stop_auto_backup(self):
        """Avtomatik backup-ı dayandır"""
        self.running = False
        logger.info("Avtomatik backup dayandırıldı")

    def _backup_loop(self, interval_hours):
        """Backup döngüsü"""
        while self.running:
            try:
                self.create_backup()
                # Növbəti backup-a qədər gözlə
                for _ in range(interval_hours * 3600):
                    if not self.running:
                        break
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Backup döngü xətası: {e}")
                time.sleep(3600)  # 1 saat gözlə, təkrar cəhd et

    def create_backup(self, backup_type="daily"):
        """Backup yarat"""
        try:
            # Backup qovluğunun olduğuna əmin ol
            self.backup_dir.mkdir(exist_ok=True, parents=True)

            # Tarix formatı
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Backup fayl adı
            if backup_type == "daily":
                backup_file = self.backup_dir / f"daily_backup_{timestamp}.db"
            elif backup_type == "weekly":
                backup_file = self.backup_dir / f"weekly_backup_{timestamp}.db"
            else:
                backup_file = self.backup_dir / f"manual_backup_{timestamp}.db"

            # Backup yarat
            shutil.copy2(self.db_path, backup_file)

            # Köhnə backup-ları təmizlə (30 gündən köhnələri sil)
            self._clean_old_backups()

            logger.info(f"✅ Backup yaradıldı: {backup_file}")

            return backup_file

        except Exception as e:
            logger.error(f"❌ Backup xətası: {e}")
            return None

    def _clean_old_backups(self, days=30):
        """Köhnə backup-ları təmizlə"""
        try:
            now = datetime.now()
            for backup_file in self.backup_dir.glob("*.db"):
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if (now - file_time) > timedelta(days=days):
                    backup_file.unlink()
                    logger.info(f"Köhnə backup silindi: {backup_file}")
        except Exception as e:
            logger.error(f"Backup təmizləmə xətası: {e}")

# Qlobal backup meneceri
backup_manager = BackupManager()
