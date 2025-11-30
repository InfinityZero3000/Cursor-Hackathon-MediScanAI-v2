# 🔥 Hướng dẫn Deploy lên Firebase

## 📋 Yêu cầu

- Node.js >= 16.x
- npm hoặc yarn
- Tài khoản Firebase (miễn phí tại [firebase.google.com](https://firebase.google.com))
- Firebase CLI

## 🚀 Cài đặt Firebase CLI

```bash
npm install -g firebase-tools
```

## 📝 Bước 1: Đăng nhập Firebase

```bash
firebase login
```

## 📝 Bước 2: Khởi tạo Firebase Project

### 2.1. Tạo project trên Firebase Console

1. Truy cập [Firebase Console](https://console.firebase.google.com)
2. Click "Add project" hoặc chọn project có sẵn
3. Ghi nhớ **Project ID**

### 2.2. Cấu hình project ID

Mở file `.firebaserc` và thay `your-project-id` bằng Project ID của bạn:

```json
{
  "projects": {
    "default": "your-actual-project-id"
  }
}
```

## 📝 Bước 3: Cài đặt Dependencies

### 3.1. Frontend Dependencies

```bash
cd Web
npm install
```

### 3.2. Functions Dependencies

```bash
cd functions
npm install
cd ..
```

## 📝 Bước 4: Build Frontend

```bash
cd Web
npm run build
cd ..
```

## 📝 Bước 5: Deploy

### Deploy tất cả (Hosting + Functions)

```bash
firebase deploy
```

### Hoặc deploy riêng lẻ:

**Deploy Hosting (Frontend):**
```bash
firebase deploy --only hosting
```

**Deploy Functions (Backend):**
```bash
firebase deploy --only functions
```

## 🌐 URLs sau khi Deploy

Sau khi deploy thành công, bạn sẽ có:

- **Frontend**: `https://your-project-id.web.app`
- **Frontend (custom)**: `https://your-project-id.firebaseapp.com`
- **API Health**: `https://us-central1-your-project-id.cloudfunctions.net/health`
- **API Scan**: `https://us-central1-your-project-id.cloudfunctions.net/scan`
- **API Search**: `https://us-central1-your-project-id.cloudfunctions.net/searchDrugs`

## ⚙️ Cấu hình Functions

### Region (tùy chọn)

Để thay đổi region của Functions, sửa trong `functions/index.js`:

```javascript
exports.scan = functions.region('asia-southeast1').https.onRequest(...)
```

Regions phổ biến:
- `us-central1` (mặc định)
- `asia-southeast1` (Singapore - gần Việt Nam)
- `europe-west1` (Belgium)

## 🔧 Cấu hình Environment Variables

### Thêm biến môi trường:

```bash
firebase functions:config:set api.key="your-api-key"
```

### Sử dụng trong code:

```javascript
const apiKey = functions.config().api.key;
```

### Xem cấu hình hiện tại:

```bash
firebase functions:config:get
```

## 📦 Cấu trúc Files

```
MediScanAI/
├── firebase.json          # Firebase config
├── .firebaserc           # Project config
├── functions/            # Firebase Functions
│   ├── index.js         # Functions code
│   └── package.json     # Functions dependencies
└── Web/                 # Frontend
    └── dist/            # Build output (cho hosting)
```

## 🐛 Xử lý lỗi thường gặp

### Lỗi: "Firebase CLI not found"
```bash
npm install -g firebase-tools
```

### Lỗi: "Project not found"
- Kiểm tra Project ID trong `.firebaserc`
- Đảm bảo đã đăng nhập: `firebase login`

### Lỗi: "Functions deploy failed"
- Kiểm tra Node.js version (cần >= 16)
- Xem logs: `firebase functions:log`

### Lỗi: "Hosting deploy failed"
- Đảm bảo đã build frontend: `cd Web && npm run build`
- Kiểm tra `Web/dist` folder tồn tại

### Lỗi: "Permission denied"
- Kiểm tra quyền trong Firebase Console
- Đảm bảo đã enable:
  - Firebase Hosting
  - Cloud Functions

## 🔐 Bảo mật

### CORS
Functions đã được cấu hình CORS để cho phép frontend gọi API.

### Authentication (tùy chọn)
Có thể thêm Firebase Authentication:

```javascript
const user = await admin.auth().verifyIdToken(req.headers.authorization);
```

## 📊 Monitoring

### Xem logs Functions:
```bash
firebase functions:log
```

### Xem logs real-time:
```bash
firebase functions:log --only scan
```

### Xem trong Console:
- Firebase Console → Functions → Logs

## 🔄 Update sau khi Deploy

Mỗi khi thay đổi code:

1. **Frontend**: Build lại và deploy
   ```bash
   cd Web && npm run build && cd .. && firebase deploy --only hosting
   ```

2. **Functions**: Deploy lại
   ```bash
   firebase deploy --only functions
   ```

## 💰 Pricing

Firebase có free tier:
- **Hosting**: 10GB storage, 360MB/day transfer (miễn phí)
- **Functions**: 2M invocations/month (miễn phí)
- **Bandwidth**: 1GB/day (miễn phí)

Xem chi tiết: [Firebase Pricing](https://firebase.google.com/pricing)

## 🎉 Hoàn thành!

Sau khi deploy thành công:
- ✅ Frontend tại: `https://your-project-id.web.app`
- ✅ Functions tại: Cloud Functions URLs
- ✅ HTTPS tự động
- ✅ CDN global
- ✅ Auto-scaling

## 📝 Lưu ý

1. **Database CSV**: Cần upload CSV lên Cloud Storage hoặc dùng Firestore
2. **Image Processing**: Có thể cần thêm service cho OCR (Google Vision API)
3. **Cold Start**: Functions có thể mất vài giây khi cold start
4. **File Size**: Functions có giới hạn 50MB code

## 🔗 Tài liệu tham khảo

- [Firebase Hosting Docs](https://firebase.google.com/docs/hosting)
- [Cloud Functions Docs](https://firebase.google.com/docs/functions)
- [Firebase CLI Reference](https://firebase.google.com/docs/cli)

