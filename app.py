import streamlit as st
import sqlite3
import pandas as pd
import hashlib
from datetime import datetime
import io
import re

# Cấu hình trang
st.set_page_config(
    page_title="Góp ý Văn kiện Đại hội Đoàn TCTHK",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS cho mobile-friendly
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .stTextArea > div > div > textarea {
        font-size: 16px;
        min-height: 150px;
    }
    .stSelectbox > div > div > select {
        font-size: 16px;
    }
    .stButton > button {
        width: 100%;
        height: 50px;
        font-size: 18px;
        font-weight: bold;
    }
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    .header-title {
        text-align: center;
        color: #1f77b4;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
        text-align: center;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        color: #721c24;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo database
def init_database():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    
    # Tạo bảng góp ý
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ho_ten TEXT NOT NULL,
            chi_doan TEXT NOT NULL,
            y_kien TEXT NOT NULL,
            thoi_gian TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tạo bảng admin
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Thêm tài khoản admin mặc định
    admin_password = hashlib.sha256("Admin@123".encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO admin_users (username, password_hash)
        VALUES (?, ?)
    ''', ("Admin", admin_password))
    
    conn.commit()
    conn.close()

# Lưu góp ý vào database
def save_feedback(ho_ten, chi_doan, y_kien):
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO feedback (ho_ten, chi_doan, y_kien)
        VALUES (?, ?, ?)
    ''', (ho_ten, chi_doan, y_kien))
    conn.commit()
    conn.close()

# Lấy danh sách góp ý
def get_all_feedback():
    conn = sqlite3.connect('feedback.db')
    df = pd.read_sql_query('''
        SELECT id, ho_ten as "Họ và Tên", 
               chi_doan as "Chi Đoàn", 
               y_kien as "Ý kiến góp ý", 
               thoi_gian as "Thời gian"
        FROM feedback 
        ORDER BY thoi_gian DESC
    ''', conn)
    conn.close()
    return df

# Xác thực admin
def verify_admin(username, password):
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute('''
        SELECT id FROM admin_users 
        WHERE username = ? AND password_hash = ?
    ''', (username, password_hash))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Đếm số từ
def count_words(text):
    if not text:
        return 0
    words = re.findall(r'\S+', text.strip())
    return len(words)

# Danh sách Chi Đoàn
CHI_DOAN_LIST = [
    "Chi Đoàn A1", "Chi Đoàn A2", "Chi Đoàn A3", "Chi Đoàn A4",
    "Chi Đoàn B1", "Chi Đoàn B2", "Chi Đoàn B3", "Chi Đoàn B4",
    "Chi Đoàn C1", "Chi Đoàn C2", "Chi Đoàn C3", "Chi Đoàn C4",
    "Chi Đoàn D1", "Chi Đoàn D2", "Chi Đoàn D3", "Chi Đoàn D4",
    "Khác"
]

def main():
    # Khởi tạo database
    init_database()
    
    # Initialize session state
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False
    if 'show_admin_login' not in st.session_state:
        st.session_state.show_admin_login = False

    # Header
    st.markdown('<div class="header-title">📝 GÓP Ý VĂN KIỆN ĐẠI HỘI ĐOÀN TCTHK</div>', unsafe_allow_html=True)
    
    # Admin login toggle
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if not st.session_state.admin_logged_in:
            if st.button("🔐 Đăng nhập Admin", key="admin_toggle"):
                st.session_state.show_admin_login = not st.session_state.show_admin_login
        else:
            if st.button("🚪 Đăng xuất Admin", key="admin_logout"):
                st.session_state.admin_logged_in = False
                st.session_state.show_admin_login = False
                st.rerun()

    # Admin login form
    if st.session_state.show_admin_login and not st.session_state.admin_logged_in:
        st.markdown("---")
        st.subheader("🔐 Đăng nhập Admin")
        
        with st.form("admin_login"):
            admin_username = st.text_input("Tên đăng nhập:")
            admin_password = st.text_input("Mật khẩu:", type="password")
            submit_admin = st.form_submit_button("Đăng nhập", use_container_width=True)
            
            if submit_admin:
                if verify_admin(admin_username, admin_password):
                    st.session_state.admin_logged_in = True
                    st.session_state.show_admin_login = False
                    st.success("Đăng nhập thành công!")
                    st.rerun()
                else:
                    st.error("Tên đăng nhập hoặc mật khẩu không đúng!")

    # Admin panel
    if st.session_state.admin_logged_in:
        st.markdown("---")
        st.subheader("📊 Quản lý Góp ý - Admin Panel")
        
        # Lấy dữ liệu góp ý
        df = get_all_feedback()
        
        if not df.empty:
            st.write(f"**Tổng số góp ý:** {len(df)}")
            
            # Hiển thị bảng góp ý
            st.dataframe(
                df, 
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Ý kiến góp ý": st.column_config.TextColumn(width="large"),
                    "Thời gian": st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm")
                }
            )
            
            # Xuất Excel
            if st.button("📥 Xuất file Excel", use_container_width=True):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Góp ý')
                    
                    # Định dạng Excel
                    workbook = writer.book
                    worksheet = writer.sheets['Góp ý']
                    
                    # Định dạng header
                    header_format = workbook.add_format({
                        'bold': True,
                        'text_wrap': True,
                        'valign': 'top',
                        'fg_color': '#4472C4',
                        'font_color': 'white'
                    })
                    
                    # Áp dụng định dạng cho header
                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                    
                    # Tự động điều chỉnh độ rộng cột
                    for i, col in enumerate(df.columns):
                        if col == "Ý kiến góp ý":
                            worksheet.set_column(i, i, 50)
                        elif col == "Họ và Tên":
                            worksheet.set_column(i, i, 20)
                        elif col == "Chi Đoàn":
                            worksheet.set_column(i, i, 15)
                        else:
                            worksheet.set_column(i, i, 15)
                
                output.seek(0)
                
                # Tạo tên file với timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"gop_y_dai_hoi_doan_{timestamp}.xlsx"
                
                st.download_button(
                    label="📥 Tải xuống file Excel",
                    data=output,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        else:
            st.info("Chưa có góp ý nào được gửi.")
        
        st.markdown("---")

    # Form góp ý chính
    st.subheader("✍️ Gửi góp ý của bạn")
    st.markdown("*Vui lòng điền đầy đủ thông tin để gửi góp ý*")
    
    with st.form("feedback_form", clear_on_submit=True):
        # Họ và tên
        ho_ten = st.text_input(
            "Họ và Tên *",
            placeholder="Nhập họ và tên đầy đủ của bạn",
            help="Trường bắt buộc"
        )
        
        # Chi Đoàn
        chi_doan = st.selectbox(
            "Chi Đoàn *",
            options=["-- Chọn Chi Đoàn --"] + CHI_DOAN_LIST,
            help="Chọn Chi Đoàn của bạn"
        )
        
        # Nếu chọn "Khác", cho phép nhập tên Chi Đoàn khác
        if chi_doan == "Khác":
            chi_doan_khac = st.text_input(
                "Tên Chi Đoàn khác:",
                placeholder="Nhập tên Chi Đoàn của bạn"
            )
            if chi_doan_khac.strip():
                chi_doan = chi_doan_khac.strip()
        
        # Ý kiến góp ý
        y_kien = st.text_area(
            "Ý kiến góp ý *",
            placeholder="Nhập ý kiến góp ý của bạn về Văn kiện Đại hội Đoàn TCTHK (tối đa 500 từ)",
            help="Tối đa 500 từ",
            height=150
        )
        
        # Đếm số từ
        if y_kien:
            word_count = count_words(y_kien)
            if word_count > 500:
                st.error(f"Ý kiến của bạn có {word_count} từ, vượt quá giới hạn 500 từ!")
            else:
                st.info(f"Số từ: {word_count}/500")
        
        # Submit button
        submit_button = st.form_submit_button("📤 Gửi góp ý", use_container_width=True)
        
        if submit_button:
            # Validation
            errors = []
            
            if not ho_ten or not ho_ten.strip():
                errors.append("Vui lòng nhập Họ và Tên")
            
            if not chi_doan or chi_doan == "-- Chọn Chi Đoàn --":
                errors.append("Vui lòng chọn Chi Đoàn")
            
            if not y_kien or not y_kien.strip():
                errors.append("Vui lòng nhập ý kiến góp ý")
            elif count_words(y_kien) > 500:
                errors.append("Ý kiến góp ý không được vượt quá 500 từ")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                try:
                    save_feedback(ho_ten.strip(), chi_doan, y_kien.strip())
                    st.markdown('<div class="success-message">✅ Cảm ơn bạn! Góp ý của bạn đã được gửi thành công.</div>', unsafe_allow_html=True)
                    st.balloons()
                except Exception as e:
                    st.markdown(f'<div class="error-message">❌ Có lỗi xảy ra: {str(e)}</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; font-size: 14px; margin-top: 2rem;">
            <p>📧 <strong>Form Góp ý Văn kiện Đại hội Đoàn TCTHK</strong></p>
            <p>Mọi góp ý của bạn đều được ghi nhận và sẽ được Ban tổ chức xem xét kỹ lưỡng.</p>
            <p><em>Cảm ơn sự đóng góp quý báu của bạn!</em></p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
