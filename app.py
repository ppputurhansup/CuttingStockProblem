import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# First Fit Decreasing (FFD) with Rotation
def first_fit_decreasing_rotated(orders, sheet_width):
    orders_sorted = sorted(orders, key=lambda x: max(x[0], x[1]), reverse=True)
    shelves = []
    for order in orders_sorted:
        w, l = order
        placed = False
        for shelf in shelves:
            remaining = sheet_width - sum(item[0] for item in shelf)
            if w <= remaining:
                shelf.append((w, l, False))
                placed = True
                break
            if l <= remaining:
                shelf.append((l, w, True))
                placed = True
                break
        if not placed:
            shelves.append([(w, l, False)])
    return shelves

# Plotting function
def plot_placements_shelf(shelves, sheet_width, sheet_length, algorithm_name):
    num_sheets = len(shelves)
    fig, axs = plt.subplots(1, num_sheets, figsize=(6*num_sheets, 6))
    if num_sheets == 1:
        axs = [axs]
    for i, shelf in enumerate(shelves):
        ax = axs[i]
        sheet_rect = patches.Rectangle((0, 0), sheet_width, sheet_length, linewidth=2, edgecolor='black', facecolor='none')
        ax.add_patch(sheet_rect)
        current_x = 0
        for order in shelf:
            used_w, used_l, rotated = order
            color = 'lightblue' if not rotated else 'lightgreen'
            order_rect = patches.Rectangle((current_x, 0), used_w, used_l, linewidth=1, edgecolor='blue', facecolor=color, alpha=0.7)
            ax.add_patch(order_rect)
            ax.text(current_x + used_w/2, used_l/2, f"{used_w}x{used_l}" + (" R" if rotated else ""), ha='center', va='center', fontsize=8)
            current_x += used_w
        ax.set_xlim(0, sheet_width)
        ax.set_ylim(0, sheet_length)
        ax.set_title(f"Sheet {i+1} ({algorithm_name})")
        ax.set_aspect('equal')
    st.pyplot(fig)

# Streamlit UI
st.title("Cutting Stock Problem Solver")

sheet_width = st.number_input("🔹 ความกว้างของแผ่นเมทัลชีท (cm)", min_value=1.0, value=91.4)
sheet_length = st.number_input("🔹 ความยาวของแผ่นเมทัลชีท (cm)", min_value=1.0, value=400.0)

uploaded_file = st.file_uploader("อัปโหลดไฟล์ CSV (คอลัมน์ 'Width' และ 'Length')", type=["csv"])
orders = []

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if 'Width' in df.columns and 'Length' in df.columns:
        orders = list(zip(df['Width'], df['Length']))
    else:
        st.error("❌ ไฟล์ CSV ต้องมีคอลัมน์ 'Width' และ 'Length'")

if orders:
    start = time.time()
    shelves = first_fit_decreasing_rotated(orders, sheet_width)
    processing_time = time.time() - start

    st.subheader("📊 ผลลัพธ์การจัดวาง")
    st.write(f"⏳ ใช้เวลาในการประมวลผล: {processing_time:.4f} วินาที")
    st.write(f"📌 จำนวนแผ่นที่ใช้: {len(shelves)}")
    plot_placements_shelf(shelves, sheet_width, sheet_length, "FFD")
else:
    st.info("โปรดอัปโหลดไฟล์ CSV เพื่อดำเนินการต่อ")
