"""
OCR Service - Nhận diện chữ từ ảnh sử dụng EasyOCR và Tesseract
"""
import cv2
import numpy as np
from PIL import Image
import easyocr
import logging

logger = logging.getLogger(__name__)


class OCRService:
    def __init__(self):
        """
        Initialize OCR service with EasyOCR (supports Vietnamese)
        """
        try:
            # Initialize EasyOCR with Vietnamese and English
            self.reader = easyocr.Reader(['vi', 'en'], gpu=False)
            logger.info("EasyOCR initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {str(e)}")
            self.reader = None

    def preprocess_image(self, image):
        """
        Tiền xử lý ảnh nâng cao để cải thiện độ chính xác OCR trên bao bì thuốc
        
        Args:
            image: numpy array hoặc đường dẫn file
        """
        try:
            # Read image if it's a path
            if isinstance(image, str):
                img = cv2.imread(image)
                if img is None:
                    raise ValueError(f"Cannot read image: {image}")
            else:
                img = image.copy()
            
            # 1. Resize để tăng độ phân giải nếu ảnh quá nhỏ
            height, width = img.shape[:2]
            if height < 800 or width < 800:
                scale = max(800 / height, 800 / width)
                img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            
            # 2. Khử nhiễu ban đầu
            img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
            
            # 3. Tăng độ tương phản (CLAHE - Contrast Limited Adaptive Histogram Equalization)
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            # 4. Convert to grayscale
            gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
            
            # 5. Làm sắc nét (Unsharp Masking)
            gaussian = cv2.GaussianBlur(gray, (0, 0), 2.0)
            sharpened = cv2.addWeighted(gray, 1.5, gaussian, -0.5, 0)
            
            # 6. Adaptive thresholding với nhiều phương pháp
            # Method 1: Gaussian adaptive threshold
            thresh1 = cv2.adaptiveThreshold(
                sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Method 2: Mean adaptive threshold  
            thresh2 = cv2.adaptiveThreshold(
                sharpened, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Method 3: Otsu's thresholding
            _, thresh3 = cv2.threshold(
                sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            
            # Combine best of all methods
            combined = cv2.bitwise_and(thresh1, thresh2)
            combined = cv2.bitwise_or(combined, thresh3)
            
            # 7. Morphological operations để làm sạch text
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            morph = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel)
            morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)
            
            # 8. Denoise cuối cùng
            denoised = cv2.fastNlMeansDenoising(morph, None, 10, 7, 21)
            
            return denoised
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            # Fallback to simple processing
            try:
                if isinstance(image, str):
                    img = cv2.imread(image)
                else:
                    img = image.copy()
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                return gray
            except:
                return image if not isinstance(image, str) else None

    def extract_text_multi_angle(self, image):
        """
        Thử OCR với nhiều góc xoay khác nhau để tăng độ chính xác
        """
        try:
            best_result = {'text': '', 'confidence': 0, 'angle': 0}
            
            # Thử với các góc xoay: 0, 90, 180, 270 độ
            for angle in [0, 90, 180, 270]:
                # Xoay ảnh
                if angle == 0:
                    rotated = image.copy()
                else:
                    height, width = image.shape[:2]
                    center = (width // 2, height // 2)
                    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                    rotated = cv2.warpAffine(image, matrix, (width, height), 
                                            flags=cv2.INTER_CUBIC, 
                                            borderMode=cv2.BORDER_REPLICATE)
                
                # OCR
                results = self.reader.readtext(rotated)
                
                # Tính confidence trung bình
                if results:
                    avg_conf = sum(conf for _, _, conf in results) / len(results)
                    texts = [text.strip() for _, text, conf in results if conf > 0.3]
                    combined_text = ' '.join(texts)
                    
                    if avg_conf > best_result['confidence']:
                        best_result = {
                            'text': combined_text,
                            'confidence': avg_conf,
                            'angle': angle
                        }
            
            logger.info(f"Best angle: {best_result['angle']}° with confidence {best_result['confidence']:.2f}")
            return best_result
            
        except Exception as e:
            logger.error(f"Error in multi-angle extraction: {str(e)}")
            return {'text': '', 'confidence': 0, 'angle': 0}

    def extract_text(self, image):
        """
        Trích xuất text từ ảnh với thuật toán nâng cao
        
        Args:
            image: numpy array hoặc đường dẫn file ảnh
            
        Returns:
            dict: {'success': bool, 'text': str, 'confidence': float}
        """
        try:
            if not self.reader:
                return {'success': False, 'error': 'OCR reader not initialized'}
            
            logger.info(f"Processing image with advanced OCR...")
            
            # Preprocess image với nhiều phương pháp
            processed_img = self.preprocess_image(image)
            
            # Method 1: OCR trên ảnh đã xử lý
            results_processed = self.reader.readtext(processed_img)
            
            # Method 2: OCR trên ảnh gốc (đôi khi tốt hơn)
            if isinstance(image, str):
                original = cv2.imread(image)
            else:
                original = image.copy()
            results_original = self.reader.readtext(original)
            
            # Method 3: OCR với nhiều góc xoay
            multi_angle_result = self.extract_text_multi_angle(processed_img)
            
            # Combine results từ cả 3 phương pháp
            all_texts = []
            all_confidences = []
            
            # From processed image
            for (bbox, text, conf) in results_processed:
                if conf > 0.25:  # Lower threshold
                    cleaned_text = self.clean_text(text)
                    if cleaned_text:
                        all_texts.append(cleaned_text)
                        all_confidences.append(conf)
                        logger.info(f"[Processed] '{cleaned_text}' (conf: {conf:.2f})")
            
            # From original image
            for (bbox, text, conf) in results_original:
                if conf > 0.25:
                    cleaned_text = self.clean_text(text)
                    if cleaned_text and cleaned_text not in all_texts:
                        all_texts.append(cleaned_text)
                        all_confidences.append(conf)
                        logger.info(f"[Original] '{cleaned_text}' (conf: {conf:.2f})")
            
            # From multi-angle
            if multi_angle_result['text']:
                angle_texts = multi_angle_result['text'].split()
                for text in angle_texts:
                    cleaned_text = self.clean_text(text)
                    if cleaned_text and cleaned_text not in all_texts:
                        all_texts.append(cleaned_text)
                        all_confidences.append(multi_angle_result['confidence'])
                        logger.info(f"[Angle {multi_angle_result['angle']}°] '{cleaned_text}' (conf: {multi_angle_result['confidence']:.2f})")
            
            # Remove duplicates và sắp xếp theo thứ tự xuất hiện
            unique_texts = []
            seen = set()
            for text in all_texts:
                text_lower = text.lower()
                if text_lower not in seen:
                    unique_texts.append(text)
                    seen.add(text_lower)
            
            # Combine all detected text
            full_text = ' '.join(unique_texts)
            avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0
            
            logger.info(f"✅ Final extracted text: '{full_text}' (avg confidence: {avg_confidence:.2f})")
            
            return {
                'success': True,
                'text': full_text.strip(),
                'confidence': round(avg_confidence, 2),
                'word_count': len(unique_texts)
            }
            
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e), 'text': ''}
    
    def clean_text(self, text):
        """
        Làm sạch text đã trích xuất
        """
        if not text:
            return ''
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove very short texts (likely noise)
        if len(text) < 2:
            return ''
        
        # Remove texts with too many special characters
        special_char_ratio = sum(not c.isalnum() and not c.isspace() for c in text) / len(text)
        if special_char_ratio > 0.5:
            return ''
        
        return text.strip()

    def extract_text_with_details(self, image_path):
        """
        Trích xuất text kèm thông tin chi tiết (bounding box, confidence)
        
        Returns:
            list: List of dict containing text, bbox, confidence
        """
        try:
            if not self.reader:
                raise Exception("OCR reader not initialized")
            
            # Preprocess image
            processed_img = self.preprocess_image(image_path)
            
            # Perform OCR
            results = self.reader.readtext(processed_img)
            
            # Format results
            formatted_results = []
            for (bbox, text, confidence) in results:
                if confidence > 0.3:
                    formatted_results.append({
                        'text': text.strip(),
                        'bbox': bbox,
                        'confidence': float(confidence)
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error extracting text with details: {str(e)}")
            return []
