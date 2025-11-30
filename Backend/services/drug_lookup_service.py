"""
Drug Lookup Service - Tra cứu thông tin thuốc từ CSV database
"""
import pandas as pd
import logging
from difflib import SequenceMatcher
import re

logger = logging.getLogger(__name__)


class DrugLookupService:
    def __init__(self, csv_path):
        """
        Initialize drug lookup service with CSV database
        
        Args:
            csv_path: Path to drug database CSV file
        """
        try:
            self.df = pd.read_csv(csv_path)
            logger.info(f"Loaded {len(self.df)} drugs from database")
            
            # Preprocess drug names for better matching
            self.df['DrugName_Lower'] = self.df['DrugName'].str.lower().str.strip()
            self.df['ActiveIngredient_Lower'] = self.df['ActiveIngredient'].str.lower().str.strip()
            
        except Exception as e:
            logger.error(f"Failed to load drug database: {str(e)}")
            self.df = None

    def normalize_text(self, text):
        """
        Chuẩn hóa text để so sánh (loại bỏ ký tự đặc biệt, viết thường)
        """
        # Convert to lowercase
        text = text.lower().strip()
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', '', text)
        # Remove extra spaces
        text = ' '.join(text.split())
        return text

    def calculate_similarity(self, str1, str2):
        """
        Tính độ tương đồng giữa 2 chuỗi (0-1)
        """
        return SequenceMatcher(None, str1, str2).ratio()

    def search_drugs(self, query, threshold=0.6, top_n=20):
        """
        Tìm kiếm thuốc theo tên (hỗ trợ fuzzy matching)
        
        Args:
            query: Text query từ OCR
            threshold: Ngưỡng độ tương đồng tối thiểu (0-1)
            top_n: Số lượng kết quả tối đa trả về
            
        Returns:
            list: Danh sách thuốc phù hợp, sắp xếp theo độ tương đồng
        """
        if self.df is None:
            return []
        
        try:
            # Normalize query
            normalized_query = self.normalize_text(query)
            query_words = normalized_query.split()
            
            matches = []
            
            # Search in drug names and active ingredients
            for idx, row in self.df.iterrows():
                drug_name = row['DrugName_Lower']
                active_ingredient = row['ActiveIngredient_Lower']
                
                # Calculate similarity scores
                name_similarity = self.calculate_similarity(normalized_query, drug_name)
                ingredient_similarity = self.calculate_similarity(normalized_query, active_ingredient)
                
                # Check if any word in query matches drug name
                word_match_score = 0
                for word in query_words:
                    if len(word) >= 3:  # Only consider words with 3+ characters
                        if word in drug_name or word in active_ingredient:
                            word_match_score = max(word_match_score, 0.8)
                
                # Take the best similarity score
                best_score = max(name_similarity, ingredient_similarity, word_match_score)
                
                if best_score >= threshold:
                    matches.append({
                        'DrugName': row['DrugName'],
                        'ActiveIngredient': row['ActiveIngredient'],
                        'Category': row['Category'],
                        'Is_Prescription': bool(row['Is_Prescription']),
                        'PageNumber': row['PageNumber'],
                        'similarity_score': round(best_score, 3)
                    })
            
            # Sort by similarity score (descending)
            matches.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Limit results
            matches = matches[:top_n]
            
            logger.info(f"Found {len(matches)} matches for query: '{query}'")
            
            return matches
            
        except Exception as e:
            logger.error(f"Error searching drugs: {str(e)}")
            return []

    def get_drug_by_name(self, drug_name):
        """
        Lấy thông tin thuốc theo tên chính xác
        
        Args:
            drug_name: Tên thuốc
            
        Returns:
            dict: Thông tin thuốc hoặc None nếu không tìm thấy
        """
        if self.df is None:
            return None
        
        try:
            # Search for exact match (case-insensitive)
            result = self.df[self.df['DrugName'].str.lower() == drug_name.lower()]
            
            if len(result) > 0:
                row = result.iloc[0]
                return {
                    'DrugName': row['DrugName'],
                    'ActiveIngredient': row['ActiveIngredient'],
                    'Category': row['Category'],
                    'Is_Prescription': bool(row['Is_Prescription']),
                    'PageNumber': row['PageNumber']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting drug by name: {str(e)}")
            return None

    def get_suggestions(self, query, limit=5):
        """
        Lấy gợi ý thuốc dựa trên query (với threshold thấp hơn)
        
        Args:
            query: Text query
            limit: Số lượng gợi ý tối đa
            
        Returns:
            list: Danh sách gợi ý
        """
        matches = self.search_drugs(query, threshold=0.3)
        return [m['DrugName'] for m in matches[:limit]]

    def get_all_categories(self):
        """
        Lấy tất cả danh mục thuốc
        """
        if self.df is None:
            return []
        
        return self.df['Category'].unique().tolist()

    def search_by_category(self, category):
        """
        Tìm kiếm thuốc theo danh mục
        """
        if self.df is None:
            return []
        
        try:
            result = self.df[self.df['Category'].str.contains(category, case=False, na=False)]
            return result[['DrugName', 'ActiveIngredient', 'Category', 'Is_Prescription', 'PageNumber']].to_dict('records')
        except Exception as e:
            logger.error(f"Error searching by category: {str(e)}")
            return []
