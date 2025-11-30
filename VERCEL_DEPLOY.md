# MediScanAI - Vercel Deployment

## Bước 1: Cài đặt Vercel CLI

```bash
npm install -g vercel
```

## Bước 2: Login vào Vercel

```bash
vercel login
```

## Bước 3: Deploy Frontend lên Vercel

```bash
# Từ thư mục gốc
vercel --prod
```

Vercel sẽ tự động:
- Build React app từ thư mục `Web/`
- Deploy static files
- Cung cấp URL: `https://your-app.vercel.app`

## Bước 4: Deploy Backend

⚠️ **Lưu ý quan trọng**: Vercel không hỗ trợ Python backend với EasyOCR (quá nặng).

### Giải pháp cho Backend:

#### Option 1: Railway (Recommended)
```bash
# Install Railway CLI
npm install -g railway

# Login
railway login

# Deploy backend
cd Backend
railway up
```

#### Option 2: Render
1. Tạo tài khoản tại https://render.com
2. Connect GitHub repo
3. Chọn thư mục `Backend/`
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python app.py`

#### Option 3: Heroku
```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login
heroku login

# Create app
heroku create mediscan-backend

# Deploy
cd Backend
git subtree push --prefix Backend heroku master
```

#### Option 4: Google Cloud Run (Best for ML apps)
```bash
# Tạo Dockerfile trong Backend/
# Deploy với Cloud Run (auto-scaling, pay per use)
```

## Bước 5: Cập nhật API URL

Sau khi deploy backend, cập nhật `Web/src/utils/api.js`:

```javascript
const API_URL = 'https://your-backend-url.com/api';
```

## Bước 6: Redeploy Frontend

```bash
vercel --prod
```

## Environment Variables trên Vercel

Vào Vercel Dashboard → Settings → Environment Variables:

```
# Frontend không cần biến môi trường
# Backend URL được hardcode trong api.js
```

## Backend Environment Variables (Railway/Render)

```
PORT=5002
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash
CSV_PATH=/app/Crawldata/drug_database_refined.csv
PDF_PATH=/app/Crawldata/duoc-thu-quoc-gia-viet-nam-2018.pdf
```

## Kiểm tra Deployment

```bash
# Test frontend
curl https://your-app.vercel.app

# Test backend
curl https://your-backend-url.com/api/health
```

## Giới hạn Vercel

- ✅ Frontend: Perfect cho React static site
- ❌ Backend: Không hỗ trợ Python với ML models
- ✅ Free tier: 100GB bandwidth/month
- ⚠️ Build time: Max 45 phút

## Chi phí dự kiến

### Vercel (Frontend)
- **Free**: Unlimited projects, 100GB bandwidth
- **Pro ($20/month)**: Nếu cần nhiều bandwidth hơn

### Railway (Backend - Recommended)
- **Free**: $5 credit/month (~500 hours)
- **Developer ($5/month)**: Unlimited usage
- **Pros**: Tự động scaling, hỗ trợ Python ML

### Render (Backend - Alternative)
- **Free**: 750 hours/month (đủ cho 1 app)
- **Starter ($7/month)**: Always-on, faster
- **Cons**: Free tier sleep sau 15 phút không dùng

## Khuyến nghị

1. **Frontend**: Deploy lên Vercel ✅
2. **Backend**: Deploy lên Railway hoặc Google Cloud Run
3. **Database**: Giữ nguyên CSV file (upload cùng backend)
4. **PDF**: Upload lên Google Cloud Storage hoặc S3

## Quick Deploy Script

Tạo file `deploy-vercel.sh`:

```bash
#!/bin/bash
echo "🚀 Deploying MediScanAI to Vercel..."

# Build frontend
cd Web
npm install
npm run build

# Deploy
cd ..
vercel --prod

echo "✅ Deployed!"
```

```bash
chmod +x deploy-vercel.sh
./deploy-vercel.sh
```
