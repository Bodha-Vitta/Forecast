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
        
        # Globally standardized user-requested defaults: 1000 Units and Rs 5000 Rate
        default_qty = 1000.0 if is_month else None
        default_rate = 5000.0
            
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
# FINANCIAL ANALYTICS & SAFE ROW-BY-ROW PARSING LAYER
# -----------------------------------------------------------------------------
display_columns = months + ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]

def safe_float(val):
    if pd.isna(val) or val == "" or val is None:
        return 0.0
    try:
        return float(val)
    except:
        return 0.0

# Initialize blank storage dictionaries structured by product name keys
product_data_store = {p: {"qty": {}, "rate": {}} for p in products}

# Parse data safely by looping through table rows directly
for idx, row in edited_ui.iterrows():
    p_id = row["Product ID"]
    horizon = row["Timeline Horizon"]
    
    if p_id in product_data_store:
        product_data_store[p_id]["qty"][horizon] = safe_float(row["Sales Qty (M1-M12 Active Only)"])
        product_data_store[p_id]["rate"][horizon] = safe_float(row["Absolute Price/Rate (Rs)"])

qty_matrix = {}
rate_matrix = {}
rev_matrix = {}

for p in products:
    # 1. Rebuild arrays sequentially from the storage dictionaries
    q_months = [product_data_store[p]["qty"].get(m, 0.0) for m in months]
    r_months = [product_data_store[p]["rate"].get(m, 0.0) for m in months]
    v_months = [q * r for q, r in zip(q_months, r_months)]
    
    # 2. Grab future absolute rates safely
    r_y2 = product_data_store[p]["rate"].get("Year 2", 0.0)
    r_y3 = product_data_store[p]["rate"].get("Year 3", 0.0)
    r_y4 = product_data_store[p]["rate"].get("Year 4", 0.0)
    r_y5 = product_data_store[p]["rate"].get("Year 5", 0.0)
    
    # 3. Compute Year 1 Summary
    y1_q_total = sum(q_months)
    y1_v_total = sum(v_months)
    y1_r_weighted_avg = y1_v_total / y1_q_total if y1_q_total > 0 else 0.0
    y1_q_avg_monthly = y1_q_total / 12.0
    
    # 4. Compute Volume Compounding Chain Projections
    y2_q = (y1_q_avg_monthly * (1 + g_y2)) * 12
    y3_q = ((y2_q / 12.0) * (1 + g_y3)) * 12
    y4_q = ((y3_q / 12.0) * (1 + g_y4)) * 12
    y5_q = ((y4_q / 12.0) * (1 + g_y5)) * 12
    
    # 5. Build Final Structural Horizons
    qty_matrix[p] = q_months + [y1_q_total, y2_q, y3_q, y4_q, y5_q]
    rate_matrix[p] = r_months + [y1_r_weighted_avg, r_y2, r_y3, r_y4, r_y5]
    rev_matrix[p] = v_months + [y1_v_total, (y2_q * r_y2), (y3_q * r_y3), (y4_q * r_y4), (y5_q * r_y5)]

# -----------------------------------------------------------------------------
# DISPLAY REVENUE TABLE: Forecasting : Sales (Lacs)
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📊 Forecasting : Sales (Lacs)")
st.write("Calculates total absolute revenue values formatted in Lakhs (L):")

df_rev = pd.DataFrame({p: [val / 100000.0 for val in rev_matrix[p]] for p in products}, index=display_columns).T
df_rev.insert(0, "Product", df_rev.index)

rev_total_row = {"Product": "Total"}
for col in display_columns:
    rev_total_row[col] = df_rev[col].sum()
df_rev = pd.concat([df_rev, pd.DataFrame([rev_total_row])], ignore_index=True)

st.dataframe(df_rev.style.format({col: "{:,.2f} L" for col in display_columns}), use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# DISPLAY QUANTITY TABLE: Forecasting : Qt(T)
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📦 Forecasting : Qt(T)")
st.write("Tracks total volumetric material physical distributions across the horizon roadmap:")

df_qty = pd.DataFrame(qty_matrix, index=display_columns).T
df_qty.insert(0, "Product", df_qty.index)

qty_total_row = {"Product": "Total"}
for col in display_columns:
    qty_total_row[col] = df_qty[col].sum()
df_qty = pd.concat([df_qty, pd.DataFrame([qty_total_row])], ignore_index=True)

st.dataframe(df_qty.style.format({col: "{:,.0f}" for col in display_columns}), use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# DISPLAY RATES TABLE: Forecasting : Price/T
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("💵 Forecasting : Price/T")
st.write("Reflects tracking pricing indexes (Weighted Average for Year 1, Absolute for Year 2-5):")

df_rate = pd.DataFrame(rate_matrix, index=display_columns).T
df_rate.insert(0, "Product", df_rate.index)
st.dataframe(df_rate.style.format({col: "Rs {:,.2f}" for col in display_columns}), use_container_width=True, hide_index=True)
