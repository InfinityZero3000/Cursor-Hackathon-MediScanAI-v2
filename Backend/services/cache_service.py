"""
Cache Service
Lưu trữ summaries và audio để tránh gọi API nhiều lần
"""

import os
import json
import hashlib
import time
from pathlib import Path
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        """Initialize cache service"""
        self.cache_folder = './cache'
        self.enabled = os.getenv('ENABLE_CACHE', 'True').lower() == 'true'
        self.expiry_hours = int(os.getenv('CACHE_EXPIRY_HOURS', 24))
        
        if self.enabled:
            self._ensure_cache_folder()
            logger.info(f"✅ Cache service initialized (expiry: {self.expiry_hours}h)")
        else:
            logger.info("⚠️ Cache service disabled")

    def _ensure_cache_folder(self):
        """Tạo thư mục cache nếu chưa tồn tại"""
        Path(self.cache_folder).mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, drug_name, category=""):
        """
        Tạo cache key từ drug name và category
        
        Args:
            drug_name (str): Tên thuốc
            category (str): Danh mục
            
        Returns:
            str: Cache key (hash)
        """
        key_string = f"{drug_name.lower().strip()}_{category.lower().strip()}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_cache_path(self, cache_key):
        """
        Lấy đường dẫn file cache
        
        Args:
            cache_key (str): Cache key
            
        Returns:
            str: Đường dẫn file
        """
        return os.path.join(self.cache_folder, f"{cache_key}.json")

    def get(self, drug_name, category=""):
        """
        Lấy summary từ cache
        
        Args:
            drug_name (str): Tên thuốc
            category (str): Danh mục
            
        Returns:
            dict or None: Cached data nếu có và còn hiệu lực
        """
        if not self.enabled:
            return None
        
        try:
            cache_key = self._get_cache_key(drug_name, category)
            cache_path = self._get_cache_path(cache_key)
            
            if not os.path.exists(cache_path):
                logger.debug(f"❌ Cache miss: {drug_name}")
                return None
            
            # Đọc cache
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # Kiểm tra expiry
            cached_time = cached_data.get('timestamp', 0)
            current_time = time.time()
            age_hours = (current_time - cached_time) / 3600
            
            if age_hours > self.expiry_hours:
                logger.info(f"⏰ Cache expired: {drug_name} (age: {age_hours:.1f}h)")
                # Xóa cache cũ
                os.remove(cache_path)
                return None
            
            logger.info(f"✅ Cache hit: {drug_name} (age: {age_hours:.1f}h)")
            return cached_data.get('data')
            
        except Exception as e:
            logger.error(f"❌ Error reading cache: {e}")
            return None

    def set(self, drug_name, category, summary_data):
        """
        Lưu summary vào cache
        
        Args:
            drug_name (str): Tên thuốc
            category (str): Danh mục
            summary_data (dict): Dữ liệu cần cache
            
        Returns:
            bool: True nếu thành công
        """
        if not self.enabled:
            return False
        
        try:
            cache_key = self._get_cache_key(drug_name, category)
            cache_path = self._get_cache_path(cache_key)
            
            # Tạo cache object
            cache_object = {
                'drug_name': drug_name,
                'category': category,
                'timestamp': time.time(),
                'data': summary_data
            }
            
            # Lưu vào file
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_object, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Cached summary: {drug_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error writing cache: {e}")
            return False

    def clear_expired(self):
        """
        Xóa tất cả cache đã hết hạn
        
        Returns:
            dict: Thống kê cleanup
        """
        if not self.enabled:
            return {'success': False, 'message': 'Cache disabled'}
        
        try:
            current_time = time.time()
            expiry_seconds = self.expiry_hours * 3600
            
            deleted_count = 0
            deleted_size = 0
            
            cache_folder = Path(self.cache_folder)
            
            for cache_file in cache_folder.glob("*.json"):
                file_age = current_time - cache_file.stat().st_mtime
                
                if file_age > expiry_seconds:
                    file_size = cache_file.stat().st_size
                    cache_file.unlink()
                    deleted_count += 1
                    deleted_size += file_size
            
            logger.info(f"🧹 Cache cleanup: {deleted_count} files, {deleted_size/1024:.2f} KB")
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'deleted_size': deleted_size
            }
            
        except Exception as e:
            logger.error(f"❌ Error clearing cache: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def clear_all(self):
        """
        Xóa toàn bộ cache
        
        Returns:
            dict: Thống kê cleanup
        """
        if not self.enabled:
            return {'success': False, 'message': 'Cache disabled'}
        
        try:
            deleted_count = 0
            deleted_size = 0
            
            cache_folder = Path(self.cache_folder)
            
            for cache_file in cache_folder.glob("*.json"):
                file_size = cache_file.stat().st_size
                cache_file.unlink()
                deleted_count += 1
                deleted_size += file_size
            
            logger.info(f"🗑️ Cleared all cache: {deleted_count} files, {deleted_size/1024:.2f} KB")
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'deleted_size': deleted_size
            }
            
        except Exception as e:
            logger.error(f"❌ Error clearing all cache: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_stats(self):
        """
        Lấy thống kê cache
        
        Returns:
            dict: Thống kê
        """
        try:
            cache_folder = Path(self.cache_folder)
            
            if not cache_folder.exists():
                return {
                    'enabled': self.enabled,
                    'total_files': 0,
                    'total_size': 0
                }
            
            cache_files = list(cache_folder.glob("*.json"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            return {
                'enabled': self.enabled,
                'total_files': len(cache_files),
                'total_size': total_size,
                'total_size_kb': round(total_size / 1024, 2),
                'expiry_hours': self.expiry_hours
            }
            
        except Exception as e:
            return {
                'enabled': self.enabled,
                'error': str(e)
            }


# Singleton instance
_cache_instance = None

def get_cache_service():
    """Get singleton instance of CacheService"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheService()
    return _cache_instance


if __name__ == "__main__":
    # Test script
    print("🧪 Testing Cache Service...")
    
    cache = get_cache_service()
    
    # Test 1: Stats
    print("\n1️⃣ Cache stats:")
    stats = cache.get_stats()
    print(f"   Enabled: {stats['enabled']}")
    print(f"   Files: {stats.get('total_files', 0)}")
    print(f"   Size: {stats.get('total_size_kb', 0)} KB")
    
    # Test 2: Set cache
    print("\n2️⃣ Test set cache:")
    test_data = {
        'summary': 'Paracetamol là thuốc giảm đau hạ sốt...',
        'word_count': 100
    }
    success = cache.set('Paracetamol', 'Giảm đau', test_data)
    print(f"   Set cache: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 3: Get cache
    print("\n3️⃣ Test get cache:")
    cached = cache.get('Paracetamol', 'Giảm đau')
    if cached:
        print(f"   ✅ Cache hit!")
        print(f"   Summary: {cached['summary'][:50]}...")
    else:
        print(f"   ❌ Cache miss")
    
    # Test 4: Clear expired
    print("\n4️⃣ Test cleanup:")
    result = cache.clear_expired()
    print(f"   Deleted: {result.get('deleted_count', 0)} files")
