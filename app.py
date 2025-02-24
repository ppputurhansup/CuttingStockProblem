import streamlit as st
from algorithms import (
    first_fit_decreasing_rotated,
    best_fit_decreasing_rotated,
    guillotine_cutting_rotated,
    plot_placements_shelf,
    plot_placements_guillotine
)
import pandas as pd
import matplotlib.pyplot as plt

st.title("📦 Cutting Stock Problem with Rotation")

# --- รับขนาดแผ่น ---
st.header("🔖 กำหนดขนาดแผ่นเมทัลชีท")
sheet_width = st.number_input("ความกว้างของแผ่นเมทัลชีท (cm)", min_value=0.0, value=91.4)
sheet_length = st.number_input("ความยาวของแผ่นเมทัลชีท (cm)", min_value=0.0, value=400.0)

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
if orders and st.button("🚀 เริ่มคำนวณ"):
    total_used_area = sum(w * l for w, l in orders)
    sheet_area = sheet_width * sheet_length

    # เรียกใช้อัลกอริทึม
    shelves_ffd = first_fit_decreasing_rotated(orders, sheet_width)
    shelves_bfd = best_fit_decreasing_rotated(orders, sheet_width)
    placements_guillotine, sheets_guillotine = guillotine_cutting_rotated(orders, sheet_width, sheet_length)

    # แสดง KPI
    df_kpi = pd.DataFrame({
        "Algorithm": ["FFD with Rotation", "BFD with Rotation", "Guillotine with Rotation"],
        "Sheets Used": [len(shelves_ffd), len(shelves_bfd), len(sheets_guillotine)]
    })

    st.subheader("📌 KPI Summary")
    st.dataframe(df_kpi)

    # เลือกแสดง Visualization
    selected_algo = st.selectbox("🔍 เลือกอัลกอริทึมที่ต้องการแสดง Visualization",
                                 ["FFD with Rotation", "BFD with Rotation", "Guillotine with Rotation"])

    if selected_algo == "FFD with Rotation":
        fig = plot_placements_shelf(shelves_ffd, sheet_width, sheet_length, selected_algo)
        st.pyplot(fig)

    elif selected_algo == "BFD with Rotation":
        fig = plot_placements_shelf(shelves_bfd, sheet_width, sheet_length, selected_algo)
        st.pyplot(fig)

    elif selected_algo == "Guillotine with Rotation":
        fig = plot_placements_guillotine(placements_guillotine, sheets_guillotine, sheet_width, sheet_length, selected_algo)
        st.pyplot(fig)
