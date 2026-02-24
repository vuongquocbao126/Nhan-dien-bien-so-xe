# ETC Backend - Hệ thống Thu phí Tự động

## 🚀 Tổng quan

ETC Backend là hệ thống API cho thu phí tự động với khả năng nhận diện biển số xe bằng AI và quản lý tài khoản ETC.

## ✨ Tính năng chính

- 🔍 **Nhận diện biển số xe** bằng AI (EasyOCR)
- 💰 **Quản lý số dư** và giao dịch ETC
- 🚗 **Quản lý thông tin xe** và chủ xe
- 📊 **Theo dõi lịch sử** quét và giao dịch
- 🌐 **Web Interface** để upload và test
- 📖 **API Documentation** với Swagger UI

## 🛠️ Cài đặt nhanh

### 1. Yêu cầu hệ thống
- Python 3.8+
- Windows/Linux/macOS

### 2. Chạy dự án
```bash
# Clone repository
git clone <repo-url>
cd ETC_Backend

# Chạy script setup (Windows)
run.bat

# Hoặc chạy thủ công
pip install -r requirements.txt
python main.py
```

### 3. Truy cập hệ thống
- **Web Interface**: http://localhost:5000
- **API Documentation**: http://localhost:5000/swagger/
- **Health Check**: http://localhost:5000/api/health

## 🌐 Web Interface

Trang chủ mới cung cấp:

### Upload và Quét biển số
- Drag & drop hình ảnh
- Preview hình ảnh trước khi quét
- Hiển thị kết quả nhận diện
- Thông tin chi tiết xe và chủ xe
- Số dư tài khoản ETC

### Giao diện thân thiện
- Responsive design
- Bootstrap 5 UI
- Font Awesome icons
- Smooth animations

## 📡 API Endpoints

### 🚗 Vehicles (Quản lý xe)
- `GET /api/vehicles` - Danh sách xe
- `POST /api/vehicles` - Tạo xe mới
- `GET /api/vehicles/{plate}` - Thông tin xe
- `GET /api/vehicles/{plate}/balance` - Số dư tài khoản

### 💰 Transactions (Giao dịch)
- `POST /api/transactions/topup` - Nạp tiền
- `POST /api/transactions/toll` - Thu phí BOT
- `GET /api/transactions/{plate}/history` - Lịch sử giao dịch

### 🔍 Scanning (Quét)
- `POST /api/scan/license-plate` - Nhận diện biển số
- `GET /api/scan/history` - Lịch sử quét

### 🔧 Health (Kiểm tra)
- `GET /api/health` - Trạng thái hệ thống

## 📁 Cấu trúc dự án

```
ETC_Backend/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── run.bat                # Quick start script
├── README.md              # Documentation
├── config/                # Configuration
│   └── settings.py
├── src/                   # Source code
│   ├── app.py            # Flask app factory
│   ├── api/              # API routes
│   ├── core/             # Business logic
│   └── utils/            # Utilities
├── templates/            # HTML templates
│   └── index.html        # Web interface
├── static/              # Static files
│   ├── css/
│   └── js/
├── uploads/             # Upload directory
├── logs/               # Log files
└── instance/           # Database
    └── etc_backend.db
```

## 🔧 Cấu hình

### Environment Variables
```bash
FLASK_ENV=development      # development/production
DATABASE_URL=sqlite:///etc_backend.db
```

### Config trong settings.py
- Upload folder
- Log settings
- Database config
- AI model settings

## 🚀 Deployment

### Development
```bash
python main.py
```

### Production
```bash
# Sử dụng Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "src.app:create_app()"
```



### Truy cập Swagger UI
Mở trình duyệt: `http://localhost:5000/swagger/`

## 📡 API Endpoints

### 🚗 Quản lý Xe & Tài khoản

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/vehicles` | Danh sách xe (có phân trang) |
| POST | `/api/vehicles` | Tạo xe mới |
| GET | `/api/vehicles/{plate}` | Thông tin xe theo biển số |
| GET | `/api/vehicles/{plate}/balance` | Số dư tài khoản |

### 💰 Giao dịch

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/transactions/topup` | Nạp tiền vào tài khoản |
| POST | `/api/transactions/toll` | Thu phí BOT |
| GET | `/api/transactions/{plate}/history` | Lịch sử giao dịch |

