from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import pytz
from ..core.models import db, Vehicle, Transaction, ScanHistory

VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

def vietnam_now():
    """Trả về thời gian hiện tại theo múi giờ Việt Nam"""
    return datetime.now(VN_TZ)


class VehicleService:
    """Service xử lý thông tin xe"""
    
    @staticmethod
    def get_vehicle_by_plate(license_plate):
        """Lấy thông tin xe theo biển số"""
        return Vehicle.query.filter_by(license_plate=license_plate.upper()).first()
    
    @staticmethod
    def get_vehicle_detailed_info(license_plate):
        """Lấy thông tin chi tiết xe bao gồm lịch sử giao dịch gần đây"""
        vehicle = Vehicle.query.filter_by(license_plate=license_plate.upper()).first()
        if not vehicle:
            return None
        
        vehicle_info = vehicle.to_dict()
        
        recent_transactions = Transaction.query.filter_by(
            vehicle_id=vehicle.id
        ).order_by(Transaction.created_at.desc()).limit(5).all()
        
        vehicle_info['recent_transactions'] = [
            {
                'id': t.id,
                'type': t.transaction_type,
                'amount': float(t.amount),
                'balance_before': float(t.balance_before),
                'balance_after': float(t.balance_after),
                'toll_station': t.toll_station,
                'date': t.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'status': t.status,
                'description': t.description
            }
            for t in recent_transactions
        ]
        
        # Lấy lịch sử quét gần nhất
        recent_scans = ScanHistory.query.filter_by(
            scanned_data=license_plate.upper()
        ).order_by(ScanHistory.created_at.desc()).limit(5).all()
        
        vehicle_info['recent_scans'] = [
            {
                'id': s.id,
                'scan_type': s.scan_type,
                'confidence': float(s.confidence) if s.confidence else 0.0,
                'location': s.station_location,
                'scan_time': s.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for s in recent_scans
        ]
        
        # Thống kê
        total_transactions = Transaction.query.filter_by(vehicle_id=vehicle.id).count()
        total_spent_result = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.vehicle_id == vehicle.id,
            Transaction.transaction_type == 'toll'
        ).scalar()
        total_spent = abs(float(total_spent_result)) if total_spent_result else 0.0
        
        total_topup_result = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.vehicle_id == vehicle.id,
            Transaction.transaction_type == 'topup'
        ).scalar()
        total_topup = float(total_topup_result) if total_topup_result else 0.0
        
        vehicle_info['statistics'] = {
            'total_transactions': total_transactions,
            'total_spent': total_spent,
            'total_topup': total_topup,
            'current_balance': float(vehicle.account_balance),
            'account_status': 'sufficient' if vehicle.account_balance >= 50000 else 'low' if vehicle.account_balance > 0 else 'empty',
            'last_activity': recent_transactions[0].created_at.strftime('%Y-%m-%d %H:%M:%S') if recent_transactions else None
        }
        
        return vehicle_info
    
    @staticmethod
    def get_vehicle_by_id(vehicle_id):
        """Lấy thông tin xe theo ID"""
        return Vehicle.query.get(vehicle_id)
    
    @staticmethod
    def create_vehicle(vehicle_data):
        """Tạo xe mới"""
        try:
            vehicle = Vehicle(
                license_plate=vehicle_data['license_plate'].upper(),
                owner_name=vehicle_data['owner_name'],
                owner_phone=vehicle_data.get('owner_phone'),
                vehicle_type=vehicle_data.get('vehicle_type'),
                brand=vehicle_data.get('brand'),
                model=vehicle_data.get('model'),
                color=vehicle_data.get('color'),
                year=vehicle_data.get('year'),
                account_balance=vehicle_data.get('account_balance', 0.0)
            )
            
            db.session.add(vehicle)
            db.session.commit()
            return vehicle, None
            
        except IntegrityError:
            db.session.rollback()
            return None, "Biển số xe đã tồn tại trong hệ thống"
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def update_vehicle(vehicle_id, vehicle_data):
        """Cập nhật thông tin xe"""
        try:
            vehicle = Vehicle.query.get(vehicle_id)
            if not vehicle:
                return None, "Không tìm thấy xe"
            
            # Cập nhật các trường
            for field in ['owner_name', 'owner_phone', 'vehicle_type', 'brand', 'model', 'color', 'year']:
                if field in vehicle_data:
                    setattr(vehicle, field, vehicle_data[field])
            
            vehicle.updated_at = vietnam_now()
            db.session.commit()
            return vehicle, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_all_vehicles(page=1, per_page=20):
        """Lấy danh sách xe với phân trang"""
        return Vehicle.query.paginate(
            page=page, per_page=per_page, error_out=False
        )


