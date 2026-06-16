import streamlit as st
import time
from langchain_core.messages import HumanMessage, AIMessage
from bai_hoc_agent import agent_executor, df_laptop

# Cấu hình giao diện 
st.set_page_config(page_title="LaptopGame - Hệ thống cửa hàng", layout="wide")

# Ép nút chat bo tròn, nằm góc dưới phải và hộp chat bung lên trên
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .price { color: #e63946; font-size: 22px; font-weight: bold; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Ghim góc phải */
    div[data-testid="stPopover"] {
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        width: auto !important;
        z-index: 9999 !important;
    }

    /* Nhắm thẳng vào button bên trong, bất kể nó nằm ở lớp nào */
    div[data-testid="stPopover"] button {
        border-radius: 50% !important;
        width: 65px !important;
        height: 65px !important;
        background-color: #ff0000 !important; /* Ép màu đỏ nổi bật */
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
            
    /* Phóng to icon AI */
    div[data-testid="stPopover"] button p {
        font-size: 35px !important;
        margin: 0 !important;
    }

    /* Khống chế hộp chat bung lên, canh lề phải */
    div[data-testid="stPopoverBody"] {
        position: fixed !important;
        bottom: 100px !important; /* Cánh nút bấm một khoảng an toàn */
        right: 30px !important;   /* Thẳng hàng với nút bấm */
        top: auto !important;     
        left: auto !important;    
        transform: none !important; /* Tắt tự động tính toán vị trí của Streamlit */
        width: 380px !important; 
        height: 550px !important;
        border-radius: 15px !important;
        padding: 15px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)


# Header, thanh tìm kiếm, hotline
col_logo, col_search, col_hotline = st.columns([1, 2, 1])

with col_logo:
    st.header("💻 LaptopGame")

with col_search:
    search_keyword = st.text_input("", placeholder="🔍 Nhập tên laptop bạn muốn tìm...")

with col_hotline:
    st.markdown("""
        <div style="text-align: right; padding-top: 10px;">
            <span style="font-size: 18px; font-weight: bold; color: #007bff;">📞 Hotline: 0386.084.568</span><br>
            <span style="font-size: 14px; color: gray;">Hỗ trợ 24/7</span>
        </div>
    """, unsafe_allow_html=True)

# Menu ngang
menu_home, menu_gaming, menu_ultra, menu_old, menu_acc, menu_policy = st.tabs([
    "🏠 Trang chủ", "🎮 Laptop Gaming", "💼 Ultrabook", "♻️ Laptop Cũ", "🖱️ Phụ kiện", "📜 Chính sách"
])

# Hiển thị sản phẩm mục trang chủ
with menu_home:
    st.subheader("🔥 Sản phẩm nổi bật dành cho bạn")
    if search_keyword:
        df_display = df_laptop[df_laptop['ten_may'].str.contains(search_keyword, case=False)]
    else:
        df_display = df_laptop.head(8) 

    if df_display.empty:
        st.warning("Không tìm thấy laptop nào phù hợp với từ khóa của bạn.")
    else:
        rows = len(df_display) // 4 + (1 if len(df_display) % 4 > 0 else 0)
        for r in range(rows):
            cols = st.columns(4)
            for c in range(4):
                idx = r * 4 + c
                if idx < len(df_display):
                    row = df_display.iloc[idx]
                    with cols[c]:
                        with st.container(border=True):
                            st.image("https://img.icons8.com/fluency/200/laptop.png", width=120)
                            st.write(f"**{row['ten_may']}**")
                            st.caption(f"⚙️ {row['cpu']} | RAM {row['ram']}GB | SSD {row['o_cung']}GB | Card {row['card']}")
                            st.markdown(f"<span class='price'>{row['gia']:,} đ</span>", unsafe_allow_html=True)
                            st.button("Xem chi tiết", key=f"view_{idx}", use_container_width=True)

with menu_policy:
    st.info("Các chính sách mua hàng, bảo hành, đổi trả, trả góp, vận chuyển và bảo mật thông tin được niêm yết tại đây.")


# AI agent chat
# Dùng biểu tượng Robot thay cho chữ để nút có dạng hình tròn chuẩn
with st.popover("🤖"):
    st.markdown("#### 💬 LaptopGame AI")
    st.caption("Trợ lý ảo thông minh sẵn sàng hỗ trợ!")
    st.divider()
    
    # Lịch sử chat của phiên đó
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Khung chứa nội dung chat để thanh nhập liệu luôn ở đáy
    chat_container = st.container(height=320)

    # Hiển thị nội dung chat
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Nhận câu hỏi
    if user_query := st.chat_input("Hỏi về laptop hoặc chính sách..."):
        # Lưu lại, hiển thị câu hỏi
        st.session_state.messages.append({"role": "user", "content": user_query})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_query)

        # Tạo lịch sử chat để gửi cho LLM giữ ngữ cảnh
        history = []
        for m in st.session_state.messages[:-1]: 
            if m["role"] == "user":
                history.append(HumanMessage(content=m["content"]))
            else:
                history.append(AIMessage(content=m["content"]))

        # Hiển thị câu trả lời, thời gian phản hồi, đánh giá của người dùng
        with chat_container:
            with st.chat_message("assistant"):
                start_t = time.time()
                try:
                    # Gọi LLM lấy câu trả lời
                    response = agent_executor.invoke({
                        "input": user_query,
                        "chat_history": history 
                    })
                    
                    # Làm sạch câu trả lời
                    raw_out = response.get("output", "")
                    clean_answer = ""
                    if isinstance(raw_out, list):
                        for p in raw_out:
                            if isinstance(p, str): clean_answer += p
                            elif isinstance(p, dict) and 'text' in p: clean_answer += p['text']
                    else:
                        clean_answer = str(raw_out)
                        
                except Exception as e:
                    clean_answer = f"⚠️ Oops! Hệ thống gặp sự cố. Vui lòng thử lại sau!"
                
                st.markdown(clean_answer)
                st.caption(f"⏱️ Phản hồi trong: {time.time() - start_t:.2f}s")
                
                c1, c2 = st.columns(2)
                with c1: st.button("👍", key=f"l_{time.time()}")
                with c2: st.button("👎", key=f"d_{time.time()}")

        # Lưu lại câu trả lời
        st.session_state.messages.append({"role": "assistant", "content": clean_answer})