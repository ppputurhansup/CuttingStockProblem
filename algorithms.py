import pandas as pd
from collections import defaultdict
import plotly.graph_objects as go

# ----------------------------------------
# 1. First Fit Decreasing with Rotation (Fixed)
# ----------------------------------------
def first_fit_decreasing_rotated(orders, sheet_width):
    orders_sorted = sorted(orders, key=lambda x: max(x[0], x[1]), reverse=True)
    shelves = [[]]  # ใช้ list เพื่อให้ไม่จำกัดความยาว

    for order in orders_sorted:
        w, l = order
        placed = False
        for shelf in shelves:
            remaining = sheet_width - sum(item[0] for item in shelf)
            orientations = [(w, l, False), (l, w, True)]
            feasible = [o for o in orientations if o[0] <= remaining]

            if feasible:
                shelf.append(min(feasible, key=lambda x: x[0]))  # เลือกแบบที่ใช้พื้นที่น้อยสุด
                placed = True
                break

        if not placed:
            orientations = [(w, l, False), (l, w, True)]
            feasible = [o for o in orientations if o[0] <= sheet_width]
            if feasible:
                shelves.append([min(feasible, key=lambda x: x[0])])

    return shelves

# ----------------------------------------
# 2. Best Fit Decreasing with Rotation (Fixed)
# ----------------------------------------
def best_fit_decreasing_rotated(orders, sheet_width):
    orders_sorted = sorted(orders, key=lambda x: max(x[0], x[1]), reverse=True)
    shelves = [[]]

    for order in orders_sorted:
        w, l = order
        best_shelf = None
        best_fit = float('inf')
        orientations = [(w, l, False), (l, w, True)]

        for shelf in shelves:
            remaining = sheet_width - sum(item[0] for item in shelf)
            for o in orientations:
                if o[0] <= remaining and remaining - o[0] < best_fit:
                    best_fit = remaining - o[0]
                    best_shelf = shelf

        if best_shelf is not None:
            best_shelf.append(min(orientations, key=lambda x: x[0]))
        else:
            feasible = [o for o in orientations if o[0] <= sheet_width]
            if feasible:
                shelves.append([min(feasible, key=lambda x: x[0])])

    return shelves

# ----------------------------------------
# 3. Guillotine Cutting with Rotation (Fixed)
# ----------------------------------------
def guillotine_cutting_rotated(orders, sheet_width):
    sheets = [[(0, 0, sheet_width, float('inf'))]]  # ไม่จำกัดความยาว
    placements = []
    orders_sorted = sorted(orders, key=lambda x: max(x[0], x[1]), reverse=True)

    for order in orders_sorted:
        w, l = order
        placed = False

        for s, free_rects in enumerate(sheets):
            for i, rect in enumerate(free_rects):
                rx, ry, rw, rh = rect
                orientations = [(w, l, False), (l, w, True)]

                for used_w, used_l, rotated in orientations:
                    if used_w <= rw and used_l <= rh:
                        placements.append((s, order, rx, ry, used_w, used_l, rotated))
                        new_rects = []
                        if rw - used_w > 0:
                            new_rects.append((rx + used_w, ry, rw - used_w, used_l))
                        if rh - used_l > 0:
                            new_rects.append((rx, ry + used_l, rw, rh - used_l))
                        free_rects.pop(i)
                        free_rects.extend(new_rects)
                        placed = True
                        break

                if placed:
                    break
            if placed:
                break

        if not placed:
            new_sheet = [(0, 0, sheet_width, float('inf'))]
            sheets.append(new_sheet)

    return placements, sheets

# -----------------
# Plot ffd/bfd (Fixed)
# -----------------
def plot_placements_shelf_plotly(shelves, sheet_width, sheet_length, algorithm_name):
    import plotly.graph_objects as go

    figs = []
    for sheet_idx, shelves in enumerate(shelves, start=1):
        fig = go.Figure()
        y_position = 0  # ✅ ตำแหน่งเริ่มต้น

        for shelf in shelves:
            if not isinstance(shelf, list) or len(shelf) == 0:  # ✅ แก้ให้เช็คว่าต้องเป็น list เท่านั้น
                continue

            shelf_height = max(order[1] for order in shelf)  # ✅ ต้องแน่ใจว่า shelf ไม่ใช่ int
            x_position = 0

            for order_w, order_l, rotated in shelf:
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

            y_position += shelf_height  # ✅ ขยับลงมา

        fig.update_layout(
            title=f"Sheet {sheet_idx} ({algorithm_name})",
            xaxis=dict(title="Width (cm)", range=[0, sheet_width]),
            yaxis=dict(title="Height (cm)", range=[0, sheet_length]),
            showlegend=True,
            width=600, height=600
        )

        figs.append(fig)

    return figs

# -----------------
# Plot guillotine (Fixed)
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
        yaxis=dict(title="Height (cm)", range=[0, sheet_length]),
        showlegend=True,
        width=600, height=600
    )

    return fig
