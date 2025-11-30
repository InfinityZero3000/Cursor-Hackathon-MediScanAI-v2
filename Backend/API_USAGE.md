# 📝 HƯỚNG DẪN SỬ DỤNG API MỚI

## 🎯 Tổng Quan

Backend MediScanAI đã được nâng cấp với 2 API endpoints:

### 1. `/api/scan` - API Cơ Bản (Không có AI)
- OCR nhận diện text
- Database lookup
- PDF extraction
- ❌ Không có Gemini summary
- ❌ Không có Text-to-Speech

### 2. `/api/scan-complete` - API Hoàn Chỉnh (Full AI) ⭐
- OCR nhận diện text
- Database lookup
- PDF extraction
- ✅ Gemini AI tóm tắt (100 từ)
- ✅ Text-to-Speech audio

---

## 🔧 Cách Sử Dụng API

### Endpoint: `POST /api/scan-complete`

**URL:** `http://localhost:5000/api/scan-complete`

**Method:** `POST`

**Content-Type:** `multipart/form-data` hoặc `application/json`

---

## 📤 Request Format

### Option 1: File Upload (Form Data)
```javascript
const formData = new FormData();
formData.append('image', imageFile);

fetch('http://localhost:5000/api/scan-complete', {
  method: 'POST',
  body: formData
})
```

### Option 2: Base64 Image (JSON)
```javascript
const data = {
  image: 'data:image/jpeg;base64,/9j/4AAQSkZJRg...'
};

fetch('http://localhost:5000/api/scan-complete', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
})
```

---

## 📥 Response Format

### Success Response (200 OK)
```json
{
  "success": true,
  "extracted_text": "Paracetamol 500mg",
  "drug_info": {
    "name": "Paracetamol",
    "active_ingredient": "Paracetamol",
    "category": "Giảm đau; hạ sốt",
    "page_number": 1118,
    "is_prescription": false,
    "similarity_score": 0.95
  },
  "summary": {
    "text": "Paracetamol là thuốc giảm đau và hạ sốt...",
    "word_count": 98,
    "generated_by": "gemini"
  },
  "audio": {
    "url": "/static/audio/paracetamol_abc123_1234567890.mp3",
    "filename": "paracetamol_abc123_1234567890.mp3",
    "duration": 45.5,
    "file_size": 729600,
    "format": "mp3"
  },
  "detailed_info": {
    "raw_text": "Full text from PDF...",
    "indication": "...",
    "dosage": "...",
    "side_effects": "..."
  },
  "ocr_confidence": 0.87,
  "processing_steps": {
    "ocr": true,
    "database_lookup": true,
    "pdf_extraction": true,
    "gemini_summary": true,
    "tts": true
  }
}
```

### Error Response (404 Not Found)
```json
{
  "success": false,
  "message": "Không tìm thấy thông tin thuốc trong database",
  "extracted_text": "UnknownDrug123"
}
```

### Error Response (400 Bad Request)
```json
{
  "error": "Invalid image data"
}
```

---

## 🎨 Frontend Integration

### Cập nhật ScanOverlay Component

```javascript
// Web/src/components/ScanOverlay.jsx

const handleScanComplete = async (imageData) => {
  try {
    setIsProcessing(true);
    
    // Call API mới
    const response = await fetch('http://localhost:5000/api/scan-complete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        image: imageData  // base64 image
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      // Hiển thị modal với đầy đủ thông tin
      setShowResult(true);
      setScanResult(result);
    } else {
      alert(result.message || 'Không tìm thấy thuốc');
    }
    
  } catch (error) {
    console.error('Error:', error);
    alert('Lỗi kết nối server');
  } finally {
    setIsProcessing(false);
  }
};
```

### Hiển thị Audio trong Modal

Modal đã được cập nhật để hiển thị:
- ✅ Summary text từ Gemini AI
- ✅ Audio player với play/pause/replay
- ✅ Progress bar
- ✅ Duration display

