"""
Text-to-Speech Service
Chuyển đổi văn bản thành giọng nói sử dụng Google Text-to-Speech (gTTS)
"""

import os
import hashlib
import time
from gtts import gTTS
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        """Initialize Text-to-Speech service"""
        self.audio_folder = os.getenv('AUDIO_FOLDER', './static/audio')
        self.language = os.getenv('TTS_LANGUAGE', 'vi')
        self.tts_service = os.getenv('TTS_SERVICE', 'gtts')
        
        # Tạo thư mục audio nếu chưa tồn tại
        self._ensure_audio_folder()
        
        logger.info(f"✅ TTS Service initialized: {self.tts_service}, Language: {self.language}")

    def _ensure_audio_folder(self):
        """Tạo thư mục lưu audio nếu chưa tồn tại"""
        Path(self.audio_folder).mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Audio folder: {self.audio_folder}")

    def text_to_speech(self, text, drug_name="drug", slow=False):
        """
        Chuyển đổi text thành file audio
        
        Args:
            text (str): Văn bản cần đọc
            drug_name (str): Tên thuốc (dùng cho filename)
            slow (bool): Đọc chậm hay không
            
        Returns:
            dict: {
                'success': bool,
                'audio_path': str,
                'audio_url': str,
                'duration': float (giây),
                'file_size': int (bytes),
                'error': str (nếu có)
            }
        """
        try:
            # Tạo filename unique dựa trên text hash + timestamp
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            timestamp = int(time.time())
            clean_name = self._clean_filename(drug_name)
            filename = f"{clean_name}_{text_hash}_{timestamp}.mp3"
            audio_path = os.path.join(self.audio_folder, filename)
            
            logger.info(f"🎤 Đang tạo audio cho: {drug_name}")
            logger.info(f"   Text length: {len(text)} ký tự")
            
            # Tạo audio với gTTS
            tts = gTTS(text=text, lang=self.language, slow=slow)
            tts.save(audio_path)
            
            # Lấy thông tin file
            file_size = os.path.getsize(audio_path)
            duration = self._estimate_duration(text)
            
            # Tạo URL tương đối
            audio_url = f"/static/audio/{filename}"
            
            logger.info(f"✅ Tạo audio thành công:")
            logger.info(f"   File: {filename}")
            logger.info(f"   Size: {file_size / 1024:.2f} KB")
            logger.info(f"   Duration: ~{duration:.1f}s")
            
            return {
                'success': True,
                'audio_path': audio_path,
                'audio_url': audio_url,
                'filename': filename,
                'duration': duration,
                'file_size': file_size,
                'format': 'mp3',
                'error': None
            }
            
        except Exception as e:
            logger.error(f"❌ Lỗi tạo audio: {e}")
            return {
                'success': False,
                'audio_path': None,
                'audio_url': None,
                'duration': 0,
                'file_size': 0,
                'error': str(e)
            }

    def _clean_filename(self, name):
        """
        Làm sạch tên file (loại bỏ ký tự đặc biệt)
        
        Args:
            name (str): Tên gốc
            
        Returns:
            str: Tên đã làm sạch
        """
        # Loại bỏ ký tự đặc biệt, giữ chữ, số, dấu gạch
        import re
        clean = re.sub(r'[^\w\s-]', '', name)
        clean = re.sub(r'[-\s]+', '_', clean)
        return clean.lower()[:50]  # Giới hạn 50 ký tự

    def _estimate_duration(self, text):
        """
        Ước tính thời gian đọc (giây)
        
        Args:
            text (str): Văn bản
            
        Returns:
            float: Thời gian ước tính (giây)
        """
        # Tiếng Việt: trung bình 150-180 từ/phút
        words = len(text.split())
        words_per_minute = 160
        duration = (words / words_per_minute) * 60
        return round(duration, 1)

    def cleanup_old_files(self, max_age_hours=24):
        """
        Xóa các file audio cũ
        
        Args:
            max_age_hours (int): Tuổi file tối đa (giờ)
            
        Returns:
            dict: Thông tin cleanup
        """
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            deleted_count = 0
            deleted_size = 0
            
            audio_folder = Path(self.audio_folder)
            
            for audio_file in audio_folder.glob("*.mp3"):
                file_age = current_time - audio_file.stat().st_mtime
                
                if file_age > max_age_seconds:
                    file_size = audio_file.stat().st_size
                    audio_file.unlink()
                    deleted_count += 1
                    deleted_size += file_size
                    logger.info(f"🗑️ Deleted old audio: {audio_file.name}")
            
            logger.info(f"✅ Cleanup completed:")
            logger.info(f"   Deleted files: {deleted_count}")
            logger.info(f"   Freed space: {deleted_size / 1024:.2f} KB")
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'deleted_size': deleted_size,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"❌ Lỗi cleanup: {e}")
            return {
                'success': False,
                'deleted_count': 0,
                'deleted_size': 0,
                'error': str(e)
            }

    def get_audio_info(self, audio_path):
        """
        Lấy thông tin về file audio
        
        Args:
            audio_path (str): Đường dẫn file audio
            
        Returns:
            dict: Thông tin file
        """
        try:
            if not os.path.exists(audio_path):
                return {
                    'exists': False,
                    'error': 'File không tồn tại'
                }
            
            file_size = os.path.getsize(audio_path)
            file_name = os.path.basename(audio_path)
            
            return {
                'exists': True,
                'filename': file_name,
                'size': file_size,
                'size_kb': round(file_size / 1024, 2),
                'path': audio_path,
                'error': None
            }
            
        except Exception as e:
            return {
                'exists': False,
                'error': str(e)
            }


