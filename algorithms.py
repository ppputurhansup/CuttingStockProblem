import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.patches as patches  # เพิ่มบรรทัดนี้


# ----------------------------
# 1. First Fit Decreasing (FFD) with Rotation (fixed)
# ----------------------------
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
                shelves.append(chosen)
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

# ----------------------------
# 2. Best Fit Decreasing (BFD) with Rotation (fixed)
# ----------------------------
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
                shelves.append([chosen])  # แก้ตรงนี้แล้ว
            else:
                print("❌ Order", order, "ไม่สามารถวางบนแผ่นใหม่ได้")
    return shelves

# ----------------------------
# 3. Guillotine Cutting with Rotation
# ----------------------------
def guillotine_cutting_rotated(orders, sheet_width, sheet_length):
    sheets = [ [(0, 0, sheet_width, sheet_length)] ]
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
            new_sheet_free_rects = [(0, 0, sheet_width, sheet_length)]
            sheets.append(new_sheet_free_rects)
            s = len(sheets) - 1
            feasible_orientations = []
            if w <= sheet_width and l <= sheet_length:
                feasible_orientations.append((w, l, False))
            if l <= sheet_width and w <= sheet_length:
                feasible_orientations.append((l, w, True))
            if feasible_orientations:
                chosen = min(feasible_orientations, key=lambda x: x[0])
                used_w, used_l, rotated = chosen
                placements.append((s, order, 0, 0, used_w, used_l, rotated))
                new_rects = []
                if sheet_width - used_w > 0:
                    new_rects.append((used_w, 0, sheet_width - used_w, used_l))
                if sheet_length - used_l > 0:
                    new_rects.append((0, used_l, sheet_width, sheet_length - used_l))
                new_sheet_free_rects.pop(0)
                new_sheet_free_rects.extend(new_rects)
            else:
                print("❌ Order", order, "ไม่สามารถวางบนแผ่นใหม่ได้")
    return placements, sheets
# ----------------------------
# สร้างตารางสรุปรายละเอียด per sheet สำหรับ shelf 2 มิติ
# ----------------------------
def get_shelf_summary_ffd(sheets, sheet_width, sheet_length, algorithm_name):
    rows = []
    total_waste = 0

    for sheet_idx, sheet in enumerate(sheets, start=1):
        orders_details = []
        used_area = 0
        used_height = 0

        for shelf in sheet:
            shelf_height = max(order[1] for order in shelf)
            shelf_width_used = sum(order[0] for order in shelf)
            for order_w, order_l, rotated in shelf:
                detail = f"{order_w}x{order_l}"
                if rotated:
                    detail += " (R)"
                orders_details.append(detail)
                used_area += order_w * order_l
            used_height += shelf_height

        waste_area = (sheet_width * used_height) - used_area
        total_waste += waste_area

        rows.append({
            "Sheet": sheet_idx,
            "Orders": ", ".join(orders_details),
            "Orders Count": len(orders_details),
            "Used Area": used_area,
            "Used Height": used_height,
            "Waste (Area)": waste_area,
            "Algorithm": algorithm_name
        })

    rows.append({
        "Sheet": "Total",
        "Orders": "",
        "Orders Count": "",
        "Used Area": "",
        "Used Height": "",
        "Waste (Area)": total_waste,
        "Algorithm": algorithm_name
    })

    return pd.DataFrame(rows)


# ----------------------------
# สร้างตารางสรุปรายละเอียด per sheet สำหรับ Guillotine
# ----------------------------
def get_sheet_summary_guillotine(placements, sheets, sheet_width, sheet_length, algorithm_name):
    sheet_groups = defaultdict(list)
    for placement in placements:
        s, order, x, y, used_w, used_l, rotated = placement
        sheet_groups[s].append((used_w, used_l, rotated))
    rows = []
    for s in range(len(sheets)):
        shelf_placements = sheet_groups.get(s, [])
        orders_details = []
        for used_w, used_l, rotated in shelf_placements:
            detail = f"{used_w}x{used_l}"
            if rotated:
                detail += " (R)"
            orders_details.append(detail)
        orders_str = ", ".join(orders_details)
        count_orders = len(shelf_placements)
        free_rects = sheets[s]
        waste_area = sum(rw * rh for (_, _, rw, rh) in free_rects)
        waste_dims = ", ".join([f"{rw:.1f}x{rh:.1f}" for (_, _, rw, rh) in free_rects])
        rows.append({
            "Sheet": s+1,
            "Orders": orders_str,
            "Orders Count": count_orders,
            "Used Width": "N/A",
            "Waste (Area)": waste_area,
            "Waste (Dim)": waste_dims,
            "Algorithm": algorithm_name
        })
    total_waste = sum(row["Waste (Area)"] for row in rows)
    rows.append({
        "Sheet": "Total",
        "Orders": "",
        "Orders Count": "",
        "Used Width": "",
        "Waste (Area)": total_waste,
        "Waste (Dim)": "",
        "Algorithm": algorithm_name
    })
    return pd.DataFrame(rows)

# ----------------------------
# ฟังก์ชัน Plot shelf 2 มิติ (สำหรับ FFD/BFD)
# ----------------------------
def plot_placements_shelf(sheets, sheet_width, sheet_length, algorithm_name):
    num_sheets = len(sheets)
    fig, axs = plt.subplots(1, num_sheets, figsize=(6*num_sheets, 8))

    if num_sheets == 1:
        axs = [axs]

    for sheet_idx, shelves in enumerate(sheets):
        ax = axs[sheet_idx]
        y_position = 0
        sheet_rect = patches.Rectangle((0, 0), sheet_width, sheet_length, linewidth=2, edgecolor='black', facecolor='none')
        ax.add_patch(sheet_rect)

        for shelf in shelves:
            shelf_height = max(item[1] for item in shelf)
            x_position = 0

            for order_w, order_l, rotated in shelf:
                color = 'lightblue' if not rotated else 'lightgreen'
                order_rect = patches.Rectangle((x_position, y_position), order_w, order_l, linewidth=1, edgecolor='blue', facecolor=color, alpha=0.7)
                ax.add_patch(order_rect)
                ax.text(x_position + order_w/2, y_position + order_l/2, f"{order_w}x{order_l}" + (" R" if rotated else ""), ha='center', va='center', fontsize=8)
                x_position += order_w

            y_position += shelf_height

        ax.set_xlim(0, sheet_width)
        ax.set_ylim(0, sheet_length)
        ax.set_title(f"Sheet {sheet_idx+1} ({algorithm_name})")
        ax.set_aspect('equal')

    plt.suptitle(f"Order Placements for {algorithm_name}")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

# ----------------------------
# ฟังก์ชัน Plot สำหรับ Guillotine
# ----------------------------
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
    plt.suptitle(f"Order Placements for {algorithm_name}")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

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
