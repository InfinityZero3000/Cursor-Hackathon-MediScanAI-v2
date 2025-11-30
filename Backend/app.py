from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import base64
import cv2
import numpy as np
from PIL import Image
import io
import pandas as pd
import re
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Import custom services
from services.ocr_service import OCRService
from services.drug_lookup_service import DrugLookupService
from services.pdf_extractor_service import PDFExtractorService
from services.gemini_summarizer_service import get_summarizer
from services.tts_service import get_tts_service

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Cho phép frontend gọi API

# Cấu hình
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Load configuration from environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.getenv('CSV_PATH', '../Crawldata/drug_database_refined.csv')
PDF_PATH = os.getenv('PDF_PATH', '../Crawldata/duoc-thu-quoc-gia-viet-nam-2018.pdf')

# Convert relative paths to absolute
if not os.path.isabs(CSV_PATH):
    CSV_PATH = os.path.join(BASE_DIR, CSV_PATH)
if not os.path.isabs(PDF_PATH):
    PDF_PATH = os.path.join(BASE_DIR, PDF_PATH)

# Initialize services
ocr_service = None
drug_lookup_service = None
pdf_extractor_service = None
gemini_summarizer = None
tts_service = None

def initialize_services():
    """Initialize all backend services"""
    global ocr_service, drug_lookup_service, pdf_extractor_service, gemini_summarizer, tts_service
    
    print("🔧 Initializing services...")
    
    # OCR Service
    ocr_service = OCRService()
    
    # Drug Lookup Service
    drug_lookup_service = DrugLookupService(CSV_PATH)
    
    # PDF Extractor Service
    pdf_extractor_service = PDFExtractorService(PDF_PATH)
    
    # Gemini Summarizer Service
    gemini_summarizer = get_summarizer()
    
    # TTS Service
    tts_service = get_tts_service()
    
    print("✅ All services initialized successfully!")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def decode_base64_image(base64_string):
    """Decode base64 string thành image"""
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return np.array(image)
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

def preprocess_image(image_array):
    """Tiền xử lý ảnh để cải thiện OCR"""
    # Convert to grayscale
    if len(image_array.shape) == 3:
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = image_array
    
    # Apply denoising
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # Apply threshold
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return thresh

def extract_text_from_image(image_array):
    """Trích xuất text từ ảnh (placeholder - có thể tích hợp OCR thật như Tesseract)"""
    # TODO: Tích hợp Tesseract OCR hoặc Google Vision API
    # Hiện tại return placeholder
    return "Panadol Extra"  # Placeholder

def search_drug_in_database(drug_name):
    """Tìm kiếm thuốc trong database"""
    if drug_db is None or drug_db.empty:
        return None
    
    # Tìm kiếm không phân biệt hoa thường
    drug_name_lower = drug_name.lower().strip()
    
    # Tìm exact match
    exact_match = drug_db[drug_db['DrugName'].str.lower() == drug_name_lower]
    if not exact_match.empty:
        return exact_match.iloc[0].to_dict()
    
    # Tìm partial match
    partial_match = drug_db[drug_db['DrugName'].str.lower().str.contains(drug_name_lower, na=False)]
    if not partial_match.empty:
        return partial_match.iloc[0].to_dict()
    
    # Tìm theo từ khóa
    keywords = drug_name_lower.split()
    for keyword in keywords:
        if len(keyword) > 3:  # Chỉ tìm từ có > 3 ký tự
            keyword_match = drug_db[drug_db['DrugName'].str.lower().str.contains(keyword, na=False)]
            if not keyword_match.empty:
                return keyword_match.iloc[0].to_dict()
    
    return None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Backend API is running',
        'services': {
            'ocr': ocr_service is not None,
            'drug_lookup': drug_lookup_service is not None,
            'pdf_extractor': pdf_extractor_service is not None,
            'gemini': gemini_summarizer is not None and gemini_summarizer.configured,
            'tts': tts_service is not None
        },
        'drugs_loaded': len(drug_lookup_service.df) if drug_lookup_service and drug_lookup_service.df is not None else 0
    })

@app.route('/static/audio/<path:filename>')
def serve_audio(filename):
    """Serve audio files"""
    audio_folder = os.getenv('AUDIO_FOLDER', './static/audio')
    return send_from_directory(audio_folder, filename)

