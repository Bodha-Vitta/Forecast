import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# Chapter 1: Initial Setup, Structural Imports & Session State Memory
st.set_page_config(page_title="Corporate Forecast Cockpit", layout="wide")

products = ["P1", "P2", "P3"]
months = [f"M{i}" for i in range(1, 13)]
future_years = ["Year 2", "Year 3", "Year 4", "Year 5"]
display_columns = months + ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]

# Initialize global tracking tables into session persistence memory
if "sidebar_qty_df" not in st.session_state:
    st.session_state.sidebar_qty_df = pd.DataFrame(
        [[1000.0, 1000.0, 1000.0] for _ in months],
        index=months,
        columns=products
    ).reset_index().rename(columns={"index": "Timeline"})

if "sidebar_rate_df" not in st.session_state:
    st.session_state.sidebar_rate_df = pd.DataFrame(
        [[5000.0, 5000.0, 5000.0] for _ in (months + future_years)],
        index=months + future_years,
        columns=products
    ).reset_index().rename(columns={"index": "Timeline"})

if "sidebar_prod_params_df" not in st.session_state:
    prod_params_metrics = ["M1 Initial Op Stock Qty", "Target Hold Days (Closing Stock)"]
    st.session_state.sidebar_prod_params_df = pd.DataFrame(
        [[200.0, 200.0, 200.0], [30.0, 30.0, 30.0]],
        index=prod_params_metrics,
        columns=products
    ).reset_index().rename(columns={"index": "Parameters"})

# Chapter 2: Sidebar Control Panels & Interactive Input Desks
with st.sidebar:
    st.header("⚙️ Global Inputs Cockpit")
    
    # Page Routing Selection Block
    st.subheader("🧭 Page Navigation Desk")
    app_mode = st.radio(
        "Select Active Workspace:",
        ["Page 1: Sales & Revenue Forecast", "Page 2: FG Supply & Production Flow"]
    )
    
    st.markdown("---")
    
    # Compounding growth parameters input fields
    st.subheader("📈 Growth Configuration (%)")
    g_y2 = st.number_input("Year 2 Volume Growth (%)", value=5.0) / 100.0
    g_y3 = st.number_input("Year 3 Volume Growth (%)", value=5.0) / 100.0
    g_y4 = st.number_input("Year 4 Volume Growth (%)", value=5.0) / 100.0
    g_y5 = st.number_input("Year 5 Volume Growth (%)", value=5.0) / 100.0

    st.markdown("---")
    
    # Vertical Axis Data Editor tables
    st.subheader("📝 1. Quantity Base Parameters")
    edited_qty_df = st.data_editor(
        st.session_state.sidebar_qty_df,
        hide_index=True,
        column_config={"Timeline": st.column_config.TextColumn(disabled=True)}
    )
    st.session_state.sidebar_qty_df = edited_qty_df

    st.markdown("---")

    st.subheader("💵 2. Price/Rate Parameters")
    edited_rate_df = st.data_editor(
        st.session_state.sidebar_rate_df,
        hide_index=True,
        column_config={"Timeline": st.column_config.TextColumn(disabled=True)}
    )
    st.session_state.sidebar_rate_df = edited_rate_df

    st.markdown("---")

    st.subheader("🏭 3. FG & Warehouse Metrics")
    edited_prod_params_df = st.data_editor(
        st.session_state.sidebar_prod_params_df,
        hide_index=True,
        column_config={"Parameters": st.column_config.TextColumn(disabled=True)}
    )
    st.session_state.sidebar_prod_params_df = edited_prod_params_df

# Chapter 3: Analytical Formulas & Material Balance Engine
qty_matrix = {}
rate_matrix = {}
rev_matrix = {}

prod_sales_matrix = {}
fg_cl_matrix = {}
fg_op_matrix = {}
fg_prod_matrix = {}

def safe_float(val):
    if pd.isna(val) or val == "" or val is None:
        return 0.0
    try:
        return float(val)
    except:
        return 0.0

