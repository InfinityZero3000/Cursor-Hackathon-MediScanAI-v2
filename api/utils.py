import os
import base64
import cv2
import numpy as np
from PIL import Image
import io
import pandas as pd
import re
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ google-generativeai không được cài đặt, Gemini sẽ không hoạt động")

# Fix cho Pillow 10.0+ không còn Image.ANTIALIAS
# EasyOCR và một số thư viện vẫn cần ANTIALIAS
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

# Load drug database và PDF (cached)
_drug_db = None
_drug_db_path = None
_pdf_reader = None
_pdf_path = None
_ocr_reader = None  # EasyOCR reader (cache để không load lại mỗi lần)

def get_drug_database():
    """Load và cache drug database"""
    global _drug_db, _drug_db_path
    
    # Get path relative to project root
    if _drug_db_path is None:
        # Try different possible paths - sử dụng drug_database_refined.csv
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'Crawldata', 'drug_database_refined.csv'),
            os.path.join(os.getcwd(), 'Crawldata', 'drug_database_refined.csv'),
            '/var/task/Crawldata/drug_database_refined.csv',  # Vercel lambda path
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                _drug_db_path = path
                break
    
    if _drug_db is None and _drug_db_path and os.path.exists(_drug_db_path):
        try:
            _drug_db = pd.read_csv(_drug_db_path)
            print(f"✅ Loaded {len(_drug_db)} drugs from database")
        except Exception as e:
            print(f"⚠️ Error loading database: {e}")
            _drug_db = pd.DataFrame()
    elif _drug_db is None:
        _drug_db = pd.DataFrame()
    
    return _drug_db