@app.route('/api/scan', methods=['POST'])
def scan_drug():
    """API endpoint cơ bản để scan thuốc từ ảnh (không có audio)"""
    try:
        # Kiểm tra xem có file hoặc base64 image không
        if 'image' in request.files:
            # Nhận file upload
            file = request.files['image']
            if file and allowed_file(file.filename):
                # Đọc ảnh từ file
                image_bytes = file.read()
                image = Image.open(io.BytesIO(image_bytes))
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image_array = np.array(image)
        elif 'image' in request.json:
            # Nhận base64 image
            base64_image = request.json['image']
            image_array = decode_base64_image(base64_image)
            if image_array is None:
                return jsonify({'error': 'Invalid image data'}), 400
        else:
            return jsonify({'error': 'No image provided'}), 400
        
        # Step 1: OCR - Trích xuất text từ ảnh
        ocr_result = ocr_service.extract_text(image_array)
        if not ocr_result['success']:
            return jsonify({
                'success': False,
                'message': 'Không thể nhận diện text từ ảnh',
                'error': ocr_result.get('error')
            }), 400
        
        extracted_text = ocr_result['text']
        
        # Step 2: Database Lookup - Tìm kiếm thuốc
        drug_results = drug_lookup_service.search_drugs(extracted_text, top_n=1)
        
        if not drug_results:
            return jsonify({
                'success': False,
                'message': 'Không tìm thấy thông tin thuốc trong database',
                'extracted_text': extracted_text
            }), 404
        
        drug_info = drug_results[0]
        
        # Step 3: PDF Extraction - Lấy thông tin chi tiết từ PDF
        page_number = drug_info.get('PageNumber')
        pdf_info = pdf_extractor_service.extract_page_info(page_number) if page_number else {}
        
        # Trả về kết quả
        return jsonify({
            'success': True,
            'extracted_text': extracted_text,
            'drug_info': {
                'name': drug_info.get('DrugName', ''),
                'active_ingredient': drug_info.get('ActiveIngredient', ''),
                'category': drug_info.get('Category', ''),
                'page_number': page_number,
                'is_prescription': drug_info.get('Is_Prescription', False),
                'similarity_score': drug_info.get('similarity_score', 0)
            },
            'detailed_info': pdf_info,
            'ocr_confidence': ocr_result.get('confidence', 0)
        })
            
    except Exception as e:
        print(f"❌ Error processing scan: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/scan-complete', methods=['POST'])
def scan_drug_complete():
    """
    🎯 API endpoint HOÀN CHỈNH: Scan + OCR + Database + PDF + Gemini + TTS
    
    Flow:
    1. Nhận ảnh từ camera
    2. OCR nhận diện text
    3. Tìm kiếm trong database
    4. Trích xuất thông tin từ PDF
    5. Gemini AI tóm tắt thông tin
    6. Text-to-Speech tạo audio
    7. Trả về tất cả dữ liệu + audio URL
    """
    try:
        # STEP 1: Nhận và xử lý ảnh
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                image_bytes = file.read()
                image = Image.open(io.BytesIO(image_bytes))
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image_array = np.array(image)
        elif 'image' in request.json:
            base64_image = request.json['image']
            image_array = decode_base64_image(base64_image)
            if image_array is None:
                return jsonify({'error': 'Invalid image data'}), 400
        else:
            return jsonify({'error': 'No image provided'}), 400
        
        print("📸 Step 1: Received image")
        
        # STEP 2: OCR - Nhận diện text
        ocr_result = ocr_service.extract_text(image_array)
        if not ocr_result['success']:
            return jsonify({
                'success': False,
                'message': 'Không thể nhận diện text từ ảnh',
                'error': ocr_result.get('error')
            }), 400
        
        extracted_text = ocr_result['text']
        print(f"🔍 Step 2: OCR extracted: {extracted_text}")
        
        # STEP 3: Database Lookup
        drug_results = drug_lookup_service.search_drugs(extracted_text, top_n=1)
        
        if not drug_results:
            return jsonify({
                'success': False,
                'message': 'Không tìm thấy thông tin thuốc trong database',
                'extracted_text': extracted_text
            }), 404
        
        drug_info = drug_results[0]
        print(f"💊 Step 3: Found drug: {drug_info.get('DrugName')}")
        
        # STEP 4: PDF Extraction
        page_number = drug_info.get('PageNumber')
        pdf_info = pdf_extractor_service.extract_page_info(page_number) if page_number else {}
        pdf_text = pdf_info.get('raw_text', '')
        print(f"📄 Step 4: Extracted PDF info from page {page_number}")
        
        # STEP 5: Gemini AI Summarization
        summary_result = gemini_summarizer.summarize_drug_info(
            drug_name=drug_info.get('DrugName', ''),
            pdf_text=pdf_text,
            category=drug_info.get('Category', ''),
            active_ingredient=drug_info.get('ActiveIngredient', '')
        )
        
        summary_text = summary_result['summary']
        print(f"🤖 Step 5: Gemini summary ({summary_result['word_count']} words)")
        
        # STEP 6: Text-to-Speech
        tts_result = tts_service.text_to_speech(
            text=summary_text,
            drug_name=drug_info.get('DrugName', 'drug')
        )
        
        if tts_result['success']:
            print(f"🔊 Step 6: Audio generated: {tts_result['filename']}")
        else:
            print(f"⚠️ Step 6: Audio generation failed: {tts_result['error']}")
        
        # STEP 7: Trả về kết quả hoàn chỉnh
        response = {
            'success': True,
            'extracted_text': extracted_text,
            'drug_info': {
                'name': drug_info.get('DrugName', ''),
                'active_ingredient': drug_info.get('ActiveIngredient', ''),
                'category': drug_info.get('Category', ''),
                'page_number': page_number,
                'is_prescription': drug_info.get('Is_Prescription', False),
                'similarity_score': drug_info.get('similarity_score', 0)
            },
            'summary': {
                'text': summary_text,
                'word_count': summary_result['word_count'],
                'generated_by': 'gemini' if summary_result['success'] else 'fallback'
            },
            'audio': {
                'url': tts_result['audio_url'] if tts_result['success'] else None,
                'filename': tts_result.get('filename'),
                'duration': tts_result.get('duration', 0),
                'file_size': tts_result.get('file_size', 0),
                'format': tts_result.get('format', 'mp3')
            } if tts_result['success'] else None,
            'detailed_info': pdf_info,
            'ocr_confidence': ocr_result.get('confidence', 0),
            'processing_steps': {
                'ocr': ocr_result['success'],
                'database_lookup': True,
                'pdf_extraction': bool(pdf_text),
                'gemini_summary': summary_result['success'],
                'tts': tts_result['success']
            }
        }
        
        print("✅ Complete flow executed successfully!")
        return jsonify(response)
            
    except Exception as e:
        print(f"❌ Error in complete flow: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/drugs/search', methods=['GET'])
def search_drugs():
    """API endpoint để tìm kiếm thuốc theo tên"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    if not drug_lookup_service:
        return jsonify({'drugs': []})
    
    # Tìm kiếm
    results = drug_lookup_service.search_drugs(query, top_n=20)
    
    return jsonify({
        'drugs': results,
        'count': len(results)
    })

@app.route('/api/drug/<drug_name>', methods=['GET'])
def get_drug_details(drug_name):
    """API endpoint để lấy thông tin chi tiết một thuốc"""
    try:
        # Search drug
        results = drug_lookup_service.search_drugs(drug_name, top_n=1)
        
        if not results:
            return jsonify({
                'success': False,
                'message': 'Không tìm thấy thuốc'
            }), 404
        
        drug_info = results[0]
        
        # Get PDF info
        page_number = drug_info.get('PageNumber')
        pdf_info = pdf_extractor_service.extract_page_info(page_number) if page_number else {}
        
        return jsonify({
            'success': True,
            'drug_info': drug_info,
            'detailed_info': pdf_info
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    initialize_services()
    port = int(os.getenv('PORT', 5002))
    print("🚀 Starting MediScan AI Backend Server...")
    print(f"📡 API available at http://localhost:{port}")
    print("🎯 Endpoints:")
    print("   - GET  /api/health")
    print("   - POST /api/scan (basic)")
    print("   - POST /api/scan-complete (with AI + Audio)")
    print("   - GET  /api/drugs/search?q=<query>")
    print("   - GET  /api/drug/<drug_name>")
    print("   - GET  /static/audio/<filename>")
    
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)