# Singleton instance
_tts_instance = None

def get_tts_service():
    """
    Get singleton instance of TTSService
    
    Returns:
        TTSService: Instance
    """
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TTSService()
    return _tts_instance


if __name__ == "__main__":
    # Test script
    print("🧪 Testing TTS Service...")
    
    tts = get_tts_service()
    
    # Test 1: Kiểm tra cấu hình
    print("\n1️⃣ Kiểm tra cấu hình:")
    print(f"   Audio folder: {tts.audio_folder}")
    print(f"   Language: {tts.language}")
    print(f"   TTS Service: {tts.tts_service}")
    
    # Test 2: Tạo audio mẫu
    print("\n2️⃣ Test tạo audio:")
    test_text = """
    Paracetamol là thuốc giảm đau và hạ sốt phổ biến. 
    Liều dùng người lớn là 500 đến 1000 miligam mỗi 4 đến 6 giờ. 
    Không dùng quá 4 gam trong 24 giờ để tránh tổn thương gan.
    """
    
    result = tts.text_to_speech(test_text, drug_name="Paracetamol_Test")
    
    print(f"   Success: {'✅ Yes' if result['success'] else '❌ No'}")
    if result['success']:
        print(f"   File: {result['filename']}")
        print(f"   Size: {result['file_size'] / 1024:.2f} KB")
        print(f"   Duration: ~{result['duration']}s")
        print(f"   URL: {result['audio_url']}")
    else:
        print(f"   Error: {result['error']}")
    
    # Test 3: Kiểm tra file
    if result['success']:
        print("\n3️⃣ Kiểm tra file audio:")
        info = tts.get_audio_info(result['audio_path'])
        print(f"   Exists: {'✅ Yes' if info['exists'] else '❌ No'}")
        if info['exists']:
            print(f"   Size: {info['size_kb']} KB")
    
    # Test 4: Cleanup (không xóa file mới tạo)
    print("\n4️⃣ Test cleanup:")
    cleanup_result = tts.cleanup_old_files(max_age_hours=48)  # Chỉ xóa file > 48h
    print(f"   Success: {'✅ Yes' if cleanup_result['success'] else '❌ No'}")
    print(f"   Deleted files: {cleanup_result['deleted_count']}")
