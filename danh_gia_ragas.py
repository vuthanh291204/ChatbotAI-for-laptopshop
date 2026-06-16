import pandas as pd
import ast
from dotenv import load_dotenv
from datasets import Dataset

from ragas import evaluate
from ragas.run_config import RunConfig

from ragas.metrics import Faithfulness, AnswerRelevancy, ContextPrecision

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

# Sửa thư viện gốc của GROQ để khắc phục lỗi 400 BadRequest (n=3)
from groq.resources.chat.completions import AsyncCompletions, Completions

original_acreate = AsyncCompletions.create
async def patched_acreate(self, *args, **kwargs):
    kwargs.pop("n", None) 
    return await original_acreate(self, *args, **kwargs)
AsyncCompletions.create = patched_acreate

original_create = Completions.create
def patched_create(self, *args, **kwargs):
    kwargs.pop("n", None) 
    return original_create(self, *args, **kwargs)
Completions.create = patched_create

load_dotenv(override=True)

print("1. Đang đọc và giải mã dữ liệu...")
df = pd.read_csv('du_lieu_san_sang_ragas.csv')
df['contexts'] = df['contexts'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
dataset_thi_sinh = Dataset.from_pandas(df[['question', 'ground_truth', 'answer', 'contexts']])

print("2. Gọi model Llama 3 (Groq) để chấm điểm chatbot...")
giam_khao_llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0,
    timeout=180, 
    max_retries=3
)
mo_hinh_embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

print("3. BẮT ĐẦU CHẤM ĐIỂM (Chạy tuần tự 100% mượt mà)...")
try:
    ket_qua = evaluate(
        dataset=dataset_thi_sinh,
        # Sử dụng class viết hoa và có ngoặc tròn
        metrics=[Faithfulness(), AnswerRelevancy(), ContextPrecision()],
        llm=giam_khao_llm,
        embeddings=mo_hinh_embedding,
        raise_exceptions=False,
        # Chạy tuần tự, chống nghẽn mạng
        run_config=RunConfig(max_workers=1) 
    )

    print("\nBẢNG ĐIỂM TỔNG KẾT:")
    print(ket_qua)

    with open("diem_tong_ket_ragas.txt", "w", encoding="utf-8") as f:
        f.write("📊 BẢNG ĐIỂM TỔNG KẾT RAGAS:\n")
        f.write(str(ket_qua))
    print("Đã lưu bảng điểm tổng kết vào file: diem_tong_ket_ragas.txt")

    df_bao_cao = ket_qua.to_pandas()
    df_bao_cao.to_csv("bao_cao_ragas.csv", index=False, encoding='utf-8-sig')
    print("Đã lưu kết quả chi tiết!")

except Exception as e:
    print(f"\nLỗi: {e}")