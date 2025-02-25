import streamlit as st
import pandas as pd
from algorithms import (
    first_fit_decreasing_rotated,
    best_fit_decreasing_rotated,
    guillotine_cutting_rotated,
    plot_placements_shelf_matplotlib,
    plot_placements_guillotine
)
import time

st.title("📦 Cutting Stock Problem with Unlimited Length")

# --- รับขนาดแผ่น ---
st.header("🔖 กำหนดขนาดแผ่นเมทัลชีท")
sheet_width = st.number_input("ความกว้างของแผ่นเมทัลชีท (cm)", min_value=0.1, value=91.4)

# --- รับออเดอร์ ---
st.header("📥 เพิ่มออเดอร์")
input_method = st.radio("เลือกวิธีกรอกข้อมูลออเดอร์", ["กรอกข้อมูลเอง", "อัปโหลดไฟล์ CSV"])

orders = []
if input_method == "กรอกข้อมูลเอง":
    num_orders = st.number_input("จำนวนออเดอร์ที่ต้องการกรอก", min_value=1, step=1)
    for i in range(num_orders):
        col1, col2 = st.columns(2)
        with col1:
            width = st.number_input(f"ความกว้างออเดอร์ที่ {i+1} (cm)", min_value=0.1, key=f'w{i}')
        with col2:
            length = st.number_input(f"ความยาวออเดอร์ที่ {i+1} (cm)", min_value=0.1, key=f'l{i}')
        orders.append((width, length))

elif input_method == "อัปโหลดไฟล์ CSV":
    uploaded_file = st.file_uploader("อัปโหลดไฟล์ CSV (ต้องมีคอลัมน์ 'Width' และ 'Length')", type="csv")
    if uploaded_file:
        df_orders = pd.read_csv(uploaded_file)
        if "Width" in df_orders.columns and "Length" in df_orders.columns:
            orders = list(zip(df_orders["Width"], df_orders["Length"]))
            st.dataframe(df_orders)
        else:
            st.error("ไฟล์ CSV ต้องมีคอลัมน์ 'Width' และ 'Length'")

# --- คำนวณเมื่อมีข้อมูลครบ ---
if orders and st.button("🚀 คำนวณ"):
    results = {}
    algorithms = {
        "FFD Rotated": first_fit_decreasing_rotated,
        "BFD Rotated": best_fit_decreasing_rotated,
        "Guillotine Rotated": guillotine_cutting_rotated
    }

    kpi_rows = []
    total_used_area = sum(w * l for w, l in orders)
    max_sheet_length = 99999  # ✅ ไม่มีข้อจำกัดด้านความยาว ใช้ 99999

    for name, algo in algorithms.items():
        start_time = time.time()

        if name != "Guillotine Rotated":
            shelves = algo(orders, sheet_width)
            sheets_used = len(shelves)
            total_shelf_area = sum(sum(w * l for w, l, _ in shelf) for shelf in shelves)
            total_waste = sheets_used * sheet_width * max_sheet_length - total_shelf_area

        else:
            placements, sheets = algo(orders, sheet_width)
            sheets_used = len(sheets)
            
            # ✅ แก้การคำนวณ Used Area
            used_area = sum(used_w * used_l for _, _, _, _, used_w, used_l, _ in placements)
            total_sheet_area = sheets_used * sheet_width * max_sheet_length  
            total_waste = total_sheet_area - used_area

        # ✅ Efficiency เป็น % เต็ม (0.31 → 31%)
        utilization_eff = (total_used_area / (sheets_used * sheet_width * max_sheet_length)) * 100

        proc_time = time.time() - start_time

        kpi_rows.append({
            "Algorithm": name,
            "Total Waste (cm²)": round(total_waste, 2),
            "Utilization Efficiency (%)": f"{round(utilization_eff, 2)}%",  # ✅ แสดงเป็น %
            "Processing Time (s)": round(proc_time, 6)
        })

        results[name] = shelves if name != "Guillotine Rotated" else (placements, sheets)

    st.session_state.kpi_df = pd.DataFrame(kpi_rows)
    st.session_state.results = results
    st.session_state.calculated = True

if "calculated" not in st.session_state:
    st.session_state.calculated = False
if "results" not in st.session_state:
    st.session_state.results = {}
if "kpi_df" not in st.session_state:
    st.session_state.kpi_df = pd.DataFrame()

# --- แสดงผล KPI และ Visualization ---
if st.session_state.calculated:
    st.subheader("📌 KPI Summary")
    st.dataframe(st.session_state.kpi_df)

    selected_algo = st.selectbox("🔍 เลือกอัลกอริทึมดู Visualization",
                                 ["FFD Rotated", "BFD Rotated", "Guillotine Rotated"])

    if selected_algo:
        st.subheader(f"📑 รายละเอียดการวาง (per sheet) ของ {selected_algo}")
        
        if selected_algo != "Guillotine Rotated":
            shelves = st.session_state.results[selected_algo]
        
            # 🔥 ใช้ Matplotlib แทน
            fig = plot_placements_shelf_matplotlib(shelves, sheet_width, selected_algo)
            st.pyplot(fig)

        else:
            placements, sheets = st.session_state.results[selected_algo]
            fig = plot_placements_guillotine(placements, sheets, sheet_width, max_sheet_length, selected_algo)
            st.plotly_chart(fig)
