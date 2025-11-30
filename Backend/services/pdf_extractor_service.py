"""
PDF Extractor Service - Trích xuất thông tin chi tiết từ PDF Dược thư
"""
import pdfplumber
import logging
import re

logger = logging.getLogger(__name__)


class PDFExtractorService:
    def __init__(self, pdf_path):
        """
        Initialize PDF extractor service
        
        Args:
            pdf_path: Path to PDF file
        """
        self.pdf_path = pdf_path
        try:
            self.pdf = pdfplumber.open(pdf_path)
            logger.info(f"Loaded PDF with {len(self.pdf.pages)} pages")
        except Exception as e:
            logger.error(f"Failed to load PDF: {str(e)}")
            self.pdf = None

    def extract_page_info(self, page_number):
        """
        Trích xuất thông tin từ trang cụ thể trong PDF
        
        Args:
            page_number: Số trang (1-indexed)
            
        Returns:
            dict: Thông tin chi tiết về thuốc
        """
        if not self.pdf:
            return {
                'error': 'PDF not loaded',
                'content': ''
            }
        
        try:
            # PDF pages are 0-indexed
            page_index = page_number - 1
            
            if page_index < 0 or page_index >= len(self.pdf.pages):
                return {
                    'error': f'Invalid page number: {page_number}',
                    'content': ''
                }
            
            # Extract text from page
            page = self.pdf.pages[page_index]
            text = page.extract_text()
            
            if not text:
                return {
                    'error': 'No text found on page',
                    'content': '',
                    'page_number': page_number
                }
            
            # Parse structured information
            parsed_info = self.parse_drug_info(text)
            
            return {
                'page_number': page_number,
                'raw_content': text,
                'parsed_info': parsed_info
            }
            
        except Exception as e:
            logger.error(f"Error extracting page {page_number}: {str(e)}")
            return {
                'error': str(e),
                'content': '',
                'page_number': page_number
            }

    def parse_drug_info(self, text):
        """
        Parse thông tin thuốc từ raw text
        Cố gắng trích xuất các thông tin cấu trúc
        
        Returns:
            dict: Thông tin đã được parse
        """
        try:
            info = {
                'drug_name': '',
                'active_ingredient': '',
                'dosage': '',
                'indication': '',
                'contraindication': '',
                'side_effects': '',
                'dosage_administration': '',
                'precautions': '',
                'interactions': '',
                'storage': ''
            }
            
            # Split text into lines
            lines = text.split('\n')
            
            # Extract drug name (usually first line or bold)
            if lines:
                info['drug_name'] = lines[0].strip()
            
            # Keywords to identify sections
            section_keywords = {
                'active_ingredient': ['thành phần', 'hoạt chất', 'active ingredient'],
                'dosage': ['dạng bào chế', 'hàm lượng', 'dosage form'],
                'indication': ['chỉ định', 'công dụng', 'indication', 'chỉ_định'],
                'contraindication': ['chống chỉ định', 'chống_chỉ_định', 'contraindication'],
                'side_effects': ['tác dụng phụ', 'tác_dụng_phụ', 'phản ứng có hại', 'side effect'],
                'dosage_administration': ['liều dùng', 'cách dùng', 'liều_dùng', 'dosage'],
                'precautions': ['thận trọng', 'lưu ý', 'precaution', 'cảnh báo'],
                'interactions': ['tương tác', 'interaction'],
                'storage': ['bảo quản', 'storage']
            }
            
            # Simple section extraction
            current_section = None
            section_content = []
            
            for line in lines:
                line_lower = line.lower().strip()
                
                # Check if line is a section header
                for section, keywords in section_keywords.items():
                    for keyword in keywords:
                        if keyword in line_lower:
                            # Save previous section
                            if current_section and section_content:
                                info[current_section] = '\n'.join(section_content).strip()
                            
                            # Start new section
                            current_section = section
                            section_content = []
                            break
                    if current_section == section:
                        break
                else:
                    # Add line to current section
                    if current_section and line.strip():
                        section_content.append(line.strip())
            
            # Save last section
            if current_section and section_content:
                info[current_section] = '\n'.join(section_content).strip()
            
            # Clean up empty fields
            info = {k: v for k, v in info.items() if v}
            
            return info
            
        except Exception as e:
            logger.error(f"Error parsing drug info: {str(e)}")
            return {}

    def search_in_pdf(self, query):
        """
        Tìm kiếm text trong toàn bộ PDF
        
        Args:
            query: Text cần tìm
            
        Returns:
            list: Danh sách các trang có chứa query
        """
        if not self.pdf:
            return []
        
        try:
            matching_pages = []
            
            for page_num, page in enumerate(self.pdf.pages, start=1):
                text = page.extract_text()
                if text and query.lower() in text.lower():
                    matching_pages.append({
                        'page_number': page_num,
                        'snippet': self.get_text_snippet(text, query)
                    })
            
            return matching_pages
            
        except Exception as e:
            logger.error(f"Error searching in PDF: {str(e)}")
            return []

    def get_text_snippet(self, text, query, context_length=100):
        """
        Lấy đoạn text xung quanh query
        """
        try:
            text_lower = text.lower()
            query_lower = query.lower()
            
            index = text_lower.find(query_lower)
            if index == -1:
                return text[:context_length]
            
            start = max(0, index - context_length)
            end = min(len(text), index + len(query) + context_length)
            
            snippet = text[start:end]
            
            if start > 0:
                snippet = '...' + snippet
            if end < len(text):
                snippet = snippet + '...'
            
            return snippet
            
        except Exception as e:
            logger.error(f"Error getting snippet: {str(e)}")
            return ""

    def __del__(self):
        """Close PDF when object is destroyed"""
        if self.pdf:
            self.pdf.close()
