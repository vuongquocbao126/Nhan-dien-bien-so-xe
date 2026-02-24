from flask import Flask, render_template
from flask_cors import CORS
import os

from config.settings import config
from src.api.routes import init_api_routes
from src.core.models import db
from src.utils.utils import setup_logging


def create_app(config_name=None):
    """Factory function để tạo Flask app"""
    
    # Lấy config từ environment hoặc dùng default
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    app_config = config[config_name]
    
    # Tạo Flask app
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(app_config)
    
    # Cấu hình database
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///etc_backend.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Enable CORS
    CORS(app)
    
    # Khởi tạo database
    db.init_app(app)
    
    # Thiết lập logging
    setup_logging(app_config.LOG_FOLDER, app_config.LOG_LEVEL)
    
    # Tạo các thư mục cần thiết
    os.makedirs(app_config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(app_config.LOG_FOLDER, exist_ok=True)
    
    # Tạo database tables
    with app.app_context():
        db.create_all()
    
    # Đăng ký routes
    init_api_routes(app, app_config)
    
    # Route trang chủ
    @app.route('/')
    def home():
        """Trang chủ với giao diện upload và quét biển số"""
        return render_template('index.html', config_name=config_name)
    
    # Route trang quản lý
    @app.route('/management')
    def management():
        """Trang quản lý thu phí, nạp tiền và lịch sử giao dịch"""
        return render_template('management.html')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'success': False, 'message': 'Endpoint không tồn tại'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'success': False, 'message': 'Lỗi server nội bộ'}, 500
    
    return app
