"""
Gemini AI Summarizer Service
Tóm tắt thông tin thuốc từ PDF sử dụng Google Gemini API
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiSummarizerService:
    def __init__(self):
        """Initialize Gemini AI service"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-pro')
        self.max_words = int(os.getenv('MAX_SUMMARY_WORDS', 100))
        
        if not self.api_key or self.api_key == 'your_gemini_api_key_here':
            logger.warning("⚠️ GEMINI_API_KEY chưa được cấu hình!")
            logger.info("🔑 Hướng dẫn lấy API key:")
            logger.info("   1. Truy cập: https://ai.google.dev/")
            logger.info("   2. Đăng nhập với Google account")
            logger.info("   3. Get API Key → Create API Key")
            logger.info("   4. Copy key và thêm vào file .env: GEMINI_API_KEY=your_key")
            self.configured = False
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                self.configured = True
                logger.info(f"✅ Gemini AI initialized: {self.model_name}")
            except Exception as e:
                logger.error(f"❌ Lỗi khởi tạo Gemini AI: {e}")
                self.configured = False

    def summarize_drug_info(self, drug_name, pdf_text, category="", active_ingredient=""):
        """
        Tóm tắt thông tin thuốc bằng Gemini AI
        
        Args:
            drug_name (str): Tên thuốc
            pdf_text (str): Text chi tiết từ PDF
            category (str): Danh mục thuốc
            active_ingredient (str): Hoạt chất
            
        Returns:
            dict: {
                'success': bool,
                'summary': str,
                'word_count': int,
                'error': str (nếu có)
            }
        """
        if not self.configured:
            return {
                'success': False,
                'summary': self._fallback_summary(drug_name, pdf_text, category, active_ingredient),
                'word_count': 0,
                'error': 'Gemini API chưa được cấu hình. Sử dụng summary cơ bản.'
            }
        
        try:
            # Tạo prompt cho Gemini
            prompt = self._create_prompt(drug_name, pdf_text, category, active_ingredient)
            
            # Gọi Gemini API
            logger.info(f"📡 Đang tóm tắt thông tin thuốc: {drug_name}")
            response = self.model.generate_content(prompt)
            
            # Lấy summary từ response
            summary = response.text.strip()
            word_count = len(summary.split())
            
            logger.info(f"✅ Tóm tắt thành công: {word_count} từ")
            
            return {
                'success': True,
                'summary': summary,
                'word_count': word_count,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi tóm tắt với Gemini: {e}")
            return {
                'success': False,
                'summary': self._fallback_summary(drug_name, pdf_text, category, active_ingredient),
                'word_count': 0,
                'error': str(e)
            }

    def _create_prompt(self, drug_name, pdf_text, category, active_ingredient):
        """
        Tạo prompt tối ưu cho Gemini AI
        
        Args:
            drug_name (str): Tên thuốc
            pdf_text (str): Text từ PDF
            category (str): Danh mục
            active_ingredient (str): Hoạt chất
            
        Returns:
            str: Prompt cho Gemini
        """
        # Giới hạn text đầu vào (tránh quá dài)
        max_input_chars = 3000
        if len(pdf_text) > max_input_chars:
            pdf_text = pdf_text[:max_input_chars] + "..."
        
        prompt = f"""Bạn là dược sĩ chuyên nghiệp. Hãy tóm tắt thông tin thuốc sau đây trong ĐÚNG {self.max_words} từ, sử dụng tiếng Việt rõ ràng, dễ hiểu.

📋 THÔNG TIN THUỐC:
- Tên thuốc: {drug_name}
- Hoạt chất: {active_ingredient if active_ingredient else "Chưa rõ"}
- Danh mục: {category if category else "Chưa phân loại"}

📄 CHI TIẾT TỪ DƯỢC THƯ:
{pdf_text}

🎯 YÊU CẦU TÓM TẮT:
1. Tập trung vào: Công dụng chính, liều dùng cơ bản, tác dụng phụ quan trọng, lưu ý đặc biệt
2. Sử dụng ngôn ngữ đơn giản, dễ hiểu cho người không chuyên
3. Độ dài: ĐÚNG {self.max_words} từ (không quá dài, không quá ngắn)
4. Không cần tiêu đề, đi thẳng vào nội dung
5. Ưu tiên thông tin an toàn và cảnh báo quan trọng

TÓM TẮT ({self.max_words} từ):"""

        return prompt

    def _fallback_summary(self, drug_name, pdf_text, category, active_ingredient):
        """
        Tạo summary cơ bản khi Gemini API không khả dụng
        
        Args:
            drug_name (str): Tên thuốc
            pdf_text (str): Text từ PDF
            category (str): Danh mục
            active_ingredient (str): Hoạt chất
            
        Returns:
            str: Summary cơ bản
        """
        # Trích xuất các thông tin quan trọng từ PDF text
        lines = pdf_text.split('\n')
        summary_parts = []
        
        # Thêm thông tin cơ bản
        summary_parts.append(f"{drug_name}")
        
        if active_ingredient:
            summary_parts.append(f"có hoạt chất {active_ingredient}")
        
        if category:
            summary_parts.append(f"thuộc nhóm {category}")
        
        # Tìm thông tin chỉ định
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if 'chỉ định' in line_lower or 'công dụng' in line_lower:
                # Lấy 2-3 dòng tiếp theo
                next_lines = ' '.join(lines[i+1:i+4]).strip()
                if next_lines:
                    summary_parts.append(f"Chỉ định: {next_lines[:150]}")
                break
        
        # Tìm liều dùng
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if 'liều' in line_lower or 'dùng' in line_lower:
                next_lines = ' '.join(lines[i:i+2]).strip()
                if next_lines:
                    summary_parts.append(f"{next_lines[:100]}")
                break
        
        # Ghép lại và giới hạn độ dài
        summary = '. '.join(summary_parts)
        
        # Giới hạn khoảng 100 từ
        words = summary.split()
        if len(words) > self.max_words:
            summary = ' '.join(words[:self.max_words]) + '...'
        
        return summary

    def test_connection(self):
        """
        Test kết nối Gemini API
        
        Returns:
            dict: Kết quả test
        """
        if not self.configured:
            return {
                'success': False,
                'message': 'Gemini API chưa được cấu hình'
            }
        
        try:
            # Test với prompt đơn giản
            response = self.model.generate_content("Xin chào! Bạn có hoạt động không?")
            return {
                'success': True,
                'message': 'Gemini API hoạt động bình thường',
                'response': response.text
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Lỗi kết nối Gemini API: {e}'
            }


# Singleton instance
_summarizer_instance = None

def get_summarizer():
    """
    Get singleton instance of GeminiSummarizerService
    
    Returns:
        GeminiSummarizerService: Instance
    """
    global _summarizer_instance
    if _summarizer_instance is None:
        _summarizer_instance = GeminiSummarizerService()
    return _summarizer_instance


if __name__ == "__main__":
    # Test script
    print("🧪 Testing Gemini Summarizer Service...")
    
    summarizer = get_summarizer()
    
    # Test 1: Check configuration
    print("\n1️⃣ Kiểm tra cấu hình:")
    print(f"   API Key configured: {'✅ Yes' if summarizer.configured else '❌ No'}")
    print(f"   Model: {summarizer.model_name}")
    print(f"   Max words: {summarizer.max_words}")
    
    # Test 2: Test connection (nếu đã config)
    if summarizer.configured:
        print("\n2️⃣ Test kết nối:")
        result = summarizer.test_connection()
        print(f"   Status: {'✅ Success' if result['success'] else '❌ Failed'}")
        print(f"   Message: {result['message']}")
    
    # Test 3: Test summary (với hoặc không có API key)
    print("\n3️⃣ Test tóm tắt:")
    test_text = """
    Paracetamol là thuốc giảm đau và hạ sốt phổ biến.
    Chỉ định: Giảm đau nhẹ và vừa, hạ sốt.
    Liều dùng: Người lớn 500-1000mg mỗi 4-6 giờ, tối đa 4g/ngày.
    Tác dụng phụ: Hiếm gặp ở liều thông thường. Quá liều có thể gây tổn thương gan.
    Chống chỉ định: Người mẫn cảm với paracetamol, suy gan nặng.
    """
    
    result = summarizer.summarize_drug_info(
        drug_name="Paracetamol 500mg",
        pdf_text=test_text,
        category="Giảm đau, hạ sốt",
        active_ingredient="Paracetamol"
    )
    
    print(f"   Success: {'✅ Yes' if result['success'] else '❌ No'}")
    print(f"   Word count: {result['word_count']}")
    print(f"   Summary: {result['summary'][:200]}...")
    if result['error']:
        print(f"   Error: {result['error']}")
