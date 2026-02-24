from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import pytz

# Múi giờ Việt Nam
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

def vietnam_now():
    return datetime.now(VN_TZ)

db = SQLAlchemy()

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    license_plate = db.Column(db.String(20), unique=True, nullable=False, index=True)
    owner_name = db.Column(db.String(100), nullable=False)
    owner_phone = db.Column(db.String(20))
    vehicle_type = db.Column(db.String(50))
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    color = db.Column(db.String(30))
    year = db.Column(db.Integer)
    
    account_balance = db.Column(db.Float, default=0.0)
    account_status = db.Column(db.String(20), default='active')
    
    created_at = db.Column(db.DateTime, default=vietnam_now)
    updated_at = db.Column(db.DateTime, default=vietnam_now, onupdate=vietnam_now)
    
    transactions = db.relationship('Transaction', backref='vehicle', lazy=True)
    scans = db.relationship('ScanHistory', backref='vehicle', lazy=True)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'license_plate': self.license_plate,
            'owner_name': self.owner_name,
            'owner_phone': self.owner_phone,
            'vehicle_type': self.vehicle_type,
            'brand': self.brand,
            'model': self.model,
            'color': self.color,
            'year': self.year,
            'account_balance': self.account_balance,
            'account_status': self.account_status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class Transaction(db.Model):
    """Model cho lịch sử giao dịch"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    balance_before = db.Column(db.Float, nullable=False)
    balance_after = db.Column(db.Float, nullable=False)
    toll_station = db.Column(db.String(100))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='completed')
    
    created_at = db.Column(db.DateTime, default=vietnam_now)

    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'balance_before': self.balance_before,
            'balance_after': self.balance_after,
            'toll_station': self.toll_station,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class ScanHistory(db.Model):
    """Model cho lịch sử quét"""
    __tablename__ = 'scan_history'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=True)
    scan_type = db.Column(db.String(20), nullable=False)
    scanned_data = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float)
    image_path = db.Column(db.String(255))
    station_location = db.Column(db.String(100))
    scan_result = db.Column(db.String(20), default='success')
    
    created_at = db.Column(db.DateTime, default=vietnam_now)

    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'scan_type': self.scan_type,
            'scanned_data': self.scanned_data,
            'confidence': self.confidence,
            'image_path': self.image_path,
            'station_location': self.station_location,
            'scan_result': self.scan_result,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
