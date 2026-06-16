import pandas as pd
import os
import time
from bai_hoc_agent import agent_executor

FILE_DE_THI = 'golden_dataset.csv'
FILE_KET_QUA = 'du_lieu_san_sang_ragas.csv'

# Đọc bộ đề thi
try:
    df_test = pd.read_csv(FILE_DE_THI)
except FileNotFoundError:
    print(f"Không tìm thấy {FILE_DE_THI}!")
    exit()

# Kiểm tra tiến độ cũ
danh_sach_ket_qua = []
cau_da_lam = 0

if os.path.exists(FILE_KET_QUA):
    try:
        df_cu = pd.read_csv(FILE_KET_QUA)
        danh_sach_ket_qua = df_cu.to_dict('records')
        cau_da_lam = len(danh_sach_ket_qua)
        print(f"Tìm thấy tiến độ cũ: Đã làm xong {cau_da_lam}/{len(df_test)} câu.")
    except pd.errors.EmptyDataError:
        # Bẫy lỗi: Nếu file tồn tại nhưng rỗng thì coi như chưa làm gì
        print("File kết quả có tồn tại nhưng bị rỗng (0KB). Hệ thống sẽ bắt đầu làm lại từ đầu.")
        cau_da_lam = 0

# Làm tiếp những câu chưa làm
for index, row in df_test.iterrows():
    if index < cau_da_lam:
        continue # Bỏ qua câu đã làm thành công
        
    cau_hoi = row['question']
    dap_an_chuan = row['ground_truth']
    print(f"\n[{index + 1}/{len(df_test)}] Đang xử lý: {cau_hoi}")
    
    try:
        # Gọi Agent làm bài
        response = agent_executor.invoke({
            "input": cau_hoi, 
            "chat_history": []
        })
        
        # Lấy câu trả lời
        raw_out = response.get("output", "")
        ai_tra_loi = ""
        if isinstance(raw_out, list):
            for p in raw_out:
                if isinstance(p, str): ai_tra_loi += p
                elif isinstance(p, dict) and 'text' in p: ai_tra_loi += p['text']
        else:
            ai_tra_loi = str(raw_out)
            
        # Lấy bằng chứng (Giấy nháp)
        bang_chung = []
        nhat_ky = response.get("intermediate_steps", [])
        for action, observation in nhat_ky:
            bang_chung.append(str(observation))
        
        if not bang_chung:
            bang_chung = ["Không sử dụng tài liệu nội bộ"]
            
        # Lưu vào danh sách
        danh_sach_ket_qua.append({
            "question": cau_hoi, 
            "ground_truth": dap_an_chuan, 
            "answer": ai_tra_loi, 
            "contexts": bang_chung 
        })
        
        # GHI LẠI NGAY VÀO FILE SAU MỖI CÂU (Chống mất dữ liệu)
        pd.DataFrame(danh_sach_ket_qua).to_csv(FILE_KET_QUA, index=False, encoding='utf-8-sig')
        print("-> Đã lưu câu này!")
        time.sleep(30)
        
    except Exception as e:
        thong_bao_loi = str(e)
        print(f"DỪNG CUỘC CHƠI: {thong_bao_loi}")
        if "429" in thong_bao_loi:
            print("\nBẠN ĐÃ HẾT LƯỢT QUOTA CỦA KEY NÀY TRONG HÔM NAY!")
        break 

print(f"Cập nhật: Đã hoàn thành {len(danh_sach_ket_qua)}/{len(df_test)} câu.")