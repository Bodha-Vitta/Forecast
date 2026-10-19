import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(page_title="Corporate Sales Forecast Cockpit", layout="wide")

st.title("📊 Corporate Sales & Revenue Forecasting Cockpit")
st.write("Feed your baseline configurations directly into the row-column matrices below. Projections automatically cascade based on your sidebar volume growth parameters.")

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS: VOLUMETRIC GROWTH percentage OVERRIDES
# -----------------------------------------------------------------------------
st.sidebar.header("📈 Volumetric Growth Cockpit (%)")
st.sidebar.write("Configure annual compounding factors applied to prior year average monthly run-rates:")
g_y2 = st.sidebar.number_input("Year 2 Volume Growth (%)", value=5.0) / 100.0
g_y3 = st.sidebar.number_input("Year 3 Volume Growth (%)", value=5.0) / 100.0
g_y4 = st.sidebar.number_input("Year 4 Volume Growth (%)", value=5.0) / 100.0
g_y5 = st.sidebar.number_input("Year 5 Volume Growth (%)", value=5.0) / 100.0

products = ["P1", "P2", "P3"]
months = [f"M{i}" for i in range(1, 13)]
future_years = ["Year 2", "Year 3", "Year 4", "Year 5"]

# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION FOR RAW MATRIX INPUTS
# -----------------------------------------------------------------------------
# Quantities input matrix structure (Only M1 - M12 columns)
if "input_qty_df" not in st.session_state:
    init_qty = {"Product": products}
    for m in months:
        init_qty[m] = [1000.0, 1000.0, 1000.0]  # Standardized 1000 default units
    st.session_state.input_qty_df = pd.DataFrame(init_qty)

# Price Rates input matrix structure (M1 - M12 + Y2 - Y5 columns)
if "input_rate_df" not in st.session_state:
    init_rate = {"Product": products}
    for m in months + future_years:
        init_rate[m] = [5000.0, 5000.0, 5000.0]  # Standardized Rs 5000 default rate
    st.session_state.input_rate_df = pd.DataFrame(init_rate)

# -----------------------------------------------------------------------------
# DATA ENTRY WORKING DESK (THE MATRIX LAYOUTS)
# -----------------------------------------------------------------------------
st.subheader("📝 1. Quantity Base Parameters Data Entry Matrix")
st.write("Type absolute **Sales Quantities** directly into the monthly slots below (Projections are automatically computed):")
edited_qty_df = st.data_editor(
    st.session_state.input_qty_df,
    hide_index=True,
    use_container_width=True,
    column_config={"Product": st.column_config.TextColumn(disabled=True)}
)
st.session_state.input_qty_df = edited_qty_df

st.markdown("---")
st.subheader("💵 2. Price/Rate Parameters Data Entry Matrix")
st.write("Type absolute **Unit Price Rates (Rs)** for baseline months and future years directly across rows:")
edited_rate_df = st.data_editor(
    st.session_state.input_rate_df,
    hide_index=True,
    use_container_width=True,
    column_config={"Product": st.column_config.TextColumn(disabled=True)}
)
st.session_state.input_rate_df = edited_rate_df

# -----------------------------------------------------------------------------
# CORE ANALYTICAL COMPUTATION LAYER
# -----------------------------------------------------------------------------
display_columns = months + ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
qty_matrix = {}
rate_matrix = {}
rev_matrix = {}

def safe_float(val):
    if pd.isna(val) or val == "" or val is None:
        return 0.0
    try:
        return float(val)
    except:
        return 0.0

