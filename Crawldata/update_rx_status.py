import pandas as pd
from pypdf import PdfReader
import re
import os

def find_optimal_offset(pdf_reader, csv_df):
    """
    Hàm tự động tìm độ lệch trang (Offset).
    Dùng lại logic cũ vì nó đã chứng minh hiệu quả.
    """
    sample_row = csv_df[csv_df['DrugName'] == 'Kukjemefen']
    if sample_row.empty: return -1

    sample_drug = sample_row.iloc[0]
    target_name = "Meloxicam"
    csv_page = int(sample_drug['PageNumber'])
    
    print(f"🕵️ Đang dò Offset trang dựa trên thuốc '{target_name}'...")
    
    scan_range = range(csv_page - 20, csv_page + 20)
    for pdf_idx in scan_range:
        try:
            if pdf_idx < 0 or pdf_idx >= len(pdf_reader.pages): continue
            text = pdf_reader.pages[pdf_idx].extract_text()
            if re.search(f"{target_name}", text, re.IGNORECASE):
                lines = text.split('\n')
                for line in lines[:10]:
                    if target_name.upper() in line.upper():
                        return pdf_idx - csv_page
        except: continue
    return -1

def check_prescription_status(text):
    """
    Hàm kiểm tra xem thuốc có phải thuốc kê đơn/đặc trị không.
    Trả về: True (Là thuốc kê đơn/nguy hiểm), False (Thuốc thường)
    """
    if not text: return False
    text_lower = text.lower()
    
    # DANH SÁCH TỪ KHÓA CỜ ĐỎ (RED FLAGS)
    keywords = [
        "thuốc bán theo đơn", 
        "thuốc kê đơn",
        "thuốc này chỉ dùng theo đơn của thầy thuốc",
        "chỉ dùng theo sự kê đơn",
        "rx" # Ký hiệu quốc tế
    ]
    
    for kw in keywords:
        if kw in text_lower:
            return True
    return False

def update_safety_data(csv_input, pdf_path, csv_output):
    print("⏳ Đang nạp dữ liệu...")
    df = pd.read_csv(csv_input)
    reader = PdfReader(pdf_path)
    
    # 1. Tự động tính Offset
    PDF_OFFSET = find_optimal_offset(reader, df)
    print(f"🎯 Offset xác định: {PDF_OFFSET}")
    
    # 2. Tạo cột mới
    # Mặc định là False (An toàn), nếu tìm thấy từ khóa sẽ bật lên True
    df['Is_Prescription'] = False 
    
    print(f"🚀 Bắt đầu quét an toàn cho {len(df)} loại thuốc...")
    
    prescription_count = 0
    
    for index, row in df.iterrows():
        page_num_book = int(row['PageNumber'])
        pdf_page_index = page_num_book + PDF_OFFSET

        if index % 1000 == 0:
            print(f"   ...Đã quét {index}/{len(df)} thuốc")

        try:
            if 0 <= pdf_page_index < len(reader.pages):
                # Đọc trang hiện tại
                text = reader.pages[pdf_page_index].extract_text()
                
                # Đọc thêm trang tiếp theo (vì dòng 'Thuốc bán theo đơn' có thể trôi sang trang sau)
                if pdf_page_index + 1 < len(reader.pages):
                    text += "\n" + reader.pages[pdf_page_index + 1].extract_text()
                
                # Kiểm tra
                if check_prescription_status(text):
                    df.at[index, 'Is_Prescription'] = True
                    prescription_count += 1
                    # print(f"⚠️ Cảnh báo: {row['DrugName']} là thuốc kê đơn") # Bật để debug
                    
        except Exception as e:
            pass

    # Lưu file
    df.to_csv(csv_output, index=False, encoding='utf-8')
    print("-" * 30)
    print(f"🎉 HOÀN TẤT QUÉT AN TOÀN!")
    print(f"🔴 Phát hiện: {prescription_count} thuốc kê đơn/đặc trị (Đã đánh dấu TRUE).")
    print(f"🟢 Còn lại: {len(df) - prescription_count} thuốc OTC/Thông thường.")
    print(f"📂 File Database cuối cùng: {csv_output}")

# --- CẤU HÌNH ---
# Lấy đường dẫn thư mục chứa script này
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(SCRIPT_DIR, "drug_database_rich.csv") # File kết quả của bước trước
PDF_FILE = os.path.join(SCRIPT_DIR, "duoc-thu-quoc-gia-viet-nam-2018.pdf")
OUTPUT_CSV = os.path.join(SCRIPT_DIR, "drug_database_final.csv") # File Final để nạp vào App

if __name__ == "__main__":
    update_safety_data(INPUT_CSV, PDF_FILE, OUTPUT_CSV)