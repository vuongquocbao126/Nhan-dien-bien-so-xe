# 🚗 Nhận Diện Biển Số Xe - License Plate Recognition System

Hệ thống nhận diện biển số xe tự động sử dụng AI với khả năng quản lý tài khoản ETC, xử lý giao dịch thu phí tự động.

## 📊 Thông tin dự án

| Thông tin | Chi tiết |
|-----------|----------|
| **Tên dự án** | Nhận Diện Biển Số Xe (License Plate Recognition) |
| **Loại** | Backend API + Web Interface |
| **Ngôn ngữ chính** | Python (40.4%), JavaScript (23.7%), HTML (25%), CSS (10.9%) |
| **Framework** | Flask + Flask-RESTX |
| **Database** | SQLite |
| **AI/ML** | EasyOCR, OpenCV |

## ✨ Tính năng chính

- 🔍 **Nhận diện biển số xe** bằng AI (EasyOCR) - độ chính xác cao
- 💰 **Quản lý tài khoản ETC** - số dư, giao dịch, nạp tiền
- 🚗 **Quản lý thông tin xe** - chủ sở hữu, loại xe, model, năm sản xuất
- 📊 **Theo dõi lịch sử** - quét biển số, giao dịch, lịch sử nạp tiền
- 🌐 **Web Interface** - giao diện thân thiện, upload và test trực tiếp
- 📖 **API Documentation** - tự động tạo với Swagger UI
- 🔐 **RESTful API** - endpoint có cấu trúc rõ ràng

## 🛠️ Yêu cầu hệ thống

- **Python:** 3.8 trở lên
- **Hệ điều hành:** Windows, Linux, macOS
- **RAM:** ≥ 4GB (khuyến nghị cho EasyOCR)
- **Disk:** ≥ 2GB (cho model OCR)

## 🚀 Cài đặt và Chạy

### 1. Clone Repository
```bash
git clone https://github.com/vuongquocbao126/Nhan-dien-bien-so-xe.git
cd Nhan-dien-bien-so-xe
```

### 2. Cài đặt Dependencies

**Cách 1: Script tự động (Windows)**
```bash
run.bat
```

**Cách 2: Cài đặt thủ công**
```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### 3. Chạy ứng dụng

**Development Mode**
```bash
python main.py
```

**Production Mode (Gunicorn)**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "src.app:create_app()"
```

### 4. Truy cập hệ thống

| Thành phần | URL |
|-----------|-----|
| **Web Interface** | http://localhost:5000 |
| **API Documentation** | http://localhost:5000/swagger/ |
| **Health Check** | http://localhost:5000/api/health |

## 📁 Cấu trúc Dự Án

```
Nhan-dien-bien-so-xe/
├── main.py                    # Entry point chính
├── requirements.txt           # Dependencies
├── run.bat                    # Script khởi động nhanh (Windows)
├── README.md                  # Tài liệu
├── config/
│   └── settings.py           # Cấu hình chính
├── src/
│   ├── app.py               # Flask app factory
│   ├── api/
│   │   ├── routes.py        # API endpoints
│   │   └── schemas.py       # Request/Response schemas
│   ├── core/
│   │   ├── models.py        # Database models
│   │   └── services.py      # Business logic
│   └── utils/
│       ├── ocr.py          # OCR utilities
│       ├── qr.py           # QR detection
│       └── helpers.py      # Utilities
├── templates/
│   └── index.html           # Web interface
├── static/
│   ├── css/
│   │   └── style.css       # Styling
│   └── js/
│       └── main.js         # Frontend logic
├── uploads/                 # Upload directory (hình ảnh)
├── logs/                    # Log files
└── instance/
    └── etc_backend.db      # SQLite database
```

## 🌐 Web Interface

### Tính năng chính
- ✅ **Upload hình ảnh:** Drag & drop hoặc click để chọn
- 📸 **Preview:** Xem trước ảnh trước khi xử lý
- 🔍 **Nhận diện:** Kết quả OCR chi tiết với độ tin cậy
- 📋 **Thông tin xe:** Hiển thị dữ liệu xe và chủ sở hữu
- 💳 **Tài khoản:** Số dư ETC, lịch sử giao dịch

### Giao diện
- 📱 **Responsive Design** - hoạt động trên desktop và mobile
- 🎨 **Bootstrap 5** - giao diện hiện đại
- ⚡ **Smooth Animations** - trải nghiệm mượt mà

## 📡 API Endpoints

### 🚗 Quản lý Xe

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
| POST | `/api/transactions/toll` | Thu phí BOT (trừ tiền) |
| GET | `/api/transactions/{plate}/history` | Lịch sử giao dịch |

### 🔍 Quét & Nhận diện

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/scan/license-plate` | Nhận diện biển số từ ảnh |
| POST | `/api/scan/qr` | Quét mã QR từ ảnh |
| GET | `/api/scan/history` | Lịch sử quét |

### 🔧 System

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/health` | Kiểm tra trạng thái hệ thống |

## 📖 API Documentation (Swagger)

Truy cập **http://localhost:5000/swagger/** để:
- ✅ Xem tất cả endpoints
- 🧪 Test API trực tiếp trong trình duyệt
- 📝 Xem request/response examples
- 🔍 Kiểm tra schema validation

## 💾 Database Schema

### Vehicle (Bảng xe)
```
- license_plate (TEXT, unique)
- owner_name, owner_phone
- vehicle_type, brand, model, color, year
- account_balance, account_status
- created_at, updated_at
```

### Transaction (Bảng giao dịch)
```
- vehicle_id (FK)
- transaction_type (TOPUP/TOLL)
- amount
- balance_before, balance_after
- toll_station, description
- created_at
```

