import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 1. CẤU HÌNH TRANG
st.set_page_config(page_title="Vật Lí AI - Thí nghiệm chuẩn xác", page_icon="🚀", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .step-card {
        background-color: #1e2130; padding: 20px; border-radius: 15px;
        border-left: 5px solid #00f2ff; margin-bottom: 20px;
    }
    .step-number {
        background-color: #00f2ff; color: #1e2130;
        padding: 2px 8px; border-radius: 50%; font-weight: bold; margin-right: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏀 Phòng Thí Nghiệm Vật Lí AI")

# HIỂN THỊ HẰNG SỐ VẬT LÍ
G_CONST = 9.8
st.write(f"🌍 Gia tốc trọng trường chuẩn: $g = {G_CONST}$ $m/s^2$")

# 2. THANH ĐIỀU KHIỂN SIDEBAR
st.sidebar.title("⚙️ Cấu hình thí nghiệm")
MODES = [
    "↕️ 1. Ném theo phương thẳng đứng",
    "➡️ 2. Ném theo phương ngang",
    "🏟️ 3. Ném xiên từ mặt đất",
    "🏀 4. Ném bóng rổ (Mục tiêu)"
]
selected_mode = st.sidebar.selectbox("🌟 Chọn loại chuyển động", MODES)

h0, v0, angle = 0.0, 12.0, 45.0
target_x, target_y = 8.0, 3.05

with st.sidebar.expander("📝 Nhập số liệu thí nghiệm", expanded=True):
    v0 = st.number_input("⚡ Vận tốc đầu $v_0$ (m/s)", 0.0, 50.0, 12.0, 0.5)
    
    if selected_mode == MODES[0]: 
        h0 = st.number_input("📏 Độ cao ban đầu $h_0$ (m)", 0.0, 100.0, 10.0, 1.0)
        direction = st.radio("Hướng ném", ["Ném lên trên", "Ném xuống dưới"])
        angle = 90.0 if direction == "Ném lên trên" else -90.0
        if v0 == 0 and direction == "Ném xuống dưới":
            st.info("💡 Trạng thái: **Rơi tự do**.")
    elif selected_mode == MODES[1]: 
        h0 = st.number_input("📏 Độ cao ban đầu $h_0$ (m)", 0.5, 100.0, 15.0, 1.0)
        angle = 0.0
    elif selected_mode == MODES[2]: 
        angle = st.number_input("📐 Góc ném $\\alpha$ (độ)", 0.0, 90.0, 45.0, 1.0)
        h0 = 0.0
    elif selected_mode == MODES[3]: 
        h0 = st.number_input("🧍 Độ cao tay ném (m)", 0.0, 5.0, 2.0, 0.1)
        angle = st.number_input("📐 Góc ném $\\alpha$ (độ)", 0.0, 90.0, 45.0, 1.0)
        target_x = st.number_input("🚩 Khoảng cách rổ (m)", 1.0, 50.0, 8.0, 0.1)
        target_y = st.number_input("🥅 Chiều cao rổ (m)", 0.5, 5.0, 3.05, 0.05)

# --- 3. HƯỚNG DẪN KHÁM PHÁ (DYNAMIC) ---
st.markdown("### 📖 Lộ trình khám phá dành cho học sinh")

if selected_mode == MODES[0]:
    instruct = [
        f"**Kiểm chứng:** Theo dõi vận tốc đứng $v_y$ thay đổi theo gia tốc $g = {G_CONST}$ $m/s^2$.",
        "**Rơi tự do:** Chỉnh hướng xuống và $v_0 = 0$. Soi bảng thông số để xem sự tăng tốc.",
        "**Tư duy:** Tại đỉnh cao nhất, vận tốc đứng có bằng 0 không?"
    ]
elif selected_mode == MODES[1]:
    instruct = [
        "**Đặc điểm:** Vận tốc ngang $v_x$ không thay đổi suốt hành trình.",
        "**Mối liên hệ:** Soi bảng thông số để thấy vận tốc đứng $v_y$ tăng đều do gia tốc $g$.",
        "**Kết luận:** Thời gian rơi chỉ phụ thuộc vào độ cao $h_0$."
    ]
elif selected_mode == MODES[2]:
    instruct = [
        "**Phân tích:** Vận tốc tại đỉnh chỉ còn thành phần nằm ngang $v_x$.",
        "**Thử thách:** Tìm góc ném để đạt tầm xa lớn nhất với $v_0$ cố định.",
        "**Soi dữ liệu:** Thời gian bay tỉ lệ thuận với thành phần vận tốc ban đầu phương đứng."
    ]
else: 
    instruct = [
        "**Mục tiêu:** Kết hợp $v_0$ và Góc để đường dự báo đỏ đi qua tâm rổ.",
        "**Vật lí:** Quan sát sự biến đổi vận tốc tổng hợp khi bóng bay gần đến đích.",
        "**Thực hiện:** Nhấn nút để xem nhân vật xanh thực hiện mô phỏng thực tế."
    ]

# Hiển thị card hướng dẫn dùng markdown thuần để tránh lỗi font $
for i, text in enumerate(instruct):
    st.markdown(f"""<div class="step-card"><p><span class="step-number">{i+1}</span> {text}</p></div>""", unsafe_allow_html=True)

# --- 4. TÍNH TOÁN ĐỘNG HỌC ĐỒNG BỘ ---
angle_rad = np.radians(angle)
vx0 = v0 * np.cos(angle_rad)
vy0 = v0 * np.sin(angle_rad)

discriminant = vy0**2 + 2 * G_CONST * h0
t_flight = (vy0 + np.sqrt(max(0, discriminant))) / G_CONST if discriminant >= 0 else 0

t_steps = np.linspace(0, t_flight, num=120)
x_coords = vx0 * t_steps
if selected_mode == MODES[0]: x_coords = x_coords + 1e-9 
y_coords = np.maximum(h0 + vy0 * t_steps - 0.5 * G_CONST * t_steps**2, 0)

vx_inst = np.full_like(t_steps, vx0)
vy_inst = vy0 - G_CONST * t_steps
v_total = np.sqrt(vx_inst**2 + vy_inst**2)

# --- 5. ĐỒ THỊ ---
fig = go.Figure()
custom_data = np.stack((v_total, t_steps, vx_inst, vy_inst), axis=-1)



fig.add_trace(go.Scatter(
    x=x_coords, y=y_coords, mode='lines', name='Quỹ đạo dự báo', 
    line=dict(color='#FF4B4B', width=2, dash='dash'),
    customdata=custom_data,
    hovertemplate=(
        "Thời gian: %{customdata[1]:.2f} s<br>" +
        "Vận tốc tổng: %{customdata[0]:.2f} m/s<br>" +
        "v_ngang: %{customdata[2]:.2f} m/s<br>" +
        "v_đứng: %{customdata[3]:.2f} m/s<br>" +
        "Tầm xa: %{x:.2f} m | Độ cao: %{y:.2f} m<extra></extra>"
    )
))

fig.add_trace(go.Scatter(x=[x_coords[0]], y=[y_coords[0]], mode='lines', name='Đã bay', line=dict(color='#00f2ff', width=4), hoverinfo='skip'))
fig.add_trace(go.Scatter(x=[x_coords[0]], y=[y_coords[0]], mode='markers', name='Bóng', marker=dict(color='#FF6600', size=16, line=dict(color='white', width=1)), hoverinfo='skip'))

if selected_mode == MODES[3]:
    p_color = "#00f2ff"
    fig.add_shape(type="line", x0=0, y0=max(0, h0-1.5), x1=0, y1=h0-0.5, line=dict(color=p_color, width=6))
    fig.add_shape(type="circle", x0=-0.15, y0=h0-0.4, x1=0.15, y1=h0-0.1, fillcolor=p_color, line=dict(color=p_color))
    fig.add_shape(type="line", x0=0, y0=h0-0.5, x1=0.25 if angle >= 0 else -0.1, y1=h0, line=dict(color=p_color, width=4))
    fig.add_shape(type="line", x0=target_x, y0=0, x1=target_x, y1=target_y, line=dict(color="#555", width=3))
    fig.add_trace(go.Scatter(x=[target_x], y=[target_y], mode='markers', marker=dict(size=20, color='red', symbol='circle-open', line=dict(width=3)), hoverinfo='none'))

fig.update_layout(
    xaxis=dict(range=[-1, max(x_coords) + 5], title="Tầm xa (m)", gridcolor='#333'),
    yaxis=dict(range=[-0.5, max(y_coords) + 5], title="Độ cao (m)", gridcolor='#333'),
    template="plotly_dark", height=500, margin=dict(l=20, r=20, t=20, b=20),
    updatemenus=[{
        "type": "buttons", "showactive": False, "x": 0.5, "y": -0.15, "xanchor": "center",
        "buttons": [{"label": "🚀 BẮT ĐẦU THÍ NGHIỆM", "method": "animate", 
                     "args": [None, {"frame": {"duration": 16, "redraw": True}, "fromcurrent": True, "transition": {"duration": 0}}]}]
    }]
)

fig.frames = [go.Frame(data=[
    go.Scatter(x=x_coords, y=y_coords), 
    go.Scatter(x=x_coords[:i+1], y=y_coords[:i+1]), 
    go.Scatter(x=[x_coords[i]], y=[y_coords[i]])
]) for i in range(len(t_steps))]

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
c1, c2, c3 = st.columns(3)
c1.metric("📏 Tầm xa tối đa", f"{max(x_coords):.2f} m")
c2.metric("🔝 Độ cao cực đại", f"{max(y_coords):.2f} m")
c3.metric("⏱️ Tổng thời gian bay", f"{t_flight:.2f} s")

if selected_mode == MODES[3]:
    idx = (np.abs(x_coords - target_x)).argmin()
    if abs(y_coords[idx] - target_y) < 0.4:
        st.balloons()
        st.success("🎯 TUYỆT VỜI! Bóng trúng đích.")