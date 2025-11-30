import csv
import re
import os
from pypdf import PdfReader

def extract_drug_index(pdf_path, start_page, end_page, output_csv):
    print(f"📖 Đang đọc file: {pdf_path}...")
    reader = PdfReader(pdf_path)
    
    # Mở file CSV để ghi
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Ghi Header chuẩn yêu cầu
        writer.writerow(['DrugName', 'ActiveIngredient', 'PageNumber'])
        
        count = 0
        # Regex bắt format: "Tên Thuốc - Hoạt Chất, SốTrang"
        # Ví dụ: Zyrtec - Cetirizin hydroclorid, 381
        pattern = re.compile(r'^(.+?)\s-\s(.+?),\s(\d+)$')

        # Duyệt qua từng trang (Lưu ý: pypdf đánh số từ 0, nên cần trừ 1)
        for i in range(start_page - 1, end_page):
            try:
                page = reader.pages[i]
                text = page.extract_text()
                
                if text:
                    lines = text.split('\n')
                    for line in lines:
                        line = line.strip()
                        match = pattern.search(line)
                        if match:
                            drug_name = match.group(1).strip()
                            active_ingredient = match.group(2).strip()
                            page_number = match.group(3).strip()
                            
                            writer.writerow([drug_name, active_ingredient, page_number])
                            count += 1
            except Exception as e:
                print(f"⚠️ Lỗi đọc trang {i+1}: {e}")

    print(f"✅ Hoàn tất! Đã trích xuất {count} loại thuốc.")
    print(f"📂 File kết quả: {output_csv}")

# --- CẤU HÌNH ---
# Đảm bảo tên file PDF trùng với tên file bạn đã tải về
# Lấy đường dẫn thư mục chứa script này
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FILE = os.path.join(SCRIPT_DIR, "duoc-thu-quoc-gia-viet-nam-2018.pdf")
START_PAGE = 1600
END_PAGE = 1668
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "drug_index.csv")

if __name__ == "__main__":
    extract_drug_index(PDF_FILE, START_PAGE, END_PAGE, OUTPUT_FILE)