import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# -----------------------------------------------------------------------------
# CHAPTER 1: INITIAL SETUP & PERSISTENT SESSION STATES
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Corporate Forecast Cockpit", layout="wide")

# Enhanced CSS overrides forcing the navigation container to lock at the absolute top boundary
st.markdown("""
    <style>
    header[data-testid="stHeader"] {
        z-index: 99 !important;
    }
    div[data-testid="stTabs"] {
        position: sticky !important;
        top: 0px !important;
        background-color: white !important;
        z-index: 9999 !important;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
        border-bottom: 3px solid #f0f2f6 !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        background-color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

products = ["P1", "P2", "P3"]
raw_materials = [f"RM{i}" for i in range(1, 13)]
months = [f"M{i}" for i in range(1, 13)]
future_years = ["Year 2", "Year 3", "Year 4", "Year 5"]
display_columns = months + ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
direct_exp_heads = ["Wages", "Power", "Repair & maintenance", "Freight in", "Other Direct OH"]

# Setup Global Product Filter Selector Context at the top-right corner
col_space, col_filter = st.columns([4, 1])
with col_space:
    st.write("")
with col_filter:
    global_product_filter = st.selectbox(
        "🔍 Product Filter:", 
        options=["All"] + products, 
        key="global_dashboard_product_filter_context"
    )
# 1. Initialize Baseline Quantities Matrix
if "sidebar_qty_df" not in st.session_state:
    st.session_state.sidebar_qty_df = pd.DataFrame({
        "Timeline": months, "P1": [10000.0] * 12, "P2": [5000.0] * 12, "P3": [1000.0] * 12
    })

# 2. Initialize Price Rate Parameters Matrix
if "sidebar_rate_df" not in st.session_state:
    st.session_state.sidebar_rate_df = pd.DataFrame({
        "Timeline": months + future_years, "P1": [170.0] * 16, "P2": [200.0] * 16, "P3": [450.0] * 16
    })

# 3. Initialize Product Long-Term Price Inflation Feeder Grid Matrix
if "sidebar_fg_inflation_df" not in st.session_state:
    st.session_state.sidebar_fg_inflation_df = pd.DataFrame({
        "Timeline": ["Year 2 FG Price Inflation (%)", "Year 3 FG Price Inflation (%)", "Year 4 FG Price Inflation (%)", "Year 5 FG Price Inflation (%)"],
        "P1": [5.0] * 4, "P2": [5.0] * 4, "P3": [5.0] * 4
    })

# 4. Initialize Finished Goods Warehouse Parameters Matrix
if "sidebar_prod_params_df" not in st.session_state:
    st.session_state.sidebar_prod_params_df = pd.DataFrame({
        "Parameters": ["M1 Initial Op Stock Qty", "Target Hold Days (Closing Stock)"],
        "P1": [12000.0, 30.0], "P2": [4000.0, 45.0], "P3": [2500.0, 60.0]
    })

# 5. Initialize Dynamic BOM Matrix Setup
if "sidebar_bom_df" not in st.session_state:
    bom_data = {
        "RM Name": ["RM1", "RM2", "RM3", "RM4", "RM5", "RM6", "RM1", "RM7", "RM8", "RM9", "RM10", "RM1", "RM11", "RM12"],
        "Target FG": ["P1", "P1", "P1", "P1", "P1", "P1", "P2", "P2", "P2", "P2", "P2", "P3", "P3", "P3"],
        "Con%": [0.70, 0.15, 0.05, 0.04, 0.03, 0.03, 0.70, 0.20, 0.03, 0.04, 0.03, 0.70, 0.20, 0.10],
        "Visible Loss": [0.04] * 14, "Invisible Loss": [0.01] * 14
    }
    st.session_state.sidebar_bom_df = pd.DataFrame(bom_data)
# 6. Initialize Raw Material Logistics Inventory parameters
if "sidebar_rm_logistics_df" not in st.session_state:
    logistics_data = {
        "Raw Material": raw_materials,
        "M1 Initial Op Stock Qty": [13000.0, 1658.0, 553.0, 442.0, 332.0, 332.0, 1700.0, 250.0, 350.0, 250.0, 100.0, 50.0],
        "Days Hold": [45.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0]
    }
    st.session_state.sidebar_rm_logistics_df = pd.DataFrame(logistics_data)

# 7. Initialize Raw Material Base Unit Commercial Procurement Price Feeder
if "sidebar_rm_price_df" not in st.session_state:
    st.session_state.sidebar_rm_price_df = pd.DataFrame({
        "Raw Material": raw_materials,
        "Initial Price": [100.0, 400.0, 20.0, 250.0, 200.0, 250.0, 200.0, 250.0, 20.0, 100.0, 600.0, 400.0]
    })

# 8. Initialize Long-Term Compound Price Inflation Assumptions Grid Matrix
if "sidebar_rm_inflation_df" not in st.session_state:
    st.session_state.sidebar_rm_inflation_df = pd.DataFrame({
        "Timeline": ["Year 2 Price Inflation (%)", "Year 3 Price Inflation (%)", "Year 4 Price Inflation (%)", "Year 5 Price Inflation (%)"],
        "Inflation Rates (%)": [5.0, 5.0, 5.0, 5.0]
    })

# 9. Initialize Direct Expenses Base Unit Rate Feed Matrix (Defaults matching Pic 1)
if "sidebar_direct_exp_rates_df" not in st.session_state:
    st.session_state.sidebar_direct_exp_rates_df = pd.DataFrame({
        "Expense Head": direct_exp_heads,
        "P1": [7.00, 15.00, 5.00, 3.50, 2.00],
        "P2": [8.00, 18.00, 6.00, 3.50, 2.00],
        "P3": [9.00, 20.00, 7.00, 3.50, 2.00]
    })

# 10. Initialize Direct Expenses Annual Price Inflation Feed Matrix starting from Y2-Y5
if "sidebar_direct_exp_inflation_df" not in st.session_state:
    st.session_state.sidebar_direct_exp_inflation_df = pd.DataFrame({
        "Timeline": ["Year 2 Inflation (%)", "Year 3 Inflation (%)", "Year 4 Inflation (%)", "Year 5 Inflation (%)"],
        "P1": [5.0] * 4, "P2": [5.0] * 4, "P3": [5.0] * 4
    })

if "pl_open_nodes" not in st.session_state:
    st.session_state.pl_open_nodes = set()
if "pl_editor_ver" not in st.session_state:
    st.session_state.pl_editor_ver = 0
if "growth_saved" not in st.session_state:
    st.session_state.growth_saved = [5.0, 5.0, 5.0, 5.0]
with st.sidebar:
    st.header("📋 Workspace Configuration Cockpit")
    sidebar_context = st.radio(
        "🧭 Focus Workspace Target Viewport Context:",
        options=["Sales / FG Feed", "RM Qt Feed", "RM Val Feed", "Direct Exp Feed"],
        key="synchronized_sidebar_context_radio_widget"
    )
    st.markdown("---")

    if sidebar_context == "Sales / FG Feed":
        st.header("📈 1. Sales & FG Feed Desk")
        g2_pct = st.number_input("Year 2 Volume Growth (%)", value=st.session_state.growth_saved[0])
        g3_pct = st.number_input("Year 3 Volume Growth (%)", value=st.session_state.growth_saved[1])
        g4_pct = st.number_input("Year 4 Volume Growth (%)", value=st.session_state.growth_saved[2])
        g5_pct = st.number_input("Year 5 Volume Growth (%)", value=st.session_state.growth_saved[3])
        st.session_state.growth_saved = [g2_pct, g3_pct, g4_pct, g5_pct]
        
        st.session_state.sidebar_qty_df = st.data_editor(st.session_state.sidebar_qty_df, hide_index=True, column_config={"Timeline": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_rate_df = st.data_editor(st.session_state.sidebar_rate_df, hide_index=True, column_config={"Timeline": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_fg_inflation_df = st.data_editor(st.session_state.sidebar_fg_inflation_df, hide_index=True, column_config={"Timeline": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_prod_params_df = st.data_editor(st.session_state.sidebar_prod_params_df, hide_index=True, column_config={"Parameters": st.column_config.TextColumn(disabled=True)})
        
    elif sidebar_context == "RM Qt Feed":
        st.header("📦 2. RM Qt Feed Desk")
        st.session_state.sidebar_bom_df = st.data_editor(st.session_state.sidebar_bom_df, hide_index=True, column_config={"RM Name": st.column_config.TextColumn(disabled=True), "Target FG": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_rm_logistics_df = st.data_editor(st.session_state.sidebar_rm_logistics_df, hide_index=True, column_config={"Raw Material": st.column_config.TextColumn(disabled=True)})
        
    elif sidebar_context == "RM Val Feed":
        st.header("💰 3. RM Val Feed Desk")
        st.session_state.sidebar_rm_price_df = st.data_editor(st.session_state.sidebar_rm_price_df, hide_index=True, column_config={"Raw Material": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_rm_inflation_df = st.data_editor(st.session_state.sidebar_rm_inflation_df, hide_index=True, column_config={"Timeline": st.column_config.TextColumn(disabled=True)})
        
    elif sidebar_context == "Direct Exp Feed":
        st.header("🛠️ 4. Direct Exp Input Desk")
        st.markdown("**Initial Entry Production Base Rate (Per Unit):**")
        st.session_state.sidebar_direct_exp_rates_df = st.data_editor(st.session_state.sidebar_direct_exp_rates_df, hide_index=True, column_config={"Expense Head": st.column_config.TextColumn(disabled=True)})
        st.markdown("**Long-Term Compounding Annual Inflation starting Y2-Y5 (%)**")
        st.session_state.sidebar_direct_exp_inflation_df = st.data_editor(st.session_state.sidebar_direct_exp_inflation_df, hide_index=True, column_config={"Timeline": st.column_config.TextColumn(disabled=True)})

g_y2, g_y3, g_y4, g_y5 = [x / 100.0 for x in st.session_state.growth_saved]
edited_qty_df = st.session_state.sidebar_qty_df
edited_rate_df = st.session_state.sidebar_rate_df
edited_fg_inflation_df = st.session_state.sidebar_fg_inflation_df
edited_prod_params_df = st.session_state.sidebar_prod_params_df
edited_bom_df = st.session_state.sidebar_bom_df
edited_rm_logistics_df = st.session_state.sidebar_rm_logistics_df
edited_rm_price_df = st.session_state.sidebar_rm_price_df
edited_rm_inflation_df = st.session_state.sidebar_rm_inflation_df
edited_direct_exp_rates_df = st.session_state.sidebar_direct_exp_rates_df
edited_direct_exp_inflation_df = st.session_state.sidebar_direct_exp_inflation_df
qty_matrix, rate_matrix, rev_matrix = {}, {}, {}
prod_sales_matrix, fg_cl_matrix, fg_op_matrix, fg_prod_matrix = {}, {}, {}, {}

def safe_float(val):
    if pd.isna(val) or val == "" or val is None: return 0.0
    try:
        if isinstance(val, (list, np.ndarray, pd.Series)):
            return float(val[0]) if len(val) > 0 else 0.0
        return float(val)
    except: return 0.0

for p in products:
    q_months = [safe_float(edited_qty_df.loc[edited_qty_df["Timeline"] == m, p].values) for m in months]
    p_inf_y2 = safe_float(edited_fg_inflation_df.loc[edited_fg_inflation_df["Timeline"] == "Year 2 FG Price Inflation (%)", p].values) / 100.0
    p_inf_y3 = safe_float(edited_fg_inflation_df.loc[edited_fg_inflation_df["Timeline"] == "Year 3 FG Price Inflation (%)", p].values) / 100.0
    p_inf_y4 = safe_float(edited_fg_inflation_df.loc[edited_fg_inflation_df["Timeline"] == "Year 4 FG Price Inflation (%)", p].values) / 100.0
    p_inf_y5 = safe_float(edited_fg_inflation_df.loc[edited_fg_inflation_df["Timeline"] == "Year 5 FG Price Inflation (%)", p].values) / 100.0
    r_months = [safe_float(edited_rate_df.loc[edited_rate_df["Timeline"] == m, p].values) for m in months]
    v_months = [q * r for q, r in zip(q_months, r_months)]
    
    y1_q_total = sum(q_months)
    y1_v_total = sum(v_months)
    y1_r_weighted_avg = y1_v_total / y1_q_total if y1_q_total > 0 else 0.0
    y1_q_avg_monthly = y1_q_total / 12.0
    
    base_r_y2 = safe_float(edited_rate_df.loc[edited_rate_df["Timeline"] == "Year 2", p].values)
    base_r_y3 = safe_float(edited_rate_df.loc[edited_rate_df["Timeline"] == "Year 3", p].values)
    base_r_y4 = safe_float(edited_rate_df.loc[edited_rate_df["Timeline"] == "Year 4", p].values)
    base_r_y5 = safe_float(edited_rate_df.loc[edited_rate_df["Timeline"] == "Year 5", p].values)
    
    r_y2 = base_r_y2 * (1.0 + p_inf_y2)
    r_y3 = base_r_y3 * (1.0 + p_inf_y2) * (1.0 + p_inf_y3)
    r_y4 = base_r_y4 * (1.0 + p_inf_y2) * (1.0 + p_inf_y3) * (1.0 + p_inf_y4)
    r_y5 = base_r_y5 * (1.0 + p_inf_y2) * (1.0 + p_inf_y3) * (1.0 + p_inf_y4) * (1.0 + p_inf_y5)
    
    y2_q = (y1_q_avg_monthly * (1 + g_y2)) * 12
    y3_q = ((y2_q / 12.0) * (1 + g_y3)) * 12
    y4_q = ((y3_q / 12.0) * (1 + g_y4)) * 12
    y5_q = ((y4_q / 12.0) * (1 + g_y5)) * 12
    
    qty_matrix[p] = q_months + [y1_q_total, y2_q, y3_q, y4_q, y5_q]
    rate_matrix[p] = r_months + [y1_r_weighted_avg, r_y2, r_y3, r_y4, r_y5]
    rev_matrix[p] = v_months + [y1_v_total, (y2_q * r_y2), (y3_q * r_y3), (y4_q * r_y4), (y5_q * r_y5)]

    m1_op_input = safe_float(edited_prod_params_df.loc[edited_prod_params_df["Parameters"] == "M1 Initial Op Stock Qty", p].values)
    hold_days = safe_float(edited_prod_params_df.loc[edited_prod_params_df["Parameters"] == "Target Hold Days (Closing Stock)", p].values)
    
    p_sales = qty_matrix[p]
    p_cl = [0.0] * 17
    for idx in range(12): p_cl[idx] = (hold_days / 30.0) * p_sales[idx]
    
    p_op_list = [0.0] * 17
    p_op_list[0] = m1_op_input
    for idx in range(1, 12): p_op_list[idx] = p_cl[idx - 1]
    
    p_prod_calc = [0.0] * 17
    for idx in range(12): p_prod_calc[idx] = p_sales[idx] + p_cl[idx] - p_op_list[idx]
    
    p_op_list[12], p_cl[12], p_prod_calc[12] = p_op_list[0], p_cl[11], sum(p_prod_calc[0:12])
    
    horizon_map, prev_map = {"Year 2": 13, "Year 3": 14, "Year 4": 15, "Year 5": 16}, {"Year 2": 12, "Year 3": 13, "Year 4": 14, "Year 5": 15}
    for yr, idx in horizon_map.items():
        p_op_list[idx] = p_cl[prev_map[yr]]
        p_cl[idx] = (hold_days / 30.0) * (p_sales[idx] / 12.0)
        p_prod_calc[idx] = p_sales[idx] + p_cl[idx] - p_op_list[idx]
    prod_sales_matrix[p], fg_cl_matrix[p], fg_op_matrix[p], fg_prod_matrix[p] = p_sales, p_cl, p_op_list, p_prod_calc
rm_gross_cons_matrix, rm_total_loss_matrix, fg_scrap_matrix = {rm: [0.0]*17 for rm in raw_materials}, {rm: [0.0]*17 for rm in raw_materials}, {p: [0.0]*17 for p in products}
valid_time_indices = [i for i in range(17) if i != 12]

for idx in valid_time_indices:
    for _, row in edited_bom_df.iterrows():
        rm, p, c_pct, v_loss, i_loss = row["RM Name"], row["Target FG"], safe_float(row["Con%"]), safe_float(row["Visible Loss"]), safe_float(row["Invisible Loss"])
        fg_qty = fg_prod_matrix[p][idx]
        denom = (1.0 - v_loss - i_loss)
        if denom > 0:
            gross_c = (fg_qty * c_pct) / denom
            v_scrap_val = gross_c * v_loss
            total_loss_val = gross_c * (v_loss + i_loss)
            rm_gross_cons_matrix[rm][idx] += gross_c
            rm_total_loss_matrix[rm][idx] += total_loss_val
            fg_scrap_matrix[p][idx] += v_scrap_val

for rm in raw_materials:
    rm_gross_cons_matrix[rm][12] = sum(rm_gross_cons_matrix[rm][0:12])
    rm_total_loss_matrix[rm][12] = sum(rm_total_loss_matrix[rm][0:12])
for p in products: fg_scrap_matrix[p][12] = sum(fg_scrap_matrix[p][0:12])

rm_op_matrix, rm_cl_matrix, rm_purch_matrix = {rm: [0.0]*17 for rm in raw_materials}, {rm: [0.0]*17 for rm in raw_materials}, {rm: [0.0]*17 for rm in raw_materials}
for rm in raw_materials:
    m1_op_rm = safe_float(edited_rm_logistics_df.loc[edited_rm_logistics_df["Raw Material"] == rm, "M1 Initial Op Stock Qty"].values)
    days_hold_rm = safe_float(edited_rm_logistics_df.loc[edited_rm_logistics_df["Raw Material"] == rm, "Days Hold"].values)
    for idx in range(12): rm_cl_matrix[rm][idx] = (rm_gross_cons_matrix[rm][idx] / 30.0) * days_hold_rm
    rm_op_matrix[rm][0] = m1_op_rm
    for idx in range(1, 12): rm_op_matrix[rm][idx] = rm_cl_matrix[rm][idx - 1]
    for idx in range(12): rm_purch_matrix[rm][idx] = max(0.0, rm_gross_cons_matrix[rm][idx] + rm_cl_matrix[rm][idx] - rm_op_matrix[rm][idx])
    rm_op_matrix[rm][12], rm_cl_matrix[rm][12], rm_purch_matrix[rm][12] = rm_op_matrix[rm][0], rm_cl_matrix[rm][11], sum(rm_purch_matrix[rm][0:12])
    horizon_map, prev_map = {"Year 2": 13, "Year 3": 14, "Year 4": 15, "Year 5": 16}, {"Year 2": 12, "Year 3": 13, "Year 4": 14, "Year 5": 15}
    for yr, idx in horizon_map.items():
        rm_op_matrix[rm][idx] = rm_cl_matrix[rm][prev_map[yr]]
        rm_cl_matrix[rm][idx] = ((rm_gross_cons_matrix[rm][idx] / 12.0) / 30.0) * days_hold_rm
        rm_purch_matrix[rm][idx] = max(0.0, rm_gross_cons_matrix[rm][idx] + rm_cl_matrix[rm][idx] - rm_op_matrix[rm][idx])

rm_price_horizon = {rm: [0.0]*17 for rm in raw_materials}
inf_y2 = safe_float(edited_rm_inflation_df.loc[edited_rm_inflation_df["Timeline"] == "Year 2 Price Inflation (%)", "Inflation Rates (%)"].values) / 100.0
inf_y3 = safe_float(edited_rm_inflation_df.loc[edited_rm_inflation_df["Timeline"] == "Year 3 Price Inflation (%)", "Inflation Rates (%)"].values) / 100.0
inf_y4 = safe_float(edited_rm_inflation_df.loc[edited_rm_inflation_df["Timeline"] == "Year 4 Price Inflation (%)", "Inflation Rates (%)"].values) / 100.0
inf_y5 = safe_float(edited_rm_inflation_df.loc[edited_rm_inflation_df["Timeline"] == "Year 5 Price Inflation (%)", "Inflation Rates (%)"].values) / 100.0

for rm in raw_materials:
    initial_base_rate = safe_float(edited_rm_price_df.loc[edited_rm_price_df["Raw Material"] == rm, "Initial Price"].values)
    for idx in range(12): rm_price_horizon[rm][idx] = initial_base_rate
    rm_price_horizon[rm][12] = initial_base_rate
    rm_price_horizon[rm][13] = initial_base_rate * (1 + inf_y2)
    rm_price_horizon[rm][14] = rm_price_horizon[rm][13] * (1 + inf_y3)
    rm_price_horizon[rm][15] = rm_price_horizon[rm][14] * (1 + inf_y4)
    rm_price_horizon[rm][16] = rm_price_horizon[rm][15] * (1 + inf_y5)

rm_purch_val_matrix, rm_cons_val_matrix, rm_loss_val_matrix, rm_op_val_matrix, rm_cl_val_matrix = {rm: [0.0]*17 for rm in raw_materials}, {rm: [0.0]*17 for rm in raw_materials}, {rm: [0.0]*17 for rm in raw_materials}, {rm: [0.0]*17 for rm in raw_materials}, {rm: [0.0]*17 for rm in raw_materials}
for rm in raw_materials:
    for idx in range(17):
        rm_purch_val_matrix[rm][idx] = (rm_purch_matrix[rm][idx] * rm_price_horizon[rm][idx]) / 100000.0
        rm_cons_val_matrix[rm][idx] = (rm_gross_cons_matrix[rm][idx] * rm_price_horizon[rm][idx]) / 100000.0
        rm_loss_val_matrix[rm][idx] = (rm_total_loss_matrix[rm][idx] * rm_price_horizon[rm][idx]) / 100000.0
        rm_op_val_matrix[rm][idx] = (rm_op_matrix[rm][idx] * rm_price_horizon[rm][idx]) / 100000.0
        rm_cl_val_matrix[rm][idx] = (rm_cl_matrix[rm][idx] * rm_price_horizon[rm][idx]) / 100000.0
# Direct Expenses are proportionate to Production Qt i.e. Production Qt X Rate per unit
direct_exp_rates = {ex: {} for ex in direct_exp_heads}
direct_exp_vals = {ex: {} for ex in direct_exp_heads}

for ex in direct_exp_heads:
    for p in products:
        base_rate = safe_float(edited_direct_exp_rates_df.loc[edited_direct_exp_rates_df["Expense Head"] == ex, p].values)
        d_inf_y2 = safe_float(edited_direct_exp_inflation_df.loc[edited_direct_exp_inflation_df["Timeline"] == "Year 2 Inflation (%)", p].values) / 100.0
        d_inf_y3 = safe_float(edited_direct_exp_inflation_df.loc[edited_direct_exp_inflation_df["Timeline"] == "Year 3 Inflation (%)", p].values) / 100.0
        d_inf_y4 = safe_float(edited_direct_exp_inflation_df.loc[edited_direct_exp_inflation_df["Timeline"] == "Year 4 Inflation (%)", p].values) / 100.0
        d_inf_y5 = safe_float(edited_direct_exp_inflation_df.loc[edited_direct_exp_inflation_df["Timeline"] == "Year 5 Inflation (%)", p].values) / 100.0
        
        rates = [base_rate] * 12
        rates.append(base_rate) # Year 1 Rate standard baseline placeholder
        
        r_y2 = base_rate * (1.0 + d_inf_y2)
        r_y3 = r_y2 * (1.0 + d_inf_y3)
        r_y4 = r_y3 * (1.0 + d_inf_y4)
        r_y5 = r_y4 * (1.0 + d_inf_y5)
        rates.extend([r_y2, r_y3, r_y4, r_y5])
        direct_exp_rates[ex][p] = rates
        
        vals = []
        for idx in range(12):
            vals.append((fg_prod_matrix[p][idx] * rates[idx]) / 100000.0)
        vals.append(sum(vals[0:12])) # Year 1 Total Sum of M1-M12
        for idx in range(13, 17):
            vals.append((fg_prod_matrix[p][idx] * rates[idx]) / 100000.0)
        direct_exp_vals[ex][p] = vals

# -----------------------------------------------------------------------------
# CHAPTER 4: COMPILING STRUCTURED REPORTING MATRICES WITH DYNAMIC FILTERS
# -----------------------------------------------------------------------------
def compile_report_base(matrix_dict, main_key="Product"):
    df = pd.DataFrame(matrix_dict, index=display_columns).T
    df.insert(0, main_key, df.index)
    t_row = {main_key: "Total"}
    for col in display_columns: t_row[col] = df[col].sum()
    return pd.concat([df, pd.DataFrame([t_row])], ignore_index=True)

df_rev_final = compile_report_base(rev_matrix, "Product")
df_rev_final.iloc[0:, 1:] = df_rev_final.iloc[0:, 1:] / 100000.0
df_qty_final = compile_report_base(qty_matrix, "Product")

all_prod_dfs = []
for p in products:
    p_flow_df = pd.DataFrame({"Product": [p, "", "", ""], "FG Inventory Metrics": ["1. Opening Stock", "2. Sales Qty", "3. Production Qty", "4. Closing Stock"]})
    for idx, col in enumerate(display_columns): p_flow_df[col] = [fg_op_matrix[p][idx], prod_sales_matrix[p][idx], fg_prod_matrix[p][idx], fg_cl_matrix[p][idx]]
    all_prod_dfs.append(p_flow_df)
master_prod_flow_df = pd.concat(all_prod_dfs, ignore_index=True)

df_summary_prod = compile_report_base(fg_prod_matrix, "Product")
df_summary_op = compile_report_base(fg_op_matrix, "Product")
df_summary_cl = compile_report_base(fg_cl_matrix, "Product")

all_rm_flow_rows = []
for rm in raw_materials:
    rm_block = pd.DataFrame({"Raw Material": [rm, "", "", ""], "RM Flow(Qt) Metrics": ["Op stk", "Generated / Purchased", "Consumption", "Cl stk"]})
    for idx, col in enumerate(display_columns): rm_block[col] = [rm_op_matrix[rm][idx], rm_purch_matrix[rm][idx], rm_gross_cons_matrix[rm][idx], rm_cl_matrix[rm][idx]]
    all_rm_flow_rows.append(rm_block)
master_rm_flow_df = pd.concat(all_rm_flow_rows, ignore_index=True)

df_rm_consumption_final = compile_report_base(rm_gross_cons_matrix, "Raw Material")
df_rm_purchase_final = compile_report_base(rm_purch_matrix, "Raw Material")
df_rm_loss_final = compile_report_base(rm_total_loss_matrix, "Raw Material")

df_scrap_final = pd.DataFrame(fg_scrap_matrix, index=display_columns).T
df_scrap_final.insert(0, "Scrap (Qt)", ["Scrap P1 (SP1)", "Scrap P2 (SP2)", "Scrap P3 (SP3)"])
t_scrap_row = {"Scrap (Qt)": "Total"}
for col in display_columns: t_scrap_row[col] = df_scrap_final[col].sum()
df_scrap_final = pd.concat([df_scrap_final, pd.DataFrame([t_scrap_row])], ignore_index=True)

df_rm_purchase_val_final = compile_report_base(rm_purch_val_matrix, "Raw Material")
df_rm_consumption_val_final = compile_report_base(rm_cons_val_matrix, "Raw Material")
df_rm_loss_val_final = compile_report_base(rm_total_loss_matrix, "Raw Material")
df_rm_op_val_final = compile_report_base(rm_op_val_matrix, "Raw Material")
df_rm_cl_val_final = compile_report_base(rm_cl_val_matrix, "Raw Material")

all_rm_val_flow_rows = []
for rm in raw_materials:
    rm_v_block = pd.DataFrame({"Raw Material": [rm, "", "", ""], "RM Flow(Rs) Metrics": ["Op stk", "Generated / Purchased", "Consumption", "Cl stk"]})
    for idx, col in enumerate(display_columns): rm_v_block[col] = [rm_op_val_matrix[rm][idx], rm_purch_val_matrix[rm][idx], rm_cons_val_matrix[rm][idx], rm_cl_val_matrix[rm][idx]]
    all_rm_val_flow_rows.append(rm_v_block)
master_rm_val_flow_df = pd.concat(all_rm_val_flow_rows, ignore_index=True)
pl_rows = []
def append_pl_row(si_no, block_id, row_depth_type, lvl1, lvl2, lvl3, data_series, format_as_pct=False):
    row_dict = {"Si No": si_no, "BlockID": block_id, "Depth": row_depth_type, "Level 1": lvl1, "Level 2": lvl2, "Level 3": lvl3}
    for col_idx, col_name in enumerate(display_columns): row_dict[col_name] = data_series[col_idx]
    row_dict["_is_pct"] = format_as_pct
    pl_rows.append(row_dict)

# 1. Sale (Qt)
append_pl_row("1", "1", "L1", "Sale (Qt) :", "", "", [sum(qty_matrix[p][i] for p in products) for i in range(17)])
for p in products: append_pl_row("", "1", "L2", "", p, "", qty_matrix[p])

# 2. Production (Qt)
append_pl_row("2", "2", "L1", "Production (Qt) :", "", "", [sum(fg_prod_matrix[p][i] for p in products) for i in range(17)])
for p in products: append_pl_row("", "2", "L2", "", p, "", fg_prod_matrix[p])

# 3. Revenue (Rs)
append_pl_row("3", "3", "L1", "Revenue (Rs) :", "", "", [sum(rev_matrix[p][i] for p in products)/100000.0 for i in range(17)])
for p in products: append_pl_row("", "3", "L2", "", p, "", [v/100000.0 for v in rev_matrix[p]])

# 4. RM Consumption (Rs)
append_pl_row("4", "4", "L1", "RM Consumption (Rs) :", "", "", [sum(rm_cons_val_matrix[rm][i] for rm in raw_materials) for i in range(17)])
for rm in raw_materials:
    append_pl_row("", "4", "L2", "", rm, "", rm_cons_val_matrix[rm])
    append_pl_row("", "4", "L3", "", "", "Opening stk", rm_op_val_matrix[rm])
    append_pl_row("", "4", "L3", "", "", "Purchase", rm_purch_val_matrix[rm])
    append_pl_row("", "4", "L3", "", "", "Consumption", rm_cons_val_matrix[rm])
    append_pl_row("", "4", "L3", "", "", "Cl stock", rm_cl_val_matrix[rm])

# 5. RM Consumption (%)
total_rev_lacs = [max(0.0001, sum(rev_matrix[p][i] for p in products)/100000.0) for i in range(17)]
total_cons_lacs = [sum(rm_cons_val_matrix[rm][i] for rm in raw_materials) for i in range(17)]
pct_series = [(c / r * 100.0) for c, r in zip(total_cons_lacs, total_rev_lacs)]
append_pl_row("5", "5", "L1", "RM Consumption (%) (4/3)", "", "", pct_series, format_as_pct=True)
for rm in raw_materials:
    rm_pct_series = [(rm_cons_val_matrix[rm][i] / total_rev_lacs[i] * 100.0) for i in range(17)]
    append_pl_row("", "5", "L2", "", rm, "", rm_pct_series, format_as_pct=True)

# 6-10. Direct Expenses Heads (As per target attachment list layout)
for idx, ex in enumerate(direct_exp_heads):
    si = str(6 + idx)
    append_pl_row(si, si, "L1", f"{ex} :", "", "", [sum(direct_exp_vals[ex][p][i] for p in products) for i in range(17)])
    for p in products: append_pl_row("", si, "L2", "", p, "", direct_exp_vals[ex][p])

# 11. Total Direct Exp
total_direct_series = [sum(direct_exp_vals[ex][p][i] for ex in direct_exp_heads for p in products) for i in range(17)]
append_pl_row("11", "11", "L1", "Total Direct Exp (6+7+8+9+10)", "", "", total_direct_series)
for p in products:
    p_dir_sum = [sum(direct_exp_vals[ex][p][i] for ex in direct_exp_heads) for i in range(17)]
    append_pl_row("", "11", "L2", "", p, "", p_dir_sum)

# 12. COGS (4+11)
cogs_series = [c + d for c, d in zip(total_cons_lacs, total_direct_series)]
append_pl_row("12", "12", "L1", "COGS (4+11)", "", "", cogs_series)
for p in products:
    if p == "P1": p_rms = ["RM1","RM2","RM3","RM4","RM5","RM6"]
    elif p == "P2": p_rms = ["RM1","RM7","RM8","RM9","RM10"]
    else: p_rms = ["RM1","RM11","RM12"]
    p_cogs = [sum(rm_cons_val_matrix[rm][i] for rm in p_rms) + sum(direct_exp_vals[ex][p][i] for ex in direct_exp_heads) for i in range(17)]
    append_pl_row("", "12", "L2", "", p, "", p_cogs)

# 13. COGS % (12/3)
cogs_pct_series = [(c / r * 100.0) for c, r in zip(cogs_series, total_rev_lacs)]
append_pl_row("13", "13", "L1", "COGS % (12/3)", "", "", cogs_pct_series, format_as_pct=True)
for p in products:
    if p == "P1": p_rms = ["RM1","RM2","RM3","RM4","RM5","RM6"]
    elif p == "P2": p_rms = ["RM1","RM7","RM8","RM9","RM10"]
    else: p_rms = ["RM1","RM11","RM12"]
    p_rev_lacs = [max(0.0001, rev_matrix[p][i]/100000.0) for i in range(17)]
    p_cogs = [sum(rm_cons_val_matrix[rm][i] for rm in p_rms) + sum(direct_exp_vals[ex][p][i] for ex in direct_exp_heads) for i in range(17)]
    append_pl_row("", "13", "L2", "", p, "", [(c / r * 100.0) for c, r in zip(p_cogs, p_rev_lacs)], format_as_pct=True)

# 14. Gross Profit
gp_series = [r - c for r, c in zip(total_rev_lacs, cogs_series)]
append_pl_row("14", "14", "L1", "Gross Profit", "", "", gp_series)
for p in products:
    if p == "P1": p_rms = ["RM1","RM2","RM3","RM4","RM5","RM6"]
    elif p == "P2": p_rms = ["RM1","RM7","RM8","RM9","RM10"]
    else: p_rms = ["RM1","RM11","RM12"]
    p_rev_lacs = [rev_matrix[p][i]/100000.0 for i in range(17)]
    p_cogs = [sum(rm_cons_val_matrix[rm][i] for rm in p_rms) + sum(direct_exp_vals[ex][p][i] for ex in direct_exp_heads) for i in range(17)]
    append_pl_row("", "14", "L2", "", p, "", [r - c for r, c in zip(p_rev_lacs, p_cogs)])

# 15. Gross Profit %
gp_pct_series = [(g / r * 100.0) for g, r in zip(gp_series, total_rev_lacs)]
append_pl_row("15", "15", "L1", "Gross Profit %", "", "", gp_pct_series, format_as_pct=True)
for p in products:
    if p == "P1": p_rms = ["RM1","RM2","RM3","RM4","RM5","RM6"]
    elif p == "P2": p_rms = ["RM1","RM7","RM8","RM9","RM10"]
    else: p_rms = ["RM1","RM11","RM12"]
    p_rev_lacs = [max(0.0001, rev_matrix[p][i]/100000.0) for i in range(17)]
    p_cogs = [sum(rm_cons_val_matrix[rm][i] for rm in p_rms) + sum(direct_exp_vals[ex][p][i] for ex in direct_exp_heads) for i in range(17)]
    p_gp = [r - c for r, c in zip(p_rev_lacs, p_cogs)]
    append_pl_row("", "15", "L2", "", p, "", [(g / r * 100.0) for g, r in zip(p_gp, p_rev_lacs)], format_as_pct=True)

df_pl_master_raw = pd.DataFrame(pl_rows)
# Helper to perform uniform product-slicing across the dashboard tabs
def filter_dataframe_by_product(df, column_name="Product"):
    if global_product_filter == "All":
        return df
    return df[df[column_name].isin([global_product_filter, "Total"])]

page_tab1, page_tab2, page_tab3, page_tab4, page_tab5, page_tab6 = st.tabs(["Revenue", "FG", "RM Qt", "RM Val", "Direct Exp", "PL"])

with page_tab1:
    st.title("Sales Forecasting")
    st.subheader("1. Revenue (Rs in Lacs)")
    st.dataframe(filter_dataframe_by_product(df_rev_final).style.format({col: "{:,.2f} L" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)
    st.subheader("2. Sale (Qt)")
    st.dataframe(filter_dataframe_by_product(df_qty_final).style.format({col: "{:,.0f}" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)

with page_tab2:
    st.title("Production Forecasting")
    st.subheader("1. FG Flow (Qt)")
    st.dataframe(master_prod_flow_df[master_prod_flow_df["Product"].isin(["", global_product_filter]) if global_product_filter != "All" else [True]*len(master_prod_flow_df)].style.format({col: "{:,.0f}" for col in display_columns if col not in ["Product", "FG Inventory Metrics"]}), use_container_width=True, hide_index=True)
    st.subheader("2. Production (Qt)")
    st.dataframe(filter_dataframe_by_product(df_summary_prod).style.format({col: "{:,.0f}" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)
    st.subheader("3. FG Closing Stock (Qt)")
    st.dataframe(filter_dataframe_by_product(df_summary_cl).style.format({col: "{:,.0f}" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)
    st.subheader("4. FG Opening Stock (Qt)")
    st.dataframe(filter_dataframe_by_product(df_summary_op).style.format({col: "{:,.0f}" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)

with page_tab3:
    st.title("Material Forecasting")
    st.subheader("1. RM Flow (Qt)")
    st.dataframe(master_rm_flow_df.style.format({col: "{:,.0f}" for col in display_columns if col not in ["Raw Material", "RM Flow(Qt) Metrics"]}), use_container_width=True, hide_index=True)
    st.subheader("2. RM Consumption (Qt)")
    st.dataframe(df_rm_consumption_final.style.format({col: "{:,.0f}" for col in display_columns if col != "Raw Material"}), use_container_width=True, hide_index=True)
    st.subheader("3. RM Purchase (Qt)")
    st.dataframe(df_rm_purchase_final.style.format({col: "{:,.0f}" for col in display_columns if col != "Raw Material"}), use_container_width=True, hide_index=True)
    st.subheader("4. RM Loss (Qt)")
    st.dataframe(df_rm_loss_final.style.format({col: "{:,.0f}" for col in display_columns if col != "Raw Material"}), use_container_width=True, hide_index=True)
    st.subheader("5. Scrap (Qt)")
    st.dataframe(df_scrap_final.style.format({col: "{:,.0f}" for col in display_columns if col != "Scrap (Qt)"}), use_container_width=True, hide_index=True)

with page_tab4:
    st.title("Material Forecasting")
    st.subheader("1. RM Flow (Rs in Lacs)")
    st.dataframe(master_rm_val_flow_df.style.format({col: "{:,.2f} L" for col in display_columns if col not in ["Raw Material", "RM Flow(Rs) Metrics"]}), use_container_width=True, hide_index=True)
    st.subheader("2. RM Purchase (Rs in Lacs)")
    st.dataframe(df_rm_purchase_val_final.style.format({col: "{:,.2f} L" for col in display_columns if col != "Raw Material"}), use_container_width=True, hide_index=True)
    st.subheader("3. RM Consumption (Rs in Lacs)")
    st.dataframe(df_rm_consumption_val_final.style.format({col: "{:,.2f} L" for col in display_columns if col != "Raw Material"}), use_container_width=True, hide_index=True)
    st.subheader("4. RM Loss (Rs in Lacs)")
    st.dataframe(df_rm_loss_val_final.style.format({col: "{:,.2f} L" for col in display_columns if col != "Raw Material"}), use_container_width=True, hide_index=True)
with page_tab5:
    st.title("Direct Production Expenses Viewport Operational Log")
    for ex in direct_exp_heads:
        st.markdown(f"### ⚙️ Direct Overhead Category Ledger: {ex}")
        
        # Table 1: Direct Expense Valuation Ledger (Rs in Lacs)
        v_dict = {p: direct_exp_vals[ex][p] for p in products}
        df_ex_val = compile_report_base(v_dict, "Product")
        st.write("**Table 1: Direct Expense Valuation Ledger (Rs in Lacs):**")
        st.dataframe(filter_dataframe_by_product(df_ex_val).style.format({col: "{:,.2f} L" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)
        
        # Table 2: Direct Expense Unit Applied Rate Matrix (Rs / Kg Volume)
        r_dict = {p: direct_exp_rates[ex][p] for p in products}
        df_ex_rate = pd.DataFrame(r_dict, index=display_columns).T.reset_index().rename(columns={"index": "Product"})
        t_rate_row = {"Product": "Total"}
        for col_name in display_columns:
            tot_val = df_ex_val.loc[df_ex_val["Product"] == "Total", col_name].values * 100000.0
            tot_prod = df_summary_prod.loc[df_summary_prod["Product"] == "Total", col_name].values
            t_rate_row[col_name] = tot_val / tot_prod if tot_prod > 0 else 0.0
        df_ex_rate = pd.concat([df_ex_rate, pd.DataFrame([t_rate_row])], ignore_index=True)
        st.write("**Table 2: Direct Expense Unit Applied Rate Matrix (Rs / Kg Volume):**")
        st.dataframe(filter_dataframe_by_product(df_ex_rate).style.format({col: "{:,.2f}" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)
        
        # Table 3: Expense Margin Percentage Matrix (% over Revenue)
        m_dict = {}
        for p in products:
            p_m_vals = []
            for idx in range(17):
                r_val = rev_matrix[p][idx] / 100000.0
                p_m_vals.append((direct_exp_vals[ex][p][idx] / r_val * 100.0) if r_val > 0 else 0.0)
            m_dict[p] = p_m_vals
        df_ex_margin = pd.DataFrame(m_dict, index=display_columns).T.reset_index().rename(columns={"index": "Product"})
        t_margin_row = {"Product": "Total"}
        for col_name in display_columns:
            tot_val = df_ex_val.loc[df_ex_val["Total" == df_ex_val["Product"], col_name]].values if "Total" in df_ex_val["Product"].values else df_ex_val[col_name].sum()
            tot_val = df_ex_val.loc[df_ex_val["Product"] == "Total", col_name].values
            tot_rev = df_rev_final.loc[df_rev_final["Product"] == "Total", col_name].values
            t_margin_row[col_name] = (tot_val / tot_rev * 100.0) if tot_rev > 0 else 0.0
        df_ex_margin = pd.concat([df_ex_margin, pd.DataFrame([t_margin_row])], ignore_index=True)
        st.write("**Table 3: Direct Exp % (Expense % against Sale):**")
        st.dataframe(filter_dataframe_by_product(df_ex_margin).style.format({col: "{:,.2f}%" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)
        st.markdown("---")

with page_tab6:
    st.title("PL Forecast")
    st.caption("Tick / untick the checkbox in the '+/-' column on any heading row to expand or collapse it. "
               "[+] = collapsed, [-] = expanded.")

    master_pl = df_pl_master_raw.reset_index(drop=True)
    
    # Global Product filter constraint matching within the P&L rows scope
    if global_product_filter != "All":
        master_pl = master_pl[(master_pl["Level 2"] == "") | (master_pl["Level 2"] == global_product_filter) | (master_pl["Level 2"] == "Total")]
        master_pl = master_pl.reset_index(drop=True)

    node_info = []
    cur_l1, cur_l2 = None, None
    for i in range(len(master_pl)):
        b_id, depth = str(master_pl.at[i, "BlockID"]), master_pl.at[i, "Depth"]
        if depth == "L1":
            node, ancestors = f"L1|{b_id}", []
            cur_l1, cur_l2 = node, None
        elif depth == "L2":
            node, ancestors = f"L2|{b_id}|{i}", [cur_l1]
            cur_l2 = node
        else:
            node, ancestors = f"L3|{b_id}|{i}", [cur_l1, cur_l2]
        child_depth = {"L1": "L2", "L2": "L3"}.get(depth)
        has_children = (
            child_depth is not None and i + 1 < len(master_pl)
            and master_pl.at[i + 1, "Depth"] == child_depth
            and str(master_pl.at[i + 1, "BlockID"]) == b_id
        )
        node_info.append({"node": node, "ancestors": ancestors, "has_children": has_children})

    open_nodes = st.session_state.pl_open_nodes
    visible_idx = [i for i, n in enumerate(node_info) if all(a in open_nodes for a in n["ancestors"])]
    st.session_state.pl_row_map = [(node_info[i]["node"], node_info[i]["has_children"]) for i in visible_idx]

    def pl_tree_toggle_cb():
        ver = st.session_state.pl_editor_ver
        editor_state = st.session_state.get(f"pl_tree_editor_{ver}", {})
        row_map = st.session_state.get("pl_row_map", [])
        for r_pos, changes in editor_state.get("edited_rows", {}).items():
            r_pos = int(r_pos)
            if "+/-" in changes and 0 <= r_pos < len(row_map) and row_map[r_pos][1]:
                if changes["+/-"]: st.session_state.pl_open_nodes.add(row_map[r_pos][0])
                else: st.session_state.pl_open_nodes.discard(row_map[r_pos][0])
        st.session_state.pl_editor_ver = ver + 1

    df_pl_filtered = master_pl.loc[visible_idx].copy() if visible_idx else pd.DataFrame(columns=master_pl.columns)

    if not df_pl_filtered.empty:
        def add_tree_prefix(r):
            info = node_info[r.name]
            mark = ("[-] " if info["node"] in open_nodes else "[+] ") if info["has_children"] else ""
            d, l1, l2, l3 = r["Depth"], r["Level 1"], r["Level 2"], r["Level 3"]
            if d == "L1": return f"{mark}{l1}", l2, l3
            elif d == "L2": return l1, f"{mark}{l2}", l3
            else: return l1, l2, l3

        prefixed_tuples = [add_tree_prefix(r) for _, r in df_pl_filtered.iterrows()]
        df_pl_filtered["Level 1"] = [t[0] for t in prefixed_tuples]
        df_pl_filtered["Level 2"] = [t[1] for t in prefixed_tuples]
        df_pl_filtered["Level 3"] = [t[2] for t in prefixed_tuples]

        display_pl_df = df_pl_filtered.drop(columns=["_is_pct", "BlockID", "Depth"])

        def format_pl_dataframe(row):
            is_pct = df_pl_filtered.loc[row.name, "_is_pct"]
            formatted_row = row.copy()
            for col in display_columns:
                val = safe_float(row[col])
                if is_pct: formatted_row[col] = f"{val:.2f}%"
                elif "Sale" in str(row["Level 1"]) or "Production" in str(row["Level 1"]) or (row["Level 2"] != "" and row["Level 1"] == "" and not str(row["Level 2"]).startswith("RM") and "Stock" not in str(row["Level 2"]) and "stk" not in str(row["Level 2"]) and "stk" not in str(row["Level 3"]) and "Stock" not in str(row["Level 3"]) and "Purchase" not in str(row["Level 3"]) and "Consumption" not in str(row["Level 3"])):
                    formatted_row[col] = f"{val:,.0f}"
                else: formatted_row[col] = f"{val:,.2f} L"
            return formatted_row

        styled_pl_df = display_pl_df.apply(format_pl_dataframe, axis=1).reset_index(drop=True)
        toggle_vals = [((node_info[i]["node"] in open_nodes) if node_info[i]["has_children"] else None) for i in visible_idx]
        styled_pl_df.insert(0, "+/-", pd.array(toggle_vals, dtype="boolean"))

        st.data_editor(
            styled_pl_df,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            disabled=[c for c in styled_pl_df.columns if c != "+/-"],
            column_config={"+/-": st.column_config.CheckboxColumn("+/-", help="Tick to expand, untick to collapse", width="small")},
            key=f"pl_tree_editor_{st.session_state.pl_editor_ver}",
            on_change=pl_tree_toggle_cb,
        )
    else:
        st.warning("No structural P&L rows selected.")
st.markdown("---")
output_buffer = BytesIO()
with pd.ExcelWriter(output_buffer, engine="openpyxl") as writer:
    df_rev_final.to_excel(writer, sheet_name="Revenue (Lacs)", index=False)
    df_qty_final.to_excel(writer, sheet_name="Quantity Volumes", index=False)
    if not master_prod_flow_df.empty: master_prod_flow_df.to_excel(writer
, sheet_name="FG Flow Ledger", index=False)
df_summary_prod.to_excel(writer, sheet_name="Summary Production", index=False)
if not master_rm_flow_df.empty: master_rm_flow_df.to_excel(writer, sheet_name="RM Flow Ledger", index=False)
df_rm_consumption_final.to_excel(writer, sheet_name="RM Consumption Vol", index=False)
df_scrap_final.to_excel(writer, sheet_name="Visible Scrap Report", index=False)
df_pl_master_raw.to_excel(writer, sheet_name="Master Financial P&L Statement", index=False)
st.download_button(
label="📥 Download Updated Comprehensive Interconnected Workbook",
data=output_buffer.getvalue(),
file_name="Sales_Production_DirectExp_And_PL_Forecasting_Report.xlsx",
mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
import streamlit.components.v1 as components
components.html(r"""

(function () {
const P = window.parent, doc = P.document;
const MAP = {"Revenue": "Sales / FG Feed", "FG": "Sales / FG Feed",
"RM Qt": "RM Qt Feed", "RM Val": "RM Val Feed",
"Direct Exp": "Direct Exp Feed", "PL": "RM Val Feed"};
const norm = s => (s || "").replace(/\s+/g, " ").trim();
if (P.__tabRadioSyncHandler) doc.removeEventListener("click", P.__tabRadioSyncHandler, true);
P.__tabRadioSyncHandler = function (e) {
const tab = e.target.closest('button[role="tab"]');
if (!tab) return;
const want = MAP[norm(tab.innerText)];
if (!want) return;
const labels = doc.querySelectorAll('[data-testid="stSidebar"] label');
for (const lb of labels) {
const inp = lb.querySelector('input[type="radio"]');
if (inp && norm(lb.innerText) === want) {
if (!inp.checked) lb.click();
return;
}
}
};
doc.addEventListener("click", P.__tabRadioSyncHandler, true);
})();

""", height=0)