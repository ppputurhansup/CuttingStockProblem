import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import defaultdict

# First Fit Decreasing (FFD) with Rotation
def first_fit_decreasing_rotated(orders, sheet_width):
    orders_sorted = sorted(orders, key=lambda x: max(x[0], x[1]), reverse=True)
    shelves = []
    for order in orders_sorted:
        w, l = order
        placed = False
        for shelf in shelves:
            remaining = sheet_width - sum(item[0] for item in shelf)
            feasible_orientations = []
            if w <= remaining:
                feasible_orientations.append((w, l, False))
            if l <= remaining:
                feasible_orientations.append((l, w, True))
            if feasible_orientations:
                chosen = min(feasible_orientations, key=lambda x: x[0])
                shelf.append(chosen)
                placed = True
                break
        if not placed:
            feasible_orientations = []
            if w <= sheet_width:
                feasible_orientations.append((w, l, False))
            if l <= sheet_width:
                feasible_orientations.append((l, w, True))
            if feasible_orientations:
                chosen = min(feasible_orientations, key=lambda x: x[0])
                shelves.append([chosen])
    return shelves

# Best Fit Decreasing (BFD) with Rotation
def best_fit_decreasing_rotated(orders, sheet_width):
    orders_sorted = sorted(orders, key=lambda x: max(x[0], x[1]), reverse=True)
    shelves = []
    for order in orders_sorted:
        w, l = order
        best_shelf_index = None
        best_orientation = None
        best_leftover = float('inf')
        for shelf_index, shelf in enumerate(shelves):
            remaining = sheet_width - sum(item[0] for item in shelf)
            for orientation in [(w, l, False), (l, w, True)]:
                used_w = orientation[0]
                if used_w <= remaining:
                    leftover = remaining - used_w
                    if leftover < best_leftover:
                        best_leftover = leftover
                        best_shelf_index = shelf_index
                        best_orientation = orientation
        if best_shelf_index is not None:
            shelves[best_shelf_index].append(best_orientation)
        else:
            shelves.append([(w, l, False)])
    return shelves

# Guillotine Cutting with Rotation
def guillotine_cutting_rotated(orders, sheet_width, sheet_length):
    sheets = [[(0, 0, sheet_width, sheet_length)]]
    placements = []
    orders_sorted = sorted(orders, key=lambda x: max(x[0], x[1]), reverse=True)
    for order in orders_sorted:
        w, l = order
        placed = False
        for s, free_rects in enumerate(sheets):
            for i, rect in enumerate(free_rects):
                rx, ry, rw, rh = rect
                if w <= rw and l <= rh:
                    placements.append((s, order, rx, ry, w, l, False))
                    free_rects.pop(i)
                    free_rects.extend([(rx + w, ry, rw - w, l), (rx, ry + l, rw, rh - l)])
                    placed = True
                    break
                elif l <= rw and w <= rh:
                    placements.append((s, order, rx, ry, l, w, True))
                    free_rects.pop(i)
                    free_rects.extend([(rx + l, ry, rw - l, w), (rx, ry + w, rw, rh - w)])
                    placed = True
                    break
            if placed:
                break
        if not placed:
            sheets.append([(0, 0, sheet_width, sheet_length)])
            s = len(sheets) - 1
            placements.append((s, order, 0, 0, w, l, False))
    return placements, sheets

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
        plot_data = shelves
    elif algorithm == "BFD with Rotation":
        shelves = best_fit_decreasing_rotated(orders, sheet_width)
        plot_data = shelves
    elif algorithm == "Guillotine with Rotation":
        placements, sheets = guillotine_cutting_rotated(orders, sheet_width, sheet_length)
        plot_data = sheets
    processing_time = time.time() - start

    st.subheader("📊 ผลลัพธ์การจัดวาง")
    st.write(f"⏳ ใช้เวลาในการประมวลผล: {processing_time:.4f} วินาที")
    st.write(f"📌 จำนวนแผ่นที่ใช้: {len(plot_data)}")
else:
    st.info("โปรดอัปโหลดไฟล์ CSV เพื่อดำเนินการต่อ")
