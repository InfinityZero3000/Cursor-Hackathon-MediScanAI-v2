# 🔥 Deploy Firebase Hosting Only (Không cần Blaze Plan)

## Vấn đề

Firebase Functions yêu cầu **Blaze plan** (pay-as-you-go), nhưng bạn có thể deploy **chỉ Hosting** (frontend) với **Spark plan** (miễn phí).

## Giải pháp

Deploy chỉ frontend lên Firebase Hosting và sử dụng API từ:
- Vercel (đã setup sẵn)
- Backend riêng
- Hoặc external API

## 🚀 Cách Deploy

### Option 1: Deploy chỉ Hosting (Khuyến nghị)

```bash
# Chỉ deploy hosting, bỏ qua functions
firebase deploy --only hosting
```

### Option 2: Tạm thời xóa Functions config

Sửa `firebase.json` để chỉ có hosting:

```json
{
  "hosting": {
    "public": "Web/dist",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

Sau đó deploy:
```bash
firebase deploy
```

## ⚙️ Cấu hình API

### Sử dụng Vercel API

Cập nhật `Web/src/utils/api.js` để sử dụng Vercel API khi deploy trên Firebase:

```javascript
const getApiUrl = () => {
  // Check if using Firebase Hosting
  const isFirebase = typeof window !== 'undefined' && (
    window.location.hostname.includes('firebaseapp.com') || 
    window.location.hostname.includes('web.app')
  );
  
  if (isFirebase) {
    // Sử dụng Vercel API hoặc external API
    return 'https://your-vercel-app.vercel.app/api';
  }
  
  // In development, use localhost
  return 'http://localhost:5000/api';
};
```

### Hoặc sử dụng Environment Variables

Tạo file `.env.production` trong `Web/`:

```env
VITE_API_URL=https://your-vercel-app.vercel.app/api
```

Cập nhật `api.js`:

```javascript
const getApiUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // Fallback
  if (import.meta.env.PROD) {
    return 'https://your-vercel-app.vercel.app/api';
  }
  
  return 'http://localhost:5000/api';
};
```

## 📝 Các bước thực hiện

1. **Build frontend:**
   ```bash
   cd Web
   npm run build
   cd ..
   ```

2. **Deploy chỉ hosting:**
   ```bash
   firebase deploy --only hosting
   ```

3. **Kiểm tra:**
   - Frontend: `https://mediscanai-96f18.web.app`
   - API sẽ gọi từ Vercel hoặc external source

## 🔄 Nếu muốn dùng Firebase Functions sau này

1. Upgrade lên Blaze plan (miễn phí cho usage nhỏ):
   - Truy cập: https://console.firebase.google.com/project/mediscanai-96f18/usage/details
   - Click "Upgrade to Blaze"
   - Blaze plan có free tier rộng rãi, chỉ trả phí khi vượt quá

2. Sau khi upgrade, deploy functions:
   ```bash
   firebase deploy --only functions
   ```

3. Cập nhật `api.js` để sử dụng Firebase Functions URLs

## 💰 Blaze Plan Free Tier

Blaze plan có free tier rộng rãi:
- **Functions**: 2M invocations/month (miễn phí)
- **Bandwidth**: 1GB/day (miễn phí)
- **Compute time**: 400K GB-seconds/month (miễn phí)

Chỉ trả phí khi vượt quá free tier.

## ✅ Kết luận

**Hiện tại**: Deploy chỉ Hosting (miễn phí)
**Sau này**: Có thể upgrade lên Blaze và thêm Functions

