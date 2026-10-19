import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Enterprise Sales Forecasting", layout="wide")

st.title("📊 Enterprise Strategic Sales Forecasting Cockpit")
st.write("Feed your baseline monthly tracking indices below. The engine calculates horizontal revenue models and volumetrics automatically.")

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS: REVENUE COMPOUNDING VECTORS
# -----------------------------------------------------------------------------
st.sidebar.header("📈 Volumetric Growth Cockpit (%)")
st.sidebar.write("Configure annual compounding factors applied to prior year average monthly run-rates:")
g_y2 = st.sidebar.number_input("Year 2 Volume Growth (%)", value=5.0) / 100.0
g_y3 = st.sidebar.number_input("Year 3 Volume Growth (%)", value=5.0) / 100.0
g_y4 = st.sidebar.number_input("Year 4 Volume Growth (%)", value=5.0) / 100.0
g_y5 = st.sidebar.number_input("Year 5 Volume Growth (%)", value=5.0) / 100.0

# -----------------------------------------------------------------------------
# INTERACTIVE DATA GRID: BASELINE PARAMETERS
# -----------------------------------------------------------------------------
st.subheader("📝 Baseline Operational Parameters & Future Absolute Rates")
st.write("Directly click and input **Quantity** and **Absolute Pricing Rates (Rs)** inside the master data matrix:")

products = ["P1", "P2", "P3"]
months = [f"M{i}" for i in range(1, 13)]
future_years = ["Year 2", "Year 3", "Year 4", "Year 5"]
input_periods = months + future_years

init_rows = []
for p in products:
    for period in input_periods:
        is_month = period.startswith("M")
        
        # Default baseline setups based on your layout data markers
        if p == "P1":
            default_qty = 1200.0 if is_month else None
            default_rate = 169800.0
        elif p == "P2":
            default_qty = 50.0 if is_month else None
            default_rate = 40000.0
        else:
            default_qty = 100.0 if is_month else None
            default_rate = 400100.0
            
        init_rows.append({
            "Product ID": p,
            "Timeline Horizon": period,
            "Sales Qty (M1-M12 Active Only)": default_qty,
            "Absolute Price/Rate (Rs)": default_rate
        })

df_feeder = pd.DataFrame(init_rows)

edited_ui = st.data_editor(
    df_feeder, 
    hide_index=True, 
    use_container_width=True,
    column_config={
        "Product ID": st.column_config.TextColumn(disabled=True),
        "Timeline Horizon": st.column_config.TextColumn(disabled=True),
        "Sales Qty (M1-M12 Active Only)": st.column_config.NumberColumn(format="%d"),
        "Absolute Price/Rate (Rs)": st.column_config.NumberColumn(format="Rs %d"),
    }
)

# -----------------------------------------------------------------------------
# FINANCIAL ANALYTICS & CALCULATION LAYER
# -----------------------------------------------------------------------------
display_columns = months + ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]

qty_matrix = {}
rate_matrix = {}
rev_matrix = {}

def safe_float(val):
    try:
        if pd.isna(val) or val == "" or val is None:
            return 0.0
        return float(val)
    except:
        return 0.0

for p in products:
    p_df = edited_ui[edited_ui["Product ID"] == p]
    
    # 1. Parse Baseline Matrices via key filters
    q_months = [safe_float(p_df[p_df["Timeline Horizon"] == m]["Sales Qty (M1-M12 Active Only)"].values) for m in months]
    r_months = [safe_float(p_df[p_df["Timeline Horizon"] == m]["Absolute Price/Rate (Rs)"].values) for m in months]
    v_months = [q * r for q, r in zip(q_months, r_months)]
    
    # 2. Parse Future Price Vector Points
    r_y2 = safe_float(p_df[p_df["Timeline Horizon"] == "Year 2"]["Absolute Price/Rate (Rs)"].values)
    r_y3 = safe_float(p_df[p_df["Timeline Horizon"] == "Year 3"]["Absolute Price/Rate (Rs)"].values)
    r_y4 = safe_float(p_df[p_df["Timeline Horizon"] == "Year 4"]["Absolute Price/Rate (Rs)"].values)
    r_y5 = safe_float(p_df[p_df["Timeline Horizon"] == "Year 5"]["Absolute Price/Rate (Rs)"].values)
    
    # 3. Compile Year 1 Aggregations
    y1_q_total = sum(q_months)
    y1_v_total = sum(v_months)
    y1_r_weighted_avg = y1_v_total / y1_q_total if y1_q_total > 0 else 0.0
    y1_q_avg_monthly = y1_q_total / 12.0
    
    # 4. Generate Compounding Volumetric Run-rates
    y2_q = (y1_q_avg_monthly * (1 + g_y2)) * 12
    y3_q = ((y2_q / 12.0) * (1 + g_y3)) * 12
    y4_q = ((y3_q / 12.0) * (1 + g_y4)) * 12
    y5_q = ((y4_q / 12.0) * (1 + g_y5)) * 12
    
    # 5. Build Unified Horizontal Vectors
    q_horizon = q_months + [y1_q_total, y2_q, y3_q, y4_q, y5_q]
    r_horizon = r_months + [y1_r_weighted_avg, r_y2, r_y3, r_y4, r_y5]
    v_horizon = v_months + [y1_v_total, (y2_q * r_y2), (y3_q * r_y3), (y4_q * r_y4), (y5_q * r_y5)]
    
    qty_matrix[p] = q_horizon
    rate_matrix[p] = r_horizon
    rev_matrix[p] = v_horizon

# -----------------------------------------------------------------------------
# TABLE 1: REVENUE VALUE VIEW - Forecasting : Sales (Lacs)
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📊 Forecasting : Sales (Lacs)")
st.write("Calculates total absolute revenue values formatted in Lakhs (L):")

# Convert currency numbers to Lakhs (divide by 1,00,000)
df_rev = pd.DataFrame({p: [val / 100000.0 for val in rev_matrix[p]] for p in products}, index=display_columns).T
df_rev.insert(0, "Product", df_rev.index)

# Add Total Row
rev_total_row = {"Product": "Total"}
for col in display_columns:
    rev_total_row[col] = df_rev[col].sum()
df_rev = pd.concat([df_rev, pd.DataFrame([rev_total_row])], ignore_index=True)

st.dataframe(df_rev.style.format({col: "{:,.2f} L" for col in display_columns}), use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# TABLE 2: QUANTITY RUN VIEW - Forecasting : Qt(T)
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📦 Forecasting : Qt(T)")
st.write("Tracks total volumetric material physical distributions across the horizon roadmap:")

df_qty = pd.DataFrame(qty_matrix, index=display_columns).T
df_qty.insert(0, "Product", df_qty.index)

# Add Total Row
qty_total_row = {"Product": "Total"}
for col in display_columns:
    qty_total_row[col] = df_qty[col].sum()
df_qty = pd.concat([df_qty, pd.DataFrame([qty_total_row])], ignore_index=True)

st.dataframe(df_qty.style.format({col: "{:,.0f}" for col in display_columns}), use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# TABLE 3: RATE PERSPECTIVE INDEX - Forecasting : Price/T
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("💵 Forecasting : Price/T")
st.write("Reflects tracking pricing indexes (Weighted Average for Year 1, Absolute for Year 2-5):")

df_rate = pd.DataFrame(rate_matrix, index=display_columns).T
df_rate.insert(0, "Product", df_rate.index)
st.dataframe(df_rate.style.format({col: "Rs {:,.2f}" for col in display_columns}), use_container_width=True, hide_index=True)