class AccountService:
    """Service xử lý tài khoản ETC"""
    
    @staticmethod
    def get_balance(license_plate):
        """Lấy số dư tài khoản"""
        vehicle = VehicleService.get_vehicle_by_plate(license_plate)
        if not vehicle:
            return None, "Không tìm thấy xe"
        
        return {
            'license_plate': vehicle.license_plate,
            'balance': vehicle.account_balance,
            'status': vehicle.account_status
        }, None
    
    @staticmethod
    def topup_account(license_plate, amount, description="Nạp tiền"):
        """Nạp tiền vào tài khoản"""
        try:
            vehicle = VehicleService.get_vehicle_by_plate(license_plate)
            if not vehicle:
                return None, "Không tìm thấy xe"
            
            if amount <= 0:
                return None, "Số tiền nạp phải lớn hơn 0"
            
            # Tạo transaction
            transaction = Transaction(
                vehicle_id=vehicle.id,
                transaction_type='topup',
                amount=amount,
                balance_before=vehicle.account_balance,
                balance_after=vehicle.account_balance + amount,
                description=description
            )
            
            # Cập nhật số dư
            vehicle.account_balance += amount
            vehicle.updated_at = vietnam_now()
            
            db.session.add(transaction)
            db.session.commit()
            
            return {
                'license_plate': vehicle.license_plate,
                'balance_before': transaction.balance_before,
                'balance_after': transaction.balance_after,
                'amount': amount,
                'transaction_id': transaction.id
            }, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def deduct_toll(license_plate, amount, toll_station, description="Thu phí BOT"):
        """Trừ tiền phí BOT"""
        try:
            vehicle = VehicleService.get_vehicle_by_plate(license_plate)
            if not vehicle:
                return None, "Không tìm thấy xe"
            
            if vehicle.account_status != 'active':
                return None, "Tài khoản không hoạt động"
            
            if vehicle.account_balance < amount:
                return None, "Số dư không đủ"
            
            # Tạo transaction
            transaction = Transaction(
                vehicle_id=vehicle.id,
                transaction_type='toll',
                amount=-amount,
                balance_before=vehicle.account_balance,
                balance_after=vehicle.account_balance - amount,
                toll_station=toll_station,
                description=description
            )
            
            # Cập nhật số dư
            vehicle.account_balance -= amount
            vehicle.updated_at = vietnam_now()
            
            db.session.add(transaction)
            db.session.commit()
            
            return {
                'license_plate': vehicle.license_plate,
                'balance_before': transaction.balance_before,
                'balance_after': transaction.balance_after,
                'toll_amount': amount,
                'toll_station': toll_station,
                'transaction_id': transaction.id
            }, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_transaction_history(license_plate, days=30, page=1, per_page=20):
        """Lấy lịch sử giao dịch"""
        vehicle = VehicleService.get_vehicle_by_plate(license_plate)
        if not vehicle:
            return None, "Không tìm thấy xe"
        
        since_date = vietnam_now() - timedelta(days=days)
        
        transactions = Transaction.query.filter(
            Transaction.vehicle_id == vehicle.id,
            Transaction.created_at >= since_date
        ).order_by(Transaction.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return transactions, None


class ScanService:
    """Service xử lý quét ảnh"""
    
    @staticmethod
    def record_scan(scan_data):
        """Ghi lại lịch sử quét"""
        try:
            # Tìm xe nếu có biển số
            vehicle = None
            if scan_data.get('license_plate'):
                vehicle = VehicleService.get_vehicle_by_plate(scan_data['license_plate'])
            
            scan_record = ScanHistory(
                vehicle_id=vehicle.id if vehicle else None,
                scan_type=scan_data['scan_type'],
                scanned_data=scan_data['scanned_data'],
                confidence=scan_data.get('confidence'),
                image_path=scan_data.get('image_path'),
                station_location=scan_data.get('station_location'),
                scan_result='success' if vehicle else 'unknown'
            )
            
            db.session.add(scan_record)
            db.session.commit()
            
            return scan_record, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_scan_history(license_plate=None, days=7, page=1, per_page=20):
        """Lấy lịch sử quét"""
        query = ScanHistory.query
        
        if license_plate:
            vehicle = VehicleService.get_vehicle_by_plate(license_plate)
            if vehicle:
                query = query.filter(ScanHistory.vehicle_id == vehicle.id)
        
        since_date = vietnam_now() - timedelta(days=days)
        query = query.filter(ScanHistory.created_at >= since_date)
        
        return query.order_by(ScanHistory.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
