import pandas as pd

def refine_prescription_status(csv_path, output_path):
    print("🔧 Đang tinh chỉnh trạng thái thuốc kê đơn...")
    df = pd.read_csv(csv_path)
    
    # Danh sách từ khóa NHÓM THUỐC nguy hiểm/cần kê đơn
    # Nếu Category chứa từ này -> Đánh dấu là Rx ngay
    danger_keywords = [
        "kháng sinh", "antibiotic", "cephalosporin", "penicilin", "quinolon", "aminoglycosid",
        "tiêm", "injection", "truyền", "infusion", # Thuốc tiêm/truyền luôn cần bác sĩ
        "ung thư", "cancer", "hóa trị",
        "tim mạch", "huyết áp", "loạn nhịp",
        "thần kinh", "loạn thần", "trầm cảm", "ngủ", "an thần",
        "corticoid", "steroid", "hormon",
        "đái tháo đường", "insulin",
        "virus", "retrovirus", "hiv"
    ]
    
    count_fixed = 0
    
    for index, row in df.iterrows():
        # Nếu đã là True rồi thì bỏ qua
        if row['Is_Prescription'] == True:
            continue
            
        category = str(row['Category']).lower()
        drug_name = str(row['DrugName']).lower()
        
        # Kiểm tra từ khóa trong Category
        is_danger = False
        for kw in danger_keywords:
            if kw in category:
                is_danger = True
                break
        
        # Nếu tìm thấy từ khóa nguy hiểm
        if is_danger:
            df.at[index, 'Is_Prescription'] = True
            count_fixed += 1
            # print(f"Đã sửa: {row['DrugName']} ({row['Category']}) -> Rx")

    print(f"✅ Đã sửa lại trạng thái cho {count_fixed} loại thuốc dựa trên Nhóm thuốc.")
    
    # Tính lại thống kê
    total = len(df)
    rx_true = len(df[df['Is_Prescription'] == True])
    print(f"📊 Thống kê mới:")
    print(f" - Tổng: {total}")
    print(f" - Thuốc kê đơn/Đặc trị: {rx_true} ({rx_true/total*100:.2f}%)")
    print(f" - Thuốc OTC/An toàn: {total - rx_true} ({(total - rx_true)/total*100:.2f}%)")
    
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"📂 Đã lưu file chuẩn tại: {output_path}")

# --- CHẠY ---
if __name__ == "__main__":
    refine_prescription_status("drug_database_final.csv", "drug_database_refined.csv")