import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# -----------------------------------------------------------------------------
# CHAPTER 1: INITIAL SETUP & PERSISTENT SESSION STATES
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Corporate Forecast Cockpit", layout="wide")

products = ["P1", "P2", "P3"]
months = [f"M{i}" for i in range(1, 13)]
future_years = ["Year 2", "Year 3", "Year 4", "Year 5"]
display_columns = months + ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]

# 1. Initialize Baseline Quantities Matrix
if "sidebar_qty_df" not in st.session_state:
    st.session_state.sidebar_qty_df = pd.DataFrame({
        "Timeline": months,
        "P1": [10000.0] * 12,
        "P2": [5000.0] * 12,
        "P3": [1000.0] * 12
    })

# 2. Initialize Price Rate parameters matrix
if "sidebar_rate_df" not in st.session_state:
    st.session_state.sidebar_rate_df = pd.DataFrame({
        "Timeline": months + future_years,
        "P1": [200.0] * 16,
        "P2": [500.0] * 16,
        "P3": [1000.0] * 16
    })

# 3. Initialize Warehouse Parameters metrics matrix
if "sidebar_prod_params_df" not in st.session_state:
    st.session_state.sidebar_prod_params_df = pd.DataFrame({
        "Parameters": ["M1 Initial Op Stock Qty", "Target Hold Days (Closing Stock)"],
        "P1": [12000.0, 30.0],
        "P2": [4000.0, 45.0],
        "P3": [2500.0, 60.0]
    })

# -----------------------------------------------------------------------------
# CHAPTER 2: SIDEBAR CONTROL PANEL DESK
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Workspace Configuration Cockpit")
    
    st.subheader("📈 Annual Volume Growth (%)")
    g_y2 = st.number_input("Year 2 Volume Growth (%)", value=5.0) / 100.0
    g_y3 = st.number_input("Year 3 Volume Growth (%)", value=5.0) / 100.0
    g_y4 = st.number_input("Year 4 Volume Growth (%)", value=5.0) / 100.0
    g_y5 = st.number_input("Year 5 Volume Growth (%)", value=5.0) / 100.0

    st.markdown("---")
    st.subheader("📝 1. Quantity Base Parameters")
    edited_qty_df = st.data_editor(st.session_state.sidebar_qty_df, hide_index=True, column_config={"Timeline": st.column_config.TextColumn(disabled=True)})
    st.session_state.sidebar_qty_df = edited_qty_df

    st.markdown("---")
    st.subheader("💵 2. Price/Rate Parameters")
    edited_rate_df = st.data_editor(st.session_state.sidebar_rate_df, hide_index=True, column_config={"Timeline": st.column_config.TextColumn(disabled=True)})
    st.session_state.sidebar_rate_df = edited_rate_df

    st.markdown("---")
    st.subheader("🏭 3. FG & Warehouse Metrics")
    edited_prod_params_df = st.data_editor(st.session_state.sidebar_prod_params_df, hide_index=True, column_config={"Parameters": st.column_config.TextColumn(disabled=True)})
    st.session_state.sidebar_prod_params_df = edited_prod_params_df

# -----------------------------------------------------------------------------
# CHAPTER 3: ANALYTICAL COMPUTATION LAYER
# -----------------------------------------------------------------------------
qty_matrix, rate_matrix, rev_matrix = {}, {}, {}
prod_sales_matrix, fg_cl_matrix, fg_op_matrix, fg_prod_matrix = {}, {}, {}, {}

def safe_float(val):
    if pd.isna(val) or val == "" or val is None: return 0.0
    try: return float(val)
    except: return 0.0

for p in products:
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

    m1_op_input = safe_float(edited_prod_params_df.loc[edited_prod_params_df["Parameters"] == "M1 Initial Op Stock Qty", p].values[0])
    hold_days = safe_float(edited_prod_params_df.loc[edited_prod_params_df["Parameters"] == "Target Hold Days (Closing Stock)", p].values[0])
    
    p_sales = qty_matrix[p]
    p_op, p_cl, p_prod = [0.0] * 17, [0.0] * 17, [0.0] * 17
    
    for idx in range(12): p_cl[idx] = (hold_days / 30.0) * p_sales[idx]
    p_op[0] = m1_op_input
    for idx in range(1, 12): p_op[idx] = p_cl[idx - 1]
    for idx in range(12): p_prod[idx] = p_sales[idx] + p_cl[idx] - p_op[idx]
    
    p_op[12], p_cl[12], p_prod[12] = p_op[0], p_cl[11], sum(p_prod[0:12])
    
    horizon_map = {"Year 2": 13, "Year 3": 14, "Year 4": 15, "Year 5": 16}
    prev_map = {"Year 2": 12, "Year 3": 13, "Year 4": 14, "Year 5": 15}
    for yr, idx in horizon_map.items():
        p_op[idx] = p_cl[prev_map[yr]]
        p_cl[idx] = (hold_days / 30.0) * (p_sales[idx] / 12.0)
        p_prod[idx] = p_sales[idx] + p_cl[idx] - p_op[idx]

    prod_sales_matrix[p], fg_cl_matrix[p], fg_op_matrix[p], fg_prod_matrix[p] = p_sales, p_cl, p_op, p_prod

