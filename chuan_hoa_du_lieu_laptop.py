import pandas
import re
import unidecode

# Đọc file raw
df = pandas.read_csv('du_lieu_laptop_raw.csv')

# Chuẩn hóa tên cột (Viết thường, không dấu, dùng gạch dưới)
df.columns = [unidecode.unidecode(col).lower().replace(".", "_").replace(" ", "_") for col in df.columns]

# Chuẩn hóa giá: kiểu int, xóa dấu chấm và kí tự tiền, ép kiểu
df['gia'] = df['gia'].astype(str).str.replace('.', '').str.replace('₫', '')
df['gia'] = pandas.to_numeric(df['gia'], errors='coerce').fillna(0).astype(int)

# Chuẩn hóa ram: kiểu float, dùng  regex \d+ để bắt con số đầu tiên trong chuỗi
df['ram'] = df['ram'].astype(str).str.extract(r'(\d+)').astype(float)

# Chuẩn hóa ổ cứng: quy hết về GB, kiểu float
def clean_storage(text):
    text = str(text).upper()
    match = re.search(r'(\d+)', text)
    if not match:
        return 0
    val = float(match.group(1))
    if 'TB' in text:
        val = val * 1024
    return val
df['o_cung'] = df['o_cung'].apply(clean_storage)

# Chuẩn hóa khối lượng: kiểu float, xóa ký tự thừa, thay phẩy bằng chấm
df['khoi_luong'] = df['khoi_luong'].astype(str).str.replace('kg', '', flags=re.IGNORECASE)\
                                                .str.replace('~', '')\
                                                .str.replace(' ', '')\
                                                .str.replace(',', '.')\
                                                .str.replace('"', '')
df['khoi_luong'] = pandas.to_numeric(df['khoi_luong'], errors='coerce')

# Lưu ra file mới sẵn sàng cho AI
df.to_csv('du_lieu_laptop_sach.csv', index=False, encoding='utf-8-sig')
print("Dọn dẹp thành công! AI có thể soi nội dung.")