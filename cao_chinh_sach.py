import requests
from bs4 import BeautifulSoup
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

list_url_chinh_sach = [
    "https://laptopgame.vn/huong-dan-mua-hang-tu-xa",
    "https://laptopgame.vn/mua-laptop-tra-gop",
    "https://laptopgame.vn/che-do-van-chuyen-va-thanh-toan",
    "https://laptopgame.vn/chinh-sach-doi-tra-hang",
    "https://laptopgame.vn/dieu-kien-chinh-sach-bao-hanh",
    "https://laptopgame.vn/chinh-sach-bao-mat"
]

for url in list_url_chinh_sach:
    print(f"Đang kết nối tới: {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            noi_dung = soup.find('div', class_='com_info')
            cac_the = noi_dung.find_all(['h1', 'p', 'li'])
            with open('du_lieu_chinh_sach.txt', 'a', encoding='utf-8') as f:
                f.write(f"\n\n--- Dữ liệu từ: {url} ---\n\n")
                for the in cac_the:
                    text = the.get_text(separator=" ", strip=True)
                    if len(text) > 5:
                        f.write(f"{text}\n")
            print(f"Đã gom xong dữ liệu laptop từ: {url}")
        else:
            print(f"Bị chặn rồi! Mã lỗi: {response.status_code}")
        time.sleep(2)
    except requests.exceptions.Timeout:
        print("Lỗi Timeout: Máy chủ web phản hồi quá chậm, tự động bỏ qua!")
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")