### 🔍 Quét & Nhận diện

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/scan/qr` | Quét mã QR từ ảnh |
| POST | `/api/scan/license-plate` | Nhận diện biển số xe |
| GET | `/api/scan/history` | Lịch sử quét |

### 🔧 System

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/health` | Health check |

## 📖 Swagger Documentation

API documentation được tạo tự động với Swagger UI:

- **URL:** `http://localhost:5000/swagger/`
- **Tính năng:** 
  - Interactive API testing
  - Request/Response examples
  - Schema validation
  - Authentication support

## 💾 Database Schema

### Vehicle (Xe)
- license_plate, owner_name, owner_phone
- vehicle_type, brand, model, color, year
- account_balance, account_status

### Transaction (Giao dịch)
- vehicle_id, transaction_type, amount
- balance_before, balance_after, toll_station

### ScanHistory (Lịch sử quét)
- vehicle_id, scan_type, scanned_data
- confidence, image_path, station_location

## 🛠️ CLI Tools

### Nhận diện biển số xe
```bash
python detect_license_plate.py
```

### Khởi tạo lại database
```bash
python init_db.py
```

### Xem dữ liệu mẫu
```bash
python init_db.py --show
```

## ⚙️ Cấu hình

### Environment Variables
```bash
FLASK_ENV=development          # development/production/testing
DATABASE_URL=sqlite:///etc.db  # Database connection string
SECRET_KEY=your-secret-key     # Flask secret key
DEBUG=True                     # Debug mode
LOG_LEVEL=INFO                # Logging level
HOST=0.0.0.0                  # Server host
PORT=5000                     # Server port
```

### Config Files
- `config/settings.py` - Cấu hình chính
- Development/Production/Testing configs

## 🧪 Testing

### Dữ liệu mẫu
Script `init_db.py` tạo sẵn:
- 5 xe mẫu với thông tin đầy đủ
- Giao dịch nạp tiền và thu phí
- Lịch sử quét QR và biển số

### Test API với Swagger
1. Truy cập `http://localhost:5000/swagger/`
2. Chọn endpoint muốn test
3. Click "Try it out"
4. Nhập parameters và execute

### Test bằng curl
```bash
# Lấy danh sách xe
curl -X GET "http://localhost:5000/api/vehicles"

# Lấy thông tin xe
curl -X GET "http://localhost:5000/api/vehicles/30G12345"

# Nạp tiền
curl -X POST "http://localhost:5000/api/transactions/topup" \
  -H "Content-Type: application/json" \
  -d '{"license_plate": "30G12345", "amount": 100000}'
```

## � Dependencies chính

- **Flask + Flask-RESTX:** Web framework + API documentation
- **SQLAlchemy:** ORM cho database
- **OpenCV + EasyOCR:** Computer vision và OCR
- **pyzbar:** QR/Barcode detection
- **Marshmallow:** Data serialization

## 🔧 Development

### Thêm API endpoint mới
1. Thêm route trong `src/api/routes.py`
2. Implement business logic trong `src/core/services.py`
3. Thêm model nếu cần trong `src/core/models.py`
4. Test với Swagger UI

### Thêm model database mới
1. Định nghĩa model trong `src/core/models.py`
2. Chạy `python init_db.py` để tạo lại database
3. Cập nhật services tương ứng

## � Troubleshooting

### Database issues
```bash
# Xóa database và tạo lại
rm etc_backend*.db
python init_db.py
```

### EasyOCR không hoạt động
- Kiểm tra cài đặt: `pip install easyocr`
- Đảm bảo có đủ RAM (>= 4GB recommended)

### Import errors
- Kiểm tra virtual environment đã activate
- Cài đặt lại requirements: `pip install -r requirements.txt`

## 📞 API Usage Examples

### JavaScript/Fetch
```javascript
// Nạp tiền
fetch('/api/transactions/topup', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    license_plate: '30G12345',
    amount: 100000
  })
})

// Upload ảnh nhận diện biển số
const formData = new FormData();
formData.append('image', fileInput.files[0]);
fetch('/api/scan/license-plate', {
  method: 'POST',
  body: formData
})
```

### Python/Requests
```python
import requests

# Lấy thông tin xe
response = requests.get('http://localhost:5000/api/vehicles/30G12345')
vehicle_info = response.json()

# Nạp tiền
response = requests.post('http://localhost:5000/api/transactions/topup', 
  json={'license_plate': '30G12345', 'amount': 100000})
```

## 📄 License

MIT License - see LICENSE file for details
