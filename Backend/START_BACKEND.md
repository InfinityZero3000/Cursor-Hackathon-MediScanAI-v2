# 🚀 Hướng dẫn chạy Backend

## ✅ Dependencies đã cài đặt

Các package cơ bản đã được cài đặt:
- ✅ Flask
- ✅ flask-cors
- ✅ opencv-python
- ✅ Pillow
- ✅ pandas
- ✅ numpy
- ✅ Werkzeug
- ✅ pypdf

## ⚠️ EasyOCR (Optional)

EasyOCR chưa được cài đặt vì cần torch (chưa hỗ trợ Python 3.13).

**Backend vẫn chạy được** nhưng OCR sẽ không hoạt động. Khi cần OCR:
- Sử dụng Python 3.11 hoặc 3.12
- Hoặc cài đặt torch từ source

## 🚀 Cách chạy Backend

### Cách 1: Chạy trực tiếp
```bash
cd Backend
python3 app.py
```

### Cách 2: Chạy trong background
```bash
cd Backend
python3 app.py &
```

### Cách 3: Sử dụng screen/tmux
```bash
screen -S backend
cd Backend
python3 app.py
# Nhấn Ctrl+A, D để detach
```

## 📡 Kiểm tra Backend

### Test Health Endpoint
```bash
curl http://localhost:5000/api/health
```

**Kết quả mong đợi:**
```json
{
  "status": "ok",
  "message": "Backend API is running",
  "drugs_loaded": 8610
}
```

### Test Search Endpoint
```bash
curl "http://localhost:5000/api/drugs/search?q=panadol"
```

## 🐛 Xử lý lỗi

### Lỗi: "Port already in use"
```bash
# Tìm process đang dùng port 5000
lsof -i :5000

# Kill process
kill -9 <PID>
```

### Lỗi: "Module not found"
```bash
# Cài đặt lại dependencies
cd Backend
pip3 install -r requirements.txt
```

### Lỗi: "Database not found"
- Đảm bảo file `Crawldata/drug_database_refined.csv` tồn tại
- Kiểm tra đường dẫn trong `app.py`

## ✅ Backend đang chạy

Khi backend chạy thành công, bạn sẽ thấy:
```
✅ Đã load 8610 thuốc từ database
✅ Đã load PDF với XXXX trang
🚀 Starting MediScan AI Backend Server...
📡 API available at http://localhost:5000
 * Running on http://0.0.0.0:5000
```

## 🔗 Endpoints

- **Health**: `GET http://localhost:5000/api/health`
- **Scan**: `POST http://localhost:5000/api/scan`
- **Search**: `GET http://localhost:5000/api/drugs/search?q=...`

## 📝 Lưu ý

1. **OCR**: Nếu EasyOCR chưa cài, OCR sẽ trả về `None` và backend sẽ báo warning
2. **Database**: Cần file `drug_database_refined.csv` trong thư mục `Crawldata/`
3. **PDF**: Cần file `duoc-thu-quoc-gia-viet-nam-2018.pdf` trong thư mục `Crawldata/`

