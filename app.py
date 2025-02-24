import streamlit as st
import pandas as pd
import time
from algorithms import (
    first_fit_decreasing_rotated,
    best_fit_decreasing_rotated,
    guillotine_cutting_rotated,
    plot_placements_shelf_plotly,
    plot_placements_guillotine
)

st.title("📦 Cutting Stock Problem with Rotation")

# Initialize session state
if 'calculated' not in st.session_state:
    st.session_state.calculated = False

# --- ขนาดแผ่น ---
st.header("🔖 ขนาดแผ่นเมทัลชีท")
sheet_width = st.number_input("ความกว้างแผ่น (cm)", value=91.4)
sheet_length = st.number_input("ความยาวแผ่น (cm)", value=400.0)

# --- รับออเดอร์ ---
st.header("📥 ออเดอร์")
method = st.radio("วิธีกรอกข้อมูล", ["กรอกเอง", "CSV"])

orders = []
if method == "กรอกเอง":
    num_orders = st.number_input("จำนวนออเดอร์", 1, step=1)
    for i in range(num_orders):
        cols = st.columns(2)
        w = cols[0].number_input(f"กว้าง {i+1}", key=f'w{i}', min_value=0.1)
        l = cols[1].number_input(f"ยาว {i+1}", key=f'l{i}', min_value=0.1)
        orders.append((w, l))

elif method == "CSV":
    file = st.file_uploader("อัปโหลด CSV (มีคอลัมน์ Width, Length)", type="csv")
    if file:
        df_orders = pd.read_csv(file)
        if {'Width', 'Length'}.issubset(df_orders.columns):
            orders = list(zip(df_orders['Width'], df_orders['Length']))
            st.dataframe(df_orders)
        else:
            st.error("❌ ต้องมีคอลัมน์ 'Width' และ 'Length'")

# --- ประมวลผล ---
if orders and st.button("🚀 คำนวณ"):
    results = {}

    algorithms = {
        "FFD Rotated": first_fit_decreasing_rotated,
        "BFD Rotated": best_fit_decreasing_rotated,
        "Guillotine Rotated": guillotine_cutting_rotated
    }

    total_area_orders = sum(w*l for w, l in orders)

    kpi_rows = []

    for name, algo in algorithms.items():
        start_time = time.time()
        if name != "Guillotine Rotated":
            shelves = algo(orders, sheet_width)
            sheets_used = len(shelves)
            total_waste = sum(sheet_width * sheet_length - sum(w*l for w,l,_ in shelf) for shelf in shelves)
        else:
            placements, sheets = algo(orders, sheet_width, sheet_length)
            sheets_used = len(sheets)
            total_waste = sum(sum(w*h for _,_,w,h in sheet) for sheet in sheets)

        utilization_eff = (total_area_orders / (sheets_used * sheet_width * sheet_length)) * 100
        proc_time = time.time() - start_time

        kpi_rows.append({
            "Algorithm": name,
            "Sheets Used": sheets_used,
            "Total Waste (cm²)": round(total_waste, 2),
            "Utilization Efficiency (%)": round(utilization_eff, 2),
            "Processing Time (s)": round(proc_time, 6)
        })

        results[name] = shelves if name != "Guillotine Rotated" else (placements, sheets)

    kpi_df = pd.DataFrame(kpi_rows)
    st.session_state.kpi_df = kpi_df
    st.session_state.results = results
    st.session_state.calculated = True

if st.session_state.calculated:
    st.subheader("📌 KPI Summary")
    st.dataframe(st.session_state.kpi_df)


# --- แสดงผลลัพธ์ (จะไม่หายเมื่อเลือก visualization ใหม่) ---
if st.session_state.calculated:
    st.subheader("📌 KPI")
    selected_algo = st.selectbox("🔍 เลือกอัลกอริทึมดู Visualization",
                             ["FFD Rotated", "BFD Rotated", "Guillotine Rotated"])

if selected_algo:
    st.subheader(f"📑 รายละเอียดการวาง (per sheet) ของ {selected_algo}")
    
    if selected_algo != "Guillotine Rotated":
        shelves = st.session_state.results[selected_algo]
        detail_rows = []
        for idx, shelf in enumerate(shelves, 1):
            orders_str = ", ".join([f"{w}x{l}{' (R)' if r else ''}" for w, l, r in shelf])
            waste_area = sheet_width * sheet_length - sum(w*l for w, l, _ in shelf)
            detail_rows.append({
                "Sheet": idx,
                "Orders": orders_str,
                "Orders Count": len(shelf),
                "Used Width": "N/A",
                "Waste (Area)": round(waste_area, 2),
                "Waste (Dim)": "N/A"
            })
        total_waste = sum(row["Waste (Area)"] for row in detail_rows)
        detail_rows.append({
            "Sheet": "Total",
            "Orders": "",
            "Orders Count": "",
            "Used Width": "",
            "Waste (Area)": round(total_waste, 2),
            "Waste (Dim)": ""
        })

        details_df = pd.DataFrame(detail_rows)
        st.dataframe(details_df)

        figs = plot_placements_shelf_plotly(shelves, sheet_width, sheet_length, selected_algo)
        for fig in figs:
            st.plotly_chart(fig)

    else:  # Guillotine
        placements, sheets = st.session_state.results[selected_algo]
        detail_rows = []
        for idx, sheet in enumerate(sheets, 1):
            sheet_orders = [f"{p[4]}x{p[5]}{' (R)' if p[6] else ''}" for p in placements if p[0] == idx-1]
            waste_area = sum(w*h for _,_,w,h in sheet)
            waste_dims = ", ".join([f"{w:.1f}x{h:.1f}" for _,_,w,h in sheet])
            detail_rows.append({
                "Sheet": idx,
                "Orders": ", ".join(sheet_orders),
                "Orders Count": len(sheet_orders),
                "Used Width": "N/A",
                "Waste (Area)": round(waste_area, 2),
                "Waste (Dim)": waste_dims
            })

        total_waste = sum(row["Waste (Area)"] for row in detail_rows)
        detail_rows.append({
            "Sheet": "Total",
            "Orders": "",
            "Orders Count": "",
            "Used Width": "",
            "Waste (Area)": round(total_waste, 2),
            "Waste (Dim)": ""
        })

        details_df = pd.DataFrame(detail_rows)
        st.dataframe(details_df)

        fig = plot_placements_guillotine(placements, sheets, sheet_width, sheet_length, selected_algo)
        st.pyplot(fig)
