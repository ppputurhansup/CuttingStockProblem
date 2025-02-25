import pandas as pd
from collections import defaultdict
import plotly.graph_objects as go

# ----------------------------------------
# 1. First Fit Decreasing with Rotation
# ----------------------------------------
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
# ----------------------------------------
# 2. Best Fit Decreasing with Rotation
# ----------------------------------------
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
            feasible_orientations = []
            if w <= sheet_width:
                feasible_orientations.append((w, l, False))
            if l <= sheet_width:
                feasible_orientations.append((l, w, True))
            if feasible_orientations:
                chosen = min(feasible_orientations, key=lambda x: x[0])
                shelves.append([chosen])

    return shelves
# ----------------------------------------
# 3. Guillotine Cutting with Rotation
# ----------------------------------------
def guillotine_cutting_rotated(orders, sheet_width):
    sheets = [[]]
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
                    
                    # ✅ ปรับปรุงการสร้างพื้นที่ใหม่ (ตรวจสอบค่าติดลบ)
                    new_rects = []
                    if rw - w > 0:
                        new_rects.append((rx + w, ry, rw - w, rh))
                    if rh - l > 0:
                        new_rects.append((rx, ry + l, rw, rh - l))
                    
                    free_rects.pop(i)
                    free_rects.extend(new_rects)
                    placed = True
                    break

                elif l <= rw and w <= rh:
                    placements.append((s, order, rx, ry, l, w, True))
                    
                    # ✅ ปรับปรุงการสร้างพื้นที่ใหม่ (ตรวจสอบค่าติดลบ)
                    new_rects = []
                    if rw - l > 0:
                        new_rects.append((rx + l, ry, rw - l, rh))
                    if rh - w > 0:
                        new_rects.append((rx, ry + w, rw, rh - w))
                    
                    free_rects.pop(i)
                    free_rects.extend(new_rects)
                    placed = True
                    break

            if placed:
                break

        if not placed:
            # ✅ ถ้าวาง order ไม่ได้ ให้วางลงบนแผ่นใหม่
            new_sheet_free_rects = [(0, 0, sheet_width, float('inf'))]
            sheets.append(new_sheet_free_rects)

            placements.append((len(sheets)-1, order, 0, 0, w, l, False))
            new_rects = []
            if sheet_width - w > 0:
                new_rects.append((w, 0, sheet_width - w, l))
            new_rects.append((0, l, sheet_width, float('inf') - l))
            new_sheet_free_rects.extend(new_rects)

    return placements, sheets

# -----------------
# 📌 Plot FFD/BFD (แก้ไขให้ถูกต้อง)
# -----------------
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def plot_placements_shelf_matplotlib(shelves, sheet_width, algorithm_name):
    fig, ax = plt.subplots(figsize=(10, 6))

    y_position = 0  # กำหนดจุดเริ่มต้นที่แกน Y
    for sheet_idx, shelf in enumerate(shelves, start=1):
        x_position = 0  # เริ่มวางจากซ้ายสุด
        shelf_height = max(order[1] for order in shelf) if shelf else 0

        for order_w, order_l, rotated in shelf:
            color = "lightblue" if not rotated else "lightgreen"
            rect = patches.Rectangle((x_position, y_position), order_w, order_l, edgecolor="black", facecolor=color, linewidth=1)
            ax.add_patch(rect)

            # ใส่ Label ที่กึ่งกลางชิ้นงาน
            ax.text(x_position + order_w / 2, y_position + order_l / 2, f"{order_w}x{order_l}",
                    ha="center", va="center", fontsize=8, color="black")

            x_position += order_w  # ขยับตำแหน่ง x ไปทางขวา

        y_position += shelf_height  # ขยับไป shelf ถัดไป

    ax.set_xlim(0, sheet_width)
    ax.set_ylim(0, y_position)
    ax.set_xlabel("Width (cm)")
    ax.set_ylabel("Height (cm)")
    ax.set_title(f"{algorithm_name} Cutting Result")

    plt.gca().invert_yaxis()  # พลิกแกน Y ให้วางจากบนลงล่าง
    return fig
# -----------------
# 📌 Plot Guillotine (แก้ไขให้ถูกต้อง)
# -----------------
def plot_placements_guillotine(placements, sheets, sheet_width, sheet_length, algorithm_name):
    fig = go.Figure()

    for s, order, x, y, used_w, used_l, rotated in placements:
        color = "lightcoral" if not rotated else "lightyellow"
        fig.add_trace(go.Scatter(
            x=[x, x + used_w, x + used_w, x, x],
            y=[y, y, y + used_l, y + used_l, y],
            fill="toself",
            line=dict(color="red"),
            fillcolor=color,
            name=f"{used_w}x{used_l}" + (" R" if rotated else ""),
        ))

    fig.update_layout(
        title=f"Guillotine Cutting ({algorithm_name})",
        xaxis=dict(title="Width (cm)", range=[0, sheet_width]),
        yaxis=dict(title="Height (cm)", range=[0, sheet_length], autorange="reversed"),  # ✅ พลิกแกน Y
        showlegend=True,
        width=600, height=600
    )

    return fig
