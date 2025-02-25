# --- คำนวณเมื่อมีข้อมูลครบ ---
if orders and st.button("🚀 คำนวณ"):
    results = {}
    algorithms = {
        "FFD Rotated": first_fit_decreasing_rotated,
        "BFD Rotated": best_fit_decreasing_rotated,
        "Guillotine Rotated": guillotine_cutting_rotated
    }

    kpi_rows = []
    total_used_area = sum(w * l for w, l in orders)  # ✅ คำนวณพื้นที่ทั้งหมดที่ใช้จริง

    for name, algo in algorithms.items():
        start_time = time.time()
        if name != "Guillotine Rotated":
            shelves = algo(orders, sheet_width)

            # ✅ หาค่าความยาวสูงสุดของแต่ละแผ่น (ความยาวสูงสุดของชิ้นที่ถูกตัดในแผ่นนั้น)
            max_used_length_per_sheet = [max(l for _, l, *_ in shelf) for shelf in shelves]
            total_used_length = sum(max_used_length_per_sheet)  # ✅ รวมค่าความยาวทั้งหมด

            # ✅ คำนวณพื้นที่รวมของแผ่นที่ใช้
            total_sheet_area = sheet_width * total_used_length
        else:
            placements, sheets = algo(orders, sheet_width)

            # ✅ หาความยาวสูงสุดที่ถูกใช้จริงจาก Guillotine
            total_used_length = max((y + used_l) for _, _, _, y, _, used_l, _ in placements) if placements else 0

            # ✅ คำนวณพื้นที่รวมของแผ่นที่ใช้
            total_sheet_area = sheet_width * total_used_length

        # ✅ ป้องกัน total_waste ไม่ให้ติดลบ
        total_waste = max(0, total_sheet_area - total_used_area)

        # ✅ ป้องกัน utilization_efficiency ไม่ให้เกิน 100%
        utilization_eff = min((total_used_area / total_sheet_area) * 100 if total_sheet_area > 0 else 0, 100)

        proc_time = time.time() - start_time

        # ✅ **เพิ่ม total length used เข้าไปใน KPI Summary**
        kpi_rows.append({
            "Algorithm": name,
            "Total Length Used (cm)": round(total_used_length, 2),  # 🔥 เพิ่มคอลัมน์นี้!
            "Total Waste (cm²)": round(total_waste, 2),
            "Utilization Efficiency (%)": f"{round(utilization_eff, 2)}%",
            "Processing Time (s)": round(proc_time, 6)
        })

        results[name] = shelves if name != "Guillotine Rotated" else (placements, sheets, total_used_length)

    st.session_state.kpi_df = pd.DataFrame(kpi_rows)
    st.session_state.results = results
    st.session_state.calculated = True

if "calculated" not in st.session_state:
    st.session_state.calculated = False
if "results" not in st.session_state:
    st.session_state.results = {}
if "kpi_df" not in st.session_state:
    st.session_state.kpi_df = pd.DataFrame()

# --- แสดงผล KPI และ Visualization ---
if st.session_state.calculated:
    st.subheader("📌 KPI Summary")
    st.dataframe(st.session_state.kpi_df)  # ✅ แสดง KPI Summary พร้อม Total Length Used
