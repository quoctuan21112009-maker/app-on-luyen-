# 🚀 ONLUYEN Batch - Flask Web Application

Ứng dụng web Flask giúp nhập thông tin học sinh và chạy tự động bài tập.

## 📋 Mô Tả

Ứng dụng có 2 trang chính:

1. **Trang Đăng Ký** (`/`) - Nhập thông tin học sinh
   - Họ và tên
   - Lớp
   - Tài khoản (email)
   - Mật khẩu
   - Dữ liệu sẽ được lưu vào `Acc-onluyen.csv`

2. **Trang Nhập ID Bài** (`/homework`) - Chạy main.py
   - Nhập ID bài (log ID)
   - Ấn "Chạy ✓" để thực thi
   - Xem log output in real-time
   - Log sẽ hiển thị trạng thái thành công/lỗi

## 🛞 Cài Đặt

### Yêu Cầu
- Python 3.7+
- pip (Python package manager)

### Bước 1: Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

Hoặc chạy trực tiếp file batch:
```bash
run_app.bat
```

## ▶️ Chạy Ứng Dụng

### Cách 1: Sử dụng File Batch (Windows)
```bash
run_app.bat
```

### Cách 2: Chạy trực tiếp Python
```bash
python app.py
```

### Cách 3: Dòng lệnh với cổng tùy chỉnh
```bash
python app.py --port 8000
```

## 🌐 Truy Cập

Sau khi khởi động, mở trình duyệt và truy cập:
- **Trang chủ**: http://localhost:5000/
- **Trang đăng ký**: http://localhost:5000/ (tự động)
- **Trang nhập ID**: http://localhost:5000/homework

## 📝 Luồng Công Việc

1. ✅ Khởi động `app.py` (chạy `run_app.bat`)
2. ✅ Trên trình duyệt, truy cập http://localhost:5000/
3. ✅ Điền thông tin học sinh:
   - Họ tên
   - Lớp (ví dụ: 11a1)
   - Email/Tài khoản
   - Mật khẩu
4. ✅ Ấn "Đăng Ký & Tiếp Tục →"
5. ✅ Tự động chuyển sang trang nhập ID bài
6. ✅ Nhập ID bài (có thể nhập một phần)
7. ✅ Ấn "Chạy ✓"
8. ✅ Chờ chương trình chạy và xem log output
9. ✅ Log sẽ hiển thị trạng thái ✓ Thành công hoặc ✗ Lỗi

## 📂 Cấu Trúc File

```
.
├── app.py                  # Flask web server chính
├── main.py                 # Chương trình xử lý bài tập (được gọi từ app.py)
├── Acc-onluyen.csv        # File CSV chứa thông tin học sinh
├── requirements.txt       # List dependencies
├── run_app.bat            # Batch file để chạy app
├── templates/
│   ├── login.html         # Trang đăng ký
│   └── homework.html      # Trang nhập ID bài
└── README_APP.md          # File hướng dẫn này
```

## 🔧 API Endpoints

### POST `/register`
Lưu thông tin học sinh vào CSV

**Request:**
```json
{
    "ten": "Chu quoc tuan",
    "lop": "11a1",
    "taikhoan": "tuancq49@example.com",
    "matkhau": "429164"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Đăng ký thành công cho Chu quoc tuan",
    "stt": 8
}
```

### POST `/run`
Chạy `main.py` với ID bài

**Request:**
```json
{
    "logid": "69a57498ec661e102c25f43b"
}
```

**Response:**
```json
{
    "success": true,
    "status": "✓ Thành công",
    "message": "Output từ console",
    "log_file": "Nội dung file latest.log",
    "timestamp": "2026-03-18 10:30:45"
}
```

## 🐛 Khắc Phục Sự Cố

### Lỗi "Module not found"
```bash
pip install -r requirements.txt
```

### Cổng 5000 đã được sử dụng
```bash
python app.py --port 8000
```

### Lỗi khi gọi main.py
- Kiểm tra file `main.py` tồn tại
- Kiểm tra các module dependencies trong `main.py`
- Xem log file `latest.log`

### CSV không được tạo
- Kiểm tra quyền ghi trong thư mục
- Xóa file `Acc-onluyen.csv` cũ nếu bị hỏng

## 📊 Log File

Log output được lưu vào file `latest.log` trong thư mục làm việc.

## 🔐 Lưu Ý Bảo Mật

- **Không sử dụng trong production** mà không có HTTPS
- **Mật khẩu được lưu dưới dạng plain text** trong CSV
- Sử dụng `debug=False` khi deployed

## 📞 Hỗ Trợ

Nếu gặp vấn đề:
1. Kiểm tra console log
2. Xem nội dung file `latest.log`
3. Đảm bảo Python và Flask được cài đặt đúng

---

**Version:** 1.0  
**Last Updated:** 2026-03-18
