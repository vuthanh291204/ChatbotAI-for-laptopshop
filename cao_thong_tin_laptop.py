import requests
from bs4 import BeautifulSoup
import pandas 
import time

# Link các web chứa danh sách laptop
list_url_laptop = [
    "https://laptopgame.vn/laptop-gaming",
    "https://laptopgame.vn/laptop-mong-nhe",
    "https://laptopgame.vn/laptop-gia-re"
]

# Đóng giả làm người thật, tránh bị web chặn bot
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

list_laptop = []

# Vòng lặp tự động chạy qua từng đường link
for url in list_url_laptop:
    print(f"Đang cào dữ liệu từ: {url}...")
    try:
        response = requests.get(url, headers=headers)
        
        # Kiểm tra xem web có cho phép không
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            list_ten = soup.find_all('a', class_='line_2')
            list_gia = soup.find_all('div', class_='item-price')
            list_thong_so = soup.find_all('div', class_='rte prd_sum')
            for i in range(len(list_ten)):
                # Bọc try-except ở từng máy. Máy nào lỗi thì bỏ qua máy đó, không làm chết cả trang
                try:
                    ten_may = list_ten[i].text.strip()
            
                    # Kiểm tra xem list_gia có bị ngắn hơn list_ten không, tránh lỗi out of range
                    gia_may = list_gia[i].find('span').text.strip() if i < len(list_gia) and list_gia[i].find('span') else "Liên hệ"
                    
                    data_laptop = {
                        "TÊN MÁY": ten_may,
                        "GIÁ": gia_may
                    }
                    
                    # Xử lý thông số an toàn
                    if i < len(list_thong_so):
                        the_p = list_thong_so[i].find('p')
                        if the_p:
                            list_dong = list(the_p.stripped_strings)
                            for dong in list_dong:
                                if ":" in dong:
                                    key, value = dong.split(":", 1)
                                    # CHUẨN HÓA CỘT: Xóa khoảng trắng và VIẾT HOA toàn bộ (Ram -> RAM)
                                    key_chuan = key.strip().upper()
                                    data_laptop[key_chuan] = value.strip()
                                    
                    list_laptop.append(data_laptop)
                except Exception as e:
                    print(f"Bỏ qua máy thứ {i+1} do cấu trúc lỗi: {e}")
            print(f"Đã gom xong dữ liệu laptop từ: {url}")
        else:
            print(f"Bị chặn rồi! Mã lỗi: {response.status_code}")
        time.sleep(2)
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")

# Dùng Pandas để xuất ra file CSV (Excel)
df = pandas.DataFrame(list_laptop)
# utf-8-sig giúp file CSV không bị lỗi font tiếng Việt khi mở bằng Excel
df.to_csv('du_lieu_laptop_raw.csv', index=False, encoding='utf-8-sig') 