### ScanHistory (Bảng lịch sử quét)
```
- vehicle_id (FK)
- scan_type (LICENSE_PLATE/QR)
- scanned_data
- confidence
- image_path, station_location
- created_at
```

## ⚙️ Cấu hình

### Environment Variables
Tạo file `.env` hoặc thiết lập biến môi trường:

```bash
# Flask
FLASK_ENV=development              # development/production/testing
SECRET_KEY=your-secret-key-here    # Flask secret key
DEBUG=True                         # Debug mode

# Database
DATABASE_URL=sqlite:///etc_backend.db

# Server
HOST=0.0.0.0
PORT=5000

# Logging
LOG_LEVEL=INFO

# Upload
MAX_UPLOAD_SIZE=16777216           # 16MB
ALLOWED_EXTENSIONS=jpg,jpeg,png
```

### Config Files
- `config/settings.py` - Cấu hình chính của ứng dụng
- Development/Production/Testing configurations

## 🧪 Test và Dữ liệu Mẫu

### Khởi tạo dữ liệu mẫu
```bash
# Tạo database mới với dữ liệu mẫu
python init_db.py

# Xem dữ liệu mẫu
python init_db.py --show
```

**Dữ liệu mẫu được tạo:**
- 5 xe mẫu với thông tin đầy đủ
- Giao dịch nạp tiền và thu phí
- Lịch sử quét biển số và mã QR

### Test API với Swagger
1. Truy cập http://localhost:5000/swagger/
2. Chọn endpoint muốn test
3. Click **"Try it out"**
4. Nhập parameters và click **"Execute"**

### Test bằng cURL

```bash
# Lấy danh sách xe
curl -X GET "http://localhost:5000/api/vehicles"

# Lấy thông tin xe cụ thể
curl -X GET "http://localhost:5000/api/vehicles/30G12345"

# Nạp tiền
curl -X POST "http://localhost:5000/api/transactions/topup" \
  -H "Content-Type: application/json" \
  -d '{"license_plate": "30G12345", "amount": 100000}'

# Kiểm tra trạng thái hệ thống
curl -X GET "http://localhost:5000/api/health"
```

### Test bằng Python
```python
import requests

base_url = "http://localhost:5000"

# Lấy danh sách xe
response = requests.get(f"{base_url}/api/vehicles")
vehicles = response.json()

# Lấy thông tin xe
response = requests.get(f"{base_url}/api/vehicles/30G12345")
vehicle = response.json()

# Nạp tiền
response = requests.post(f"{base_url}/api/transactions/topup", 
  json={"license_plate": "30G12345", "amount": 100000})
result = response.json()
```

## 📦 Dependencies Chính

| Thư viện | Mục đích |
|---------|---------|
| **Flask + Flask-RESTX** | Web framework + API documentation |
| **SQLAlchemy** | ORM cho database |
| **EasyOCR** | Nhận diện ký tự (OCR) |
| **OpenCV** | Xử lý hình ảnh |
| **pyzbar** | Quét QR/Barcode |
| **Marshmallow** | Data serialization |

Xem file `requirements.txt` để danh sách đầy đủ.

## 🔧 Development Guide

### Thêm API Endpoint mới
1. Thêm route trong `src/api/routes.py`
2. Implement business logic trong `src/core/services.py`
3. Định nghĩa schema (request/response) trong `src/api/schemas.py`
4. Thêm database model nếu cần trong `src/core/models.py`
5. Test với Swagger UI

### Thêm Database Model
1. Định nghĩa model trong `src/core/models.py`
2. Chạy `python init_db.py` để tạo lại database
3. Cập nhật services tương ứng
4. Thêm API endpoint để quản lý model

### Phát triển Frontend
- Chỉnh sửa `templates/index.html` cho HTML
- Cập nhật `static/css/style.css` cho styling
- Chỉnh sửa `static/js/main.js` cho logic

## 🛠️ CLI Tools

```bash
# Nhận diện biển số từ ảnh
python detect_license_plate.py

# Khởi tạo/Reset database
python init_db.py

# Xem dữ liệu mẫu
python init_db.py --show
```

## ⚠️ Troubleshooting

### Database bị lỗi
```bash
# Xóa database cũ
rm etc_backend.db

# Tạo lại database
python init_db.py
```

### EasyOCR không hoạt động
```bash
# Kiểm tra cài đặt
pip install easyocr

# Đảm bảo có đủ RAM (≥ 4GB)
# Kiểm tra model được download: ~/.EasyOCR/model/
```

### Import errors
```bash
# Kích hoạt virtual environment
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Cài đặt lại dependencies
pip install -r requirements.txt
```

### Port 5000 đã được sử dụng
```bash
# Thay đổi port
python main.py --port 8000

# Hoặc dùng environment variable
set FLASK_PORT=8000  # Windows
export FLASK_PORT=8000  # Linux/macOS
```

## 📊 Performance Tips

- 💾 **RAM:** Hãy để ít nhất 2-4GB RAM rảnh cho OCR
- 🖥️ **GPU:** Nếu có GPU, EasyOCR sẽ sử dụng để tăng tốc độ
- 📁 **Upload:** Giới hạn kích thước ảnh ≤ 10MB để xử lý nhanh
- 🔄 **Batch Processing:** Sử dụng Gunicorn với worker pool cho production

## 🤝 Đóng góp

Để đóng góp vào dự án:

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📄 License

MIT License - xem file `LICENSE` để chi tiết

## 📞 Liên hệ & Hỗ trợ

- 🐛 **Report Bug:** Mở GitHub Issue
- 💡 **Feature Request:** Tạo GitHub Discussion
- 📧 **Email:** vuongquocbao126@gmail.com

---

**Cập nhật lần cuối:** 2026-02-24 | **Version:** 1.0.0