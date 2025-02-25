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
    placements = []
    free_rects = [(0, 0, sheet_width, float('inf'))]  # ✅ ไม่มีข้อจำกัดความยาว
    orders_sorted = sorted(orders, key=lambda x: max(x[0], x[1]), reverse=True)

    for order in orders_sorted:
        w, l = order
        placed = False

        for i, (rx, ry, rw, rh) in enumerate(free_rects):
            if w <= rw and l <= rh:
                placements.append((rx, ry, w, l, False))
                new_rects = [(rx + w, ry, rw - w, rh), (rx, ry + l, rw, rh - l)]
                free_rects.pop(i)
                free_rects.extend([r for r in new_rects if r[2] > 0 and r[3] > 0])
                placed = True
                break
            elif l <= rw and w <= rh:
                placements.append((rx, ry, l, w, True))
                new_rects = [(rx + l, ry, rw - l, rh), (rx, ry + w, rw, rh - w)]
                free_rects.pop(i)
                free_rects.extend([r for r in new_rects if r[2] > 0 and r[3] > 0])
                placed = True
                break

        if not placed:
            new_y = max(y + h for _, y, _, h in placements) if placements else 0
            free_rects.append((0, new_y, sheet_width, float('inf')))
            placements.append((0, new_y, w, l, False))

    return placements

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
def plot_placements_guillotine(placements, sheet_width, algorithm_name):
    fig = go.Figure()

    for x, y, w, l, rotated in placements:
        color = "lightcoral" if not rotated else "lightyellow"
        fig.add_trace(go.Scatter(
            x=[x, x + w, x + w, x, x],
            y=[y, y, y + l, y + l, y],
            fill="toself",
            line=dict(color="red"),
            fillcolor=color,
            name=f"{w}x{l}" + (" R" if rotated else ""),
        ))

    fig.update_layout(
        title=f"Guillotine Cutting ({algorithm_name})",
        xaxis=dict(title="Width (cm)", range=[0, sheet_width]),
        yaxis=dict(title="Height (cm)", autorange="reversed"),  # ✅ แก้ให้วางจากบนลงล่าง
        showlegend=True,
        width=600, height=600
    )

    return fig
