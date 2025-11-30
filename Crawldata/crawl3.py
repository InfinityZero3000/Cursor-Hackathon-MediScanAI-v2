import pandas as pd
from pypdf import PdfReader
import re
import os

def find_optimal_offset(pdf_reader, csv_df):
    """
    Hàm tự động tìm độ lệch trang (Offset) bằng cách dò thử một loại thuốc.
    Chọn thuốc 'Meloxicam' (thường nằm ở giữa sách) để test.
    """
    # Chọn một thuốc mẫu để dò (Kukjemefen - Meloxicam ở trang 940)
    # Nếu trong CSV của bạn không có thuốc này, hãy đổi tên thuốc khác
    sample_row = csv_df[csv_df['DrugName'] == 'Kukjemefen']
    
    if sample_row.empty:
        # Fallback nếu không tìm thấy thuốc mẫu
        print("⚠️ Không tìm thấy thuốc mẫu để dò Offset. Dùng mặc định = -1")
        return -1

    sample_drug = sample_row.iloc[0]
    target_name = "Meloxicam" # Hoạt chất chính cần tìm trong trang
    csv_page = int(sample_drug['PageNumber'])
    
    print(f"🕵️ Đang dò tìm vị trí thực tế của thuốc '{target_name}' (CSV báo trang {csv_page})...")
    
    # Quét trong phạm vi +/- 20 trang xung quanh số trang trong CSV
    scan_range = range(csv_page - 20, csv_page + 20)
    
    for pdf_idx in scan_range:
        try:
            if pdf_idx < 0 or pdf_idx >= len(pdf_reader.pages):
                continue
                
            text = pdf_reader.pages[pdf_idx].extract_text()
            
            # Tìm dòng tiêu đề chứa tên thuốc
            if re.search(f"{target_name}", text, re.IGNORECASE):
                # Kiểm tra kỹ hơn: Dòng đó phải ngắn (tiêu đề) và nằm ở đầu trang
                lines = text.split('\n')
                for line in lines[:10]: # Check 10 dòng đầu
                    if target_name.upper() in line.upper():
                        found_offset = pdf_idx - csv_page
                        print(f"✅ TÌM THẤY! '{target_name}' ở trang PDF {pdf_idx}.")
                        print(f"🎯 ĐỘ LỆCH (OFFSET) CHUẨN LÀ: {found_offset}")
                        return found_offset
        except:
            continue
            
    print("⚠️ Không dò thấy tự động. Dùng offset mặc định = -1.")
    return -1

def clean_text(text):
    """Hàm làm sạch văn bản: Bỏ dấu ngoặc kép, dấu chấm cuối câu"""
    if not text: return "Chưa phân loại"
    text = str(text)
    text = text.replace('"', '').replace("'", "") # Bỏ ngoặc kép/đơn
    text = text.strip()
    text = text.rstrip('.') # Bỏ dấu chấm cuối câu
    return text.capitalize()

def enrich_drug_data(csv_input, pdf_path, csv_output):
    print("⏳ Đang nạp dữ liệu...")
    df = pd.read_csv(csv_input)
    reader = PdfReader(pdf_path)
    
    # --- BƯỚC 1: TỰ ĐỘNG TÍNH OFFSET ---
    PDF_OFFSET = find_optimal_offset(reader, df)
    
    # --- BƯỚC 2: QUÉT DỮ LIỆU ---
    df['Category'] = "Chưa phân loại"
    
    # Regex tìm dòng "Loại thuốc" hoặc "Nhóm dược lý"
    category_pattern = re.compile(r'(Loại thuốc|Nhóm dược lý|Nhóm thuốc)[:\.]\s*(.*)', re.IGNORECASE)

    print(f"🚀 Bắt đầu làm giàu dữ liệu cho {len(df)} loại thuốc (Có thể mất 5-10 phút)...")
    
    success_count = 0
    
    # Duyệt qua TOÀN BỘ danh sách thuốc
    for index, row in df.iterrows(): 
        page_num_book = int(row['PageNumber'])
        pdf_page_index = page_num_book + PDF_OFFSET

        # In tiến độ mỗi 500 thuốc để biết code còn chạy
        if index % 500 == 0:
            print(f"   ...Đang xử lý đến dòng {index}/{len(df)}")

        try:
            if 0 <= pdf_page_index < len(reader.pages):
                text = reader.pages[pdf_page_index].extract_text()
                
                # Tìm dòng Loại thuốc
                match = category_pattern.search(text)
                if match:
                    raw_cat = match.group(2)
                    # Lấy câu đầu tiên (ngắt bởi dấu chấm)
                    raw_cat = raw_cat.split('.')[0]
                    
                    # Làm sạch text ngay tại đây
                    clean_cat = clean_text(raw_cat)
                    
                    df.at[index, 'Category'] = clean_cat
                    success_count += 1
                    # print(f"✅ {row['DrugName']} -> {clean_cat}") # Bỏ comment nếu muốn xem chi tiết
        except Exception as e:
            pass

    # Lưu file
    df.to_csv(csv_output, index=False, encoding='utf-8')
    print("-" * 30)
    print(f"🎉 HOÀN TẤT! Đã tìm được thông tin cho {success_count} loại thuốc.")
    print(f"📂 File kết quả sạch đẹp tại: {csv_output}")

# --- CẤU HÌNH ---
# Lấy đường dẫn thư mục chứa script này
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(SCRIPT_DIR, "drug_index.csv")
PDF_FILE = os.path.join(SCRIPT_DIR, "duoc-thu-quoc-gia-viet-nam-2018.pdf")
OUTPUT_CSV = os.path.join(SCRIPT_DIR, "drug_database_rich.csv")

if __name__ == "__main__":
    enrich_drug_data(INPUT_CSV, PDF_FILE, OUTPUT_CSV)