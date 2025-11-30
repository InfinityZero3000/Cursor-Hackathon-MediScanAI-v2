# 🔑 HƯỚNG DẪN CẤU HÌNH GEMINI API KEY

## 📋 Tổng Quan
Gemini API được sử dụng để tóm tắt thông tin thuốc từ dược thư thành văn bản ngắn gọn (100 từ).

---

## 🚀 Các Bước Lấy API Key

### Bước 1: Truy cập Google AI Studio
Mở trình duyệt và truy cập: **https://ai.google.dev/**

### Bước 2: Đăng nhập Google Account
- Click **"Get API Key"** hoặc **"Get Started"**
- Đăng nhập bằng Google Account của bạn
- (Nếu chưa có account, tạo tài khoản Google miễn phí)

### Bước 3: Tạo API Key
1. Vào **Google AI Studio** → **Get API Key**
2. Chọn **"Create API Key"**
3. Chọn Google Cloud Project:
   - Nếu đã có project: Chọn project sẵn có
   - Nếu chưa có: Click **"Create new project"** và đặt tên project
4. Click **"Create API key in new project"**
5. API Key sẽ được tạo và hiển thị

### Bước 4: Copy API Key
- API Key có dạng: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXX`
- Click **"Copy"** để sao chép
- ⚠️ **LƯU Ý:** Không chia sẻ API key này với người khác!

---

## ⚙️ Cấu Hình Backend

### Bước 1: Mở file `.env`
```bash
cd Backend
nano .env   # Hoặc dùng VS Code: code .env
```

### Bước 2: Thêm API Key
Tìm dòng:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Thay thế bằng API key của bạn:
```env
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Bước 3: Lưu file
- Nhấn `Ctrl + S` (hoặc `Cmd + S` trên Mac)
- Đóng file

---

## 🧪 Kiểm Tra Cấu Hình

### Test 1: Test Gemini Service
```bash
cd Backend
python services/gemini_summarizer_service.py
```

**Kết quả mong đợi:**
```
🧪 Testing Gemini Summarizer Service...

1️⃣ Kiểm tra cấu hình:
   API Key configured: ✅ Yes
   Model: gemini-pro
   Max words: 100

2️⃣ Test kết nối:
   Status: ✅ Success
   Message: Gemini API hoạt động bình thường

3️⃣ Test tóm tắt:
   Success: ✅ Yes
   Word count: 98
   Summary: Paracetamol là thuốc giảm đau và hạ sốt...
```

### Test 2: Test Backend API
```bash
# Terminal 1: Khởi động backend
cd Backend
python app.py

# Terminal 2: Test health endpoint
curl http://localhost:5000/api/health
```

**Kết quả mong đợi:**
```json
{
  "status": "ok",
  "services": {
    "gemini": true,
    "tts": true,
    "ocr": true
  }
}
```

---

## 🆓 Giới Hạn Free Tier

### Gemini API Free Tier:
- **60 requests/minute** (RPM)
- **1,500 requests/day** (RPD)
- **1 million tokens/minute** (TPM)

### Nếu vượt giới hạn:
- Chờ 1 phút rồi thử lại
- Hoặc nâng cấp lên Paid Plan tại Google Cloud Console

---

## 🔒 Bảo Mật API Key

### ✅ NÊN:
- Lưu API key trong file `.env`
- Thêm `.env` vào `.gitignore`
- Không commit API key lên GitHub

### ❌ KHÔNG NÊN:
- Hardcode API key trong code
- Chia sẻ API key công khai
- Commit file `.env` lên repository

### Kiểm tra `.gitignore`:
```bash
cat .gitignore | grep .env
```

Phải có dòng: `.env`

---

## 🐛 Xử Lý Lỗi Thường Gặp

### Lỗi 1: `API key not valid`
**Nguyên nhân:** API key sai hoặc đã bị disable

**Giải pháp:**
1. Kiểm tra lại API key trong `.env`
2. Đảm bảo không có khoảng trắng thừa
3. Tạo API key mới nếu cần

### Lỗi 2: `Quota exceeded`
**Nguyên nhân:** Vượt giới hạn free tier

**Giải pháp:**
1. Chờ 1 ngày (quota reset)
2. Hoặc nâng cấp lên Paid Plan

### Lỗi 3: `Service not available`
**Nguyên nhân:** Gemini API đang maintenance

**Giải pháp:**
- Backend sẽ tự động fallback về summary cơ bản
- Thử lại sau 5-10 phút

### Lỗi 4: `GEMINI_API_KEY chưa được cấu hình`
**Nguyên nhân:** Chưa thêm API key vào `.env`

**Giải pháp:**
1. Mở file `.env`
2. Thêm dòng: `GEMINI_API_KEY=your_key_here`
3. Restart backend

---

## 📊 Monitoring Usage

### Xem usage tại Google Cloud Console:
1. Truy cập: https://console.cloud.google.com/
2. Chọn Project
3. Vào **APIs & Services** → **Dashboard**
4. Xem **Gemini API** usage

---

## 🔄 Fallback Mechanism

Nếu Gemini API không khả dụng, backend sẽ tự động:
1. Sử dụng summary cơ bản từ PDF text
2. Vẫn tạo audio bằng TTS
3. Trả về kết quả cho user (không bị fail)

---

## 📞 Hỗ Trợ

### Tài liệu chính thức:
- **Gemini API Docs:** https://ai.google.dev/docs
- **Quickstart:** https://ai.google.dev/tutorials/python_quickstart

### Liên hệ:
- GitHub Issues: [Your Repo]/issues
- Email: your-email@example.com

---

## ✅ Checklist Hoàn Thành

- [ ] Đã lấy Gemini API key
- [ ] Đã thêm API key vào `.env`
- [ ] Đã test `gemini_summarizer_service.py` thành công
- [ ] Đã test `/api/health` thấy `gemini: true`
- [ ] Đã test full flow `/api/scan-complete`
- [ ] Đã kiểm tra `.gitignore` có `.env`

---

**🎉 Chúc mừng! Bạn đã cấu hình thành công Gemini API!**
