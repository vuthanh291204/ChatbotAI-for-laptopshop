from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Đọc file chính cách đã cào
with open('du_lieu_chinh_sach.txt', 'r', encoding='utf-8') as f:
    noi_dung_goc = f.read()

# Cắt bài viết theo dấu hiệu phân trang
list_chinh_sach = noi_dung_goc.split("--- Dữ liệu từ:")

list_docs = []
for bai in list_chinh_sach:
    bai = bai.strip()
    # Lọc bỏ các đoạn rác
    if len(bai) > 100:
        # Mỗi chunk là nội dung của 1 chính sách
        doc = Document(page_content=bai)
        list_docs.append(doc)

print(f"Đã cắt thành {len(list_docs)} bài chính sách.")

# Nhúng vào Vector DB
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
vector_db = Chroma.from_documents(
    documents=list_docs,
    embedding=embeddings,
    persist_directory="./db_chinh_sach"
)

# print(f"Tổng số ký tự của bài gốc: {len(noi_dung_goc)} ký tự")

# # Khởi tạo hàm cắt đoạn của LangChain
# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size = 800,     # Mỗi đoạn dài tối đa 800 ký tự
#     chunk_overlap = 80,   # Đoạn sau sẽ lặp lại 80 ký tự cuối của đoạn trước
    
#     # LangChain rất thông minh, nó sẽ ưu tiên cắt ở các mốc này để không làm gãy câu
#     separators=["\n\n", "\n", ". ", " ", ""] 
# )

# # Tiến hành cắt nhỏ văn bản
# list_chunks = text_splitter.split_text(noi_dung_goc)

# print(f"Đã băm thành: {len(list_chunks)} đoạn nhỏ hoàn hảo.\n")

# # Khởi tạo mô hình AI dịch chữ thành số (Embedding Model)
# print("Đang tải mô hình Embedding...")
# # Mô hình đa ngôn ngữ siêu nhẹ và nhanh, rất hợp với tiếng Việt
# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# # Nhét các đoạn văn vào Vector Database (Chroma)
# print("Đang nhúng dữ liệu vào Vector Database. Vui lòng đợi...")
# vector_db = Chroma.from_texts(
#     texts=list_chunks,
#     embedding=embeddings,
#     persist_directory="./db_chinh_sach"  # Lưu DB ra thư mục này để lần sau không phải nhúng lại từ đầu
# )
# print("Tuyệt vời! Đã nạp xong bộ não cho AI.\n")

# Test thử trí thông minh bot (semantic search)
# cau_hoi = "Mua máy tính có được trả góp không? Thủ tục thế nào?"
# ket_qua_tim_kiem = vector_db.similarity_search(cau_hoi, k=1)

# print("\nAI đã mò vào Database và lấy ra được tài liệu này để chuẩn bị trả lời:")
# print("-" * 50)
# print(ket_qua_tim_kiem[0].page_content)
# for i, ket_qua in enumerate(ket_qua_tim_kiem):
#     print(f"\n[Tài liệu top {i+1}]:")
#     print(ket_qua.page_content)