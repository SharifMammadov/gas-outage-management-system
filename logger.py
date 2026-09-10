"""
Loglama sistemi
"""
import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from config import Config

def setup_logging():
    """Loglama sistemini qur"""

    # EXE işləyən qovluğu tap
    if getattr(sys, 'frozen', False):
        # EXE olaraq işləyir
        base_dir = Path(sys.executable).parent
    else:
        # Python skripti olaraq işləyir
        base_dir = Config.BASE_DIR

    # Logs qovluğunu yarat
    logs_dir = base_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / f"app_{datetime.now():%Y%m%d}.log"

    # Formatlar
    detailed_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Root logger
    logging.basicConfig(
        level=logging.INFO,
        format=detailed_format,
        handlers=[
            # Fayla yaz
            logging.FileHandler(
                log_file,
                encoding='utf-8'
            ),
            # Konsola yaz
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Ayrı modullar üçün logger-lər yarat
    loggers = {
        'database': logging.getLogger('database'),
        'auth': logging.getLogger('auth'),
        'ui': logging.getLogger('ui'),
        'backup': logging.getLogger('backup')
    }

    # Başlanğıc mesajı
    root_logger = logging.getLogger()
    root_logger.info(f"📁 Log faylı: {log_file}")
    root_logger.info(f"📁 İşləmə qovluğu: {base_dir}")

    return logging.getLogger(__name__)