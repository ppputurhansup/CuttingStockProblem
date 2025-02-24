import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import defaultdict

# (ใส่ฟังก์ชันทั้งหมดที่คุณมีอยู่เดิมไว้ตรงนี้)

# ฟังก์ชัน Plot สำหรับ Guillotine
def plot_placements_guillotine(placements, sheets, sheet_width, sheet_length, algorithm_name):
    sheet_groups = defaultdict(list)
    for placement in placements:
        s, order, x, y, used_w, used_l, rotated = placement
        sheet_groups[s].append((x, y, used_w, used_l, rotated))
    num_sheets = len(sheets)
    fig, axs = plt.subplots(1, num_sheets, figsize=(6*num_sheets, 6))
    if num_sheets == 1:
        axs = [axs]
    for s in range(num_sheets):
        ax = axs[s]
        sheet_rect = patches.Rectangle((0, 0), sheet_width, sheet_length, linewidth=2, edgecolor='black', facecolor='none')
        ax.add_patch(sheet_rect)
        for (x, y, used_w, used_l, rotated) in sheet_groups[s]:
            color = 'lightcoral' if not rotated else 'lightyellow'
            rect = patches.Rectangle((x, y), used_w, used_l, linewidth=1, edgecolor='red', facecolor=color, alpha=0.7)
            ax.add_patch(rect)
            ax.text(x + used_w/2, y + used_l/2, f"{used_w}x{used_l}" + (" R" if rotated else ""), ha='center', va='center', fontsize=8)
        ax.set_xlim(0, sheet_width)
        ax.set_ylim(0, sheet_length)
        ax.set_title(f"Sheet {s+1} ({algorithm_name})")
        ax.set_aspect('equal')
    st.pyplot(fig)

# Streamlit UI
st.title("Cutting Stock Problem Solver")

sheet_width = st.number_input("🔹 ความกว้างของแผ่นเมทัลชีท (cm)", min_value=1.0, value=91.4)
sheet_length = st.number_input("🔹 ความยาวของแผ่นเมทัลชีท (cm)", min_value=1.0, value=400.0)

uploaded_file = st.file_uploader("อัปโหลดไฟล์ CSV (คอลัมน์ 'Width' และ 'Length')", type=["csv"])
orders = []

algorithm = st.selectbox("เลือกอัลกอริทึม", ["FFD with Rotation", "BFD with Rotation", "Guillotine with Rotation"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if 'Width' in df.columns and 'Length' in df.columns:
        orders = list(zip(df['Width'], df['Length']))
    else:
        st.error("❌ ไฟล์ CSV ต้องมีคอลัมน์ 'Width' และ 'Length'")

if orders:
    start = time.time()
    if algorithm == "FFD with Rotation":
        shelves = first_fit_decreasing_rotated(orders, sheet_width)
        plot_placements_shelf(shelves, sheet_width, sheet_length, algorithm)
    elif algorithm == "BFD with Rotation":
        shelves = best_fit_decreasing_rotated(orders, sheet_width)
        plot_placements_shelf(shelves, sheet_width, sheet_length, algorithm)
    elif algorithm == "Guillotine with Rotation":
        placements, sheets = guillotine_cutting_rotated(orders, sheet_width, sheet_length)
        plot_placements_guillotine(placements, sheets, sheet_width, sheet_length, algorithm)
    processing_time = time.time() - start

    st.subheader("📊 ผลลัพธ์การจัดวาง")
    st.write(f"⏳ ใช้เวลาในการประมวลผล: {processing_time:.4f} วินาที")
    st.write(f"📌 จำนวนแผ่นที่ใช้: {len(shelves) if algorithm != 'Guillotine with Rotation' else len(sheets)}")
else:
    st.info("โปรดอัปโหลดไฟล์ CSV เพื่อดำเนินการต่อ")
