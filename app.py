import streamlit as st
import pandas as pd
from algorithms import (
    first_fit_decreasing_rotated,
    best_fit_decreasing_rotated,
    guillotine_cutting_rotated,
    plot_placements_shelf_plotly,
    plot_placements_guillotine
)
import time

st.title("📦 Cutting Stock Problem with Unlimited Length")

# --- รับขนาดแผ่น ---
st.header("🔖 กำหนดขนาดแผ่นเมทัลชีท")
sheet_width = st.number_input("ความกว้างของแผ่นเมทัลชีท (cm)", min_value=0.0, value=91.4)

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

# --- เริ่มคำนวณเมื่อมีข้อมูลครบ ---
if orders and st.button("🚀 คำนวณ"):
    total_used_area = sum(w * l for w, l in orders)

    results = {}
    algorithms = {
        "FFD Rotated": first_fit_decreasing_rotated,
        "BFD Rotated": best_fit_decreasing_rotated,
        "Guillotine Rotated": guillotine_cutting_rotated
    }

    kpi_rows = []

    for name, algo in algorithms.items():
        start_time = time.time()
        if name != "Guillotine Rotated":
            shelves = algo(orders, sheet_width)
            sheets_used = len(shelves)

            # ✅ คำนวณ Waste ใหม่ (ไม่ต้องใช้ `sheet_length`)
            total_waste = sum(sheet_width - sum(w for w, _, _ in shelf) for shelf in shelves)

        else:
            placements, sheets = algo(orders, sheet_width)
            sheets_used = len(sheets)
            total_waste = sum(sum(rw * rh for (_, _, rw, rh) in sheet) for sheet in sheets)

        total_shelf_area = sum(sum(w * l for w, l, _ in shelf) for shelf in shelves) if name != "Guillotine Rotated" else total_used_area
        utilization_eff = (total_shelf_area / (sheets_used * sheet_width * 99999)) * 100  # ใช้ค่าความยาวสูงมากแทน
        proc_time = time.time() - start_time

        kpi_rows.append({
            "Algorithm": name,
            "Sheets Used": sheets_used,
            "Total Waste (cm²)": round(total_waste, 2),
            "Utilization Efficiency (%)": round(utilization_eff, 2),
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

if st.session_state.calculated:
    st.subheader("📌 KPI Summary")
    st.dataframe(st.session_state.kpi_df)

    selected_algo = st.selectbox("🔍 เลือกอัลกอริทึมดู Visualization",
                                 ["FFD Rotated", "BFD Rotated", "Guillotine Rotated"])

if selected_algo:
st.subheader(f"📑 รายละเอียดการวาง (per sheet) ของ {selected_algo}")

    if selected_algo != "Guillotine Rotated":
        shelves = st.session_state.results[selected_algo]
        figs = plot_placements_shelf_plotly(shelves, sheet_width, 99999, selected_algo)
        for fig in figs:
            st.plotly_chart(fig)

    else:
        placements, sheets = st.session_state.results[selected_algo]
        fig = plot_placements_guillotine(placements, sheets, sheet_width, 99999, selected_algo)
        st.plotly_chart(fig)  # ✅ ใช้ st.plotly_chart แทน st.pyplot