# -----------------------------------------------------------------------------
# CHAPTER 4: COMPILING TABULAR STRUCTURES WITH TOTALS
# -----------------------------------------------------------------------------
def compile_report(matrix_dict, is_rev=False):
    df = pd.DataFrame(matrix_dict, index=display_columns).T
    df.insert(0, "Product", df.index)
    t_row = {"Product": "Total"}
    for col in display_columns: t_row[col] = df[col].sum()
    return pd.concat([df, pd.DataFrame([t_row])], ignore_index=True)

df_rev_final = compile_report(rev_matrix)
df_rev_final.iloc[0:, 1:] = df_rev_final.iloc[0:, 1:] / 100000.0
df_qty_final = compile_report(qty_matrix)
df_rate_final = pd.DataFrame(rate_matrix, index=display_columns).T.reset_index().rename(columns={"index": "Product"})

# Format Finished Goods Stacked Summary Reports Matrix
all_prod_dfs = []
for p in products:
    p_flow_df = pd.DataFrame({"Product": [p, "", "", ""], "FG Inventory Metrics": ["1. Opening Stock", "2. Sales Qty", "3. Production Qty", "4. Closing Stock"]})
    for idx, col in enumerate(display_columns):
        p_flow_df[col] = [fg_op_matrix[p][idx], prod_sales_matrix[p][idx], fg_prod_matrix[p][idx], fg_cl_matrix[p][idx]]
    all_prod_dfs.append(p_flow_df)
master_prod_flow_df = pd.concat(all_prod_dfs, ignore_index=True)

df_summary_prod = compile_report(fg_prod_matrix)
df_summary_op = compile_report(fg_op_matrix)
df_summary_cl = compile_report(fg_cl_matrix)

# -----------------------------------------------------------------------------
# CHAPTER 5: TOP PANEL NAVIGATION ROUTER & WORKSPACE VIEWPORTS
# -----------------------------------------------------------------------------
page_tab1, page_tab2 = st.tabs(["Revenue", "FG"])

with page_tab1:
    st.title("Sales Forecasting")
    
    st.subheader("1. Revenue (Rs in Lacs)")
    st.dataframe(df_rev_final.style.format({col: "{:,.2f} L" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)
    
    st.subheader("2. Sale (Qt)")
    st.dataframe(df_qty_final.style.format({col: "{:,.0f}" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)

with page_tab2:
    st.title("Production Forecasting")
    
    st.subheader("1. FG Flow (Qt)")
    st.dataframe(master_prod_flow_df.style.format({col: "{:,.0f}" for col in display_columns if col not in ["Product", "FG Inventory Metrics"]}), use_container_width=True, hide_index=True)
    
    st.subheader("2. Production (Qt)")
    st.dataframe(df_summary_prod.style.format({col: "{:,.0f}" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)
    
    st.subheader("3. FG Closing Stock (Qt)")
    st.dataframe(df_summary_cl.style.format({col: "{:,.0f}" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)
    
    st.subheader("4. FG Opening Stock (Qt)")
    st.dataframe(df_summary_op.style.format({col: "{:,.0f}" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# CHAPTER 6: GLOBAL EXCEL PIPELINE DOWNSTREAM COMPILER
# -----------------------------------------------------------------------------
st.markdown("---")
output_buffer = BytesIO()

try:
    with pd.ExcelWriter(output_buffer, engine="openpyxl") as writer:
        df_rev_final.to_excel(writer, sheet_name="Revenue (Lacs)", index=False)
        df_qty_final.to_excel(writer, sheet_name="Quantity Volumes", index=False)
        master_prod_flow_df.to_excel(writer, sheet_name="FG Flow Ledger", index=False)
        df_summary_prod.to_excel(writer, sheet_name="Summary Production", index=False)
    excel_data = output_buffer.getvalue()
except ModuleNotFoundError:
    with pd.ExcelWriter(output_buffer, engine="xlsxwriter") as writer:
        df_rev_final.to_excel(writer, sheet_name="Revenue (Lacs)", index=False)
        df_qty_final.to_excel(writer, sheet_name="Quantity Volumes", index=False)
master_prod_flow_df.to_excel(writer, sheet_name="FG Flow Ledger", index=False)
df_summary_prod.to_excel(writer, sheet_name="Summary Production", index=False)
excel_data = output_buffer.getvalue()
st.download_button(
label="📥 Download Updated Comprehensive Interconnected Workbook",
data=excel_data,
file_name="Sales_And_Production_Forecasting_Report.xlsx",
mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)