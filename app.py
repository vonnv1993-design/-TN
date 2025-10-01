import streamlit as st
import sqlite3
import pandas as pd
import hashlib
from datetime import datetime
import io
import re
import base64
import os

# Cấu hình trang
st.set_page_config(
    page_title="Góp ý Văn kiện Đại hội Đoàn TCTHK",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS hiện đại với màu vàng đồng và xanh
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Root variables */
    :root {
        --primary-blue: #1E40AF;
        --secondary-blue: #3B82F6;
        --light-blue: #DBEAFE;
        --golden: #F59E0B;
        --light-golden: #FEF3C7;
        --dark-golden: #D97706;
        --gradient-primary: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
        --gradient-golden: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        --gradient-bg: linear-gradient(135deg, #DBEAFE 0%, #FEF3C7 100%);
        --text-dark: #1F2937;
        --text-light: #6B7280;
        --white: #FFFFFF;
        --shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        --shadow-hover: 0 15px 35px rgba(0, 0, 0, 0.15);
        --border-radius: 16px;
        --border-radius-small: 12px;
    }

    /* Base styles */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Remove default streamlit styling */
    .main > div {
        padding-top: 1rem;
        max-width: 100%;
    }
    
    .main .block-container {
        padding: 1rem;
        max-width: 100%;
    }
    
    /* Main container */
    .stApp {
        background: var(--gradient-bg);
        min-height: 100vh;
    }
    
    /* Header styling */
    .header-container {
        background: var(--gradient-primary);
        padding: 2rem 1.5rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 var(--border-radius) var(--border-radius);
        text-align: center;
        box-shadow: var(--shadow);
        position: relative;
        overflow: hidden;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 100" fill="rgba(255,255,255,0.1)"><polygon points="0,0 1000,100 1000,0"/></svg>');
        background-size: cover;
    }
    
    .header-title {
        color: var(--white);
        font-size: 28px;
        font-weight: 700;
        margin: 0;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .header-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 16px;
        font-weight: 400;
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }

    /* Modern card styling */
    .modern-card {
        background: var(--white);
        padding: 2rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(59, 130, 246, 0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .modern-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--gradient-golden);
    }
    
    .modern-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
    }

    /* Admin card special styling */
    .admin-card {
        background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
        color: var(--white);
        border: none;
    }
    
    .admin-card::before {
        background: var(--gradient-golden);
    }

    /* Form styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        font-size: 16px !important;
        border: 2px solid #E5E7EB !important;
        border-radius: var(--border-radius-small) !important;
        padding: 0.75rem !important;
        background: var(--white) !important;
        transition: all 0.3s ease !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--secondary-blue) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
    }
    
    .stTextArea > div > div > textarea {
        min-height: 120px !important;
        resize: vertical !important;
    }

    /* Label styling */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: var(--text-dark) !important;
        margin-bottom: 0.5rem !important;
    }

    /* Button styling */
    .stButton > button {
        background: var(--gradient-golden) !important;
        color: var(--white) !important;
        border: none !important;
        border-radius: var(--border-radius-small) !important;
        padding: 0.75rem 2rem !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        width: 100% !important;
        height: auto !important;
        min-height: 52px !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3) !important;
        text-transform: none !important;
    }
    
    .stButton > button:hover {
        background: var(--dark-golden) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(245, 158, 11, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* Secondary button styling */
    .secondary-btn > button {
        background: var(--gradient-primary) !important;
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3) !important;
    }
    
    .secondary-btn > button:hover {
        background: var(--primary-blue) !important;
        box-shadow: 0 8px 20px rgba(30, 64, 175, 0.4) !important;
    }

    /* Download button styling */
    .stDownloadButton > button {
        background: var(--gradient-primary) !important;
        color: var(--white) !important;
        border: none !important;
        border-radius: var(--border-radius-small) !important;
        padding: 0.75rem 2rem !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        width: 100% !important;
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3) !important;
    }
    
    .stDownloadButton > button:hover {
        background: var(--primary-blue) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(30, 64, 175, 0.4) !important;
    }

    /* Alert boxes */
    .success-box {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: var(--white);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        text-align: center;
        margin: 1rem 0;
        font-weight: 600;
        font-size: 16px;
        box-shadow: var(--shadow);
        border: none;
    }
    
    .info-box {
        background: var(--light-blue);
        color: var(--primary-blue);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
        border: 2px solid rgba(59, 130, 246, 0.2);
        position: relative;
    }
    
    .warning-box {
        background: var(--light-golden);
        color: var(--dark-golden);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
        border: 2px solid rgba(245, 158, 11, 0.2);
        font-weight: 500;
    }

    /* Stats card */
    .stats-card {
        background: var(--gradient-golden);
        color: var(--white);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        text-align: center;
        margin: 1rem 0;
        box-shadow: var(--shadow);
    }
    
    .stats-number {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .stats-label {
        font-size: 14px;
        opacity: 0.9;
        font-weight: 500;
    }

    /* Expander styling */
    .streamlit-expander {
        border: 2px solid var(--secondary-blue) !important;
        border-radius: var(--border-radius) !important;
        overflow: hidden !important;
        box-shadow: var(--shadow) !important;
        margin-bottom: 1.5rem !important;
    }
    
    .streamlit-expander > summary {
        background: var(--gradient-primary) !important;
        color: var(--white) !important;
        padding: 1rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    
    .streamlit-expander > div[data-testid="stExpanderDetails"] {
        background: var(--white) !important;
        padding: 1.5rem !important;
    }

    /* Dataframe styling */
    .stDataFrame {
        border-radius: var(--border-radius) !important;
        overflow: hidden !important;
        box-shadow: var(--shadow) !important;
    }

    /* Word counter */
    .word-counter {
        background: var(--light-golden);
        color: var(--dark-golden);
        padding: 0.75rem 1rem;
        border-radius: var(--border-radius-small);
        font-weight: 600;
        text-align: center;
        margin: 0.5rem 0;
        font-size: 14px;
        border: 2px solid rgba(245, 158, 11, 0.2);
    }
    
    .word-counter.warning {
        background: #FEE2E2;
        color: #DC2626;
        border-color: rgba(220, 38, 38, 0.2);
    }

    /* Footer styling */
    .footer {
        background: var(--white);
        padding: 2rem;
        border-radius: var(--border-radius);
        text-align: center;
        margin-top: 2rem;
        box-shadow: var(--shadow);
        border-top: 4px solid var(--golden);
    }

    /* Mobile responsive */
    @media (max-width: 768px) {
        .header-container {
            margin: -1rem -1rem 1.5rem -1rem;
            padding: 1.5rem 1rem;
        }
        
        .header-title {
            font-size: 24px;
        }
        
        .modern-card {
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .main .block-container {
            padding: 0.5rem;
        }
    }

    /* Form container */
    .form-container {
        background: var(--white);
        padding: 2rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        border-top: 4px solid var(--golden);
        margin: 1rem 0;
    }

    /* Section headers */
    .section-header {
        font-size: 20px;
        font-weight: 700;
        color: var(--primary-blue);
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--light-blue);
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Tạo thư mục data để lưu database persistent
@st.cache_data
def create_data_directory():
    if not os.path.exists('data'):
        os.makedirs('data')
    return True

# Database path - lưu trong thư mục data để persistent
DATABASE_PATH = os.path.join('data', 'feedback.db')

# Khởi tạo database với migration support
def init_database():
    create_data_directory()
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
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
    
    # Kiểm tra xem bảng admin_users đã tồn tại chưa và có cột nào
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_users'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        # Kiểm tra cấu trúc bảng hiện tại
        cursor.execute("PRAGMA table_info(admin_users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Nếu bảng có cấu trúc cũ, xóa và tạo lại
        if 'username_hash' not in columns:
            cursor.execute("DROP TABLE IF EXISTS admin_users")
            table_exists = False
    
    # Tạo bảng admin_users mới với cấu trúc đúng
    if not table_exists:
        cursor.execute('''
            CREATE TABLE admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username_hash TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tạo tài khoản admin mặc định với mã hóa nâng cao
        admin_username = "Admin"
        admin_password = "Admin@123"
        
        # Tạo salt ngẫu nhiên
        import secrets
        salt = secrets.token_hex(32)
        
        # Mã hóa username và password với salt
        username_hash = hashlib.pbkdf2_hmac('sha256', admin_username.encode(), salt.encode(), 100000)
        password_hash = hashlib.pbkdf2_hmac('sha256', admin_password.encode(), salt.encode(), 100000)
        
        # Encode to base64 để lưu trữ
        username_hash_b64 = base64.b64encode(username_hash).decode()
        password_hash_b64 = base64.b64encode(password_hash).decode()
        
        cursor.execute('''
            INSERT INTO admin_users (username_hash, password_hash, salt)
            VALUES (?, ?, ?)
        ''', (username_hash_b64, password_hash_b64, salt))
    
    conn.commit()
    conn.close()
    return True

# Lưu góp ý vào database
def save_feedback(ho_ten, chi_doan, y_kien):
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO feedback (ho_ten, chi_doan, y_kien)
        VALUES (?, ?, ?)
    ''', (ho_ten, chi_doan, y_kien))
    conn.commit()
    conn.close()

# Lấy danh sách góp ý
def get_all_feedback():
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        df = pd.read_sql_query('''
            SELECT id, ho_ten as "Họ và Tên", 
                   chi_doan as "Chi Đoàn", 
                   y_kien as "Ý kiến góp ý", 
                   datetime(thoi_gian, 'localtime') as "Thời gian"
            FROM feedback 
            ORDER BY thoi_gian DESC
        ''', conn)
        conn.close()
        return df
    except Exception as e:
        # Nếu có lỗi, trả về DataFrame rỗng
        return pd.DataFrame(columns=["Họ và Tên", "Chi Đoàn", "Ý kiến góp ý", "Thời gian"])

# Xác thực admin với mã hóa nâng cao
def verify_admin(username, password):
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        cursor = conn.cursor()
        
        # Lấy tất cả admin users để kiểm tra
        cursor.execute('SELECT username_hash, password_hash, salt FROM admin_users')
        users = cursor.fetchall()
        conn.close()
        
        for username_hash_stored, password_hash_stored, salt in users:
            try:
                # Mã hóa username và password input với salt từ database
                username_hash_input = hashlib.pbkdf2_hmac('sha256', username.encode(), salt.encode(), 100000)
                password_hash_input = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
                
                # Encode to base64
                username_hash_input_b64 = base64.b64encode(username_hash_input).decode()
                password_hash_input_b64 = base64.b64encode(password_hash_input).decode()
                
                # So sánh hash
                if (username_hash_input_b64 == username_hash_stored and 
                    password_hash_input_b64 == password_hash_stored):
                    return True
            except Exception:
                continue
        
        return False
    except Exception:
        return False

# Đếm số từ
def count_words(text):
    if not text:
        return 0
    words = re.findall(r'\S+', text.strip())
    return len(words)

def main():
    # Khởi tạo database (chỉ chạy 1 lần khi startup)
    if 'db_initialized' not in st.session_state:
        try:
            init_database()
            st.session_state.db_initialized = True
        except Exception as e:
            st.error(f"Lỗi khởi tạo database: {e}")
            st.stop()
    
    # Initialize session state
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False

    # Header với thiết kế hiện đại
    st.markdown('''
    <div class="header-container">
        <div class="header-title">📝 GÓP Ý VĂN KIỆN</div>
        <div class="header-title">ĐẠI HỘI ĐOÀN TCTHK</div>
        <div class="header-subtitle">Chia sẻ ý kiến đóng góp của bạn để xây dựng tương lai tốt đẹp hơn</div>
    </div>
    ''', unsafe_allow_html=True)

    # Admin Panel với thiết kế card hiện đại
    with st.expander("🔐 KHU VỰC QUẢN TRỊ", expanded=False):
        if not st.session_state.admin_logged_in:
            st.markdown('<div class="section-header">🔑 Đăng nhập Admin</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                admin_username = st.text_input("👤 Tên đăng nhập", key="admin_user", placeholder="Nhập tên đăng nhập")
            with col2:
                admin_password = st.text_input("🔒 Mật khẩu", type="password", key="admin_pass", placeholder="Nhập mật khẩu")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button("🔓 ĐĂNG NHẬP", key="login_btn"):
                    if admin_username and admin_password:
                        if verify_admin(admin_username, admin_password):
                            st.session_state.admin_logged_in = True
                            st.success("✅ Đăng nhập thành công!")
                            st.rerun()
                        else:
                            st.error("❌ Thông tin đăng nhập không đúng!")
                    else:
                        st.warning("⚠️ Vui lòng điền đầy đủ thông tin!")
        
        else:
            # Admin Dashboard
            st.markdown('<div class="success-box">✅ Đăng nhập thành công với quyền Admin!</div>', unsafe_allow_html=True)
            
            col_logout1, col_logout2, col_logout3 = st.columns([1, 2, 1])
            with col_logout2:
                st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
                if st.button("🚪 ĐĂNG XUẤT", key="logout_btn"):
                    st.session_state.admin_logged_in = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            try:
                df = get_all_feedback()
                
                if not df.empty:
                    # Statistics
                    st.markdown(f'''
                    <div class="stats-card">
                        <div class="stats-number">{len(df)}</div>
                        <div class="stats-label">📈 TỔNG SỐ GÓP Ý</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    st.markdown('<div class="section-header">📋 DANH SÁCH GÓP Ý</div>', unsafe_allow_html=True)
                    
                    # Hiển thị bảng với styling đẹp
                    st.dataframe(
                        df.drop('id', axis=1, errors='ignore'), 
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Export Excel button
                    st.markdown("---")
                    col_export1, col_export2, col_export3 = st.columns([1, 2, 1])
                    with col_export2:
                        if st.button("📥 TẢI XUỐNG EXCEL", key="export_btn"):
                            try:
                                output = io.BytesIO()
                                df_export = df.drop('id', axis=1, errors='ignore')
                                df_export.to_excel(output, index=False, sheet_name='Góp ý')
                                output.seek(0)
                                
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"gop_y_dai_hoi_doan_{timestamp}.xlsx"
                                
                                st.download_button(
                                    label="💾 TẢI FILE EXCEL",
                                    data=output.getvalue(),
                                    file_name=filename,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key="download_excel"
                                )
                                
                            except Exception as e:
                                st.error(f"❌ Lỗi tạo file Excel: {e}")
                else:
                    st.markdown('''
                    <div class="info-box">
                        <h4 style="margin-top: 0;">📭 Chưa có góp ý nào</h4>
                        <p style="margin-bottom: 0;">Hiện tại chưa có góp ý nào được gửi. Hãy chia sẻ form này để nhận được nhiều phản hồi hơn!</p>
                    </div>
                    ''', unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"❌ Lỗi truy xuất dữ liệu: {e}")

    # Spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Form góp ý chính với thiết kế hiện đại
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">✍️ GỬI GÓP Ý CỦA BẠN</div>', unsafe_allow_html=True)
    
    with st.form("feedback_form", clear_on_submit=True):
        # Họ và tên
        ho_ten = st.text_input(
            "👤 Họ và Tên *",
            placeholder="Ví dụ: Nguyễn Văn An",
            help="Nhập họ và tên đầy đủ của bạn"
        )
        
        # Spacing
        st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
        
        # Chi Đoàn - Text input tự do
        chi_doan = st.text_input(
            "🏢 Chi Đoàn *",
            placeholder="Ví dụ: Chi Đoàn Ban CĐSCN",
            help="Nhập tên Chi Đoàn mà bạn đang sinh hoạt"
        )
        
        # Spacing
        st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
        
        # Ý kiến góp ý
        y_kien = st.text_area(
            "💭 Ý kiến góp ý *",
            placeholder="Chia sẻ những ý kiến, đề xuất, góp ý của bạn về Văn kiện Đại hội Đoàn TCTHK. Hãy thể hiện quan điểm một cách rõ ràng và chi tiết...",
            help="Tối đa 500 từ - Hãy chia sẻ những suy nghĩ chân thành của bạn",
            height=140
        )
        
        # Word counter với thiết kế đẹp
        if y_kien:
            word_count = count_words(y_kien)
            if word_count > 500:
                st.markdown(f'''
                <div class="word-counter warning">
                    ⚠️ Vượt quá giới hạn: {word_count}/500 từ
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                <div class="word-counter">
                    📊 Số từ: {word_count}/500
                </div>
                ''', unsafe_allow_html=True)
        
        # Spacing
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        
        # Submit button
        submitted = st.form_submit_button("📤 GỬI GÓP Ý")
        
        if submitted:
            # Validation
            errors = []
            
            if not ho_ten or len(ho_ten.strip()) < 2:
                errors.append("👤 Vui lòng nhập Họ và Tên (ít nhất 2 ký tự)")
            
            if not chi_doan or len(chi_doan.strip()) < 2:
                errors.append("🏢 Vui lòng nhập tên Chi Đoàn (ít nhất 2 ký tự)")
            
            if not y_kien or len(y_kien.strip()) < 10:
                errors.append("💭 Vui lòng nhập ý kiến góp ý (ít nhất 10 ký tự)")
            elif count_words(y_kien) > 500:
                errors.append("📝 Ý kiến góp ý không được vượt quá 500 từ")
            
            # Hiển thị lỗi hoặc lưu
            if errors:
                st.markdown('''
                <div class="warning-box">
                    <h4 style="margin-top: 0; color: #D97706;">⚠️ Cần hoàn thiện thông tin</h4>
                    <ul style="margin: 0.5rem 0 0 1rem;">
                ''', unsafe_allow_html=True)
                for error in errors:
                    st.markdown(f'<li>{error}</li>', unsafe_allow_html=True)
                st.markdown('</ul></div>', unsafe_allow_html=True)
            else:
                try:
                    save_feedback(ho_ten.strip(), chi_doan.strip(), y_kien.strip())
                    
                    st.markdown('''
                    <div class="success-box">
                        🎉 THÀNH CÔNG!<br><br>
                        <strong>Cảm ơn bạn đã gửi góp ý quý báu!</strong><br>
                        Góp ý của bạn đã được lưu thành công và sẽ được Ban tổ chức xem xét kỹ lưỡng.<br><br>
                        <em>Sự đóng góp của bạn rất có ý nghĩa! 🙏</em>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    st.balloons()
                    
                except Exception as e:
                    st.markdown(f'''
                    <div class="warning-box">
                        ❌ <strong>Có lỗi xảy ra:</strong> {e}<br>
                        Vui lòng thử lại hoặc liên hệ Ban tổ chức.
                    </div>
                    ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer với thiết kế đẹp
    st.markdown('''
    <div class="footer">
        <h3 style="color: #1E40AF; margin-bottom: 1rem;">📧 Form Góp ý Văn kiện Đại hội Đoàn TCTHK</h3>
        <div style="display: grid; gap: 1rem; text-align: center; color: #6B7280; line-height: 1.6;">
            <p style="margin: 0;">
                🙏 <strong style="color: #1F2937;">Cảm ơn sự quan tâm và đóng góp tích cực của bạn!</strong>
            </p>
            <p style="margin: 0;">
                Mọi góp ý đều được ghi nhận và sẽ được Ban tổ chức nghiên cứu, xem xét một cách kỹ lưỡng<br>
                để hoàn thiện Văn kiện phục vụ Đại hội.
            </p>
            <div style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); color: white; padding: 1rem; border-radius: 12px; margin-top: 1rem;">
                <strong>✨ Sự đóng góp của bạn là động lực quý báu giúp Đại hội thành công! ✨</strong>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
