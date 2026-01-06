import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 1. Cấu hình trang và Style Times New Roman (Đã sửa tham số allow_html)
st.set_page_config(page_title="Mô phỏng Vật lí 10", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap');
    html, body, [class*="st-"] {
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
    # Delta = v0y^2 - 4*(-4.9)*h0
    discriminant = v0y**2 + 2 * G * h0
    if discriminant < 0: t_flight = 0
    else: t_flight = (v0y + np.sqrt(discriminant)) / G

    # Tạo mảng thời gian (Mô phỏng 60 FPS tương đối bằng cách tăng số điểm mẫu)
    t_steps = np.linspace(0, t_flight, num=200)
    
    x = v0x * t_steps
    y = h0 + v0y * t_steps - 0.5 * G * t_steps**2
    
    # Giới hạn y không âm (chạm đất là dừng)
    y = np.maximum(y, 0)
    
    vx = np.full_like(t_steps, v0x)
    vy = v0y - G * t_steps
    v_total = np.sqrt(vx**2 + vy**2)
    
    return t_steps, x, y, vx, vy, v_total

# --- SIDEBAR ---
st.sidebar.header("⚙️ CÀI ĐẶT THÔNG SỐ")
mode = st.sidebar.selectbox("Chế độ chuyển động", 
    ["Ném thẳng đứng", "Ném ngang", "Ném xiên từ mặt đất", "Ném bóng rổ (Mục tiêu)"])

h0 = st.sidebar.slider("Độ cao ban đầu (h) [m]", 0.0, 50.0, 10.0 if "ngang" in mode else 0.0)
v0 = st.sidebar.slider("Vận tốc đầu (v0) [m/s]", 0.0, 50.0, 20.0)

if mode == "Ném thẳng đứng":
    alpha_deg = 90.0
elif mode == "Ném ngang":
    alpha_deg = 0.0
elif mode == "Ném xiên từ mặt đất":
    h0 = 0.0
    alpha_deg = st.sidebar.slider("Góc ném (α)", 0, 90, 45)
else: # Ném bóng rổ
    alpha_deg = st.sidebar.slider("Góc ném (α)", 0, 90, 45)

# --- NỘI DUNG ---
st.title("🏹 Phòng Thí Nghiệm Vật Lí Ảo")

# Lộ trình khám phá
with st.container(border=True):
    st.subheader("📘 Lộ trình khám phá")
    c1, c2, c3 = st.columns(3)
    if mode == "Ném thẳng đứng":
        c1.info("**Bước 1:** Đặt $v_0=0$ để quan sát rơi tự do.")
        c2.info("**Bước 2:** Ném lên và quan sát $v_y=0$ tại đỉnh.")
        c3.info("**Bước 3:** So sánh thời gian lên và xuống.")
    elif mode == "Ném ngang":
        c1.info("**Bước 1:** Quan sát $v_x$ không đổi (chuyển động thẳng đều).")
        c2.info("**Bước 2:** Quan sát $v_y$ tăng dần (rơi tự do).")
        c3.info("**Bước 3:** Kiểm tra tầm xa $L = v_0\sqrt{2h/g}$.")
    else:
        c1.info("**Bước 1:** Phân tích vector vận tốc tại đỉnh quỹ đạo.")
        c2.info("**Bước 2:** Tìm góc $\\alpha$ để đạt tầm xa lớn nhất.")
        c3.info("**Bước 3:** Thay đổi $v_0$ để bóng vào rổ ($x=15, y=3.05$).")

# Tính toán
t_s, x_s, y_s, vx_s, vy_s, vt_s = get_trajectory(mode, v0, alpha_deg, h0)

# Vẽ đồ thị
fig = go.Figure()

# Quỹ đạo
fig.add_trace(go.Scatter(
    x=x_s, y=y_s, mode='lines', name='Quỹ đạo',
    line=dict(color='#1f77b4', width=3),
    customdata=np.stack((t_s, vt_s, vx_s, vy_s), axis=-1),
    hovertemplate="<b>Thời gian:</b> %{customdata[0]:.2f}s<br>" +
                  "<b>Độ cao:</b> %{y:.2f}m<br>" +
                  "<b>Tầm xa:</b> %{x:.2f}m<br>" +
                  "<b>Vận tốc:</b> %{customdata[1]:.2f}m/s<br>" +
                  "<b>vx:</b> %{customdata[2]:.2f}m/s | <b>vy:</b> %{customdata[3]:.2f}m/s" +
                  "<extra></extra>"
))

if mode == "Ném bóng rổ (Mục tiêu)":
    # Vẽ người ném (Xanh dương)
    fig.add_trace(go.Scatter(x=[0], y=[1.6], mode="markers", marker=dict(size=15, color="Blue"), name="Người ném"))
    fig.add_trace(go.Scatter(x=[0, 0], y=[0, 1.6], mode="lines", line=dict(color="Blue", width=3), showlegend=False))
    # Vẽ rổ bóng
    fig.add_trace(go.Scatter(x=[15], y=[3.05], mode="markers", marker=dict(size=20, symbol="circle-open", color="orange", line=dict(width=3)), name="Rổ (3.05m)"))

fig.update_layout(
    xaxis_title="Tầm xa (m)", yaxis_title="Độ cao (m)",
    hovermode="x unified",
    xaxis=dict(range=[-1, max(max(x_s)+5, 20)]),
    yaxis=dict(range=[0, max(max(y_s)+5, 15)])
)

st.plotly_chart(fig, use_container_width=True)

# Bảng số liệu
col1, col2, col3, col4 = st.columns(4)
col1.metric("⏱ Thời gian bay", f"{t_
