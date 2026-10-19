import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sales Forecasting Engine", layout="wide")

st.title("📊 Strategic Sales Forecasting Engine")
st.write("Configure baseline inputs and future price targets below. Future quantity projections are automatically calculated based on your sidebar growth rates.")

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS: QUANTITY GROWTH FACTORS ONLY
# -----------------------------------------------------------------------------
st.sidebar.header("📈 Volume Growth Targets (%)")
st.sidebar.write("Applied on top of the calculated prior year average monthly run-rate")
g_y2 = st.sidebar.number_input("Year 2 Volume Growth (%)", value=5.0) / 100.0
g_y3 = st.sidebar.number_input("Year 3 Volume Growth (%)", value=5.0) / 100.0
g_y4 = st.sidebar.number_input("Year 4 Volume Growth (%)", value=5.0) / 100.0
g_y5 = st.sidebar.number_input("Year 5 Volume Growth (%)", value=5.0) / 100.0

# -----------------------------------------------------------------------------
# INTERACTIVE DATA MATRIX: INTEGRATED DATA ENTRY FEEDER
# -----------------------------------------------------------------------------
st.subheader("📝 Baseline Months (Qty & Rate) & Future Absolute Price Input Matrix")
st.write("Directly edit **Sales Qty** and **Rates** for M1-M12. For Years 2 to 5, provide **only** your absolute price targets:")

products = ["P1", "P2", "P3"]
months = [f"M{i}" for i in range(1, 13)]
future_years = ["Year 2", "Year 3", "Year 4", "Year 5"]

init_rows = []
for p in products:
    # 1. Add Month entries (Both Quantity and Rate are active)
    for m in months:
        if p == "P1":
            default_rate = 50.0
        elif p == "P2":
            default_rate = 120.0
        else:
            default_rate = 75.0
            
        init_rows.append({
            "Product": p,
            "Period/Horizon": m,
            "Sales Qty (M1-M12 Only)": 10000.0,
            "Absolute Rate / Price (Rs)": default_rate
        })
    
    # 2. Add Future Year entries (Quantity input is hidden, only Price is active)
    for y in future_years:
        if p == "P1":
            default_rate = 50.0
        elif p == "P2":
            default_rate = 120.0
        else:
            default_rate = 75.0
            
        init_rows.append({
            "Product": p,
            "Period/Horizon": y,
            "Sales Qty (M1-M12 Only)": None,  # Hidden field placeholder
            "Absolute Rate / Price (Rs)": default_rate
        })

df_feeder = pd.DataFrame(init_rows)

edited_ui = st.data_editor(
    df_feeder, 
    hide_index=True, 
    use_container_width=True,
    column_config={
        "Product": st.column_config.TextColumn(disabled=True),
        "Period/Horizon": st.column_config.TextColumn(disabled=True),
        # Disables and cleanly wipes out entry edit capability for future year quantities
        "Sales Qty (M1-M12 Only)": st.column_config.NumberColumn(format="%d"),
    }
)

# -----------------------------------------------------------------------------
# CALCULATION COMPILING ENGINE
# -----------------------------------------------------------------------------
display_columns = months + ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
compiled_records = []

def safe_float(val):
    try:
        if pd.isna(val) or val == "" or val is None:
            return 0.0
        return float(val)
    except:
        return 0.0

edited_ui_clean = edited_ui.reset_index(drop=True)
rows_per_product = 16  # 12 months + 4 future year slots

for idx, p in enumerate(products):
    start_row = idx * rows_per_product
    
    # Extract Month vectors safely by location index
    q_months = [safe_float(edited_ui_clean.loc[start_row + m, "Sales Qty (M1-M12 Only)"]) for m in range(12)]
    r_months = [safe_float(edited_ui_clean.loc[start_row + m, "Absolute Rate / Price (Rs)"]) for m in range(12)]
    v_months = [q * r for q, r in zip(q_months, r_months)]
    
    # Extract future year rates directly from their specific index slots
    r_y2 = safe_float(edited_ui_clean.loc[start_row + 12, "Absolute Rate / Price (Rs)"])
    r_y3 = safe_float(edited_ui_clean.loc[start_row + 13, "Absolute Rate / Price (Rs)"])
    r_y4 = safe_float(edited_ui_clean.loc[start_row + 14, "Absolute Rate / Price (Rs)"])
    r_y5 = safe_float(edited_ui_clean.loc[start_row + 15, "Absolute Rate / Price (Rs)"])
    
    # Process Year 1 Horizon math
    y1_q_total = sum(q_months)
    y1_v_total = sum(v_months)
    y1_r_weighted_avg = y1_v_total / y1_q_total if y1_q_total > 0 else 0.0
    y1_q_avg_monthly = y1_q_total / 12.0
    
    # Automatically compute Year 2 to Year 5 quantities based on sidebar growth % parameters
    y2_q = (y1_q_avg_monthly * (1 + g_y2)) * 12
    y3_q = ((y2_q / 12.0) * (1 + g_y3)) * 12
    y4_q = ((y3_q / 12.0) * (1 + g_y4)) * 12
    y5_q = ((y4_q / 12.0) * (1 + g_y5)) * 12
    
    q_horizon = q_months + [y1_q_total, y2_q, y3_q, y4_q, y5_q]
    r_horizon = r_months + [y1_r_weighted_avg, r_y2, r_y3, r_y4, r_y5]
    v_horizon = v_months + [y1_v_total, (y2_q * r_y2), (y3_q * r_y3), (y4_q * r_y4), (y5_q * r_y5)]
    
    compiled_records.append([p, "Sales Qty (Units)"] + q_horizon)
    compiled_records.append([p, "Unit Rate (Rs)"] + r_horizon)
    compiled_records.append([p, "Revenue Value (Rs)"] + v_horizon)

df_display = pd.DataFrame(compiled_records, columns=["Product", "Metric Type"] + display_columns)

# -----------------------------------------------------------------------------
# GRAPH PRESENTATION INTERFACE
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📋 Consolidated Sales & Revenue Analytical Forecast Horizon")

st.dataframe(df_display.style.format(subset=display_columns, formatter="{:,.2f}"), use_container_width=True, hide_index=True)

grand_total_revenue_y1 = df_display[df_display["Metric Type"] == "Revenue Value (Rs)"]["Year 1"].sum()
grand_total_revenue_y5 = df_display[df_display["Metric Type"] == "Revenue Value (Rs)"]["Year 5"].sum()

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.metric("📦 GRAND TOTAL REVENUE (Year 1 Baseline)", f"Rs {grand_total_revenue_y1 / 10000000:.2f} Cr")
with col2:
    st.metric("🚀 PROJECTED REVENUE (Year 5 Horizon)", f"Rs {grand_total_revenue_y5 / 10000000:.2f} Cr")
