from http.server import BaseHTTPRequestHandler
import json
import sys
from api.utils import (
    decode_base64_image,
    preprocess_image,
    extract_text_from_image,
    search_drug_in_database,
    extract_drug_details_from_pdf,
    generate_recommendations,
    summarize_drug_info_with_gemini
)
import pandas as pd

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return
    
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # Parse JSON
            try:
                data = json.loads(body.decode('utf-8'))
            except:
                self.send_error(400, 'Invalid JSON')
                return
            
            # Get image from request
            if 'image' not in data:
                self.send_error(400, 'No image provided')
                return
            
            base64_image = data['image']
            image_array = decode_base64_image(base64_image)
            
            if image_array is None:
                self.send_error(400, 'Invalid image data')
                return
            
            # Process image
            processed_image = preprocess_image(image_array)
            
            # Trích xuất text từ ảnh (OCR) - dùng ảnh gốc
            extracted_text, all_ocr_texts = extract_text_from_image(image_array)
            
            if not extracted_text:
                response = {
                    'success': False,
                    'message': 'Không thể nhận diện text từ ảnh. Vui lòng thử lại với ảnh rõ hơn.',
                    'extracted_text': '',
                    'all_ocr_texts': all_ocr_texts or []
                }
                status_code = 400
            else:
                print(f"📝 Text nhận diện được: {extracted_text}")
                
                # Search in database
                drug_info = search_drug_in_database(extracted_text)
                
                if drug_info:
                    # KIỂM TRA AN TOÀN: Nếu là thuốc kê đơn (Is_Prescription = True), chặn lại
                    is_prescription = drug_info.get('Is_Prescription', False)
                
                # Chuyển đổi giá trị boolean từ CSV
                if isinstance(is_prescription, str):
                    is_prescription = is_prescription.lower() in ['true', '1', 'yes']
                elif pd.isna(is_prescription):
                    is_prescription = False
                
                if is_prescription:
                    response = {
                        'success': False,
                        'error': 'PRESCRIPTION_REQUIRED',
                        'message': '⚠️ Đây là thuốc kê đơn. Vui lòng sử dụng theo chỉ định của bác sĩ.',
                        'drug_name': drug_info.get('DrugName', ''),
                        'active_ingredient': drug_info.get('ActiveIngredient', ''),
                        'category': drug_info.get('Category', ''),
                        'extracted_text': extracted_text
                    }
                    status_code = 403  # 403 Forbidden
                else:
                    # Nếu là thuốc OTC, tiếp tục tra cứu thông tin chi tiết từ PDF
                    page_number = drug_info.get('PageNumber', '')
                    pdf_details = {}
                    
                    if page_number:
                        pdf_details = extract_drug_details_from_pdf(page_number)
                        
                        # Sử dụng Gemini để tổng hợp thông tin từ PDF
                        drug_name = drug_info.get('DrugName', '')
                        pdf_full_text = pdf_details.get('full_text', '')
                        
                        if pdf_full_text:
                            # Tổng hợp với Gemini: cách dùng + lưu ý
                            gemini_summary = summarize_drug_info_with_gemini(pdf_full_text, drug_name, drug_info)
                            
                            # Cập nhật usage và thêm notes
                            if gemini_summary.get('usage'):
                                pdf_details['usage'] = gemini_summary['usage']
                            if gemini_summary.get('notes'):
                                pdf_details['notes'] = gemini_summary['notes']
                    
                    # Tạo khuyến nghị
                    recommendations = generate_recommendations(drug_info, pdf_details)
                    
                    response = {
                        'success': True,
                        'drug_name': drug_info.get('DrugName', ''),
                        'active_ingredient': drug_info.get('ActiveIngredient', ''),
                        'page_number': str(page_number),
                        'category': drug_info.get('Category', ''),
                        'extracted_text': extracted_text,
                        'all_ocr_texts': all_ocr_texts or [],  # Trả về tất cả text OCR
                        'rx_status': 'OTC',
                        'composition': pdf_details.get('composition', ''),
                        'indications': pdf_details.get('indications', ''),
                        'contraindications': pdf_details.get('contraindications', ''),
                        'dosage': pdf_details.get('dosage', ''),
                        'usage': pdf_details.get('usage', ''),  # Cách dùng
                        'recommendations': recommendations  # Khuyến nghị
                    }
                    status_code = 200
                else:
                    # Không tìm thấy trong database
                    response = {
                        'success': False,
                        'message': 'Không tìm thấy thông tin thuốc trong database',
                        'extracted_text': extracted_text,
                        'all_ocr_texts': all_ocr_texts or []
                    }
                    status_code = 404
            
            # Send response
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"Error processing scan: {e}", file=sys.stderr)
            error_response = {
                'error': 'Internal server error',
                'message': str(e)
            }
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())

