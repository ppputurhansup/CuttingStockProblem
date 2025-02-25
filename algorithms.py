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

# -----------------
# 📌 Plot FFD/BFD (แก้ไขให้ถูกต้อง)
# -----------------
def plot_placements_shelf_plotly(shelves, sheet_width, sheet_length, algorithm_name):
    figs = []
    print(f"📌 Debug: Received shelves for {algorithm_name} =", shelves)  # ✅ Debugging

    for sheet_idx, shelf in enumerate(shelves, start=1):
        fig = go.Figure()
        y_position = 0

        for shelf_row in shelf:
            print(f"📌 Debug: Processing shelf_row =", shelf_row)  # ✅ Debugging
            if not isinstance(shelf_row, list) or not shelf_row:
                continue

            # ✅ ตรวจสอบว่าทุก `order` เป็น tuple ที่ถูกต้อง
            valid_orders = [order for order in shelf_row if isinstance(order, tuple) and len(order) == 3]
            if not valid_orders:
                print(f"⚠️ Debug: Invalid shelf_row detected =", shelf_row)
                continue

            shelf_height = max(order[1] for order in valid_orders)
            x_position = 0

            for order_w, order_l, rotated in valid_orders:
                color = "lightblue" if not rotated else "lightgreen"

                fig.add_trace(go.Scatter(
                    x=[x_position, x_position + order_w, x_position + order_w, x_position, x_position],
                    y=[y_position, y_position, y_position + order_l, y_position + order_l, y_position],
                    fill="toself",
                    line=dict(color="blue"),
                    fillcolor=color,
                    name=f"{order_w}x{order_l}" + (" R" if rotated else ""),
                ))
                x_position += order_w

            y_position += shelf_height

        fig.update_layout(
            title=f"Sheet {sheet_idx} ({algorithm_name})",
            xaxis=dict(title="Width (cm)", range=[0, sheet_width]),
            yaxis=dict(title="Height (cm)", range=[0, sheet_length], autorange="reversed"),
            showlegend=True,
            width=600, height=600
        )
        figs.append(fig)

    return figs