for p_idx, p in enumerate(products):
    # Extract structural rows directly from clean horizontal session matrices
    q_row = edited_qty_df[edited_qty_df["Product"] == p].iloc[0]
    r_row = edited_rate_df[edited_rate_df["Product"] == p].iloc[0]
    
    # Map out the 12 month baseline vectors sequentially
    q_months = [safe_float(q_row[m]) for m in months]
    r_months = [safe_float(r_row[m]) for m in months]
    v_months = [q * r for q, r in zip(q_months, r_months)]
    
    # Extract absolute pricing target columns directly from matrix mapping
    r_y2 = safe_float(r_row["Year 2"])
    r_y3 = safe_float(r_row["Year 3"])
    r_y4 = safe_float(r_row["Year 4"])
    r_y5 = safe_float(r_row["Year 5"])
    
    # Financial Pipeline Formulations
    y1_q_total = sum(q_months)
    y1_v_total = sum(v_months)
    y1_r_weighted_avg = y1_v_total / y1_q_total if y1_q_total > 0 else 0.0
    y1_q_avg_monthly = y1_q_total / 12.0
    
    # Cascade quantity compounding parameters
    y2_q = (y1_q_avg_monthly * (1 + g_y2)) * 12
    y3_q = ((y2_q / 12.0) * (1 + g_y3)) * 12
    y4_q = ((y3_q / 12.0) * (1 + g_y4)) * 12
    y5_q = ((y4_q / 12.0) * (1 + g_y5)) * 12
    
    # Store complete continuous horizon vectors
    qty_matrix[p] = q_months + [y1_q_total, y2_q, y3_q, y4_q, y5_q]
    rate_matrix[p] = r_months + [y1_r_weighted_avg, r_y2, r_y3, r_y4, r_y5]
    rev_matrix[p] = v_months + [y1_v_total, (y2_q * r_y2), (y3_q * r_y3), (y4_q * r_y4), (y5_q * r_y5)]

# -----------------------------------------------------------------------------
# RENDER CONSOLIDATED OUTPUT VIEWS
# -----------------------------------------------------------------------------
# REPORT 1: REVENUE VALUATIONS (LACS) WITH AUTOMATED TOTALING
st.markdown("---")
st.subheader("📊 Forecasting : Sales (Lacs)")
df_rev = pd.DataFrame({p: [val / 100000.0 for val in rev_matrix[p]] for p in products}, index=display_columns).T
df_rev.insert(0, "Product", df_rev.index)
rev_total = {"Product": "Total"}
for col in display_columns:
    rev_total[col] = df_rev[col].sum()
df_rev = pd.concat([df_rev, pd.DataFrame([rev_total])], ignore_index=True)
st.dataframe(df_rev.style.format({col: "{:,.2f} L" for col in display_columns}), use_container_width=True, hide_index=True)

# REPORT 2: PHYSICAL VOLUME RUNS (UNITS) WITH AUTOMATED TOTALING
st.markdown("---")
st.subheader("📦 Forecasting : Qt(T)")
df_qty = pd.DataFrame(qty_matrix, index=display_columns).T
df_qty.insert(0, "Product", df_qty.index)
qty_total = {"Product": "Total"}
for col in display_columns:
    qty_total[col] = df_qty[col].sum()
df_qty = pd.concat([df_qty, pd.DataFrame([qty_total])], ignore_index=True)
st.dataframe(df_qty.style.format({col: "{:,.0f}" for col in display_columns}), use_container_width=True, hide_index=True)

# REPORT 3: THE UNIT PRICING PERSPECTIVE REGISTER
st.markdown("---")
st.subheader("💵 Forecasting : Price/T")
df_rate = pd.DataFrame(rate_matrix, index=display_columns).T
df_rate.insert(0, "Product", df_rate.index)
st.dataframe(df_rate.style.format({col: "Rs {:,.2f}" for col in display_columns}), use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# WORKBOOK GENERATION DISPATCH PROTOCOLS
# -----------------------------------------------------------------------------
st.markdown("---")
output_buffer = BytesIO()
with pd.ExcelWriter(output_buffer, engine="xlsxwriter") as writer:
    df_rev.to_excel(writer, sheet_name="Revenue (Lacs)", index=False)
    df_qty.to_excel(writer, sheet_name="Quantity Volumes", index=False)
    df_rate.to_excel(writer, sheet_name="Unit Pricing Index", index=False)

st.download_button(
    label="📥 Download Interconnected Excel Workbook",
    data=output_buffer.getvalue(),
    file_name="Sales_Forecasting_Report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
