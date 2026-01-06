import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 1. Cấu hình trang và Style Times New Roman
st.set_page_config(page_title="Mô phỏng Vật lí 10", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap');
    html, body, [class*="st-"], div, span, p {
        font-family: 'Times New Roman', Times, serif !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Khởi tạo hằng số
G = 9.8

def get_trajectory(mode, v0, alpha_deg, h0):
    alpha = np.radians(alpha_deg)
    v0x = v0 * np.cos(alpha)
    v0y = v0 * np.sin(alpha)
    
    # Tính thời gian chạm đất: h0 + v0y*t - 0.5*g*t^2 = 0
    discriminant = v0y**2 + 2 * G * h0
    if discriminant < 0: 
        t_flight = 0
    else: 
        t_flight = (v0y + np.sqrt(discriminant)) / G

    # Tạo mảng thời gian
    t_steps = np.linspace(0, t_flight, num=200)
    
    x = v0x * t_steps
    y = h0 + v0y * t_steps - 0.5 * G * t_steps**2
    y = np.maximum(y, 0) # Không cho phép y âm
    
    vx = np.full_like(t_steps, v0x)
    vy = v0y - G * t_steps
    v_total = np.sqrt(vx**2 + vy**2)
    
    return t_steps, x, y, vx, vy, v_total

# --- SIDEBAR ---
st.sidebar.header("⚙️ THÔNG SỐ VẬT LÍ")
mode = st.sidebar.selectbox("Chế độ chuyển động", 
    ["Ném thẳng đứng", "Ném ngang", "Ném xiên từ mặt đất", "Ném bóng rổ (Mục tiêu)"])

h_default = 10.0 if mode == "Ném ngang" else 0.0
h0 = st.sidebar.slider("Độ cao ban đầu (h) [m]", 0.0, 50.0, float(h_default))
v0 = st.sidebar.slider("Vận tốc đầu (v0) [m/s]", 0.0, 50.0, 20.0)

if mode == "Ném thẳng đứng":
    alpha_deg = 90.0
elif mode == "Ném ngang":
    alpha_deg = 0.0
else:
    alpha_deg = st.sidebar.slider("Góc ném (α) [độ]", 0, 90, 45)

# --- NỘI DUNG CHÍNH ---
st.title("🔭 Mô phỏng Chuyển động Động học Vật lí 10")

# Lộ trình khám phá
with st.container():
    st.subheader("📘 Lộ trình khám phá")
    c1, c2, c3 = st.columns(3)
    if mode == "Ném thẳng đứng":
        c1.info("**Bước 1:** Đặt $v_0=0$ để khảo sát sự rơi tự do.")
        c2.info("**Bước 2:** Ném lên và tìm điểm $v_y = 0$ (độ cao cực đại).")
        c3.info("**Bước 3:** Kiểm tra gia tốc không đổi $g=9.8m/s^2$.")
    elif mode == "Ném ngang":
        c1.info("**Bước 1:** Quan sát $v_x$ không đổi suốt quá trình.")
        c2.info("**Bước 2:** Kiểm tra thời gian rơi chỉ phụ thuộc vào $h$.")
        c3.info("**Bước 3:** Tính tầm xa $L = v_0 \cdot t$.")
    else:
        c1.info("**Bước 1:** Phân tích vận tốc thành 2 thành phần $Ox, Oy$.")
        c2.info("**Bước 2:** Tìm góc $\\alpha$ để tầm xa lớn nhất.")
        c3.info("**Bước 3:** Thử ném vào rổ tại vị trí $x=15m, y=3.05m$.")

# Tính toán dữ liệu
t_s, x_s, y_s, vx_s, vy_s, vt_s = get_trajectory(mode, v0, alpha_deg, h0)

# Vẽ đồ thị
fig = go.Figure()

# Thêm quỹ đạo dự báo
fig.add_trace(go.Scatter(
    x=x_s, y=y_s, mode='lines', 
    name='Quỹ đạo vật thể',
    line=dict(color='#1f77b4', width=3, dash='dash'),
    customdata=np.stack((t_s, vt_s, vx_s, vy_s), axis=-1),
    hovertemplate="<b>Thời gian:</b> %{customdata[0]:.2f}s<br>" +
                  "<b>Tầm xa:</b> %{x:.2f}m<br>" +
                  "<b>Độ cao:</b> %{y:.2f}m<br>" +
                  "<b>Vận tốc tổng:</b> %{customdata[1]:.2f}m/s<br>" +
                  "<b>vx:</b> %{customdata[2]:.2f}m/s | <b>vy:</b> %{customdata[3]:.2f}m/s" +
                  "<extra></extra>"
))

# Vẽ nhân vật & mục tiêu nếu là ném bóng rổ
if mode == "Ném bóng rổ (Mục tiêu)":
    # Người ném
    fig.add_trace(go.Scatter(x=[0], y=[1.6], mode="markers", marker=dict(size=15, color="Blue"), name="Người ném"))
    fig.add_trace(go.Scatter(x=[0, 0], y=[0, 1.6], mode="lines", line=dict(color="Blue", width=2), showlegend=False))
    # Rổ
    fig.add_trace(go.Scatter(x=[15], y=[3.05], mode="markers", 
                             marker=dict(size=18, symbol="circle-open", color="orange", line=dict(width=3)), 
                             name="Rổ (15m; 3.05m)"))

fig.update_layout(
    xaxis_title="Tầm xa (m)",
    yaxis_title="Độ cao (m)",
    xaxis=dict(range=[-1, max(max(x_s)+5, 20)], gridcolor='lightgrey'),
    yaxis=dict(range=[0, max(max(y_s)+5, 15)], gridcolor='lightgrey'),
    plot_bgcolor='white',
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# Bảng hiển thị thông số (Phần bị lỗi Syntax trước đó)
st.subheader("📊 Thông số kết quả")
res1, res2, res3, res4 = st.columns(4)
res1.metric("Thời gian bay", f"{t_s[-1]:.2f} s")
res2.metric("Tầm xa tối đa", f"{x_s[-1]:.2f} m")
res3.metric("Độ cao tối đa", f"{max(y_s):.2f} m")
res4.metric("Vận tốc cuối", f"{vt_s[-1]:.2f} m/s")
