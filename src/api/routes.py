from flask import request
from flask_restx import Api, Resource, Namespace, fields
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import os
from datetime import datetime

from ..core.image_processor import LicensePlateProcessor
from ..core.services import VehicleService, AccountService, ScanService
from ..core.models import Vehicle, Transaction, ScanHistory
from ..utils.utils import allowed_file


def init_api_routes(app, config):
    """Khởi tạo API với Swagger documentation"""
    
    # Tạo API instance với Swagger
    api = Api(
        app,
        version='1.0',
        title='ETC Backend API',
        description='API cho hệ thống thu phí tự động ETC',
        doc='/swagger/',
        prefix='/api'
    )
    
    # Khởi tạo processor
    license_processor = LicensePlateProcessor(config.__dict__)
    
    # ===================== MODELS =====================
    
    # Model cho response chung
    base_response = api.model('BaseResponse', {
        'success': fields.Boolean(required=True, description='Trạng thái thành công'),
        'message': fields.String(required=True, description='Thông báo'),
        'data': fields.Raw(description='Dữ liệu trả về')
    })
    
    # Model cho thông tin xe
    vehicle_model = api.model('Vehicle', {
        'id': fields.Integer(description='ID xe'),
        'license_plate': fields.String(required=True, description='Biển số xe'),
        'owner_name': fields.String(required=True, description='Tên chủ xe'),
        'owner_phone': fields.String(description='Số điện thoại'),
        'vehicle_type': fields.String(description='Loại xe'),
        'brand': fields.String(description='Hãng xe'),
        'model': fields.String(description='Model xe'),
        'color': fields.String(description='Màu xe'),
        'year': fields.Integer(description='Năm sản xuất'),
        'account_balance': fields.Float(description='Số dư tài khoản'),
        'account_status': fields.String(description='Trạng thái tài khoản')
    })
    
    # Model cho tạo xe mới
    vehicle_create = api.model('VehicleCreate', {
        'license_plate': fields.String(required=True, description='Biển số xe'),
        'owner_name': fields.String(required=True, description='Tên chủ xe'),
        'owner_phone': fields.String(description='Số điện thoại'),
        'vehicle_type': fields.String(description='Loại xe (Car/Motorcycle/Truck)'),
        'brand': fields.String(description='Hãng xe'),
        'model': fields.String(description='Model xe'),
        'color': fields.String(description='Màu xe'),
        'year': fields.Integer(description='Năm sản xuất'),
        'account_balance': fields.Float(description='Số dư ban đầu', default=0.0)
    })
    
    # Model cho nạp tiền
    topup_model = api.model('TopUp', {
        'license_plate': fields.String(required=True, description='Biển số xe'),
        'amount': fields.Float(required=True, description='Số tiền nạp'),
        'description': fields.String(description='Mô tả giao dịch')
    })
    
    # Model cho thu phí
    toll_model = api.model('TollCharge', {
        'license_plate': fields.String(required=True, description='Biển số xe'),
        'amount': fields.Float(required=True, description='Số tiền thu phí'),
        'toll_station': fields.String(required=True, description='Trạm thu phí'),
        'description': fields.String(description='Mô tả giao dịch')
    })
    
    # Model cho lịch sử giao dịch
    transaction_model = api.model('Transaction', {
        'id': fields.Integer(description='ID giao dịch'),
        'transaction_type': fields.String(description='Loại giao dịch'),
        'amount': fields.Float(description='Số tiền'),
        'balance_before': fields.Float(description='Số dư trước giao dịch'),
        'balance_after': fields.Float(description='Số dư sau giao dịch'),
        'toll_station': fields.String(description='Trạm thu phí'),
        'description': fields.String(description='Mô tả'),
        'status': fields.String(description='Trạng thái'),
        'created_at': fields.String(description='Thời gian tạo')
    })
    
    # ===================== NAMESPACES =====================
    
    # Namespace cho xe và tài khoản
    vehicle_ns = Namespace('vehicles', description='Quản lý thông tin xe và tài khoản ETC')
    api.add_namespace(vehicle_ns)
    
    # Namespace cho quét ảnh
    scan_ns = Namespace('scan', description='Nhận diện biển số xe từ ảnh')
    api.add_namespace(scan_ns)
    
    # Namespace cho giao dịch
    transaction_ns = Namespace('transactions', description='Quản lý giao dịch và số dư')
    api.add_namespace(transaction_ns)
    
    # ===================== VEHICLE ENDPOINTS =====================
    
    @vehicle_ns.route('')
    class VehicleListAPI(Resource):
        @vehicle_ns.doc('list_vehicles')
        @vehicle_ns.marshal_with(base_response)
        @vehicle_ns.param('page', 'Số trang', type=int, default=1)
        @vehicle_ns.param('per_page', 'Số bản ghi mỗi trang', type=int, default=20)
        def get(self):
            """Lấy danh sách xe"""
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            pagination = VehicleService.get_all_vehicles(page, per_page)
            
            return {
                'success': True,
                'message': f'Lấy danh sách xe thành công',
                'data': {
                    'vehicles': [vehicle.to_dict() for vehicle in pagination.items],
                    'total': pagination.total,
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'pages': pagination.pages
                }
            }
        
        @vehicle_ns.doc('create_vehicle')
        @vehicle_ns.expect(vehicle_create)
        @vehicle_ns.marshal_with(base_response)
        def post(self):
            """Tạo xe mới"""
            data = request.json
            
            vehicle, error = VehicleService.create_vehicle(data)
            if error:
                return {'success': False, 'message': error}, 400
            
            return {
                'success': True,
                'message': 'Tạo xe thành công',
                'data': vehicle.to_dict()
            }, 201
    
    @vehicle_ns.route('/<string:license_plate>')
    class VehicleAPI(Resource):
        @vehicle_ns.doc('get_vehicle')
        @vehicle_ns.marshal_with(base_response)
        def get(self, license_plate):
            """Lấy thông tin xe theo biển số"""
            vehicle = VehicleService.get_vehicle_by_plate(license_plate)
            if not vehicle:
                return {'success': False, 'message': 'Không tìm thấy xe'}, 404
            
            return {
                'success': True,
                'message': 'Lấy thông tin xe thành công',
                'data': vehicle.to_dict()
            }
    
    @vehicle_ns.route('/<string:license_plate>/detailed')
    class VehicleDetailedAPI(Resource):
        @vehicle_ns.doc('get_vehicle_detailed')
        @vehicle_ns.marshal_with(base_response)
        def get(self, license_plate):
            """Lấy thông tin chi tiết xe và tài khoản"""
            vehicle_info = VehicleService.get_vehicle_detailed_info(license_plate)
            if not vehicle_info:
                return {'success': False, 'message': 'Không tìm thấy xe'}, 404
            
            return {
                'success': True,
                'message': 'Lấy thông tin chi tiết xe thành công',
                'data': vehicle_info
            }
    
    @vehicle_ns.route('/<string:license_plate>/balance')
    class VehicleBalanceAPI(Resource):
        @vehicle_ns.doc('get_balance')
        @vehicle_ns.marshal_with(base_response)
        def get(self, license_plate):
            """Lấy số dư tài khoản"""
            result, error = AccountService.get_balance(license_plate)
            if error:
                return {'success': False, 'message': error}, 404
            
            return {
                'success': True,
                'message': 'Lấy số dư thành công',
                'data': result
            }
    
    # ===================== TRANSACTION ENDPOINTS =====================
    
    @transaction_ns.route('/topup')
    class TopUpAPI(Resource):
        @transaction_ns.doc('topup_account')
        @transaction_ns.expect(topup_model)
        @transaction_ns.marshal_with(base_response)
        def post(self):
            """Nạp tiền vào tài khoản"""
            data = request.json
            
            result, error = AccountService.topup_account(
                data['license_plate'],
                data['amount'],
                data.get('description', 'Nạp tiền')
            )
            
            if error:
                return {'success': False, 'message': error}, 400
            
            return {
                'success': True,
                'message': 'Nạp tiền thành công',
                'data': result
            }
    
    @transaction_ns.route('/toll')
    class TollChargeAPI(Resource):
        @transaction_ns.doc('charge_toll')
        @transaction_ns.expect(toll_model)
        @transaction_ns.marshal_with(base_response)
        def post(self):
            """Thu phí BOT"""
            data = request.json
            
            result, error = AccountService.deduct_toll(
                data['license_plate'],
                data['amount'],
                data['toll_station'],
                data.get('description', 'Thu phí BOT')
            )
            
            if error:
                return {'success': False, 'message': error}, 400
            
            return {
                'success': True,
                'message': 'Thu phí thành công',
                'data': result
            }
    
    @transaction_ns.route('/<string:license_plate>/history')
    class TransactionHistoryAPI(Resource):
        @transaction_ns.doc('get_transaction_history')
        @transaction_ns.marshal_with(base_response)
        @transaction_ns.param('days', 'Số ngày lịch sử', type=int, default=30)
        @transaction_ns.param('page', 'Số trang', type=int, default=1)
        @transaction_ns.param('per_page', 'Số bản ghi mỗi trang', type=int, default=20)
        def get(self, license_plate):
            """Lấy lịch sử giao dịch"""
            days = request.args.get('days', 30, type=int)
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            pagination, error = AccountService.get_transaction_history(
                license_plate, days, page, per_page
            )
            
            if error:
                return {'success': False, 'message': error}, 404
            
            return {
                'success': True,
                'message': 'Lấy lịch sử giao dịch thành công',
                'data': {
                    'transactions': [t.to_dict() for t in pagination.items],
                    'total': pagination.total,
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'pages': pagination.pages
                }
            }
    
    # ===================== SCAN ENDPOINTS =====================
    
    upload_parser = api.parser()
    upload_parser.add_argument('image', location='files', type=FileStorage, required=True, help='File ảnh')
    upload_parser.add_argument('station_location', location='form', type=str, help='Vị trí trạm')
    
    @scan_ns.route('/license-plate')
    class LicensePlateScanAPI(Resource):
        @scan_ns.doc('scan_license_plate')
        @scan_ns.expect(upload_parser)
        @scan_ns.marshal_with(base_response)
        def post(self):
            """Nhận diện biển số xe từ ảnh"""
            if 'image' not in request.files:
                return {'success': False, 'message': 'Không có file được gửi'}, 400
            
            file = request.files['image']
            station_location = request.form.get('station_location')
            
            if not allowed_file(file.filename, config.ALLOWED_EXTENSIONS):
                return {'success': False, 'message': 'File phải là ảnh hợp lệ'}, 400
            
            # Tạo tên file
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            filename = f"plate_{current_time}.{file_extension}"
            
            # Lưu file
            filepath = os.path.join(config.UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Nhận diện biển số với logic cải tiến
            result = license_processor.detect_license_plate(filepath)
            
            # Xử lý kết quả và ghi lịch sử
            processed_results = []
            if result['success'] and result.get('license_plates'):
                for plate_info in result['license_plates']:
                    # Ghi lịch sử quét
                    ScanService.record_scan({
                        'scan_type': 'license_plate',
                        'scanned_data': plate_info['text'],
                        'confidence': plate_info['confidence'],
                        'license_plate': plate_info['text'],
                        'image_path': filepath,
                        'station_location': station_location
                    })
                    
                    # Lấy thông tin xe từ database
                    vehicle = VehicleService.get_vehicle_by_plate(plate_info['text'])
                    vehicle_detailed = None
                    
                    if vehicle:
                        # Lấy thông tin chi tiết cho biển số có trong hệ thống
                        vehicle_detailed = VehicleService.get_vehicle_detailed_info(plate_info['text'])
                    
                    processed_result = {
                        'license_plate': plate_info['text'],
                        'confidence': round(plate_info['confidence'], 3),
                        'score': round(plate_info.get('score', 0), 3),
                        'source': plate_info.get('source', 'unknown'),
                        'formatted': plate_info.get('formatted', plate_info['text']),
                        'original_text': plate_info.get('original_text', ''),
                        'vehicle_found': vehicle is not None
                    }
                    
                    if vehicle_detailed:
                        processed_result['vehicle_info'] = vehicle_detailed
                        # Thêm thông tin trạng thái tài khoản
                        balance = vehicle_detailed.get('account_balance', 0)
                        processed_result['account_status'] = {
                            'balance': balance,
                            'status': 'sufficient' if balance >= 50000 else 'low' if balance > 0 else 'empty',
                            'warning': balance < 50000,
                            'can_travel': balance > 0
                        }
                    
                    processed_results.append(processed_result)
            
            # Tính toán thống kê
            stats = {
                'total_candidates': result.get('total_candidates', 0),
                'processing_versions': result.get('processing_versions', 1),
                'valid_plates_found': len(processed_results),
                'vehicles_in_system': sum(1 for r in processed_results if r['vehicle_found'])
            }
            
            return {
                'success': result['success'],
                'message': result.get('message', 'Hoàn tất nhận diện biển số'),
                'data': {
                    'license_plates': processed_results,
                    'statistics': stats,
                    'debug_info': result.get('debug_info', ''),
                    'processing_method': result.get('method', 'easyocr')
                }
            }
    
    @scan_ns.route('/history')
    class ScanHistoryAPI(Resource):
        @scan_ns.doc('get_scan_history')
        @scan_ns.marshal_with(base_response)
        @scan_ns.param('license_plate', 'Biển số xe (tùy chọn)', type=str)
        @scan_ns.param('days', 'Số ngày lịch sử', type=int, default=7)
        @scan_ns.param('page', 'Số trang', type=int, default=1)
        @scan_ns.param('per_page', 'Số bản ghi mỗi trang', type=int, default=20)
        def get(self):
            """Lấy lịch sử quét"""
            license_plate = request.args.get('license_plate')
            days = request.args.get('days', 7, type=int)
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            pagination = ScanService.get_scan_history(license_plate, days, page, per_page)
            
            return {
                'success': True,
                'message': 'Lấy lịch sử quét thành công',
                'data': {
                    'scans': [scan.to_dict() for scan in pagination.items],
                    'total': pagination.total,
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'pages': pagination.pages
                }
            }
    
    # Health check endpoint
    @api.route('/health')
    class HealthCheckAPI(Resource):
        @api.doc('health_check')
        def get(self):
            """Kiểm tra trạng thái server"""
            try:
                # Test database connection
                total_vehicles = Vehicle.query.count()
                total_transactions = Transaction.query.count()
                
                return {
                    'success': True,
                    'message': 'ETC Backend API is running',
                    'data': {
                        'status': 'healthy',
                        'database_status': 'connected',
                        'total_vehicles': total_vehicles,
                        'total_transactions': total_transactions,
                        'timestamp': datetime.now().isoformat(),
                        'version': '1.0'
                    }
                }
            except Exception as e:
                return {
                    'success': False,
                    'message': f'Health check failed: {str(e)}',
                    'data': {
                        'status': 'unhealthy',
                        'database_status': 'error',
                        'timestamp': datetime.now().isoformat(),
                        'version': '1.0'
                    }
                }, 500