def get_pdf_reader():
    """Load và cache PDF reader"""
    global _pdf_reader, _pdf_path
    
    if _pdf_path is None:
        # Try different possible paths
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'Crawldata', 'duoc-thu-quoc-gia-viet-nam-2018.pdf'),
            os.path.join(os.getcwd(), 'Crawldata', 'duoc-thu-quoc-gia-viet-nam-2018.pdf'),
            '/var/task/Crawldata/duoc-thu-quoc-gia-viet-nam-2018.pdf',  # Vercel lambda path
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                _pdf_path = path
                break
    
    if _pdf_reader is None and _pdf_path and os.path.exists(_pdf_path):
        try:
            from pypdf import PdfReader
            _pdf_reader = PdfReader(_pdf_path)
            print(f"✅ Loaded PDF with {len(_pdf_reader.pages)} pages")
        except Exception as e:
            print(f"⚠️ Error loading PDF: {e}")
            _pdf_reader = None
    elif _pdf_reader is None:
        _pdf_reader = None
    
    return _pdf_reader

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
    try:
        # Convert to grayscale
        if len(image_array.shape) == 3:
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_array
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Apply threshold
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Resize nếu ảnh quá nhỏ (tối thiểu 300px width để OCR tốt hơn)
        height, width = thresh.shape
        if width < 300:
            scale = 300 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            thresh = cv2.resize(thresh, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        return thresh
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return image_array

def get_ocr_reader():
    """Lấy hoặc khởi tạo EasyOCR reader (cache để không load lại mỗi lần)"""
    global _ocr_reader
    if _ocr_reader is None:
        try:
            import easyocr
            print("🔄 Đang khởi tạo EasyOCR (lần đầu có thể mất vài phút để tải model)...")
            # Hỗ trợ tiếng Việt và tiếng Anh
            _ocr_reader = easyocr.Reader(['vi', 'en'], gpu=False)
            print("✅ EasyOCR đã sẵn sàng!")
        except ImportError:
            print("⚠️ EasyOCR chưa được cài đặt. Chạy: pip install easyocr")
            return None
        except Exception as e:
            print(f"⚠️ Lỗi khởi tạo EasyOCR: {e}")
            return None
    return _ocr_reader

def extract_text_from_image(image_array):
    """Trích xuất text từ ảnh sử dụng EasyOCR, trả về (selected_text, all_ocr_texts)"""
    try:
        reader = get_ocr_reader()
        if reader is None:
            return None, []
        
        # EasyOCR cần ảnh ở dạng numpy array (BGR hoặc RGB)
        if len(image_array.shape) == 2:
            image_rgb = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
        else:
            image_rgb = image_array
        
        # Chuyển từ RGB sang BGR (OpenCV format)
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # OCR với EasyOCR
        results = reader.readtext(image_bgr)
        
        if not results:
            return None, []
        
        # Lấy tất cả text đã nhận diện
        all_texts = []
        for (bbox, text, confidence) in results:
            if confidence > 0.3:  # Chỉ lấy text có độ tin cậy > 30%
                all_texts.append(text.strip())
        
        if not all_texts:
            return None, []
        
        # Ưu tiên text dài nhất (thường là tên thuốc)
        selected_text = max(all_texts, key=len) if all_texts else ' '.join(all_texts)
        
        # Trả về text đã chọn và danh sách tất cả text
        return selected_text, all_texts
        
    except Exception as e:
        print(f"⚠️ Lỗi OCR: {e}")
        return None, []

def search_drug_in_database(drug_name):
    """Tìm kiếm thuốc trong database"""
    drug_db = get_drug_database()
    
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

def summarize_drug_info_with_gemini(pdf_text, drug_name, drug_info):
    """
    Sử dụng Gemini AI để đọc toàn bộ thông tin từ PDF và tổng hợp thành:
    - Cách dùng (usage): Dễ hiểu, ngắn gọn
    - Lưu ý (notes): Từ chống chỉ định, tương tác thuốc, tác dụng phụ
    """
    if not pdf_text or len(pdf_text.strip()) < 50:
        return {'usage': '', 'notes': ''}
    
    if not GEMINI_AVAILABLE:
        return {'usage': '', 'notes': ''}
    
    # Lấy API key từ environment variable
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if not gemini_api_key:
        print("⚠️ GEMINI_API_KEY không được cấu hình, trả về rỗng")
        return {'usage': '', 'notes': ''}
    
    try:
        # Cấu hình Gemini
        genai.configure(api_key=gemini_api_key)
        # Sử dụng Gemini 2.0 Flash (model mới nhất, nhanh và chính xác)
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
        except Exception as e:
            print(f"⚠️ Không thể dùng gemini-2.0-flash-exp, thử gemini-2.0-flash: {e}")
            try:
                model = genai.GenerativeModel('gemini-2.0-flash')
            except Exception as e2:
                print(f"⚠️ Không thể dùng gemini-2.0-flash, thử gemini-1.5-flash: {e2}")
                model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Lấy thông tin bổ sung từ drug_info
        category = drug_info.get('Category', '')
        active_ingredient = drug_info.get('ActiveIngredient', '')
        
        # Giới hạn độ dài PDF text để tránh vượt quá token limit
        # Tăng lên 4000 để có đủ context cho Gemini filter đúng thuốc
        pdf_text_limited = pdf_text[:4000] if len(pdf_text) > 4000 else pdf_text
        
        # Prompt để tổng hợp thông tin - cải thiện để filter đúng thuốc
        prompt = f"""Bạn là một dược sĩ chuyên nghiệp. Hãy đọc và tổng hợp thông tin từ Dược thư Quốc gia về thuốc CỤ THỂ sau:

**THUỐC CẦN TÌM:**
- Tên thuốc: {drug_name}
- Hoạt chất: {active_ingredient}
- Phân loại: {category}

**LƯU Ý QUAN TRỌNG:**
- Trang PDF có thể chứa thông tin của NHIỀU thuốc khác nhau
- BẠN CHỈ ĐƯỢC tổng hợp thông tin về thuốc "{drug_name}" hoặc "{active_ingredient}"
- BỎ QUA hoàn toàn thông tin về các thuốc khác (như Polymyxin, Polygelin, hoặc bất kỳ thuốc nào khác)
- Nếu không tìm thấy thông tin về thuốc này, trả về "Không tìm thấy thông tin" thay vì thông tin của thuốc khác

**Thông tin từ Dược thư (có thể chứa nhiều thuốc):**
{pdf_text_limited}

**YÊU CẦU:**
1. Tổng hợp phần "CÁCH DÙNG" (usage) - CHỈ về thuốc "{drug_name}":
   - Viết bằng ngôn ngữ đơn giản, dễ hiểu
   - Tập trung vào: liều lượng, thời điểm uống, cách uống, tần suất
   - Sử dụng câu ngắn gọn, rõ ràng
   - Loại bỏ thuật ngữ y khoa phức tạp
   - Nếu không có thông tin, viết: "Thông tin cách dùng không có trong dược thư"

2. Tổng hợp phần "LƯU Ý" (notes) - CHỈ về thuốc "{drug_name}":
   - Từ chống chỉ định: ai không nên dùng
   - Tương tác thuốc: không dùng cùng với thuốc gì
   - Tác dụng phụ: cần chú ý gì
   - Đối tượng đặc biệt: phụ nữ có thai, trẻ em, người già
   - Bảo quản: cách bảo quản thuốc
   - Nếu không có thông tin, viết: "Thông tin lưu ý không có trong dược thư"

**Trả về theo định dạng JSON:**
{{
  "usage": "Phần cách dùng đã tổng hợp (CHỈ về {drug_name})",
  "notes": "Phần lưu ý đã tổng hợp (CHỈ về {drug_name})"
}}

**QUAN TRỌNG:** Chỉ trả về JSON, không thêm text khác. KHÔNG được trả về thông tin của thuốc khác."""
        
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Loại bỏ markdown code blocks nếu có
        result_text = result_text.replace('```json', '').replace('```', '').strip()
        
        # Parse JSON
        import json
        try:
            result = json.loads(result_text)
            usage = result.get('usage', '').strip()
            notes = result.get('notes', '').strip()
            
            # Kiểm tra xem có phải là thông báo lỗi không
            if 'không tìm thấy' in usage.lower() or 'không có trong' in usage.lower():
                usage = "Thông tin cách dùng không có trong dược thư cho thuốc này."
            if 'không tìm thấy' in notes.lower() or 'không có trong' in notes.lower():
                notes = "Thông tin lưu ý không có trong dược thư cho thuốc này."
            
            # Giới hạn độ dài
            if len(usage) > 500:
                usage = usage[:500] + "..."
            if len(notes) > 600:
                notes = notes[:600] + "..."
            
            print(f"✅ Đã tổng hợp thông tin với Gemini cho {drug_name}")
            return {
                'usage': usage,
                'notes': notes
            }
        except json.JSONDecodeError:
            # Nếu không parse được JSON, thử extract thủ công
            print("⚠️ Không parse được JSON từ Gemini, thử extract thủ công")
            # Tìm phần usage và notes trong text
            usage_start = result_text.find('"usage"') or result_text.find('CÁCH DÙNG')
            notes_start = result_text.find('"notes"') or result_text.find('LƯU Ý')
            
            if usage_start > -1 and notes_start > -1:
                usage = result_text[usage_start:notes_start].replace('"usage":', '').strip('",')
                notes = result_text[notes_start:].replace('"notes":', '').strip('",')
                return {'usage': usage[:500], 'notes': notes[:600]}
            else:
                # Fallback: chia text làm 2 phần
                parts = result_text.split('\n\n')
                usage = parts[0] if len(parts) > 0 else ''
                notes = parts[1] if len(parts) > 1 else ''
                return {'usage': usage[:500], 'notes': notes[:600]}
        
    except Exception as e:
        print(f"⚠️ Lỗi khi gọi Gemini API: {e}")
        return {'usage': '', 'notes': ''}

def generate_recommendations(drug_info, pdf_details):
    """
    Tạo khuyến nghị sử dụng thuốc dựa trên thông tin thuốc
    """
    recommendations = []
    
    # Khuyến nghị dựa trên phân loại
    category = drug_info.get('Category', '').lower()
    if 'kháng sinh' in category:
        recommendations.append("Kháng sinh cần uống đủ liều và đủ thời gian theo chỉ định của bác sĩ, không tự ý ngừng thuốc.")
    elif 'giảm đau' in category or 'hạ sốt' in category:
        recommendations.append("Thuốc giảm đau hạ sốt nên uống sau khi ăn để tránh kích ứng dạ dày.")
    elif 'chống viêm' in category:
        recommendations.append("Thuốc chống viêm nên uống sau khi ăn và uống nhiều nước.")
    elif 'vitamin' in category or 'bổ sung' in category:
        recommendations.append("Vitamin và chất bổ sung nên uống theo liều lượng khuyến nghị, không lạm dụng.")
    
    # Khuyến nghị dựa trên chống chỉ định
    contraindications = pdf_details.get('contraindications', '').lower()
    if contraindications:
        if 'phụ nữ có thai' in contraindications or 'mang thai' in contraindications:
            recommendations.append("Không sử dụng cho phụ nữ có thai hoặc đang cho con bú nếu không có chỉ định của bác sĩ.")
        if 'trẻ em' in contraindications or 'trẻ nhỏ' in contraindications:
            recommendations.append("Cần thận trọng khi sử dụng cho trẻ em, nên tham khảo ý kiến bác sĩ.")
    
    # Khuyến nghị dựa trên cách dùng
    usage = pdf_details.get('usage', '') or pdf_details.get('dosage', '')
    if usage:
        if 'sau khi ăn' in usage.lower() or 'sau bữa ăn' in usage.lower():
            recommendations.append("Nên uống thuốc sau khi ăn để đạt hiệu quả tốt nhất và giảm tác dụng phụ.")
        if 'trước khi ăn' in usage.lower() or 'khi đói' in usage.lower():
            recommendations.append("Nên uống thuốc trước khi ăn hoặc khi đói để hấp thu tốt hơn.")
    
    # Khuyến nghị chung
    if not recommendations:
        recommendations.append("Vui lòng đọc kỹ hướng dẫn sử dụng trước khi dùng và tuân thủ liều lượng khuyến nghị.")
        recommendations.append("Nếu có bất kỳ dấu hiệu bất thường nào, hãy ngừng sử dụng và tham khảo ý kiến bác sĩ.")
    else:
        recommendations.append("Nếu có bất kỳ dấu hiệu bất thường nào, hãy ngừng sử dụng và tham khảo ý kiến bác sĩ.")
    
    return recommendations

def extract_drug_details_from_pdf(page_number, offset=-1):
    """
    Trích xuất thông tin chi tiết từ PDF dựa trên số trang
    Tìm thành phần, công dụng, chỉ định, chống chỉ định...
    """
    pdf_reader = get_pdf_reader()
    
    if pdf_reader is None:
        return {}
    
    try:
        # Chuyển đổi số trang sách thành index PDF (pypdf đánh số từ 0)
        pdf_page_index = int(page_number) + offset - 1
        
        # Đảm bảo index hợp lệ
        if pdf_page_index < 0 or pdf_page_index >= len(pdf_reader.pages):
            # Thử không có offset
            pdf_page_index = int(page_number) - 1
            if pdf_page_index < 0 or pdf_page_index >= len(pdf_reader.pages):
                return {}
        
        # Đọc trang PDF
        page = pdf_reader.pages[pdf_page_index]
        text = page.extract_text()
        
        if not text:
            return {}
        
        details = {
            'composition': '',
            'indications': '',
            'contraindications': '',
            'dosage': '',
            'usage': '',  # Cách dùng
            'full_text': text[:2000]  # Giới hạn để tránh quá dài
        }
        
        # Regex patterns để tìm các thông tin
        patterns = {
            'composition': re.compile(r'(Thành phần|Thành phần chính|Hoạt chất)[:\.]\s*(.+?)(?:\n|$)', re.IGNORECASE),
            'indications': re.compile(r'(Chỉ định|Công dụng|Tác dụng)[:\.]\s*(.+?)(?:\n|Chống chỉ định|Liều dùng|$)', re.IGNORECASE | re.DOTALL),
            'contraindications': re.compile(r'(Chống chỉ định|Không dùng)[:\.]\s*(.+?)(?:\n|Liều dùng|Cách dùng|$)', re.IGNORECASE | re.DOTALL),
            'dosage': re.compile(r'(Liều dùng|Cách dùng|Liều lượng|Cách sử dụng)[:\.]\s*(.+?)(?:\n|Tác dụng phụ|Lưu ý|Bảo quản|$)', re.IGNORECASE | re.DOTALL),
            'usage': re.compile(r'(Cách dùng|Hướng dẫn sử dụng|Sử dụng)[:\.]\s*(.+?)(?:\n|Lưu ý|Tác dụng phụ|$)', re.IGNORECASE | re.DOTALL)
        }
        
        # Tìm từng loại thông tin
        for key, pattern in patterns.items():
            match = pattern.search(text)
            if match:
                details[key] = match.group(2).strip()[:500]  # Giới hạn độ dài
        
        # Nếu không tìm thấy "usage", dùng "dosage" làm cách dùng
        if not details['usage'] and details['dosage']:
            details['usage'] = details['dosage']
        
        return details
        
    except Exception as e:
        print(f"⚠️ Lỗi đọc PDF trang {page_number}: {e}")
        return {}