for p in products:
    # Restructure vertical columns back into vector metrics for calculations
    q_months = [safe_float(edited_qty_df.loc[edited_qty_df["Timeline"] == m, p].values[0]) for m in months]
    r_months = [safe_float(edited_rate_df.loc[edited_rate_df["Timeline"] == m, p].values[0]) for m in months]
    v_months = [q * r for q, r in zip(q_months, r_months)]
    
    r_y2 = safe_float(edited_rate_df.loc[edited_rate_df["Timeline"] == "Year 2", p].values[0])
    r_y3 = safe_float(edited_rate_df.loc[edited_rate_df["Timeline"] == "Year 3", p].values[0])
    r_y4 = safe_float(edited_rate_df.loc[edited_rate_df["Timeline"] == "Year 4", p].values[0])
    r_y5 = safe_float(edited_rate_df.loc[edited_rate_df["Timeline"] == "Year 5", p].values[0])
    
    y1_q_total = sum(q_months)
    y1_v_total = sum(v_months)
    y1_r_weighted_avg = y1_v_total / y1_q_total if y1_q_total > 0 else 0.0
    y1_q_avg_monthly = y1_q_total / 12.0
    
    y2_q = (y1_q_avg_monthly * (1 + g_y2)) * 12
    y3_q = ((y2_q / 12.0) * (1 + g_y3)) * 12
    y4_q = ((y3_q / 12.0) * (1 + g_y4)) * 12
    y5_q = ((y4_q / 12.0) * (1 + g_y5)) * 12
    
    qty_matrix[p] = q_months + [y1_q_total, y2_q, y3_q, y4_q, y5_q]
    rate_matrix[p] = r_months + [y1_r_weighted_avg, r_y2, r_y3, r_y4, r_y5]
    rev_matrix[p] = v_months + [y1_v_total, (y2_q * r_y2), (y3_q * r_y3), (y4_q * r_y4), (y5_q * r_y5)]

    # Inventory Warehouse Flow Calculations Engine
    m1_op_input = safe_float(edited_prod_params_df.loc[edited_prod_params_df["Parameters"] == "M1 Initial Op Stock Qty", p].values[0])
    hold_days = safe_float(edited_prod_params_df.loc[edited_prod_params_df["Parameters"] == "Target Hold Days (Closing Stock)", p].values[0])
    
    p_sales = qty_matrix[p]
    p_op = [0.0] * len(display_columns)
    p_cl = [0.0] * len(display_columns)
    p_prod = [0.0] * len(display_columns)
    
    for idx in range(12):
        p_cl[idx] = (hold_days / 30.0) * p_sales[idx]
        
    p_op[0] = m1_op_input
    for idx in range(1, 12):
        p_op[idx] = p_cl[idx - 1]
        
    for idx in range(12):
        p_prod[idx] = p_sales[idx] + p_cl[idx] - p_op[idx]
        
    y1_idx = 12
    p_op[y1_idx] = p_op[0]
    p_cl[y1_idx] = p_cl[11]
    p_prod[y1_idx] = sum(p_prod[0:12])
    
    horizon_indices = {"Year 2": 13, "Year 3": 14, "Year 4": 15, "Year 5": 16}
    prev_indices = {"Year 2": 12, "Year 3": 13, "Year 4": 14, "Year 5": 15}
    
    for yr_name, idx in horizon_indices.items():
        prev_idx = prev_indices[yr_name]
        p_op[idx] = p_cl[prev_idx]
        p_cl[idx] = (hold_days / 30.0) * (p_sales[idx] / 12.0)
        p_prod[idx] = p_sales[idx] + p_cl[idx] - p_op[idx]

    prod_sales_matrix[p] = p_sales
    fg_cl_matrix[p] = p_cl
    fg_op_matrix[p] = p_op
    fg_prod_matrix[p] = p_prod

