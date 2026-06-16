import os
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
import pandas
from langchain.tools import tool
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


# Load file dữ liệu đã chuẩn hóa
try:
    df_laptop = pandas.read_csv('du_lieu_laptop_sach.csv')
except FileNotFoundError:
    print("LỖI: Không tìm thấy file 'du_lieu_laptop_sach.csv")
    exit()

# Load ChromaDB tìm kiếm ngữ nghĩa
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
vector_db = Chroma(persist_directory="./db_chinh_sach", embedding_function=embeddings)

print("Nạp dữ liệu thành công!")

# Luồng truy xuất cấu trúc
@tool
def tra_cuu_thong_so_laptop(lenh_query: str) -> str:
    """
    CÔNG CỤ NÀY RẤT QUAN TRỌNG. Hữu ích khi khách hàng hỏi về cấu hình, giá tiền, khối lượng, hoặc muốn lọc tìm laptop theo yêu cầu.
    
    Đầu vào (lenh_query) PHẢI LÀ MỘT CÂU LỆNH HỢP LỆ CỦA PANDAS DATAFRAME QUERY.
    Các cột hiện có và kiểu dữ liệu:
    - ten_may (chuỗi): Tên sản phẩm.
    - gia (số nguyên): Giá bán VNĐ (Ví dụ: 25000000).
    - cpu (chuỗi): Vi xử lý.
    - ram (số thực): Dung lượng RAM tính bằng GB (Ví dụ: 16.0, 32.0).
    - o_cung (số thực): Dung lượng ổ cứng tính bằng GB (Ví dụ: 512.0, 1024.0).
    - card (chuỗi): Card đồ họa.
    - m_hinh (chuỗi): Thông số màn hình.
    - khoi_luong (số thực): Nặng bao nhiêu kg (Ví dụ: 1.5).

    VÍ DỤ LỆNH QUERY CHUẨN: 
    "gia <= 25000000 and ram >= 16"
    "o_cung == 1024"
    "ten_may.str.contains('ThinkBook', case=False)"
    """
    try:
        # Chạy lệnh query do AI tự sinh ra
        ket_qua = df_laptop.query(lenh_query).sort_values(by="gia", ascending=False)
        if ket_qua.empty:
            return "Trong kho hiện tại không có mẫu laptop nào đáp ứng đúng yêu cầu này."
        # Trả về top 3 máy để tránh làm tràn bộ nhớ của LLM
        return ket_qua.head(3).to_markdown(index=False)
    except Exception as e:
        return f"Lỗi cú pháp nội bộ khi truy vấn Pandas: {e}. HÃY THỬ VIẾT LẠI LỆNH QUERY MỘT CÁCH ĐƠN GIẢN HƠN."

# Luồng truy xuất ngữ nghĩa  
@tool
def tra_cuu_chinh_sach(cau_hoi: str) -> str:
    """
    Hữu ích KHI VÀ CHỈ KHI khách hàng hỏi về các thông tin quy định chung như: 
    chính sách mua hàng, trả góp, vận chuyển, đổi trả, bảo hành, bảo mật thông tin.
    TUYỆT ĐỐI KHÔNG dùng công cụ này để tìm thông số kỹ thuật hay giá laptop.
    Đầu vào là nguyên văn câu hỏi của khách hàng.
    """
    ket_qua = vector_db.similarity_search(cau_hoi, k=1)
    if ket_qua:
        return ket_qua[0].page_content
    return "Không tìm thấy chính sách nào liên quan đến câu hỏi này trong hệ thống. Hãy kết nối đến nhân viên."

# Đóng gói bộ công cụ
list_cong_cu = [tra_cuu_thong_so_laptop, tra_cuu_chinh_sach]

print("Hệ thống đã sẵn sàng kết nối với Google Gemini!")

# Khởi tạo bộ não gemini và system prompt
load_dotenv(override=True)

# Gọi model gemini 2.5 flash
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, timeout=60)

# Prompt chuẩn theo kiến trúc 3 luồng
system_prompt = """
Bạn là một chuyên gia tư vấn laptop siêu đẳng của cửa hàng LaptopGame.
Nhiệm vụ của bạn là tư vấn cho khách hàng dựa trên 3 nguyên tắc tối thượng sau:

1. THÔNG SỐ & GIÁ CẢ (Luồng 1): Nếu khách hỏi tìm máy theo tầm giá, cấu hình, hoặc hỏi giá một máy cụ thể, BẮT BUỘC dùng công cụ `tra_cuu_thong_so_laptop`. Tuyệt đối không tự bịa giá.
2. CHÍNH SÁCH (Luồng 2): Nếu khách hỏi về mua hàng, trả góp, vận chuyển, đổi trả, bảo hành, bảo mật thông tin, BẮT BUỘC dùng công cụ `tra_cuu_chinh_sach`.
3. TƯ VẤN CHUYÊN SÂU (Luồng 3): Nếu khách hỏi các câu không có trong dữ liệu (ví dụ: tư vấn máy cho ngành học, hiệu năng chip, thời lượng pin), hãy TỰ DO dùng kiến thức công nghệ uyên bác của bạn để giải thích cặn kẽ, sau đó có thể khéo léo dùng công cụ tìm máy để gợi ý sản phẩm phù hợp.

Hãy trả lời bằng giọng điệu thân thiện, chuyên nghiệp, format chữ dễ đọc. Không được để lộ tên các công cụ cho khách hàng biết.
"""

#  Tạo bộ khung giao tiếp cho agent
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"), 
])

# Lắp ráp agent
agent = create_tool_calling_agent(llm, list_cong_cu, prompt)
# Tham số verbose=True sẽ in ra màn hình toàn bộ suy nghĩ của AI
agent_executor = AgentExecutor(
    agent=agent, 
    tools=list_cong_cu, 
    verbose=False,
    return_intermediate_steps=True # Thêm dòng này để AI khai báo tài liệu nó đã đọc
)

# # Test luồng 1 (Tìm Excel)
# print("TEST 1: Khách hỏi mua máy")
# agent_executor.invoke({"input": "Mình có 20 triệu, muốn tìm máy RAM 16GB. Shop có mẫu nào không?"})
# time.sleep(20)

# # Test Luồng 2 (Tìm text)
# print("\nTEST 2: Khách hỏi chính sách")
# agent_executor.invoke({"input": "Shop có cho mua trả góp online không, mình ở xa?"})
# time.sleep(20)

# # Test Luồng 3 (Kiến thức nền + Công cụ)
# print("\nTEST 3: Khách hỏi tư vấn chuyên sâu")
# agent_executor.invoke({"input": "Sinh viên học Lập trình AI thì nên mua máy cấu hình như nào? Shop có mẫu nào phù hợp không?"})

# tao csdl test va embedding
# danh gia response, do toc do phan hoi va kiem tra chat luong response
# giao dien web va phan hoi nguoi dung