"""
Utilities cho ETC Backend
"""
import logging
import os
from datetime import datetime
from pathlib import Path
import pytz

# Múi giờ Việt Nam
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

def vietnam_now():
    return datetime.now(VN_TZ)

def setup_logging(log_folder, log_level='INFO'):
    
    # Tạo thư mục logs nếu chưa có
    Path(log_folder).mkdir(parents=True, exist_ok=True)
    
    # Tạo tên file log theo ngày (múi giờ Việt Nam)
    log_filename = f"etc_backend_{vietnam_now().strftime('%Y%m%d')}.log"
    log_path = os.path.join(log_folder, log_filename)
    
    # Cấu hình logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()  # Console output
        ]
    )
    
    return logging.getLogger(__name__)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