# Chapter 4: Multi-Page Content Switching & Excel Download Utility
# Format Sales Forecast Analytical Summary Matrices
df_rev = pd.DataFrame({p: [val / 100000.0 for val in rev_matrix[p]] for p in products}, index=display_columns).T
df_rev.insert(0, "Product", df_rev.index)
rev_total = {"Product": "Total"}
for col in display_columns: rev_total[col] = df_rev[col].sum()
df_rev = pd.concat([df_rev, pd.DataFrame([rev_total])], ignore_index=True)

df_qty = pd.DataFrame(qty_matrix, index=display_columns).T
df_qty.insert(0, "Product", df_qty.index)
qty_total = {"Product": "Total"}
for col in display_columns: qty_total[col] = df_qty[col].sum()
df_qty = pd.concat([df_qty, pd.DataFrame([qty_total])], ignore_index=True)

df_rate = pd.DataFrame(rate_matrix, index=display_columns).T
df_rate.insert(0, "Product", df_rate.index)

# Format Finished Goods Production Dataframes
all_prod_dfs = []
for p in products:
    p_flow_df = pd.DataFrame({
        "Product": [p, p, p, p],
        "FG Inventory Metrics": [
            "1. Forecast FG Op Stock", 
            "2. Forecast Prod Sales Qty", 
            "3. Forecast FG Cl Stock", 
            "4. Forecast Production Qt"
        ]
    })
    for idx, col in enumerate(display_columns):
        p_flow_df[col] = [
            fg_op_matrix[p][idx],
            prod_sales_matrix[p][idx],
            fg_cl_matrix[p][idx],
            fg_prod_matrix[p][idx]
        ]
    all_prod_dfs.append(p_flow_df)
master_prod_flow_df = pd.concat(all_prod_dfs, ignore_index=True)

# MULTI-PAGE DESKTOP VIEWPORTS SWITCHER
if app_mode == "Page 1: Sales & Revenue Forecast":
    st.title("📊 Page 1: Sales & Revenue Forecasting Desktop")
    st.write("Review real-time cascaded demand estimations across revenue, volumetric scales, and pricing weights below:")
    
    tab1, tab2, tab3 = st.tabs(["Revenue Volumes (Lacs)", "Sales Volumes (Units)", "Price Index Target"])
    with tab1:
        st.subheader("💰 Calculated Revenue Horizon Matrix")
        st.dataframe(df_rev.style.format({col: "{:,.2f} L" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)
    with tab2:
        st.subheader("📦 Calculated Demand Physical Unit Log")
        st.dataframe(df_qty.style.format({col: "{:,.0f}" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)
    with tab3:
        st.subheader("💵 Active Evaluated Price Master Index")
        st.dataframe(df_rate.style.format({col: "Rs {:,.2f}" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)

elif app_mode == "Page 2: FG Supply & Production Flow":
    st.title("🏭 Page 2: Finished Goods Supply & Production Planner")
    st.write("Review computed structural material balances and target inventory tracking arrays grouped below:")
    
    st.subheader("📦 Continuous Material Pipeline Control Sheet")
    st.dataframe(
        master_prod_flow_df.style.format({col: "{:,.0f}" for col in display_columns if col not in ["Product", "FG Inventory Metrics"]}),
        use_container_width=True,
        hide_index=True
    )

# GLOBAL EXCEL PIPELINE GENERATOR (COMPATIBLE WITH BOTH PAGES)
st.markdown("---")
output_buffer = BytesIO()
with pd.ExcelWriter(output_buffer, engine="xlsxwriter") as writer:
    df_rev.to_excel(writer, sheet_name="Revenue (Lacs)", index=False)
    df_qty.to_excel(writer, sheet_name="Quantity Volumes", index=False)
    df_rate.to_excel(writer, sheet_name="Unit Pricing Index", index=False)
    master_prod_flow_df.to_excel(writer, sheet_name="FG Production Flow", index=False)

st.download_button(
label="📥 Download Updated Comprehensive Interconnected Workbook",
data=output_buffer.getvalue(),
file_name="Sales_And_Production_Forecasting_Report.xlsx",
mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

<FollowUp>
Go ahead and run `streamlit run app.py` now! Let me know if everything **renders correctly** on your side.
</FollowUp>