---

## 🧪 Testing

### Test 1: Test với cURL
```bash
# Tạo file test image (base64)
echo 'data:image/jpeg;base64,/9j/4AAQSkZJRg...' > test_image.txt

# Call API
curl -X POST http://localhost:5000/api/scan-complete \
  -H "Content-Type: application/json" \
  -d @test_image.txt
```

### Test 2: Test với Postman
1. Mở Postman
2. Create New Request → POST
3. URL: `http://localhost:5000/api/scan-complete`
4. Body → form-data
   - Key: `image`
   - Type: File
   - Value: Select image file
5. Send

### Test 3: Test Frontend
```bash
# Terminal 1: Start backend
cd Backend
python app.py

# Terminal 2: Start frontend
cd Web
npm run dev

# Mở browser: http://localhost:3000
# Click vào "AI Doctor" banner
# Chụp ảnh thuốc
# Kiểm tra kết quả có audio player
```

---

## 📊 API Comparison

| Feature | `/api/scan` | `/api/scan-complete` |
|---------|------------|---------------------|
| OCR | ✅ | ✅ |
| Database Lookup | ✅ | ✅ |
| PDF Extraction | ✅ | ✅ |
| Gemini Summary | ❌ | ✅ |
| Text-to-Speech | ❌ | ✅ |
| Response Time | ~2s | ~5-8s |
| Requires API Key | ❌ | ✅ (Gemini) |

---

## ⚡ Performance Tips

### 1. Cache Results
Backend tự động cache summaries trong 24 giờ để tránh gọi Gemini API nhiều lần cho cùng thuốc.

### 2. Async Processing
Gemini và TTS chạy tuần tự, có thể tối ưu bằng async nếu cần:
```python
# Future optimization
import asyncio

async def process_complete():
    ocr_task = asyncio.create_task(ocr_service.extract_text(image))
    # ... parallel tasks
```

### 3. Cleanup Old Audio
```bash
# Run cleanup script
cd Backend
python -c "from services.tts_service import get_tts_service; get_tts_service().cleanup_old_files(max_age_hours=24)"
```

---

## 🔒 Security Notes

### CORS Configuration
Backend đã enable CORS cho frontend:
```python
CORS(app)  # Allow all origins in development
```

**Production:** Restrict CORS:
```python
CORS(app, origins=['https://yourdomain.com'])
```

### API Rate Limiting
Consider adding rate limiting:
```python
from flask_limiter import Limiter

limiter = Limiter(app, default_limits=["100 per hour"])

@app.route('/api/scan-complete')
@limiter.limit("10 per minute")
def scan_drug_complete():
    # ...
```

---

## 🐛 Troubleshooting

### Issue 1: Audio không play được
**Giải pháp:**
- Kiểm tra CORS headers
- Đảm bảo audio URL đúng: `http://localhost:5000/static/audio/...`
- Check browser console for errors

### Issue 2: Gemini API timeout
**Giải pháp:**
- Backend tự động fallback về summary cơ bản
- User vẫn nhận được kết quả (không bị block)

### Issue 3: TTS audio quality
**Giải pháp:**
- gTTS: Free nhưng giọng robot
- Upgrade to Google Cloud TTS: Giọng tự nhiên hơn (có phí)

---

## 📈 Next Steps

### Future Enhancements:
1. **Async Processing:** Parallel Gemini + TTS
2. **Audio Streaming:** Stream audio thay vì download
3. **Multiple Languages:** Support English, Chinese
4. **Voice Selection:** Nam/Nữ, tốc độ khác nhau
5. **Summary Length:** User có thể chọn 50/100/150 từ

---

## 📞 Support

- **Backend API Docs:** `http://localhost:5000/api/health`
- **GitHub Issues:** [Your Repo]/issues
- **Email:** your-email@example.com

---

**🚀 Happy Coding!**
