import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Cấu hình trang và Style Times New Roman
st.set_page_config(page_title="Mô phỏng Động học Vật lí 10", layout="wide")
st.markdown("""
    <style>
    * {font-family: 'Times New Roman', Times, serif;}
    .stMarkdown, .stText, h1, h2, h3 {font-family: 'Times New Roman', Times, serif;}
    </style>
    """, unsafe_content_allowed=True)

# Khởi tạo hằng số
G = 9.8

def get_trajectory(mode, v0, alpha_deg, h0, target_x=None, target_y=None):
    alpha = np.radians(alpha_deg)
    v0x = v0 * np.cos(alpha)
    v0y = v0 * np.sin(alpha)
    
    # Tính thời gian chạm đất: h0 + v0y*t - 0.5*g*t^2 = 0
    # Phương trình bậc 2: -4.9t^2 + v0y*t + h0 = 0
    if mode == "Ném thẳng đứng":
        v0x = 0
        if v0y == 0 and h0 == 0: t_flight = 0
        else:
            discriminant = v0y**2 + 2 * G * h0
            t_flight = (v0y + np.sqrt(discriminant)) / G
    else:
        discriminant = v0y**2 + 2 * G * h0
        t_flight = (v0y + np.sqrt(discriminant)) / G

    t_steps = np.linspace(0, t_flight, num=100)
    
    x = v0x * t_steps
    y = h0 + v0y * t_steps - 0.5 * G * t_steps**2
    
    vx = np.full_like(t_steps, v0x)
    vy = v0y - G * t_steps
    v_total = np.sqrt(vx**2 + vy**2)
    
    return t_steps, x, y, vx, vy, v_total

# --- GIAO DIỆN SIDEBAR ---
st.sidebar.title("🎮 Bảng Điều Khiển")
mode = st.sidebar.selectbox("Chọn chế độ chuyển động", 
    ["Ném thẳng đứng", "Ném ngang", "Ném xiên từ mặt đất", "Ném bóng rổ (Mục tiêu)"])

st.sidebar.markdown("---")
h0 = st.sidebar.slider("Độ cao ban đầu (h) [m]", 0.0, 50.0, 0.0 if "xiên" in mode else 10.0)
v0 = st.sidebar.slider("Vận tốc ban đầu (v0) [m/s]", 0.0, 40.0, 15.0)

if mode == "Ném thẳng đứng":
    alpha_deg = 90.0
elif mode == "Ném ngang":
    alpha_deg = 0.0
elif mode == "Ném xiên từ mặt đất":
    h0 = 0.0
    alpha_deg = st.sidebar.slider("Góc ném (α)", 0, 90, 45)
else: # Ném bóng rổ
    alpha_deg = st.sidebar.slider("Góc ném (α)", 0, 90, 45)
    st.sidebar.info("Mục tiêu cố định tại x=15m, y=3.05m (Rổ)")

# --- NỘI DUNG CHÍNH ---
st.title(f"🔭 Mô phỏng: {mode}")

# Bảng lộ trình khám phá (Tính sư phạm)
with st.expander("📘 Lộ trình khám phá (Dành cho học sinh)", expanded=True):
    col1, col2, col3 = columns = st.columns(3)
    if mode == "Ném thẳng đứng":
        col1.markdown("**Bước 1:** Quan sát sự thay đổi vận tốc $v_y$ khi đi lên và đi xuống.")
        col2.markdown("**Bước 2:** Xác định thời điểm vật đạt độ cao cực đại ($v_y = 0$).")
        col3.markdown("**Bước 3:** Kiểm tra tính đối xứng của thời gian lên và xuống.")
    elif mode == "Ném ngang":
        col1.markdown("**Bước 1:** Tại sao vận tốc $v_x$ không đổi theo thời gian?")
        col2.markdown("**Bước 2:** Hình dạng quỹ đạo có phải là một nhánh Parabol?")
        col3.markdown("**Bước 3:** Tầm xa phụ thuộc như thế nào vào $h$ và $v_0$?")
    else:
        col1.markdown("**Bước 1:** Phân tích vận tốc thành 2 thành phần $v_x$ (đều) và $v_y$ (biến đổi).")
        col2.markdown("**Bước 2:** Tìm góc $\\alpha$ để tầm xa $L$ là lớn nhất.")
        col3.markdown("**Bước 3:** Thử thách ném trúng mục tiêu trong chế độ Bóng rổ.")

# Tính toán dữ liệu
t_steps, x_vals, y_vals, vx_vals, vy_vals, v_total_vals = get_trajectory(mode, v0, alpha_deg, h0)

# Vẽ đồ thị bằng Plotly
fig = go.Figure()

# Thêm quỹ đạo
fig.add_trace(go.Scatter(
    x=x_vals, y=y_vals,
    mode='lines',
    name='Quỹ đạo dự báo',
    line=dict(color='firebrick', width=3, dash='dash'),
    hovertemplate = 
        "<b>Thông số tức thời:</b><br>" +
        "Thời gian: %{customdata[0]:.2f} s<br>" +
        "Độ cao: %{y:.2f} m<br>" +
        "Tầm xa: %{x:.2f} m<br>" +
        "Vận tốc tổng: %{customdata[1]:.2f} m/s<br>" +
        "vx: %{customdata[2]:.2f} m/s<br>" +
        "vy: %{customdata[3]:.2f} m/s<br>" +
        "<extra></extra>",
    customdata=np.stack((t_steps, v_total_vals, vx_vals, vy_vals), axis=-1)
))

# Vẽ nhân vật (Chỉ ở chế độ bóng rổ)
if mode == "Ném bóng rổ (Mục tiêu)":
    # Vẽ người đơn giản
    fig.add_trace(go.Scatter(x=[0], y=[0.8], mode="markers", marker=dict(size=20, color="Blue"), name="Người ném"))
    fig.add_trace(go.Scatter(x=[0, 0], y=[0, 1.5], mode="lines", line=dict(color="Blue", width=4), showlegend=False))
    # Vẽ rổ
    fig.add_trace(go.Scatter(x=[15], y=[3.05], mode="markers+lines", 
                             marker=dict(size=15, symbol="circle-open", color="orange", line=dict(width=3)),
                             name="Rổ bóng (Mục tiêu)"))

# Cấu hình khung nhìn
fig.update_layout(
    xaxis=dict(title="Tầm xa (m)", range=[-1, max(max(x_vals)+2, 20)]),
    yaxis=dict(title="Độ cao (m)", range=[0, max(max(y_vals)+2, 15)]),
    height=600,
    template="plotly_white",
    hovermode="closest"
)

st.plotly_chart(fig, use_container_width=True)

# Hiển thị thông số kết quả
st.subheader("📊 Kết quả tính toán chi tiết")
res1, res2, res3, res4 = st.columns(4)
res1.metric("Thời gian bay", f"{t_steps[-1]:.2f} s")
res2.metric("Tầm xa tối đa", f"{x_vals[-1]:.2f} m")
res3.metric("Độ cao cực đại", f"{max(y_vals):.2f} m")
res4.metric("Vận tốc chạm đất", f"{v_total_vals[-1]:.2f} m/s")

st.markdown("---")
st.caption("Thiết kế bởi Chuyên gia Vật lí & Python - Sử dụng mô hình gia tốc trọng trường $g = 9.8 m/s^2$")
