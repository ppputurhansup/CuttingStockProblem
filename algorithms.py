import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.patches as patches  # เพิ่มบรรทัดนี้


# ----------------------------------------
# 1. First Fit Decreasing with rotation
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
            else:
                print("❌ Order", order, "ไม่สามารถวางบนแผ่นใหม่ได้")
    return shelves
# ----------------------------------------
# 2. Best Fit Decreasing with rotation
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
            else:
                print("❌ Order", order, "ไม่สามารถวางบนแผ่นใหม่ได้")
    return shelves

# ----------------------------------------
# 3. Guillotine Cutting with Rotation
# ----------------------------------------
def guillotine_cutting_rotated(orders, sheet_width):
    sheets = [[]]  # ใช้ list แทนเพื่อให้ไม่จำกัดความยาว
    placements = []
    orders_sorted = sorted(orders, key=lambda x: max(x[0], x[1]), reverse=True)

    for order in orders_sorted:
        w, l = order
        placed = False

        for s, free_rects in enumerate(sheets):
            for i, rect in enumerate(free_rects):
                rx, ry, rw, rh = rect
                # Orientation ปกติ
                if w <= rw and l <= rh:
                    placements.append((s, order, rx, ry, w, l, False))
                    new_rects = []
                    if rw - w > 0:
                        new_rects.append((rx+w, ry, rw - w, l))
                    if rh - l > 0:
                        new_rects.append((rx, ry+l, rw, rh - l))
                    free_rects.pop(i)
                    free_rects.extend(new_rects)
                    placed = True
                    break
                # Orientation rotate
                elif l <= rw and w <= rh:
                    placements.append((s, order, rx, ry, l, w, True))
                    new_rects = []
                    if rw - l > 0:
                        new_rects.append((rx+l, ry, rw - l, w))
                    if rh - w > 0:
                        new_rects.append((rx, ry+w, rw, rh - w))
                    free_rects.pop(i)
                    free_rects.extend(new_rects)
                    placed = True
                    break
            if placed:
                break

        if not placed:
            new_sheet_free_rects = [(0, 0, sheet_width, float('inf'))]  # ไม่จำกัดความยาว
            sheets.append(new_sheet_free_rects)
            s = len(sheets) - 1
            feasible_orientations = []
            if w <= sheet_width:
                feasible_orientations.append((w, l, False))
            if l <= sheet_width:
                feasible_orientations.append((l, w, True))
            if feasible_orientations:
                chosen = min(feasible_orientations, key=lambda x: x[0])
                used_w, used_l, rotated = chosen
                placements.append((s, order, 0, 0, used_w, used_l, rotated))
                new_rects = []
                if sheet_width - used_w > 0:
                    new_rects.append((used_w, 0, sheet_width - used_w, used_l))
                new_sheet_free_rects.pop(0)
                new_sheet_free_rects.extend(new_rects)
            else:
                print("❌ Order", order, "ไม่สามารถวางบนแผ่นใหม่ได้")

    return placements, sheets
    
# ---------------
# Plot ffd/bfd
# ---------------
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
from collections import defaultdict

import plotly.graph_objects as go

def plot_placements_shelf_plotly(shelves, sheet_width, sheet_length, algorithm_name):
    figs = []

    for sheet_idx, shelf in enumerate(shelves):
        fig = go.Figure()

        # เพิ่มพื้นหลัง (แผ่นเมทัลชีท)
        fig.add_shape(type="rect",
                      x0=0, y0=0, x1=sheet_width, y1=sheet_length,
                      line=dict(color="black", width=3),
                      fillcolor="white")

        y_position = 0
        shelf_height = max(item[1] for item in shelf)
        x_position = 0

        for order_w, order_l, rotated in shelf:
            fig.add_shape(type="rect",
                          x0=x_position, y0=y_position,
                          x1=x_position+order_w, y1=y_position+order_l,
                          line=dict(color="RoyalBlue"),
                          fillcolor="LightSkyBlue" if not rotated else "LightGreen",
                          opacity=0.7)

            # เพิ่ม label บอกขนาด
            fig.add_annotation(x=x_position+order_w/2, y=y_position+order_l/2,
                               text=f"{order_w}x{order_l}" + (" (R)" if rotated else ""),
                               showarrow=False,
                               font=dict(color="black", size=12))

            x_position += order_w

        fig.update_layout(
            title=f"Sheet {sheet_idx+1} ({algorithm_name})",
            xaxis=dict(range=[0, sheet_width], showgrid=False, zeroline=False),
            yaxis=dict(range=[0, sheet_length], showgrid=False, zeroline=False, scaleanchor='x'),
            width=600,
            height=800,
            plot_bgcolor='white'
        )

        figs.append(fig)

    return figs

# -----------------
# Plot guillotine
# -----------------

def plot_placements_guillotine(placements, sheets, sheet_width, sheet_length, algorithm_name):
    sheet_groups = defaultdict(list)
    for placement in placements:
        s, order, x, y, used_w, used_l, rotated = placement
        sheet_groups[s].append((x, y, used_w, used_l, rotated))

    num_sheets = len(sheets)
    fig, axs = plt.subplots(1, num_sheets, figsize=(6*num_sheets, 8))
    if num_sheets == 1:
        axs = [axs]

    for s in range(num_sheets):
        ax = axs[s]
        ax.add_patch(patches.Rectangle((0,0), sheet_width, sheet_length, linewidth=2, edgecolor='black', facecolor='none'))

        for (x, y, used_w, used_l, rotated) in sheet_groups[s]:
            color = 'lightcoral' if not rotated else 'lightyellow'
            ax.add_patch(patches.Rectangle((x,y), used_w, used_l, linewidth=1, edgecolor='red', facecolor=color, alpha=0.7))
            ax.text(x + used_w/2, y + used_l/2, f"{used_w}x{used_l}" + (" R" if rotated else ""), ha='center', va='center', fontsize=8)

        ax.set_xlim(0, sheet_width)
        ax.set_ylim(0, sheet_length)
        ax.set_title(f"Sheet {s+1} ({algorithm_name})")
        ax.set_aspect('equal')

    plt.tight_layout()

    return fig  

# ----------------------------
# ฟังก์ชันหลัก
# ----------------------------
def main():
    print("=== Cutting Stock Problem with Rotation ===")
    sheet_width, sheet_length = get_sheet_size()
    orders = get_orders()
    if not orders:
        print("❌ ไม่มีออเดอร์ที่ต้องประมวลผล")
        return

    total_used_area = sum(w * l for w, l in orders)
    sheet_area = sheet_width * sheet_length
