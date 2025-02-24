import streamlit as st
import pandas as pd
from algorithms import (
    first_fit_decreasing_rotated,
    best_fit_decreasing_rotated,
    guillotine_cutting_rotated,
    plot_placements_shelf_plotly,  # <-- เปลี่ยนมาเรียกตัวนี้แทน
    plot_placements_guillotine
)

st.title("📦 Cutting Stock Problem with Rotation")

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
    shelves_ffd = first_fit_decreasing_rotated(orders, sheet_width)
    shelves_bfd = best_fit_decreasing_rotated(orders, sheet_width)
    placements_guillotine, sheets_guillotine = guillotine_cutting_rotated(orders, sheet_width, sheet_length)

    kpi = pd.DataFrame({
        "Algorithm": ["FFD Rotated", "BFD Rotated", "Guillotine Rotated"],
        "Sheets Used": [len(shelves_ffd), len(shelves_bfd), len(sheets_guillotine)]
    })
    st.subheader("📌 KPI")
    st.dataframe(kpi)

    selected_algo = st.selectbox("🔍 เลือกอัลกอริทึมดู Visualization",
                                 ["FFD Rotated", "BFD Rotated", "Guillotine Rotated"])

    if selected_algo == "FFD Rotated":
        figs = plot_placements_shelf_plotly(shelves_ffd, sheet_width, sheet_length, selected_algo)
        for fig in figs:
            st.plotly_chart(fig)

    elif selected_algo == "BFD Rotated":
        figs = plot_placements_shelf_plotly(shelves_bfd, sheet_width, sheet_length, selected_algo)
        for fig in figs:
            st.plotly_chart(fig)

    elif selected_algo == "Guillotine Rotated":
        fig = plot_placements_guillotine(placements_guillotine, sheets_guillotine, sheet_width, sheet_length, selected_algo)
        st.pyplot(fig)
