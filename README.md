# 🏥 MediScan AI - AI-Powered Drug Information Assistant

> **v2.0** - Enhanced with Gemini AI & Text-to-Speech

Ứng dụng web thông minh sử dụng AI để quét, nhận diện và **đọc thông tin thuốc bằng giọng nói**.

## ✨ Tính Năng Mới (v2.0)

- 🤖 **Gemini AI** - Tóm tắt thông tin thuốc bằng AI
- 🔊 **Text-to-Speech** - Đọc thông tin bằng tiếng Việt
- 🎵 **Audio Player** - Nghe lại nhiều lần
- 💾 **Smart Caching** - Tối ưu hiệu suất
- 📱 **Modern UI** - Giao diện đẹp, dễ dùng

## 📋 Yêu cầu hệ thống

- **Node.js** >= 16.x (cho Frontend)
- **Python** >= 3.11 (cho Backend)
- **Camera** (webcam hoặc camera điện thoại)
- **Gemini API Key** (free tại https://ai.google.dev/)
- **npm** hoặc **yarn** hoặc **pnpm**

## 🎯 Quick Start (5 phút)

**Chi tiết đầy đủ:** Xem file [`QUICK_START.md`](QUICK_START.md)

### Bước 1: Lấy Gemini API Key (2 phút)
1. Truy cập: https://ai.google.dev/
2. Get API Key → Create API Key
3. Copy key

### Bước 2: Cấu hình (1 phút)
```bash
cd Backend
nano .env  # Thêm: GEMINI_API_KEY=your_key_here
```

### Bước 3: Chạy (2 phút)
```bash
# Terminal 1 - Backend
cd Backend && python3 app.py

# Terminal 2 - Frontend
cd Web && npm run dev
```

**Xong!** Mở http://localhost:3000 và test ngay!

## 🚀 Cài đặt Chi Tiết

### 1. Clone Repository

```bash
git clone https://github.com/TanDoan1234/MediScanAI.git
cd MediScanAI
```

### 2. Cài đặt Backend

```bash
cd Backend
pip3 install -r requirements.txt
```

**Packages mới:**
- `google-generativeai` - Gemini AI
- `gTTS` - Text-to-Speech
- `pydub` - Audio processing

### 3. Cấu hình Backend

```bash
cd Backend
nano .env  # Hoặc dùng VS Code
```

Thêm API key:
```env
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXX
```

**Lấy API key:** https://ai.google.dev/ (2 phút, miễn phí)

### 4. Chạy Backend Server

```bash
cd Backend
python3 app.py
```

Backend sẽ chạy tại: **http://localhost:5000**

✅ Kiểm tra: http://localhost:5000/api/health

### 5. Cài đặt Frontend

Mở terminal mới:

```bash
cd Web
npm install
```

### 6. Chạy Frontend

```bash
cd Web
npm run dev
```

Frontend sẽ chạy tại: **http://localhost:3000**

## 📱 Cách Sử Dụng

### Phiên Bản Mới (với AI):

1. Mở trình duyệt: `http://localhost:3000`
2. Click banner **"AI Doctor"** (màu xanh ngọc)
3. Cho phép truy cập camera
4. Đặt thuốc trong khung quét
5. Chụp ảnh
6. Chờ 5-8 giây (AI đang xử lý)
7. **Nghe thông tin thuốc bằng giọng nói!** 🔊

### Flow Xử Lý:

```
📸 Chụp ảnh → 🔍 OCR → 📊 Database → 📄 PDF → 🤖 Gemini AI → 🔊 TTS → 🎵 Audio
```

## 🏗️ Cấu Trúc Dự Án

```
MediScanAI/
├── Backend/                          # Flask API server
│   ├── services/                     # AI Services ⭐ MỚI
│   │   ├── gemini_summarizer_service.py   # Gemini AI
│   │   ├── tts_service.py                 # Text-to-Speech
│   │   ├── cache_service.py               # Caching
│   │   ├── ocr_service.py                 # OCR
│   │   ├── drug_lookup_service.py         # Database
│   │   └── pdf_extractor_service.py       # PDF
│   ├── static/audio/                 # Audio files ⭐ MỚI
│   ├── cache/                        # Cache storage ⭐ MỚI
│   ├── app.py                        # Main API (updated)
│   ├── .env                          # Config (updated)
│   ├── requirements.txt              # Dependencies (updated)
│   ├── GEMINI_SETUP.md              # Setup guide
│   ├── API_USAGE.md                 # API docs
│   ├── UPGRADE_SUMMARY.md           # Technical details
│   └── COMPLETION_REPORT.md         # Final report
├── Web/                              # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── modals/
│   │   │       └── ScanResultModal.jsx  # Updated with audio
│   │   └── App.jsx
│   └── package.json
├── Crawldata/                        # Data
│   ├── drug_database_refined.csv    # 8,608 thuốc
│   └── duoc-thu-quoc-gia-viet-nam-2018.pdf  # 1,500+ pages
├── QUICK_START.md                    # Quick guide ⭐ MỚI
└── README.md                         # This file
```

## 🔧 API Endpoints

### 1. Health Check
```bash
GET http://localhost:5000/api/health
```

### 2. Scan Basic (Không có AI)
```bash
POST http://localhost:5000/api/scan
Content-Type: application/json
{
  "image": "base64_encoded_image"
}
```

### 3. Scan Complete (Với AI + Audio) ⭐ MỚI
```bash
POST http://localhost:5000/api/scan-complete
Content-Type: multipart/form-data
image: <file>
```

**Response:**
```json
{
  "success": true,
  "drug_info": { "name": "Paracetamol", ... },
  "summary": {
    "text": "Paracetamol là thuốc...",
    "word_count": 98
  },
  "audio": {
    "url": "/static/audio/paracetamol_abc123.mp3",
    "duration": 45.5
  }
}
```

### 4. Tìm kiếm thuốc
```bash
GET http://localhost:5000/api/drugs/search?q=paracetamol
```

### 5. Chi tiết thuốc
```bash
GET http://localhost:5000/api/drug/<drug_name>
```

### 6. Serve Audio
```bash
GET http://localhost:5000/static/audio/<filename>.mp3
```

**Chi tiết API:** Xem file [`Backend/API_USAGE.md`](Backend/API_USAGE.md)

## 📚 Documentation

| File | Mô Tả | Thời Gian Đọc |
|------|-------|---------------|
| [`QUICK_START.md`](QUICK_START.md) | Hướng dẫn nhanh 5 phút | 5 min |
| [`Backend/GEMINI_SETUP.md`](Backend/GEMINI_SETUP.md) | Lấy Gemini API key | 5 min |
| [`Backend/API_USAGE.md`](Backend/API_USAGE.md) | API documentation | 10 min |
| [`Backend/UPGRADE_SUMMARY.md`](Backend/UPGRADE_SUMMARY.md) | Technical details | 15 min |
| [`Backend/COMPLETION_REPORT.md`](Backend/COMPLETION_REPORT.md) | Final report | 10 min |

## 🎯 Features

### ✅ Core Features:
- 📸 **Camera Scan** - Quét thuốc bằng camera
- 🔍 **OCR** - EasyOCR nhận diện tiếng Việt
- 📊 **Database** - 8,608 thuốc Việt Nam
- 📄 **PDF Extract** - Dược thư 1,500+ trang

### ⭐ AI Features (v2.0):
- 🤖 **Gemini AI** - Tóm tắt thông tin (100 từ)
- 🔊 **Text-to-Speech** - Đọc bằng tiếng Việt
- 🎵 **Audio Player** - Play/Pause/Replay
- 💾 **Smart Cache** - Cache 24h, tiết kiệm API

### 🎨 UI/UX:
- 📱 **Responsive Design** - Mobile-friendly
- 🎨 **Modern UI** - Gradient, animations
- ⚡ **Fast** - Response < 10s
- 🔒 **Secure** - API key protected

## 📝 Ghi Chú Kỹ Thuật

- **OCR**: Sử dụng EasyOCR với GPU support (optional)
- **Gemini AI**: Free tier 60 req/min, 1,500 req/day
- **TTS**: gTTS (free) hoặc Google Cloud TTS (paid)
- **Cache**: JSON-based, auto cleanup after 24h
- **Audio**: MP3 format, ~100KB per 45s
- **Camera**: Yêu cầu HTTPS hoặc localhost
- **CORS**: Đã cấu hình cho development

## 🐛 Troubleshooting

### ❌ "Gemini API chưa được cấu hình"
**Giải pháp:** 
- Thêm API key vào `Backend/.env`
- File: `GEMINI_API_KEY=your_key_here`
- Restart backend

### ❌ Lỗi không truy cập camera
**Giải pháp:**
- Kiểm tra quyền camera trong browser
- Sử dụng HTTPS hoặc localhost
- Reload page và cho phép lại

### ❌ Audio không phát
**Giải pháp:**
- Kiểm tra CORS settings
- Verify audio URL: http://localhost:5000/static/audio/...
- Check browser console for errors

### ❌ Lỗi kết nối API
**Giải pháp:**
- Backend đã chạy? `python3 app.py`
- Frontend đã chạy? `npm run dev`
- Check firewall/antivirus

### ❌ "Module not found"
**Giải pháp:**
```bash
cd Backend
pip3 install -r requirements.txt
```

### ❌ Gemini API Quota exceeded
**Giải pháp:**
- Chờ 1 phút (rate limit reset)
- Hoặc cache đã save kết quả
- Backend sẽ fallback về summary cơ bản

**Chi tiết:** Xem [`Backend/GEMINI_SETUP.md`](Backend/GEMINI_SETUP.md) phần "Xử Lý Lỗi"

## 🔐 Bảo Mật

- ✅ API keys trong `.env` (không commit)
- ✅ `.env` trong `.gitignore`
- ✅ Input validation (max 16MB)
- ✅ Allowed formats: PNG, JPG, JPEG, GIF, WEBP
- ✅ CORS configured
- ✅ Error handling
- 🔄 Rate limiting (recommended for production)
- 🔄 HTTPS required (production)

## 🚀 Deployment

**Production Checklist:**
- [ ] Get Gemini API key
- [ ] Set production env variables
- [ ] Configure CORS for domain
- [ ] Setup SSL certificate
- [ ] Enable logging & monitoring
- [ ] Schedule cleanup cron jobs
- [ ] Test with real devices

**Recommended Platforms:**
- **Backend:** Heroku, Railway, Render, Google Cloud Run
- **Frontend:** Vercel, Netlify, GitHub Pages
- **Database:** PostgreSQL (for user data)

## 📊 Statistics

- **Drug Database:** 8,608 thuốc Việt Nam
- **PDF Pages:** 1,500+ trang
- **Services:** 6 backend services
- **API Endpoints:** 6 endpoints
- **Documentation:** 6 markdown files
- **Code Lines:** ~1,500 lines (v2.0)

## 🙏 Acknowledgments

**Technologies:**
- Flask, Python 3.11
- React, Vite, Tailwind CSS
- Google Gemini AI
- gTTS (Google Text-to-Speech)
- EasyOCR
- pdfplumber

**Data:**
- Dược thư quốc gia Việt Nam 2018
- drug_database_refined.csv

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📞 Support

- **Documentation:** See files above
- **Issues:** GitHub Issues
- **Email:** your-email@example.com
- **Gemini API:** https://ai.google.dev/

## 📄 License

MIT License - See LICENSE file for details

---

**Project:** MediScanAI v2.0  
**Status:** ✅ Production Ready  
**Date:** November 29, 2025  
**Developer:** TanDoan1234  

**🎉 Made with ❤️ for healthcare accessibility**

