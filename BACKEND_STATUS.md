# ✅ Backend Status

## 📦 Dependencies đã cài đặt

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

**Backend vẫn chạy được** nhưng OCR sẽ không hoạt động. Khi cần OCR, backend sẽ báo warning.

## 🚀 Cách chạy Backend

### Option 1: Sử dụng script
```bash
cd Backend
./run_backend.sh
```

### Option 2: Chạy trực tiếp
```bash
cd Backend
python3 app.py
```

## 📡 Port Configuration

- **Backend Port**: `5001` (đã đổi từ 5000 vì port 5000 bị chiếm)
- **Frontend API URL**: `http://localhost:5001/api` (đã cập nhật)

## ✅ Kiểm tra Backend

Sau khi chạy backend, test:

```bash
curl http://localhost:5001/api/health
```

**Kết quả mong đợi:**
```json
{
  "status": "ok",
  "message": "Backend API is running",
  "drugs_loaded": 8610
}
```

## 🔗 Endpoints

- **Health**: `GET http://localhost:5001/api/health`
- **Scan**: `POST http://localhost:5001/api/scan`
- **Search**: `GET http://localhost:5001/api/drugs/search?q=...`

## 📝 Lưu ý

1. **Port 5001**: Đã đổi từ 5000 để tránh conflict
2. **Frontend**: Đã cập nhật API URL trong `Web/src/utils/api.js`
3. **OCR**: Sẽ không hoạt động nếu EasyOCR chưa cài, nhưng backend vẫn chạy được

## 🎯 Next Steps

1. Chạy backend: `cd Backend && python3 app.py`
2. Chạy frontend: `cd Web && npm run dev`
3. Test kết nối: Mở `http://localhost:3000` và test scan function

