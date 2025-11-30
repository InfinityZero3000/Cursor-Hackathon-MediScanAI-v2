import pandas as pd
from pypdf import PdfReader
import re
import os

def find_optimal_offset(pdf_reader, csv_df):
    """
    Hàm tự động tìm độ lệch trang (Offset) bằng cách dò thử một loại thuốc.
    Chọn thuốc 'Meloxicam' (thường nằm ở giữa sách) để test.
    """
    # Lấy mẫu thuốc Meloxicam (Trong CSV trang 940)
    # Bạn có thể đổi tên thuốc khác nếu muốn test
    sample_drug = csv_df[csv_df['DrugName'] == 'Kukjemefen'].iloc[0] 
    
    target_name = "Meloxicam" # Hoạt chất chính
    csv_page = int(sample_drug['PageNumber'])
    
    print(f"🕵️ Đang dò tìm vị trí thực tế của thuốc '{target_name}' (CSV báo trang {csv_page})...")
    
    # Quét trong phạm vi +/- 50 trang xung quanh số trang trong CSV
    # Vì file PDF thường lệch do trang bìa, mục lục
    scan_range = range(csv_page - 20, csv_page + 50)
    
    for pdf_idx in scan_range:
        try:
            text = pdf_reader.pages[pdf_idx].extract_text()
            # Tìm dòng tiêu đề thuốc (thường viết hoa hoặc đứng đầu)
            if re.search(f"{target_name}", text, re.IGNORECASE):
                # Kiểm tra kỹ hơn: Dòng đó phải ngắn (tiêu đề)
                lines = text.split('\n')
                for line in lines[:5]: # Chỉ check 5 dòng đầu trang
                    if target_name.upper() in line.upper():
                        found_offset = pdf_idx - csv_page
                        print(f"✅ TÌM THẤY! '{target_name}' ở trang PDF {pdf_idx}.")
                        print(f"🎯 ĐỘ LỆCH (OFFSET) CHUẨN LÀ: {found_offset}")
                        return found_offset
        except:
            continue
            
    print("⚠️ Không dò thấy tự động. Sẽ dùng offset mặc định = 0.")
    return 0

def enrich_drug_data(csv_input, pdf_path, csv_output):
    print("⏳ Đang nạp dữ liệu...")
    df = pd.read_csv(csv_input)
    reader = PdfReader(pdf_path)
    
    # --- BƯỚC 1: TỰ ĐỘNG TÍNH OFFSET ---
    # Thay vì điền tay, code sẽ tự đi tìm
    PDF_OFFSET = find_optimal_offset(reader, df)
    
    # --- BƯỚC 2: QUÉT DỮ LIỆU ---
    df['Category'] = "Chưa phân loại"  # Cột mới
    
    # Regex tìm dòng "Loại thuốc" hoặc "Nhóm dược lý"
    category_pattern = re.compile(r'(Loại thuốc|Nhóm dược lý|Nhóm thuốc)[:\.]\s*(.*)', re.IGNORECASE)

    print(f"🚀 Bắt đầu làm giàu dữ liệu với Offset = {PDF_OFFSET}...")
    
    success_count = 0
    
    # Demo: Chạy thử 100 thuốc đầu tiên để tiết kiệm thời gian
    # Khi chạy thật bạn xóa [0:100] đi để chạy hết
    for index, row in df.iloc[0:100].iterrows(): 
        page_num_book = int(row['PageNumber'])
        
        # Công thức: Trang PDF thực = Trang sách + Offset
        # (pypdf tính từ 0 nên đôi khi cần -1 hoặc không, tùy vào kết quả dò ở trên)
        pdf_page_index = page_num_book + PDF_OFFSET

        try:
            if 0 <= pdf_page_index < len(reader.pages):
                text = reader.pages[pdf_page_index].extract_text()
                
                # Tìm dòng Loại thuốc
                match = category_pattern.search(text)
                if match:
                    category = match.group(2).strip().split('.')[0] # Lấy câu đầu
                    df.at[index, 'Category'] = category
                    success_count += 1
                    print(f"✅ [{row['DrugName']}] -> {category}")
        except Exception as e:
            pass

    # Lưu file
    df.to_csv(csv_output, index=False, encoding='utf-8')
    print(f"🎉 Hoàn tất! Đã tìm được thông tin cho {success_count} loại thuốc.")
    print(f"📂 File kết quả: {csv_output}")

# --- CHẠY ---
if __name__ == "__main__":
    # Lấy đường dẫn thư mục chứa script này
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_input = os.path.join(SCRIPT_DIR, "drug_index.csv")
    pdf_path = os.path.join(SCRIPT_DIR, "duoc-thu-quoc-gia-viet-nam-2018.pdf")
    csv_output = os.path.join(SCRIPT_DIR, "drug_database_rich.csv")
    
    enrich_drug_data(csv_input, pdf_path, csv_output)