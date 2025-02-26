import streamlit as st
import pandas as pd
from algorithms import(
    first_fit_decreasing_rotated,
    best_fit_decreasing_rotated,
    guillotine_cutting_rotated,
    plot_placements_shelf_matplotlib,
    plot_placements_guillotine
)
import time

st.title("📦 Cutting Stock Problem with Unlimited Length")

# --- กำหนดขนาดแผ่น ---
st.header("🔖 กำหนดขนาดแผ่นเมทัลชีท")
sheet_width = st.number_input("ความกว้างของแผ่นเมทัลชีท (cm)", min_value=0.1, value=91.4)
# ✅ เพิ่มช่อง input "ราคา/เมตร"
st.header("💰 กำหนดราคาเมทัลชีท")
price_per_meter = st.number_input("ราคาเมทัลชีท (บาท/เมตร)", min_value=0.1, value=100.0)

# ✅ แปลงราคา/เมตร → ราคา/เมตร²
price_per_m2 = price_per_meter / (sheet_width / 100)  # (บาท/เมตร) ÷ (เมตร)
# ✅ **กำหนดค่าเริ่มต้นให้ orders**
orders = []  

# --- รับออเดอร์ ---
st.header("📥 เพิ่มออเดอร์")
input_method = st.radio("เลือกวิธีกรอกข้อมูลออเดอร์", ["กรอกข้อมูลเอง", "อัปโหลดไฟล์ CSV"])

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

# ✅ **ตรวจสอบว่า orders มีข้อมูลก่อนคำนวณ**
if orders and st.button("🚀 คำนวณ"):
    results = {}
    algorithms = {
        "FFD Rotated": first_fit_decreasing_rotated,
        "BFD Rotated": best_fit_decreasing_rotated,
        "Guillotine Rotated": guillotine_cutting_rotated
    }

    kpi_rows = []
    total_used_area = sum(w * l for w, l in orders)  

    for name, algo in algorithms.items():
        start_time = time.time()
        if name != "Guillotine Rotated":
            shelves = algo(orders, sheet_width)

            max_used_length_per_sheet = [max(l for _, l, *_ in shelf) for shelf in shelves]
            total_used_length = sum(max_used_length_per_sheet)

            total_sheet_area = sheet_width * total_used_length
        else:
            placements, sheets = algo(orders, sheet_width)
            total_used_length = max((y + used_l) for _, _, _, y, _, used_l, _ in placements) if placements else 0
            total_sheet_area = sheet_width * total_used_length

        total_waste = max(0, total_sheet_area - total_used_area)
        utilization_eff = min((total_used_area / total_sheet_area) * 100 if total_sheet_area > 0 else 0, 100)
        
        # ✅ **คำนวณ "ราคาขาย" และ "ค่าเสียโอกาส" โดยแปลง cm² → m²**
        total_sheet_area_m2 = total_sheet_area / 10_000  # แปลง cm² → m²
        total_waste_m2 = total_waste / 10_000  # แปลง cm² → m²

        price_sold = price_per_m2 * total_sheet_area_m2
        price_lost = price_per_m2 * total_waste_m2

        proc_time = time.time() - start_time

        kpi_rows.append({
            "Algorithm": name,
            "Length Used (cm)": round(total_used_length, 2),
            "Total Waste (cm²)": round(total_waste, 2),
            "Utilization Efficiency (%)": f"{round(utilization_eff, 2)}%",
            "Processing Time (s)": round(proc_time, 6)
            "📈 ราคาขาย (บาท)": f"{round(price_sold, 2):,}",
            "📉 ค่าเสียโอกาส (บาท)": f"{round(price_lost, 2):,}"
        })

        results[name] = shelves if name != "Guillotine Rotated" else (placements, sheets, total_used_length)

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
            placements, sheets, total_used_length = st.session_state.results[selected_algo]
            fig = plot_placements_guillotine(placements, sheets, sheet_width, total_used_length, selected_algo)
            st.plotly_chart(fig)
