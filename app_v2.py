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
    /* ===== Deep Prussian Blue + Gold theme, compact layout ===== */
    .stApp { background: #F6F4EC; }
    header[data-testid="stHeader"] { z-index: 99 !important; background: transparent !important; height: 2rem !important; min-height: 2rem !important; }
    .block-container { padding-top: 2.4rem !important; padding-bottom: 1rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; max-width: 100% !important; }
    div[data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    hr { border-color: #D4AF37 !important; margin: 0.5rem 0 !important; }

    /* Navigation tabs: same blue as the cockpit, bright-gold text + gold left accent bar (default); red text + red left bar (selected). No underline */
    div[data-testid="stTabs"] {
        position: sticky !important; top: 0px !important; background-color: #F6F4EC !important;
        z-index: 9999 !important; padding-top: 4px !important; padding-bottom: 6px !important;
    }
    .stApp div[role="tablist"], .stApp div[data-baseweb="tab-list"] {
        background: #00294A !important; border: none !important; border-radius: 8px !important;
        padding: 6px 10px !important; gap: 10px !important;
    }
    .stApp [role="tab"] { background: transparent !important; border-radius: 4px !important; border: none !important; border-left: 4px solid #D4AF37 !important; box-shadow: none !important; padding: 6px 14px !important; }
    .stApp [role="tab"], .stApp [role="tab"] *, .stApp [role="tab"] p { color: #FFD24C !important; font-weight: 700 !important; }
    .stApp [role="tab"]:hover { background: rgba(255,210,76,0.12) !important; }
    .stApp [role="tab"][aria-selected="true"] { background: #0B3D6B !important; border-left: 4px solid #E53935 !important; }
    .stApp [role="tab"][aria-selected="true"], .stApp [role="tab"][aria-selected="true"] *, .stApp [role="tab"][aria-selected="true"] p { color: #FF5252 !important; }
    div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] { display: none !important; }

    /* Headings (explicit line-height + bottom space so a heading never sits under the table below it) */
    .stApp h1 { color: #00294A !important; font-size: 1.8rem !important; padding: 0 0 0.1rem 0 !important; margin: 0 !important; border-bottom: 3px solid #D4AF37; display: inline-block; }
    .stApp h2, .stApp h3 { color: #00294A !important; font-size: 1.2rem !important; line-height: 1.6 !important; padding: 0.1rem 0 0.45rem 0.6rem !important; margin: 0.5rem 0 0.5rem 0 !important; border-left: 5px solid #D4AF37; overflow: visible !important; }
    .stApp h5 { color: #0B3D6B !important; line-height: 1.6 !important; margin: 0.4rem 0 0.4rem 0 !important; padding: 0.1rem 0 0.4rem 0 !important; overflow: visible !important; }
    div[data-testid="stHeading"], div[data-testid="stHeadingWithActionElements"] { height: auto !important; overflow: visible !important; margin-bottom: 0.3rem !important; }
    div[data-testid="stCaptionContainer"] p { color: #0B3D6B !important; }

    /* Slicer + download button */
    div[data-baseweb="select"] > div { border: 1.5px solid #D4AF37 !important; background: #FFFDF5 !important; }
    div[data-testid="stDownloadButton"] button { background: #00294A !important; border: 2px solid #D4AF37 !important; }
    div[data-testid="stDownloadButton"] button p { color: #F1DE9C !important; font-weight: 600 !important; }
    div[data-testid="stDownloadButton"] button:hover { background: #D4AF37 !important; }
    div[data-testid="stDownloadButton"] button:hover p { color: #00294A !important; }

    /* Tables */
    div[data-testid="stDataFrame"] { border: 1.5px solid #D4AF37; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,41,74,0.18); margin-top: 0.35rem; }

    /* Sidebar cockpit */
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #00294A, #001B33) !important; border-right: 2px solid #D4AF37; }
    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] { height: 2.2rem !important; min-height: 0 !important; padding-top: 0.4rem !important; margin-bottom: 0 !important; }
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] { padding-top: 0.2rem !important; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { color: #D4AF37 !important; border-left: none !important; padding-left: 0 !important; }
    section[data-testid="stSidebar"] label p, section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: #F1DE9C !important; }
    section[data-testid="stSidebar"] hr { border-color: #D4AF37 !important; }
    section[data-testid="stSidebar"] h2 { margin-top: 0.9rem !important; }
    section[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] { margin: 0.3rem 0 0.5rem 0 !important; }
    /* heading card above every feed box */
    .feed-title { color: #FFD24C; font-weight: 700; font-size: 0.9rem; line-height: 1.4; background: rgba(212,175,55,0.16); border-left: 5px solid #D4AF37; border-radius: 6px; padding: 6px 10px; margin: 1.1rem 0 0.7rem 0; }
    /* feed boxes: gold frame + glow so they read as boxes to key into */
    section[data-testid="stSidebar"] div[data-testid="stDataFrame"] { border: 2px solid #D4AF37 !important; border-radius: 10px !important; box-shadow: 0 0 0 3px rgba(212,175,55,0.35), 0 6px 14px rgba(0,0,0,0.45) !important; margin: 0.5rem 0.4rem 1.1rem 0.2rem !important; }
    section[data-testid="stSidebar"] div[data-testid="stNumberInput"] div[data-baseweb="input"] { background: #FFF6D6 !important; border: 2px solid #D4AF37 !important; border-radius: 8px !important; }
    section[data-testid="stSidebar"] div[data-testid="stNumberInput"] input { color: #00294A !important; font-weight: 700 !important; background: transparent !important; }
    /* cockpit spread / squeeze arrow button */
    section[data-testid="stSidebar"] div[data-testid="stButton"] { display: flex; justify-content: flex-end; }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button { background: #D4AF37 !important; border: 2px solid #F1DE9C !important; min-height: 2rem !important; padding: 0 0.9rem !important; }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button, section[data-testid="stSidebar"] div[data-testid="stButton"] button * { color: #00294A !important; font-weight: 800 !important; }
    </style>
""", unsafe_allow_html=True)

products = ["P1", "P2", "P3"]
raw_materials = [f"RM{i}" for i in range(1, 13)]
months = [f"M{i}" for i in range(1, 13)]
future_years = ["Year 2", "Year 3", "Year 4", "Year 5"]
display_columns = months + ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]

# 1. Initialize Baseline Quantities Matrix
if "sidebar_qty_df" not in st.session_state:
    st.session_state.sidebar_qty_df = pd.DataFrame({
        "Timeline": months, "P1": [10000.0] * 12, "P2": [5000.0] * 12, "P3": [1000.0] * 12
    })

# 2. Initialize Price Rate Parameters Matrix with request defaults
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

# PERSISTENT SWITCH DICTIONARY STORING INDEPENDENT P&L TREE BLOCK NODES
if "pl_tree_expanded_nodes" not in st.session_state:
    st.session_state.pl_tree_expanded_nodes = {
        "1": False, "2": False, "3": False, "4": "L1 Summary", "5": False
    }

if "active_tab_sync" not in st.session_state:
    st.session_state.active_tab_sync = "Revenue"

# P&L tree: set of expanded nodes (all collapsed by default) + editor version counter
if "pl_open_nodes" not in st.session_state:
    st.session_state.pl_open_nodes = set()
if "pl_editor_ver" not in st.session_state:
    st.session_state.pl_editor_ver = 0
# Volume-growth inputs live in the Sales sidebar only; keep their values when another feed is shown
if "growth_saved" not in st.session_state:
    st.session_state.growth_saved = [5.0, 5.0, 5.0, 5.0]

# ---- DEBTORS (Revenue page) and CREDITORS (RM Val page) feeds (new) ----
if "sidebar_debtor_params_df" not in st.session_state:
    st.session_state.sidebar_debtor_params_df = pd.DataFrame({
        "Parameters": ["Days Credit", "Opening Debtors (Rs Lacs)"],
        "P1": [30.0, 20.0], "P2": [45.0, 12.0], "P3": [60.0, 6.0]
    })
if "gst_sales_saved" not in st.session_state:
    st.session_state.gst_sales_saved = 18.0
if "rm_credit_days_saved" not in st.session_state:
    st.session_state.rm_credit_days_saved = 35.0
if "gst_pur_saved" not in st.session_state:
    st.session_state.gst_pur_saved = 18.0
# Opening creditors (Rs Lacs) by RM: pre-filled with M1 purchase value + 18% GST at the default inputs; the user may overwrite any figure
if "sidebar_op_cred_df" not in st.session_state:
    st.session_state.sidebar_op_cred_df = pd.DataFrame({
        "Raw Material": raw_materials,
        "Opening Creditors (Rs Lacs)": [21.613, 4.098, 0.068, 0.683, 0.409, 0.511, 4.434, 0.846, 0.086, 0.338, 0.783, 0.261]
    })

# ---- NEW: advance payment on RM orders (RM Val feed) ----
if "adv_pct_saved" not in st.session_state:
    st.session_state.adv_pct_saved = 20.0

# ---- NEW: WC (Working Capital) page feeds ----
if "wc_cash_saved" not in st.session_state:
    st.session_state.wc_cash_saved = 0.5          # opening bank / cash balance (Rs lacs)
if "wc_roi_saved" not in st.session_state:
    st.session_state.wc_roi_saved = 9.0           # rate of interest (% p.a.)
if "wc_od_saved" not in st.session_state:
    st.session_state.wc_od_saved = 2.0            # opening bank OD / CC balance (Rs lacs)
if "wc_margin_saved" not in st.session_state:
    st.session_state.wc_margin_saved = 25.0       # margin on working capital gap (%)
wc_flow_cols = ["TL Interest & Bank Charges", "FD Increment", "Tax Payment Provision", "Other Contingency Requirement"]
wc_bal_cols = ["Stock-in-Process", "Other Current Assets", "Other Current Liabilities"]
if "sidebar_wc_flow_df" not in st.session_state:
    st.session_state.sidebar_wc_flow_df = pd.DataFrame({"Timeline": months + future_years, **{c: [0.0] * 16 for c in wc_flow_cols}})
if "sidebar_wc_bal_df" not in st.session_state:
    st.session_state.sidebar_wc_bal_df = pd.DataFrame({"Timeline": months + future_years, **{c: [0.0] * 16 for c in wc_bal_cols}})

# ---- STAGE 6: DIRECT EXPENSES FEED (new) ----
direct_heads = ["Direct Wages", "Power & Fuel", "Repair & Maintenance", "Carriage inward", "Other Direct OH"]
dx_common_heads = ["Carriage inward", "Other Direct OH"]      # one rate applied to every product
dx_short = {"Direct Wages": "Wages", "Power & Fuel": "Power & Fuel", "Repair & Maintenance": "R&M",
            "Carriage inward": "Carriage", "Other Direct OH": "Other OH"}

# Rate per unit of production (Rs) - product-wise heads
if "sidebar_dx_rate_df" not in st.session_state:
    st.session_state.sidebar_dx_rate_df = pd.DataFrame({
        "Expense Head": ["Direct Wages", "Power & Fuel", "Repair & Maintenance"],
        "P1": [7.0, 5.0, 1.0], "P2": [8.0, 6.0, 1.5], "P3": [9.0, 7.0, 2.0]
    })
# Rate per unit of production (Rs) - single rate for all products
if "sidebar_dx_common_df" not in st.session_state:
    st.session_state.sidebar_dx_common_df = pd.DataFrame({
        "Expense Head": dx_common_heads, "Rate p.u. (all products)": [3.5, 2.0]
    })
# YoY inflation (%) for Y2-Y5, every head
if "sidebar_dx_infl_df" not in st.session_state:
    st.session_state.sidebar_dx_infl_df = pd.DataFrame({
        "Expense Head": direct_heads,
        "Year 2 (%)": [5.0, 3.0, 2.0, 5.0, 2.0], "Year 3 (%)": [5.0, 3.0, 2.0, 5.0, 2.0],
        "Year 4 (%)": [5.0, 3.0, 2.0, 5.0, 2.0], "Year 5 (%)": [5.0, 3.0, 2.0, 5.0, 2.0]
    })

# ---- STAGE 7: INDIRECT EXPENSES FEED (new) ----
indirect_heads = ["Employment Cost", "Selling & Distribution", "Travelling Expenses", "Carriage Outward",
                  "Rent", "Insurance", "Warehouse Exp", "Other Admin charges"]
ix_type = {"Employment Cost": "%", "Selling & Distribution": "p.u", "Travelling Expenses": "p.u", "Carriage Outward": "p.u",
           "Rent": "%", "Insurance": "%", "Warehouse Exp": "p.u", "Other Admin charges": "%"}   # basis against sale
ix_short = {"Employment Cost": "Employment", "Selling & Distribution": "S&D", "Travelling Expenses": "Travelling",
            "Carriage Outward": "Carriage Out", "Rent": "Rent", "Insurance": "Insurance",
            "Warehouse Exp": "Warehouse", "Other Admin charges": "Other Admin"}
IX_RATE_COL = "Rate (Rs/Kg or %)"

# One rate / % for all products: p.u. heads = Rs per Kg sold, % heads = % of sale value
if "sidebar_ix_df" not in st.session_state:
    st.session_state.sidebar_ix_df = pd.DataFrame({
        "Expense Head": indirect_heads,
        "Against Sale": [ix_type[h] for h in indirect_heads],
        IX_RATE_COL: [10.0, 5.0, 2.0, 2.0, 1.0, 0.5, 0.5, 1.0]
    })
# YoY inflation (%) for Y2-Y5, every head
if "sidebar_ix_infl_df" not in st.session_state:
    _ix_inf = [5.0, 3.0, 2.0, 2.0, 5.0, 2.0, 5.0, 2.0]
    st.session_state.sidebar_ix_infl_df = pd.DataFrame({
        "Expense Head": indirect_heads,
        "Year 2 (%)": _ix_inf, "Year 3 (%)": _ix_inf, "Year 4 (%)": _ix_inf, "Year 5 (%)": _ix_inf
    })
# -----------------------------------------------------------------------------
# CHAPTER 2: SIDEBAR CONTROL PANEL DESK
# -----------------------------------------------------------------------------
# NOTE: the radio below is switched automatically when the user clicks a top tab
# (small script at the very end of this file - see CHAPTER 7).

# ---- Cockpit width: the arrow button spreads the cockpit (feed tables fill the screen, no scrolling) or squeezes it back ----
if "cockpit_wide" not in st.session_state:
    st.session_state.cockpit_wide = False
def _toggle_cockpit():
    st.session_state.cockpit_wide = not st.session_state.cockpit_wide
if st.session_state.cockpit_wide:
    st.markdown("""
    <style>
    section[data-testid="stSidebar"]:not([aria-expanded="false"]) { width: min(78vw, 1150px) !important; min-width: min(78vw, 1150px) !important; max-width: min(78vw, 1150px) !important; }
    section[data-testid="stSidebar"]:not([aria-expanded="false"]) > div { width: 100% !important; }
    section[data-testid="stSidebar"] div[data-testid="stNumberInput"] { max-width: 260px !important; }
    section[data-testid="stSidebar"] div[data-testid="stButton"] { justify-content: flex-start !important; }
    </style>""", unsafe_allow_html=True)

def _col_px(df, c):
    """Column width in pixels from the longest text in the column (header or cell)."""
    head = len(str(c)) * 7.2 + 44                       # header text + sort / menu icons
    cells = max([len(str(v)) for v in df[c].tolist()] + [1]) * 8 + 24
    return int(min(max(head, cells, 64), 300))

def sb_editor(df, **kw):
    """Cockpit feed table. Every key-in column gets a red marker in its heading (fixed columns have none).
    Spread cockpit: each column is also sized to its data, so the box stays compact."""
    wide = st.session_state.cockpit_wide
    try:
        cfg = dict(kw.get("column_config") or {})
        total = 0
        for c in df.columns:
            base = dict(cfg[c]) if c in cfg else dict(st.column_config.Column(label=str(c)))
            keyin = not base.get("disabled")
            if keyin:
                base["label"] = "🔴 " + str(c)
            if wide:
                px = _col_px(df, c) + (26 if keyin else 0)
                base["width"] = px
                total += px
            cfg[c] = base
        kw2 = dict(kw, column_config=cfg)
        if wide:
            try:
                return st.data_editor(df, width=total + 12, **kw2)
            except TypeError:
                pass
        return st.data_editor(df, **kw2)
    except Exception:
        return st.data_editor(df, **kw)

def feed_title(text):
    """Heading shown above every feed box so the user knows what to key in."""
    st.markdown(f'<div class="feed-title">▸ {text}</div>', unsafe_allow_html=True)

with st.sidebar:
    # top line: Spread (top-right) when squeezed, Squeeze (top-left) when spread; heading sits below it
    st.button("❮  Squeeze" if st.session_state.cockpit_wide else "Spread  ❯", on_click=_toggle_cockpit,
              help="Click to squeeze the cockpit back" if st.session_state.cockpit_wide else "Click to spread the cockpit so the feed tables are fully visible")
    st.header("⚙️ Cockpit Feed")
    st.caption("🔴 = key-in column  |  heading without 🔴 = fixed, not editable")
    sidebar_context = st.radio(
        "Cockpit Feed",
        options=["Sales / FG Feed", "RM Qt Feed", "RM Val Feed", "Direct Expenses Feed", "Indirect Expenses Feed", "WC Feed"],
        key="synchronized_sidebar_context_radio_widget",
        label_visibility="collapsed"
    )
    st.markdown("---")

    # Direct Expenses feed tables (edited only inside the Direct Expenses Feed desk below)
    edited_dx_rate_df = st.session_state.sidebar_dx_rate_df
    edited_dx_common_df = st.session_state.sidebar_dx_common_df
    edited_dx_infl_df = st.session_state.sidebar_dx_infl_df
    # Indirect Expenses feed tables (edited only inside the Indirect Expenses Feed desk below)
    edited_ix_df = st.session_state.sidebar_ix_df
    edited_ix_infl_df = st.session_state.sidebar_ix_infl_df
    # Debtors / creditors feeds (edited only inside the Sales / FG Feed and RM Val Feed desks below)
    edited_debtor_df = st.session_state.sidebar_debtor_params_df
    gst_sales_pct = st.session_state.gst_sales_saved
    rm_credit_days = st.session_state.rm_credit_days_saved
    gst_pur_pct = st.session_state.gst_pur_saved
    edited_op_cred_df = st.session_state.sidebar_op_cred_df
    adv_pct = st.session_state.adv_pct_saved
    # WC feeds (edited only inside the WC Feed desk below)
    wc_cash_open, wc_roi = st.session_state.wc_cash_saved, st.session_state.wc_roi_saved
    wc_od_open, wc_margin = st.session_state.wc_od_saved, st.session_state.wc_margin_saved
    edited_wc_flow_df, edited_wc_bal_df = st.session_state.sidebar_wc_flow_df, st.session_state.sidebar_wc_bal_df

    if sidebar_context == "Sales / FG Feed":
        st.header("📊 1. Sales & FG Feed Desk")
        g2_pct = st.number_input("Year 2 Volume Growth (%)", value=st.session_state.growth_saved[0])
        g_y2 = g2_pct / 100.0
        g3_pct = st.number_input("Year 3 Volume Growth (%)", value=st.session_state.growth_saved[1])
        g_y3 = g3_pct / 100.0
        g4_pct = st.number_input("Year 4 Volume Growth (%)", value=st.session_state.growth_saved[2])
        g_y4 = g4_pct / 100.0
        g5_pct = st.number_input("Year 5 Volume Growth (%)", value=st.session_state.growth_saved[3])
        g_y5 = g5_pct / 100.0
        feed_title("Monthly Sales Qt (Kg) - M1 to M12, by Product")
        edited_qty_df = sb_editor(st.session_state.sidebar_qty_df, hide_index=True, column_config={"Timeline": st.column_config.TextColumn(disabled=True)})
        st.session_state.growth_saved = [g2_pct, g3_pct, g4_pct, g5_pct]
        st.session_state.sidebar_qty_df = edited_qty_df
        feed_title("FG Selling Rate (Rs/Kg) - M1 to M12 and Year 2-5 base rate, by Product")
        edited_rate_df = sb_editor(st.session_state.sidebar_rate_df, hide_index=True, column_config={"Timeline": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_rate_df = edited_rate_df
        feed_title("FG Price Inflation (% YoY) - Year 2 to Year 5, by Product")
        edited_fg_inflation_df = sb_editor(st.session_state.sidebar_fg_inflation_df, hide_index=True, column_config={"Timeline": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_fg_inflation_df = edited_fg_inflation_df
        feed_title("FG Warehouse - M1 Opening Stock Qt and Closing Stock Hold Days, by Product")
        edited_prod_params_df = sb_editor(st.session_state.sidebar_prod_params_df, hide_index=True, column_config={"Parameters": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_prod_params_df = edited_prod_params_df
        gst_sales_pct = st.number_input("GST Rate on Sales (%)", value=st.session_state.gst_sales_saved)
        st.session_state.gst_sales_saved = gst_sales_pct
        feed_title("Debtors - Days Credit and M1 Opening Debtors (Rs Lacs), by Product")
        edited_debtor_df = sb_editor(st.session_state.sidebar_debtor_params_df, hide_index=True, column_config={"Parameters": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_debtor_params_df = edited_debtor_df
        edited_bom_df, edited_rm_logistics_df, edited_rm_price_df, edited_rm_inflation_df = st.session_state.sidebar_bom_df, st.session_state.sidebar_rm_logistics_df, st.session_state.sidebar_rm_price_df, st.session_state.sidebar_rm_inflation_df
    elif sidebar_context == "RM Qt Feed":
        st.header("🧱 2. RM Qt Feed Desk")
        feed_title("BOM - RM Consumption % per FG, Visible Loss and Invisible Loss")
        edited_bom_df = sb_editor(st.session_state.sidebar_bom_df, hide_index=True, column_config={"RM Name": st.column_config.TextColumn(disabled=True), "Target FG": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_bom_df = edited_bom_df
        feed_title("RM Stock - M1 Opening Stock Qt and Days Hold, by Raw Material")
        edited_rm_logistics_df = sb_editor(st.session_state.sidebar_rm_logistics_df, hide_index=True, column_config={"Raw Material": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_rm_logistics_df = edited_rm_logistics_df
        edited_qty_df, edited_rate_df, edited_fg_inflation_df, edited_prod_params_df, edited_rm_price_df, edited_rm_inflation_df = st.session_state.sidebar_qty_df, st.session_state.sidebar_rate_df, st.session_state.sidebar_fg_inflation_df, st.session_state.sidebar_prod_params_df, st.session_state.sidebar_rm_price_df, st.session_state.sidebar_rm_inflation_df
        g_y2, g_y3, g_y4, g_y5 = [x / 100.0 for x in st.session_state.growth_saved]
    elif sidebar_context == "RM Val Feed":
        st.header("💰 3. RM Val Feed Desk")
        feed_title("RM Initial Purchase Price (Rs/Kg), by Raw Material")
        edited_rm_price_df = sb_editor(st.session_state.sidebar_rm_price_df, hide_index=True, column_config={"Raw Material": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_rm_price_df = edited_rm_price_df
        feed_title("RM Price Inflation (% YoY) - Year 2 to Year 5")
        edited_rm_inflation_df = sb_editor(st.session_state.sidebar_rm_inflation_df, hide_index=True, column_config={"Timeline": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_rm_inflation_df = edited_rm_inflation_df
        rm_credit_days = st.number_input("RM Credit Period (Days) - on Net Due, all Raw Materials", value=st.session_state.rm_credit_days_saved)
        st.session_state.rm_credit_days_saved = rm_credit_days
        gst_pur_pct = st.number_input("GST Rate on RM Purchases (%)", value=st.session_state.gst_pur_saved)
        st.session_state.gst_pur_saved = gst_pur_pct
        adv_pct = st.number_input("Advance Payment on RM Orders (%) - paid at order, on Gross Due", value=st.session_state.adv_pct_saved)
        st.session_state.adv_pct_saved = adv_pct
        feed_title("Creditors - M1 Opening Creditors (Rs Lacs), by Raw Material")
        edited_op_cred_df = sb_editor(st.session_state.sidebar_op_cred_df, hide_index=True, column_config={"Raw Material": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_op_cred_df = edited_op_cred_df
        edited_qty_df, edited_rate_df, edited_fg_inflation_df, edited_prod_params_df, edited_bom_df, edited_rm_logistics_df = st.session_state.sidebar_qty_df, st.session_state.sidebar_rate_df, st.session_state.sidebar_fg_inflation_df, st.session_state.sidebar_prod_params_df, st.session_state.sidebar_bom_df, st.session_state.sidebar_rm_logistics_df
        g_y2, g_y3, g_y4, g_y5 = [x / 100.0 for x in st.session_state.growth_saved]
    elif sidebar_context == "Direct Expenses Feed":
        st.header("🏭 4. Direct Expenses Feed Desk")
        st.caption("Rate per unit of production (Rs) - applied to Production Qt")
        edited_dx_rate_df = sb_editor(st.session_state.sidebar_dx_rate_df, hide_index=True, column_config={"Expense Head": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_dx_rate_df = edited_dx_rate_df
        feed_title("Common Rate p.u. (Rs) - same rate for all products")
        edited_dx_common_df = sb_editor(st.session_state.sidebar_dx_common_df, hide_index=True, column_config={"Expense Head": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_dx_common_df = edited_dx_common_df
        st.caption("YoY inflation (%) on rate p.u. - Year 2 to Year 5")
        edited_dx_infl_df = sb_editor(st.session_state.sidebar_dx_infl_df, hide_index=True, column_config={"Expense Head": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_dx_infl_df = edited_dx_infl_df
        edited_qty_df, edited_rate_df, edited_fg_inflation_df, edited_prod_params_df, edited_bom_df, edited_rm_logistics_df, edited_rm_price_df, edited_rm_inflation_df = st.session_state.sidebar_qty_df, st.session_state.sidebar_rate_df, st.session_state.sidebar_fg_inflation_df, st.session_state.sidebar_prod_params_df, st.session_state.sidebar_bom_df, st.session_state.sidebar_rm_logistics_df, st.session_state.sidebar_rm_price_df, st.session_state.sidebar_rm_inflation_df
        g_y2, g_y3, g_y4, g_y5 = [x / 100.0 for x in st.session_state.growth_saved]
    elif sidebar_context == "Indirect Expenses Feed":
        st.header("🏢 5. Indirect Expenses Feed Desk")
        st.caption("Initial rate - Rs per Kg sold (p.u.) or % of Sale Value, as per 'Against Sale'. Same rate for P1, P2, P3")
        edited_ix_df = sb_editor(st.session_state.sidebar_ix_df, hide_index=True, column_config={"Expense Head": st.column_config.TextColumn(disabled=True), "Against Sale": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_ix_df = edited_ix_df
        st.caption("YoY inflation (%) on rate / % - Year 2 to Year 5")
        edited_ix_infl_df = sb_editor(st.session_state.sidebar_ix_infl_df, hide_index=True, column_config={"Expense Head": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_ix_infl_df = edited_ix_infl_df
        edited_qty_df, edited_rate_df, edited_fg_inflation_df, edited_prod_params_df, edited_bom_df, edited_rm_logistics_df, edited_rm_price_df, edited_rm_inflation_df = st.session_state.sidebar_qty_df, st.session_state.sidebar_rate_df, st.session_state.sidebar_fg_inflation_df, st.session_state.sidebar_prod_params_df, st.session_state.sidebar_bom_df, st.session_state.sidebar_rm_logistics_df, st.session_state.sidebar_rm_price_df, st.session_state.sidebar_rm_inflation_df
        g_y2, g_y3, g_y4, g_y5 = [x / 100.0 for x in st.session_state.growth_saved]
    else:
        st.header("🏦 6. WC Feed Desk")
        wc_cash_open = st.number_input("Opening Bank / Cash Balance (Rs Lacs)", value=st.session_state.wc_cash_saved)
        st.session_state.wc_cash_saved = wc_cash_open
        wc_roi = st.number_input("Rate of Interest on Working Capital (% p.a.)", value=st.session_state.wc_roi_saved)
        st.session_state.wc_roi_saved = wc_roi
        wc_od_open = st.number_input("Opening Bank OD / CC Balance (Rs Lacs)", value=st.session_state.wc_od_saved)
        st.session_state.wc_od_saved = wc_od_open
        wc_margin = st.number_input("Margin on Working Capital Gap (%)", value=st.session_state.wc_margin_saved)
        st.session_state.wc_margin_saved = wc_margin
        feed_title("WC Cash Outflow Items (Rs Lacs) - M1 to M12 and Year 2-5 (other items are picked up from the other pages)")
        edited_wc_flow_df = sb_editor(st.session_state.sidebar_wc_flow_df, hide_index=True, column_config={"Timeline": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_wc_flow_df = edited_wc_flow_df
        feed_title("WC Other Balances (Rs Lacs) - closing balance, M1 to M12 and Year 2-5")
        edited_wc_bal_df = sb_editor(st.session_state.sidebar_wc_bal_df, hide_index=True, column_config={"Timeline": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_wc_bal_df = edited_wc_bal_df
        edited_qty_df, edited_rate_df, edited_fg_inflation_df, edited_prod_params_df, edited_bom_df, edited_rm_logistics_df, edited_rm_price_df, edited_rm_inflation_df = st.session_state.sidebar_qty_df, st.session_state.sidebar_rate_df, st.session_state.sidebar_fg_inflation_df, st.session_state.sidebar_prod_params_df, st.session_state.sidebar_bom_df, st.session_state.sidebar_rm_logistics_df, st.session_state.sidebar_rm_price_df, st.session_state.sidebar_rm_inflation_df
        g_y2, g_y3, g_y4, g_y5 = [x / 100.0 for x in st.session_state.growth_saved]
# -----------------------------------------------------------------------------
# CHAPTER 3: ANALYTICAL COMPUTATION LAYER
# -----------------------------------------------------------------------------
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
    p_op, p_cl, p_prod = [0.0] * 17, [0.0] * 17, [0.0] * 17
    for idx in range(12): p_cl[idx] = (hold_days / 30.0) * p_sales[idx]
    
    # Secure arrays from assignment type breaks
    p_op_list = [0.0] * 17
    p_op_list[0] = m1_op_input
    for idx in range(1, 12): p_op_list[idx] = p_cl[idx - 1]
    for idx in range(12): p_prod[idx] = p_sales[idx] + p_cl[idx] - p_op_list[idx]
    p_op_list[12], p_cl[12], p_prod[12] = p_op_list[0], p_cl[11], sum(p_prod[0:12])
    
    horizon_map, prev_map = {"Year 2": 13, "Year 3": 14, "Year 4": 15, "Year 5": 16}, {"Year 2": 12, "Year 3": 13, "Year 4": 14, "Year 5": 15}
    for yr, idx in horizon_map.items():
        p_op_list[idx] = p_cl[prev_map[yr]]
        p_cl[idx] = (hold_days / 30.0) * (p_sales[idx] / 12.0)
        p_prod[idx] = p_sales[idx] + p_cl[idx] - p_op_list[idx]
    prod_sales_matrix[p], fg_cl_matrix[p], fg_op_matrix[p], fg_prod_matrix[p] = p_sales, p_cl, p_op_list, p_prod

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
# -----------------------------------------------------------------------------
# CHAPTER 3B (NEW): PRODUCT-WISE RM SPLIT (for slicers / product COGS) + DIRECT EXPENSES
# -----------------------------------------------------------------------------
# Product-wise RM consumption & loss, same BOM formula as above (existing matrices untouched)
rm_cons_p = {p: {rm: [0.0] * 17 for rm in raw_materials} for p in products}
rm_loss_p = {p: {rm: [0.0] * 17 for rm in raw_materials} for p in products}
for idx in valid_time_indices:
    for _, row in edited_bom_df.iterrows():
        rm, p, c_pct, v_loss, i_loss = row["RM Name"], row["Target FG"], safe_float(row["Con%"]), safe_float(row["Visible Loss"]), safe_float(row["Invisible Loss"])
        denom = (1.0 - v_loss - i_loss)
        if denom > 0:
            gross_c = (fg_prod_matrix[p][idx] * c_pct) / denom
            rm_cons_p[p][rm][idx] += gross_c
            rm_loss_p[p][rm][idx] += gross_c * (v_loss + i_loss)
for p in products:
    for rm in raw_materials:
        rm_cons_p[p][rm][12] = sum(rm_cons_p[p][rm][0:12])
        rm_loss_p[p][rm][12] = sum(rm_loss_p[p][rm][0:12])

# RMs used by each product (RM1 is shared, so stock / purchase are split by consumption share)
used_rms = {p: [rm for rm in raw_materials if any(v > 0 for v in rm_cons_p[p][rm])] for p in products}

def alloc_by_share(total_matrix, p, kind):
    out = {}
    for rm in raw_materials:
        tot, mine = rm_gross_cons_matrix[rm], rm_cons_p[p][rm]
        s = [((total_matrix[rm][i] * mine[i] / tot[i]) if tot[i] > 0 else 0.0) for i in range(17)]
        if kind == "sum":   s[12] = sum(s[0:12])      # Year 1 purchase = sum of months
        elif kind == "op":  s[12] = s[0]              # Year 1 opening = M1 opening
        elif kind == "cl":  s[12] = s[11]             # Year 1 closing = M12 closing
        out[rm] = s
    return out

rm_purch_p = {p: alloc_by_share(rm_purch_matrix, p, "sum") for p in products}
rm_op_p = {p: alloc_by_share(rm_op_matrix, p, "op") for p in products}
rm_cl_p = {p: alloc_by_share(rm_cl_matrix, p, "cl") for p in products}

def to_val(by_p):
    return {p: {rm: [by_p[p][rm][i] * rm_price_horizon[rm][i] / 100000.0 for i in range(17)] for rm in raw_materials} for p in products}
rm_cons_val_p, rm_purch_val_p, rm_op_val_p, rm_cl_val_p = to_val(rm_cons_p), to_val(rm_purch_p), to_val(rm_op_p), to_val(rm_cl_p)
rm_cons_val_p_total = {p: [sum(rm_cons_val_p[p][rm][i] for rm in raw_materials) for i in range(17)] for p in products}

# ---- Direct Expenses (Rs in Lacs): Production Qt x Rate p.u.; Y2-Y5 rate compounds yearly inflation ----
dx_cost = {h: {} for h in direct_heads}
for h in direct_heads:
    infl = [safe_float(edited_dx_infl_df.loc[edited_dx_infl_df["Expense Head"] == h, f"Year {y} (%)"].values) / 100.0 for y in (2, 3, 4, 5)]
    for p in products:
        if h in dx_common_heads:
            base = safe_float(edited_dx_common_df.loc[edited_dx_common_df["Expense Head"] == h, "Rate p.u. (all products)"].values)
        else:
            base = safe_float(edited_dx_rate_df.loc[edited_dx_rate_df["Expense Head"] == h, p].values)
        yr_rates, running = [], base
        for k in range(4):
            running = running * (1.0 + infl[k])
            yr_rates.append(running)
        cost = [0.0] * 17
        for idx in range(12): cost[idx] = fg_prod_matrix[p][idx] * base / 100000.0
        cost[12] = sum(cost[0:12])
        for k, idx in enumerate(range(13, 17)): cost[idx] = fg_prod_matrix[p][idx] * yr_rates[k] / 100000.0
        dx_cost[h][p] = cost
dx_total_cost = {p: [sum(dx_cost[h][p][i] for h in direct_heads) for i in range(17)] for p in products}

# -----------------------------------------------------------------------------
# CHAPTER 4: COMPILING TABULAR STRUCTURES WITH TOTALS
# -----------------------------------------------------------------------------
def compile_report(matrix_dict, main_key="Product"):
    df = pd.DataFrame(matrix_dict, index=display_columns).T
    df.insert(0, main_key, df.index)
    t_row = {main_key: "Total"}
    for col in display_columns: t_row[col] = df[col].sum()
    return pd.concat([df, pd.DataFrame([t_row])], ignore_index=True)

df_rev_final = compile_report(rev_matrix, "Product")
df_rev_final.iloc[0:, 1:] = df_rev_final.iloc[0:, 1:] / 100000.0
df_qty_final = compile_report(qty_matrix, "Product")

all_prod_dfs = []
for p in products:
    p_flow_df = pd.DataFrame({"Product": [p, "", "", ""], "FG Inventory Metrics": ["1. Opening Stock", "2. Sales Qty", "3. Production Qty", "4. Closing Stock"]})
    for idx, col in enumerate(display_columns): p_flow_df[col] = [fg_op_matrix[p][idx], prod_sales_matrix[p][idx], fg_prod_matrix[p][idx], fg_cl_matrix[p][idx]]
    all_prod_dfs.append(p_flow_df)
master_prod_flow_df = pd.concat(all_prod_dfs, ignore_index=True)

df_summary_prod = compile_report(fg_prod_matrix, "Product")
df_summary_op = compile_report(fg_op_matrix, "Product")
df_summary_cl = compile_report(fg_cl_matrix, "Product")

all_rm_flow_rows = []
for rm in raw_materials:
    rm_block = pd.DataFrame({"Raw Material": [rm, "", "", ""], "RM Flow(Qt) Metrics": ["Op stk", "Generated / Purchased", "Consumption", "Cl stk"]})
    for idx, col in enumerate(display_columns): rm_block[col] = [rm_op_matrix[rm][idx], rm_purch_matrix[rm][idx], rm_gross_cons_matrix[rm][idx], rm_cl_matrix[rm][idx]]
    all_rm_flow_rows.append(rm_block)
master_rm_flow_df = pd.concat(all_rm_flow_rows, ignore_index=True)

df_rm_consumption_final = compile_report(rm_gross_cons_matrix, "Raw Material")
df_rm_purchase_final = compile_report(rm_purch_matrix, "Raw Material")
df_rm_loss_final = compile_report(rm_total_loss_matrix, "Raw Material")

df_scrap_final = pd.DataFrame(fg_scrap_matrix, index=display_columns).T
df_scrap_final.insert(0, "Scrap (Qt)", ["Scrap P1 (SP1)", "Scrap P2 (SP2)", "Scrap P3 (SP3)"])
t_scrap_row = {"Scrap (Qt)": "Total"}
for col in display_columns: t_scrap_row[col] = df_scrap_final[col].sum()
df_scrap_final = pd.concat([df_scrap_final, pd.DataFrame([t_scrap_row])], ignore_index=True)

df_rm_purchase_val_final = compile_report(rm_purch_val_matrix, "Raw Material")
df_rm_consumption_val_final = compile_report(rm_cons_val_matrix, "Raw Material")
df_rm_loss_val_final = compile_report(rm_total_loss_matrix, "Raw Material")
df_rm_op_val_final = compile_report(rm_op_val_matrix, "Raw Material")
df_rm_cl_val_final = compile_report(rm_cl_val_matrix, "Raw Material")

all_rm_val_flow_rows = []
for rm in raw_materials:
    rm_v_block = pd.DataFrame({"Raw Material": [rm, "", "", ""], "RM Flow(Rs) Metrics": ["Op stk", "Generated / Purchased", "Consumption", "Cl stk"]})
    for idx, col in enumerate(display_columns): rm_v_block[col] = [rm_op_val_matrix[rm][idx], rm_purch_val_matrix[rm][idx], rm_cons_val_matrix[rm][idx], rm_cl_val_matrix[rm][idx]]
    all_rm_val_flow_rows.append(rm_v_block)
master_rm_val_flow_df = pd.concat(all_rm_val_flow_rows, ignore_index=True)

# ---- Indirect Expenses (Stage 7): rate p.u. x Sale Qt  OR  % x Sale Value; Y2-Y5 rate/% compounds yearly inflation ----
# (placed here, ahead of the P&L compiler, because the P&L needs it)
rev_lacs_p = {p: [v / 100000.0 for v in rev_matrix[p]] for p in products}
ix_cost, ix_rate = {h: {} for h in indirect_heads}, {}
for h in indirect_heads:
    ix_row = edited_ix_df.loc[edited_ix_df["Expense Head"] == h]
    base = safe_float(ix_row[IX_RATE_COL].values)
    infl = [safe_float(edited_ix_infl_df.loc[edited_ix_infl_df["Expense Head"] == h, f"Year {y} (%)"].values) / 100.0 for y in (2, 3, 4, 5)]
    yr_rates, running = [], base
    for k in range(4):
        running = running * (1.0 + infl[k])
        yr_rates.append(running)
    rate_series = [base] * 13 + yr_rates                      # M1-M12, Year 1, Year 2-5
    ix_rate[h] = rate_series
    for p in products:
        cost = [0.0] * 17
        for idx in range(12):
            cost[idx] = (qty_matrix[p][idx] * base / 100000.0) if ix_type[h] == "p.u" else (rev_lacs_p[p][idx] * base / 100.0)
        cost[12] = sum(cost[0:12])
        for k, idx in enumerate(range(13, 17)):
            cost[idx] = (qty_matrix[p][idx] * yr_rates[k] / 100000.0) if ix_type[h] == "p.u" else (rev_lacs_p[p][idx] * yr_rates[k] / 100.0)
        ix_cost[h][p] = cost
ix_total_cost = {p: [sum(ix_cost[h][p][i] for h in indirect_heads) for i in range(17)] for p in products}

# ---- Step 8 (NEW): COGS per unit for the Costing page (Rs per Kg) ----
# RM consumption + Direct heads : cost / Production Qt.   Indirect heads : cost / Sale Qt.
# Travelling Expenses and Carriage Outward are NOT part of this costing (not yet incurred, so not part of FG valuation).
cost_ix_heads = [h for h in indirect_heads if h not in ("Travelling Expenses", "Carriage Outward")]
def _cost_pu(cost, qty):      # Rs lacs / Qt -> Rs per Kg ; Year columns = annual cost / annual Qt (weighted), not a sum of months
    return [(c * 100000.0 / q if q > 0 else 0.0) for c, q in zip(cost, qty)]
cost_pu = {}
for p in products:
    _d = {"rm": _cost_pu(rm_cons_val_p_total[p], fg_prod_matrix[p])}
    _d["dx"] = {h: _cost_pu(dx_cost[h][p], fg_prod_matrix[p]) for h in direct_heads}
    _d["ix"] = {h: _cost_pu(ix_cost[h][p], qty_matrix[p]) for h in cost_ix_heads}
    _d["dx_tot"] = [sum(_d["dx"][h][i] for h in direct_heads) for i in range(17)]
    _d["ix_tot"] = [sum(_d["ix"][h][i] for h in cost_ix_heads) for i in range(17)]
    _d["cogs"] = [_d["rm"][i] + _d["dx_tot"][i] + _d["ix_tot"][i] for i in range(17)]
    cost_pu[p] = _d
cogs_pu = {p: cost_pu[p]["cogs"] for p in products}

def build_costing_df(p):
    """One 'COGS Per Unit : P1' table in the Attachment 1 layout (blank spacer rows included)."""
    d, rows = cost_pu[p], []
    ind = "\u00a0\u00a0\u00a0"
    def add(sl, label, series=None):
        r = {"Sl No": sl, f"COGS Per Unit : {p}": label}
        for i, c in enumerate(display_columns): r[c] = series[i] if series is not None else float("nan")
        rows.append(r)
    add("1", "RM consumption", d["rm"]);                add("", "")
    add("2", "Direct Expenses :", d["dx_tot"])
    for h in direct_heads: add("", ind + h, d["dx"][h])
    add("", "")
    add("3", "Indirect Expenses :", d["ix_tot"])
    for h in cost_ix_heads: add("", ind + h, d["ix"][h])
    add("", "")
    add("4", "COGS (1+2+3)", d["cogs"])
    return pd.DataFrame(rows)

# ---- Step 9 (NEW): FG stock valuation (Rs in Lacs) = Qt x COGS per unit (Step 8 figures) ----
# Closing = closing Qt x that period's COGS/unit (Year 1 closing = M12 closing).
# Opening : M1 = M1 opening Qt x M1 COGS/unit ; M2 onward = previous month's closing value ; Year 1 = M1 opening ; Year 2-5 = previous year's closing.
fg_cl_val, fg_op_val, fg_adj, fg_op_rate, fg_cl_rate = {}, {}, {}, {}, {}
for p in products:
    cl, op = [0.0] * 17, [0.0] * 17
    for i in list(range(12)) + [13, 14, 15, 16]: cl[i] = fg_cl_matrix[p][i] * cogs_pu[p][i] / 100000.0
    cl[12] = cl[11]
    op[0] = fg_op_matrix[p][0] * cogs_pu[p][0] / 100000.0
    for i in range(1, 12): op[i] = cl[i - 1]
    op[12] = op[0]
    for i in (13, 14, 15, 16): op[i] = cl[i - 1]
    fg_cl_val[p], fg_op_val[p] = cl, op
    fg_adj[p] = [op[i] - cl[i] for i in range(17)]                       # FG : Decrease / (Increase) = Opening - Closing
    fg_op_rate[p] = [(op[i] * 100000.0 / fg_op_matrix[p][i] if fg_op_matrix[p][i] > 0 else 0.0) for i in range(17)]
    fg_cl_rate[p] = [(cl[i] * 100000.0 / fg_cl_matrix[p][i] if fg_cl_matrix[p][i] > 0 else 0.0) for i in range(17)]
df_fg_cl_val_final = compile_report(fg_cl_val, "Product")
df_fg_op_val_final = compile_report(fg_op_val, "Product")

# ---- NEW: DEBTORS (Revenue page) and CREDITORS (RM Val page) : same credit-days logic ----
def credit_schedule(due, days, opening):
    """due = 17 values (M1-M12, Year 1-5) in Rs lacs. Returns opening, closing and cash flow (inflow for debtors / outflow for creditors).
    Closing at month t = due of the latest months that the credit days still cover: each full 30 days counts the whole month, the
    last part counts proportionately (e.g. 70 days = this month + last month + 10/30 of the month before). Months before M1 do not exist (nil).
    Only M1 closing also carries the unpaid part of the opening balance, capped at 50% of it, so at least 50% of the opening balance is
    settled in M1 and no cash flow can turn negative. Year 1 closing = M12 closing ; Year 2-5 closing = annual due / 360 x days."""
    D = max(days, 0.0)
    cl = [0.0] * 17
    for t in range(12):
        s = 0.0
        for j in range(t + 1):
            w = min(1.0, max(0.0, D / 30.0 - j))
            if w <= 0: break
            s += w * due[t - j]
        cl[t] = s
    if D > 0: cl[0] += opening * min(0.5, max(0.0, 1.0 - 30.0 / D))
    cl[12] = cl[11]
    for i in range(13, 17): cl[i] = due[i] / 360.0 * D
    op = [0.0] * 17
    op[0] = opening
    for t in range(1, 12): op[t] = cl[t - 1]
    op[12] = op[0]
    for i in range(13, 17): op[i] = cl[i - 1]
    flow = [op[i] + due[i] - cl[i] for i in range(17)]
    return {"op": op, "cl": cl, "flow": flow}

def build_block_df(blocks, keys, metric_hdr="Metrics"):
    """Block layout of the Due / Debtors / Creditors tables: a total row (Sl No + label) with one Level 2 row per product / RM beneath it."""
    rows = []
    for sl, label, by_key in blocks:
        r = {"Sl No": sl, metric_hdr: label, "Level 2": ""}
        for i, c in enumerate(display_columns): r[c] = sum(by_key[k][i] for k in keys)
        rows.append(r)
        for k in keys:
            r = {"Sl No": "", metric_hdr: "", "Level 2": k}
            for i, c in enumerate(display_columns): r[c] = by_key[k][i]
            rows.append(r)
    return pd.DataFrame(rows)

def show_block_df(df):
    sty = (df.style.format({c: "{:,.2f} L" for c in display_columns}, na_rep="")
           .apply(lambda r: ["font-weight: bold" if r["Sl No"] != "" else ""] * len(r), axis=1))
    st.dataframe(sty, use_container_width=True, hide_index=True, height=min(35 * (len(df) + 1) + 3, 1300))

# Debtors : by product
dbt_gst = {p: [v * safe_float(gst_sales_pct) / 100.0 for v in rev_lacs_p[p]] for p in products}
dbt_due = {p: [a + b for a, b in zip(rev_lacs_p[p], dbt_gst[p])] for p in products}
dbt_days = {p: safe_float(edited_debtor_df.loc[edited_debtor_df["Parameters"] == "Days Credit", p].values) for p in products}
dbt_open = {p: safe_float(edited_debtor_df.loc[edited_debtor_df["Parameters"] == "Opening Debtors (Rs Lacs)", p].values) for p in products}
dbt = {p: credit_schedule(dbt_due[p], dbt_days[p], dbt_open[p]) for p in products}

# Creditors : by raw material (one common credit period)
crd_gst = {rm: [v * safe_float(gst_pur_pct) / 100.0 for v in rm_purch_val_matrix[rm]] for rm in raw_materials}
crd_gross = {rm: [a + b for a, b in zip(rm_purch_val_matrix[rm], crd_gst[rm])] for rm in raw_materials}       # Gross Due = Purchase + GST
_adv_frac = min(max(safe_float(adv_pct), 0.0), 100.0) / 100.0
crd_adv = {rm: [v * _adv_frac for v in crd_gross[rm]] for rm in raw_materials}                               # Advance paid at order = Adv % x Gross Due
crd_due = {rm: [g - a for g, a in zip(crd_gross[rm], crd_adv[rm])] for rm in raw_materials}                  # Net Due to Suppliers = Gross Due - Advance (credit days apply on this)
crd_open = {rm: safe_float(edited_op_cred_df.loc[edited_op_cred_df["Raw Material"] == rm, "Opening Creditors (Rs Lacs)"].values) for rm in raw_materials}
crd = {rm: credit_schedule(crd_due[rm], safe_float(rm_credit_days), crd_open[rm]) for rm in raw_materials}
# Cash outflow has 2 types: (a) advance on the current purchase, (b) payment against creditors (Opening + Net Due - Closing)
crd_out_total = {rm: [a + b for a, b in zip(crd_adv[rm], crd[rm]["flow"])] for rm in raw_materials}

def debtor_due_df(prods):
    return build_block_df([("1", "Sale", rev_lacs_p), ("2", "GST", dbt_gst), ("3", "Due", dbt_due)], prods)
def debtor_flow_df(prods):
    return build_block_df([("1", "Opening Debtors", {p: dbt[p]["op"] for p in products}), ("2", "Add : Due Value", dbt_due),
                           ("3", "Less : Closing Debtors", {p: dbt[p]["cl"] for p in products}),
                           ("4", "Cash Inflow", {p: dbt[p]["flow"] for p in products})], prods)
def creditor_due_df():
    return build_block_df([("1", "Purchase", rm_purch_val_matrix), ("2", "GST", crd_gst), ("3", "Gross Due (1+2)", crd_gross),
                           ("4", "Less : Advance on Current Purchase", crd_adv), ("5", "Net Due to Suppliers (3-4)", crd_due)], raw_materials)
def creditor_flow_df():
    return build_block_df([("1", "Opening Creditors", {r: crd[r]["op"] for r in raw_materials}), ("2", "Add : Net Due to Suppliers", crd_due),
                           ("3", "Less : Closing Creditors", {r: crd[r]["cl"] for r in raw_materials}),
                           ("4", "Cash Outflow (a) : Advance on Current Purchase", crd_adv),
                           ("5", "Cash Outflow (b) : Payment against Creditors (1+2-3)", {r: crd[r]["flow"] for r in raw_materials}),
                           ("6", "Total Cash Outflow (a+b)", crd_out_total)], raw_materials)

# ---- NEW: WORKING CAPITAL (WC page) : requirement, drawing power, borrowing and interest (Rs lacs) ----
def _feed_series(df, col, kind):
    """17 values (M1-M12, Year 1, Year 2-5) from a WC feed table keyed by Timeline. flow : Year 1 = sum of months ; bal : Year 1 = M12 value."""
    v = [safe_float(df.loc[df["Timeline"] == t, col].values) for t in months + future_years]
    return v[0:12] + [sum(v[0:12]) if kind == "flow" else v[11]] + v[12:16]

_I = range(17)
# Table 1 - Working Capital Requirement (cash outflow - cash inflow - cash & bank balance)
wc_adv    = [sum(crd_adv[rm][i] for rm in raw_materials) for i in _I]                              # (a) advance to suppliers on current purchase
wc_pay    = [sum(crd[rm]["flow"][i] for rm in raw_materials) for i in _I]                          # (b) payment against creditors
wc_power  = [sum(dx_cost["Power & Fuel"][p][i] for p in products) for i in _I]
wc_labour = [sum(dx_cost["Direct Wages"][p][i] for p in products) for i in _I]
wc_othmfg = [sum(dx_cost[h][p][i] for h in ("Repair & Maintenance", "Carriage inward", "Other Direct OH") for p in products) for i in _I]
wc_selladm = [sum(ix_total_cost[p][i] for p in products) for i in _I]
wc_tlint  = _feed_series(edited_wc_flow_df, "TL Interest & Bank Charges", "flow")
wc_fd     = _feed_series(edited_wc_flow_df, "FD Increment", "flow")
wc_tax    = _feed_series(edited_wc_flow_df, "Tax Payment Provision", "flow")
wc_cont   = _feed_series(edited_wc_flow_df, "Other Contingency Requirement", "flow")
wc_out_items = [wc_adv, wc_pay, wc_power, wc_labour, wc_othmfg, wc_selladm, wc_tlint, wc_fd, wc_tax, wc_cont]
wc_out = [sum(it[i] for it in wc_out_items) for i in _I]
wc_in  = [sum(dbt[p]["flow"][i] for p in products) for i in _I]                                    # sale receipts (cash inflow from debtors)

# Table 2 - Drawing Power
wc_rm  = [sum(rm_cl_val_matrix[rm][i] for rm in raw_materials) for i in _I]
wc_wip = _feed_series(edited_wc_bal_df, "Stock-in-Process", "bal")
wc_fg  = [sum(fg_cl_val[p][i] for p in products) for i in _I]
wc_inv = [a + b + c for a, b, c in zip(wc_rm, wc_wip, wc_fg)]
wc_rec = [sum(dbt[p]["cl"][i] for p in products) for i in _I]
wc_oca = _feed_series(edited_wc_bal_df, "Other Current Assets", "bal")
wc_tca = [a + b + c for a, b, c in zip(wc_inv, wc_rec, wc_oca)]
wc_cr  = [sum(crd[rm]["cl"][i] for rm in raw_materials) for i in _I]
wc_ocl = _feed_series(edited_wc_bal_df, "Other Current Liabilities", "bal")
wc_tliab = [a + b for a, b in zip(wc_cr, wc_ocl)]
wc_gap = [a - b for a, b in zip(wc_tca, wc_tliab)]
_mpct = min(max(safe_float(wc_margin), 0.0), 100.0) / 100.0
wc_mar = [max(g, 0.0) * _mpct for g in wc_gap]
wc_dp  = [max(g, 0.0) - m for g, m in zip(wc_gap, wc_mar)]             # drawing power = maximum permissible borrowing (never below nil)

# Borrowing chain. Final borrowing = proposed borrowing if DP covers it (DP surplus > 0), otherwise DP (the permissible maximum).
# Month t opens with the OD/CC and cash closing in month t-1 (M1 = cockpit feeds); Year 1 column treats the whole year as one period; Year 2-5 follow on.
# Closing cash = Final - Proposed : surplus cash if borrowing is repaid in full, nil if borrowed as proposed, negative = unfunded gap beyond DP.
wc_od_op, wc_cash_op, wc_req, wc_prop, wc_sur, wc_fin, wc_cash_cl = ([0.0] * 17 for _ in range(7))
def _wc_step(i, od_open, cash_open):
    wc_od_op[i], wc_cash_op[i] = od_open, cash_open
    wc_req[i] = wc_out[i] - wc_in[i] - cash_open
    wc_prop[i] = wc_req[i] + od_open
    wc_sur[i] = wc_dp[i] - wc_prop[i]
    wc_fin[i] = max(wc_prop[i], 0.0) if wc_sur[i] > 0 else wc_dp[i]
    wc_cash_cl[i] = wc_fin[i] - wc_prop[i]
_od, _cash = safe_float(wc_od_open), safe_float(wc_cash_open)
for _t in range(12):
    _wc_step(_t, _od, _cash)
    _od, _cash = wc_fin[_t], wc_cash_cl[_t]
_wc_step(12, wc_od_op[0], wc_cash_op[0])
for _i in range(13, 17):
    _wc_step(_i, wc_fin[_i - 1], wc_cash_cl[_i - 1])
_roi = safe_float(wc_roi) / 100.0
wc_int = [wc_fin[t] * _roi / 12.0 for t in range(12)]
wc_int.append(sum(wc_int[0:12]))                                         # Year 1 = sum of months
for _i in range(13, 17): wc_int.append((wc_od_op[_i] + wc_fin[_i]) / 2.0 * _roi)   # Year 2-5 = rate x average of opening and closing borrowing

def _wc_df(spec, head):
    """spec rows = (Sl No, label, series or None, bold). Returns the table and the list of bold flags."""
    rows, bold = [], []
    for sl, label, series, b in spec:
        r = {"Sl No": sl, head: label}
        for i, c in enumerate(display_columns): r[c] = series[i] if series is not None else float("nan")
        rows.append(r); bold.append(b)
    return pd.DataFrame(rows), bold

def wc_req_df():
    ind = "\u00a0\u00a0\u00a0"
    spec = [("1", "Cash Outflow :", wc_out, True),
            ("", ind + "RM : Advance to Supplier", wc_adv, False), ("", ind + "Payment to Creditors", wc_pay, False),
            ("", ind + "Power and fuel", wc_power, False), ("", ind + "Direct labour", wc_labour, False),
            ("", ind + "Other mfg. Expenses", wc_othmfg, False), ("", ind + "Selling and admn OH", wc_selladm, False),
            ("", ind + "TL Interest & Bank charges", wc_tlint, False), ("", ind + "FD increament", wc_fd, False),
            ("", ind + "Tax payment provision", wc_tax, False), ("", ind + "Other Contingency requirement", wc_cont, False),
            ("2", "Cash Inflow :", wc_in, True), ("", ind + "Sale receipt : Credit", wc_in, False),
            ("3", "Cash & Bank Balance", wc_cash_op, True),
            ("4", "Net Additional WCap requirement (1-2-3)", wc_req, True)]
    return _wc_df(spec, "WORKING CAP REQUIREMENT")

def wc_dp_df():
    ind = "\u00a0\u00a0\u00a0"
    spec = [("", "CURRENT ASSETS", None, True),
            ("", ind + "Raw Materials", wc_rm, False), ("", ind + "Stock-in-process", wc_wip, False), ("", ind + "Finished Goods", wc_fg, False),
            ("", ind + "Total Inventory", wc_inv, False), ("", ind + "Receivables", wc_rec, False), ("", ind + "Other Current Assets", wc_oca, False),
            ("1", "TOTAL CA (TCA)", wc_tca, True), ("", "", None, False),
            ("", "Current Liab other than Bank Borrowing", None, True),
            ("", ind + "Trade Creditors", wc_cr, False), ("", ind + "Other Current Liabilities", wc_ocl, False),
            ("2", "TOTAL LIABILITIES", wc_tliab, True), ("", "", None, False),
            ("3", "Working Capital Gap (1-2)", wc_gap, True), ("4", "Margin", wc_mar, True), ("5", "DP (3-4)", wc_dp, True),
            ("", "Less : Working Capital Requirement", wc_req, False), ("", "Less : Opening OD/CC Bal", wc_od_op, False),
            ("6", "Total Proposed Borrowing", wc_prop, True), ("7", "DP SURPLUS / (SHORTFALL) (5-6)", wc_sur, True),
            ("8", "FINAL BORROWING (Lower of 5 or 6)", wc_fin, True), ("9", "Int on Work Cap", wc_int, True),
            ("", "Memo : Closing Cash / (Unfunded Gap)", wc_cash_cl, False)]
    return _wc_df(spec, "Drawing Power, Borrowing & Interest on Working Capital")

def show_wc_df(df_bold):
    df, bold = df_bold
    sty = (df.style.format({c: "{:,.2f} L" for c in display_columns}, na_rep="")
           .apply(lambda r: ["font-weight: bold" if bold[r.name] else ""] * len(r), axis=1))
    st.dataframe(sty, use_container_width=True, hide_index=True, height=35 * (len(df) + 1) + 3)

# ---- Hierarchical P&L compiler (20 Sl Nos, Level 1 - Level 4). Same function serves "All" and a single product ----
pct_of = lambda n, d: [(a / b * 100.0 if b > 0 else 0.0) for a, b in zip(n, d)]
per_unit = lambda n, d: [(a * 100000.0 / b if b > 0 else 0.0) for a, b in zip(n, d)]       # Rs lacs / Qt -> Rs per Kg

def build_pl(sel):
    prods = products if sel == "All" else [sel]
    allsel = (sel == "All")
    rows = []
    def add(si, blk, depth, l1, l2, l3, l4, series, fmt="lac"):
        d = {"Si No": si, "BlockID": blk, "Depth": depth, "Level 1": l1, "Level 2": l2, "Level 3": l3, "Level 4": l4}
        for i, c in enumerate(display_columns): d[c] = series[i]
        d["_fmt"] = fmt                                   # qt / lac / rate / pct  (display format of the row)
        rows.append(d)
    S = lambda f: [sum(f(p)[i] for p in prods) for i in range(17)]
    def head(si, label, f, fmt="lac"):                    # L1 = total, L2 = product(s)
        add(si, si, "L1", label, "", "", "", S(f), fmt)
        for p in prods: add("", si, "L2", "", p, "", "", f(p), fmt)

    # RM helpers (All = original total matrices, single product = product-wise split)
    rms = raw_materials if allsel else used_rms[sel]
    q_src = ({"op": rm_op_matrix, "pur": rm_purch_matrix, "con": rm_gross_cons_matrix, "cl": rm_cl_matrix} if allsel
             else {"op": rm_op_p[sel], "pur": rm_purch_p[sel], "con": rm_cons_p[sel], "cl": rm_cl_p[sel]})
    v_src = ({"op": rm_op_val_matrix, "pur": rm_purch_val_matrix, "con": rm_cons_val_matrix, "cl": rm_cl_val_matrix} if allsel
             else {"op": rm_op_val_p[sel], "pur": rm_purch_val_p[sel], "con": rm_cons_val_p[sel], "cl": rm_cl_val_p[sel]})

    sale_t = S(lambda p: qty_matrix[p])
    prod_t = S(lambda p: fg_prod_matrix[p])
    rev_t = S(lambda p: rev_lacs_p[p])
    cons_t = [sum(v_src["con"][rm][i] for rm in rms) for i in range(17)]
    dx_t = S(lambda p: dx_total_cost[p])
    ix_t = S(lambda p: ix_total_cost[p])

    # 1, 2 : Sale / Production Qt
    head("1", "Sale (Qt) :", lambda p: qty_matrix[p], "qt")
    head("2", "Production (Qt) :", lambda p: fg_prod_matrix[p], "qt")

    # 3 : Revenue  (L2 product -> L3 Qt / Rate)
    add("3", "3", "L1", "Revenue (Rs) :", "", "", "", rev_t)
    for p in prods:
        add("", "3", "L2", "", p, "", "", rev_lacs_p[p])
        add("", "3", "L3", "", "", "Qt", "", qty_matrix[p], "qt")
        add("", "3", "L3", "", "", "Rate", "", rate_matrix[p], "rate")

    # 4 : RM Consumption (L2 RM -> L3 Opening/Purchase/Consumption/Cl stock -> L4 Qt / Rate)
    add("4", "4", "L1", "RM Consumption (Rs) :", "", "", "", cons_t)
    for rm in rms:
        add("", "4", "L2", "", rm, "", "", v_src["con"][rm])
        for lbl, k in (("Opening stk", "op"), ("Purchase", "pur"), ("Consumption", "con"), ("Cl stock", "cl")):
            add("", "4", "L3", "", "", lbl, "", v_src[k][rm])
            add("", "4", "L4", "", "", "", "Qt", q_src[k][rm], "qt")
            add("", "4", "L4", "", "", "", "Rate", rm_price_horizon[rm], "rate")
    add("", "4", "L2", "", "Opening Stock", "", "", [sum(v_src["op"][rm][i] for rm in rms) for i in range(17)])
    add("", "4", "L2", "", "Less : Closing Stock", "", "", [sum(v_src["cl"][rm][i] for rm in rms) for i in range(17)])

    # 5 : RM Consumption % (4/3)   6 : RM Consumption / p.u. (4/2)
    add("5", "5", "L1", "RM Consumption (%) (4/3)", "", "", "", pct_of(cons_t, rev_t), "pct")
    for rm in rms: add("", "5", "L2", "", rm, "", "", pct_of(v_src["con"][rm], rev_t), "pct")
    add("6", "6", "L1", "RM Consumption /p.u (4/2)", "", "", "", per_unit(cons_t, prod_t), "rate")
    for rm in rms: add("", "6", "L2", "", rm, "", "", per_unit(v_src["con"][rm], prod_t), "rate")

    # 7, 7a, 7b : FG Decrease / (Increase) = Opening - Closing ; opening / closing stock value (Rs lacs) with Qt and Rate (COGS per unit)
    fgadj_t = S(lambda p: fg_adj[p])
    add("7", "7", "L1", "FG : Decrease / (Increase) of FG (7a-7b)", "", "", "", fgadj_t)
    for p in prods: add("", "7", "L2", "", p, "", "", fg_adj[p])
    for _si, _lbl, _val, _qty, _rate in (("7a", "FG : Opening stock", fg_op_val, fg_op_matrix, fg_op_rate),
                                         ("7b", "Less : FG : Closing stock", fg_cl_val, fg_cl_matrix, fg_cl_rate)):
        add(_si, _si, "L1", _lbl, "", "", "", S(lambda p: _val[p]))
        for p in prods:
            add("", _si, "L2", "", p, "", "", _val[p])
            add("", _si, "L3", "", "", "Qt", "", _qty[p], "qt")
            add("", _si, "L3", "", "", "Rate", "", _rate[p], "rate")

    # 8 : Direct Expenses (L2 Total + 5 heads -> L3 product -> L4 Qt / Rate)
    def exp_block(si, label, total_f, head_f, heads, qty_f, short_pct_heads=()):
        add(si, si, "L1", label, "", "", "", S(total_f))
        add("", si, "L2", "", "Total", "", "", S(total_f))
        for p in prods:
            add("", si, "L3", "", "", p, "", total_f(p))
            add("", si, "L4", "", "", "", "Qt", qty_f(p), "qt")
            add("", si, "L4", "", "", "", "Rate", per_unit(total_f(p), qty_f(p)), "rate")
        for h in heads:
            add("", si, "L2", "", h, "", "", S(lambda p: head_f(h, p)))
            for p in prods:
                add("", si, "L3", "", "", p, "", head_f(h, p))
                if h in short_pct_heads:      # % of sale value heads: Sale Value x Rate (%)
                    add("", si, "L4", "", "", "", "Sale Value", rev_lacs_p[p])
                    add("", si, "L4", "", "", "", "Rate (%)", pct_of(head_f(h, p), rev_lacs_p[p]), "pct")
                else:
                    add("", si, "L4", "", "", "", "Qt", qty_f(p), "qt")
                    add("", si, "L4", "", "", "", "Rate", per_unit(head_f(h, p), qty_f(p)), "rate")
    exp_block("8", "Direct Expenses", lambda p: dx_total_cost[p], lambda h, p: dx_cost[h][p], direct_heads, lambda p: fg_prod_matrix[p])

    # 9-13 : COP (4+7+8), COP %, COP/p.u., Gross Profit, Gross Profit %
    cop_p = {p: [rm_cons_val_p_total[p][i] + fg_adj[p][i] + dx_total_cost[p][i] for i in range(17)] for p in products}
    cop_t = [c + f + d for c, f, d in zip(cons_t, fgadj_t, dx_t)]
    gp_p = {p: [rev_lacs_p[p][i] - cop_p[p][i] for i in range(17)] for p in products}
    gp_t = [r - c for r, c in zip(rev_t, cop_t)]
    add("9", "9", "L1", "COP (4+7+8)", "", "", "", cop_t)
    for p in prods: add("", "9", "L2", "", p, "", "", cop_p[p])
    add("10", "10", "L1", "COP % (9/3)", "", "", "", pct_of(cop_t, rev_t), "pct")
    for p in prods: add("", "10", "L2", "", p, "", "", pct_of(cop_p[p], rev_lacs_p[p]), "pct")
    add("11", "11", "L1", "COP/ p.u. (9/2)", "", "", "", per_unit(cop_t, prod_t), "rate")
    for p in prods: add("", "11", "L2", "", p, "", "", per_unit(cop_p[p], fg_prod_matrix[p]), "rate")
    add("12", "12", "L1", "Gross Profit (3-9)", "", "", "", gp_t)
    for p in prods: add("", "12", "L2", "", p, "", "", gp_p[p])
    add("13", "13", "L1", "Gross Profit % (12/3)", "", "", "", pct_of(gp_t, rev_t), "pct")
    for p in prods: add("", "13", "L2", "", p, "", "", pct_of(gp_p[p], rev_lacs_p[p]), "pct")

    # 14 : Indirect Expenses (L2 Total + 8 heads -> L3 product -> L4 Qt / Rate)
    exp_block("14", "Indirect Expenses", lambda p: ix_total_cost[p], lambda h, p: ix_cost[h][p], indirect_heads,
              lambda p: qty_matrix[p], short_pct_heads=[h for h in indirect_heads if ix_type[h] == "%"])

    # 15-20 : COGS (9+14), COGS %, COGS/p.u., EBIDTA (3-15), EBIDTA %, EBIDTA/p.u.
    cogs_p = {p: [cop_p[p][i] + ix_total_cost[p][i] for i in range(17)] for p in products}
    cogs_t = [c + x for c, x in zip(cop_t, ix_t)]
    eb_p = {p: [rev_lacs_p[p][i] - cogs_p[p][i] for i in range(17)] for p in products}     # EBIDTA = Revenue - COGS (3-15)
    eb_t = [r - c for r, c in zip(rev_t, cogs_t)]
    add("15", "15", "L1", "COGS (9+14)", "", "", "", cogs_t)
    for p in prods: add("", "15", "L2", "", p, "", "", cogs_p[p])
    add("16", "16", "L1", "COGS % (15/3)", "", "", "", pct_of(cogs_t, rev_t), "pct")
    for p in prods: add("", "16", "L2", "", p, "", "", pct_of(cogs_p[p], rev_lacs_p[p]), "pct")
    add("17", "17", "L1", "COGS / p.u. (15/1)", "", "", "", per_unit(cogs_t, sale_t), "rate")
    for p in prods: add("", "17", "L2", "", p, "", "", per_unit(cogs_p[p], qty_matrix[p]), "rate")
    add("18", "18", "L1", "EBIDTA (3-15)", "", "", "", eb_t)
    for p in prods: add("", "18", "L2", "", p, "", "", eb_p[p])
    add("19", "19", "L1", "EBIDTA % (18/3)", "", "", "", pct_of(eb_t, rev_t), "pct")
    for p in prods: add("", "19", "L2", "", p, "", "", pct_of(eb_p[p], rev_lacs_p[p]), "pct")
    add("20", "20", "L1", "EBIDTA / p.u.(18/1)", "", "", "", per_unit(eb_t, sale_t), "rate")
    for p in prods: add("", "20", "L2", "", p, "", "", per_unit(eb_p[p], qty_matrix[p]), "rate")
    # 21-22 (NEW) : Interest on Working Capital (WC page) and PBT. Company level, so shown for "All" only (it cannot be split by product).
    if allsel:
        add("21", "21", "L1", "Interest on Working Capital (WC page)", "", "", "", wc_int)
        add("22", "22", "L1", "PBT (18-21)", "", "", "", [e - x for e, x in zip(eb_t, wc_int)])
    return pd.DataFrame(rows)

df_pl_master_raw = build_pl("All")
df_pl_by_prod = {p: build_pl(p) for p in products}

# -----------------------------------------------------------------------------
# CHAPTER 4B (NEW): PRODUCT SLICER HELPERS (view-only filters; "All" returns the original tables)
# -----------------------------------------------------------------------------
def title_with_slicer(title, key):
    c_title, c_slicer = st.columns([6, 1.3], vertical_alignment="center")
    with c_title: st.title(title)
    with c_slicer: return st.selectbox("Product", ["All", "P1", "P2", "P3"], key=key, label_visibility="collapsed", format_func=lambda x: f"Product : {x}")

def pick_matrix(df_all, matrix, sel, key="Product"):
    return df_all if sel == "All" else compile_report({sel: matrix[sel]}, key)

def pick_rev(sel):
    if sel == "All": return df_rev_final
    d = compile_report({sel: rev_matrix[sel]}, "Product")
    d.iloc[0:, 1:] = d.iloc[0:, 1:] / 100000.0
    return d

def pick_fg_flow(sel):
    return master_prod_flow_df if sel == "All" else all_prod_dfs[products.index(sel)].reset_index(drop=True)

def pick_rm(sel, df_all, by_p):
    if sel == "All": return df_all
    d = {rm: by_p[sel][rm] for rm in used_rms[sel]} or {"-": [0.0] * 17}
    return compile_report(d, "Raw Material")

def pick_rm_flow(sel, df_all, op_p, pur_p, con_p, cl_p, metric_col):
    if sel == "All": return df_all
    blocks = []
    for rm in used_rms[sel]:
        blk = pd.DataFrame({"Raw Material": [rm, "", "", ""], metric_col: ["Op stk", "Generated / Purchased", "Consumption", "Cl stk"]})
        for idx, col in enumerate(display_columns): blk[col] = [op_p[sel][rm][idx], pur_p[sel][rm][idx], con_p[sel][rm][idx], cl_p[sel][rm][idx]]
        blocks.append(blk)
    return pd.concat(blocks, ignore_index=True) if blocks else df_all.iloc[0:0]

def pick_scrap(sel):
    if sel == "All": return df_scrap_final
    return compile_report({f"Scrap {sel} (S{sel})": fg_scrap_matrix[sel]}, "Scrap (Qt)")

def ratio_table(num, den, mult):
    rows = []
    for p in num:
        r = {"Product": p}
        for i, c in enumerate(display_columns): r[c] = (num[p][i] / den[p][i] * mult) if den[p][i] > 0 else 0.0
        rows.append(r)
    t = {"Product": "Total"}
    for i, c in enumerate(display_columns):
        sn, sd = sum(num[p][i] for p in num), sum(den[p][i] for p in num)
        t[c] = (sn / sd * mult) if sd > 0 else 0.0
    return pd.DataFrame(rows + [t])

def dx_tables(cost_by_p, sel):
    ps = products if sel == "All" else [sel]
    cost = {p: cost_by_p[p] for p in ps}
    df_cost = compile_report(cost, "Product")
    df_pu = ratio_table({p: cost[p] for p in ps}, {p: fg_prod_matrix[p] for p in ps}, 100000.0)   # Rs lacs -> Rs per Kg
    df_pct = ratio_table({p: cost[p] for p in ps}, {p: rev_lacs_p[p] for p in ps}, 100.0)         # % of revenue
    return df_cost, df_pu, df_pct

def ix_tables(cost_by_p, sel):
    ps = products if sel == "All" else [sel]
    cost = {p: cost_by_p[p] for p in ps}
    df_cost = compile_report(cost, "Product")
    df_pu = ratio_table(cost, {p: qty_matrix[p] for p in ps}, 100000.0)         # Rs lacs / Sale Qt -> Rs per Kg sold
    df_pct = ratio_table(cost, {p: rev_lacs_p[p] for p in ps}, 100.0)           # % of revenue
    return df_cost, df_pu, df_pct
# -----------------------------------------------------------------------------
# CHAPTER 5: TOP PANEL NAVIGATION ROUTER & WORKSPACE VIEWPORTS
# -----------------------------------------------------------------------------
page_tab5, page_tab1, page_tab2, page_tab3, page_tab4, page_tab_dx, page_tab_ix, page_tab_cost, page_tab_wc = st.tabs(["PL", "Revenue", "FG", "RM Qt", "RM Val", "Direct Expenses", "Indirect Expenses", "Costing", "WC"])

# (Streamlit tabs are client-side only, so the sidebar radio is synced by the script in CHAPTER 7.)

with page_tab1:
    sel1 = title_with_slicer("Sales Forecasting", "slicer_rev")
    st.subheader("1. Revenue (Rs in Lacs)")
    st.dataframe(pick_rev(sel1).style.format({col: "{:,.2f} L" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)
    st.subheader("2. Sale (Qt)")
    st.dataframe(pick_matrix(df_qty_final, qty_matrix, sel1).style.format({col: "{:,.0f}" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)
    _prods1 = products if sel1 == "All" else [sel1]
    st.subheader("3. Due Forecast : Sales (Rs in Lacs)")
    st.caption(f"Due = Sale + Sale x GST ({safe_float(gst_sales_pct):g}% on sales)")
    show_block_df(debtor_due_df(_prods1))
    st.subheader("4. Debtors & Cash Flow Movement Forecast (Rs in Lacs)")
    st.caption("Credit days  " + "  |  ".join(f"{p}: {dbt_days[p]:g}" for p in _prods1) +
               "      Cash Inflow = Opening Debtors + Due Value - Closing Debtors")
    show_block_df(debtor_flow_df(_prods1))

with page_tab2:
    sel2 = title_with_slicer("Production Forecasting", "slicer_fg")
    st.subheader("1. FG Flow (Qt)")
    st.dataframe(pick_fg_flow(sel2).style.format({col: "{:,.0f}" for col in display_columns if col not in ["Product", "FG Inventory Metrics"]}), use_container_width=True, hide_index=True)
    st.subheader("2. Production (Qt)")
    st.dataframe(pick_matrix(df_summary_prod, fg_prod_matrix, sel2).style.format({col: "{:,.0f}" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)
    st.subheader("3. FG Closing Stock (Qt)")
    st.dataframe(pick_matrix(df_summary_cl, fg_cl_matrix, sel2).style.format({col: "{:,.0f}" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)
    st.subheader("4. FG Opening Stock (Qt)")
    st.dataframe(pick_matrix(df_summary_op, fg_op_matrix, sel2).style.format({col: "{:,.0f}" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)
    st.subheader("5. FG Closing Stock (Value)")
    st.caption("Rs in Lacs = FG Closing Stock Qt x COGS per unit (Costing page)")
    st.dataframe(pick_matrix(df_fg_cl_val_final, fg_cl_val, sel2).style.format({col: "{:,.2f} L" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)
    st.subheader("6. FG Opening Stock (Value)")
    st.caption("Rs in Lacs = M1 Opening Qt x M1 COGS per unit; M2 onward = previous month's closing value; Year 2-5 = previous year's closing value")
    st.dataframe(pick_matrix(df_fg_op_val_final, fg_op_val, sel2).style.format({col: "{:,.2f} L" for col in display_columns if col != "Product"}), use_container_width=True, hide_index=True)

with page_tab3:
    sel3 = title_with_slicer("Material Forecasting", "slicer_rmqt")
    st.subheader("1. RM Flow (Qt)")
    st.dataframe(pick_rm_flow(sel3, master_rm_flow_df, rm_op_p, rm_purch_p, rm_cons_p, rm_cl_p, "RM Flow(Qt) Metrics").style.format({col: "{:,.0f}" for col in display_columns if col not in ["Raw Material", "RM Flow(Qt) Metrics"]}), use_container_width=True, hide_index=True)
    st.subheader("2. RM Consumption (Qt)")
    st.dataframe(pick_rm(sel3, df_rm_consumption_final, rm_cons_p).style.format({col: "{:,.0f}" for col in display_columns if col != "Raw Material"}), use_container_width=True, hide_index=True)
    st.subheader("3. RM Purchase (Qt)")
    st.dataframe(pick_rm(sel3, df_rm_purchase_final, rm_purch_p).style.format({col: "{:,.0f}" for col in display_columns if col != "Raw Material"}), use_container_width=True, hide_index=True)
    st.subheader("4. RM Loss (Qt)")
    st.dataframe(pick_rm(sel3, df_rm_loss_final, rm_loss_p).style.format({col: "{:,.0f}" for col in display_columns if col != "Raw Material"}), use_container_width=True, hide_index=True)
    st.subheader("5. Scrap (Qt)")
    st.dataframe(pick_scrap(sel3).style.format({col: "{:,.0f}" for col in display_columns if col != "Scrap (Qt)"}), use_container_width=True, hide_index=True)

with page_tab4:
    sel4 = title_with_slicer("Material Forecasting", "slicer_rmval")
    st.subheader("1. RM Flow (Rs in Lacs)")
    st.dataframe(pick_rm_flow(sel4, master_rm_val_flow_df, rm_op_val_p, rm_purch_val_p, rm_cons_val_p, rm_cl_val_p, "RM Flow(Rs) Metrics").style.format({col: "{:,.2f} L" for col in display_columns if col not in ["Raw Material", "RM Flow(Rs) Metrics"]}), use_container_width=True, hide_index=True)
    st.subheader("2. RM Purchase (Rs in Lacs)")
    st.dataframe(pick_rm(sel4, df_rm_purchase_val_final, rm_purch_val_p).style.format({col: "{:,.2f} L" for col in display_columns if col != "Raw Material"}), use_container_width=True, hide_index=True)
    st.subheader("3. RM Consumption (Rs in Lacs)")
    st.dataframe(pick_rm(sel4, df_rm_consumption_val_final, rm_cons_val_p).style.format({col: "{:,.2f} L" for col in display_columns if col != "Raw Material"}), use_container_width=True, hide_index=True)
    st.subheader("4. RM Loss (Rs in Lacs)")
    st.dataframe(pick_rm(sel4, df_rm_loss_val_final, rm_loss_p).style.format({col: "{:,.2f} L" for col in display_columns if col != "Raw Material"}), use_container_width=True, hide_index=True)
    st.subheader("5. RM Opening Stock (Rs in Lacs)")
    st.dataframe(pick_rm(sel4, df_rm_op_val_final, rm_op_val_p).style.format({col: "{:,.2f} L" for col in display_columns if col != "Raw Material"}), use_container_width=True, hide_index=True)
    st.subheader("6. RM Closing Stock (Rs in Lacs)")
    st.dataframe(pick_rm(sel4, df_rm_cl_val_final, rm_cl_val_p).style.format({col: "{:,.2f} L" for col in display_columns if col != "Raw Material"}), use_container_width=True, hide_index=True)
    st.subheader("7. Due to Suppliers (Rs in Lacs)")
    st.caption(f"RM-wise, all products combined (the Product slicer does not apply).  Gross Due = Purchase + Purchase x GST ({safe_float(gst_pur_pct):g}% on purchases).  "
               f"Advance {_adv_frac * 100:g}% of Gross Due is paid at order; Net Due to Suppliers = Gross Due - Advance")
    show_block_df(creditor_due_df())
    st.subheader("8. Creditors Flow & Cash Outflow Movement Forecast (Rs in Lacs)")
    st.caption(f"RM-wise, all products combined.  Credit period {safe_float(rm_credit_days):g} days for all RMs, applied on Net Due.  "
               "Cash outflow (a) = advance on current purchase ; (b) = Opening Creditors + Net Due - Closing Creditors (balance paid as per credit days)")
    show_block_df(creditor_flow_df())

with page_tab_dx:
    sel_dx = title_with_slicer("Direct Expenses Forecast", "slicer_dx")
    fmt_l = {c: "{:,.2f} L" for c in display_columns}
    fmt_n = {c: "{:,.2f}" for c in display_columns}
    fmt_p = {c: "{:,.2f}%" for c in display_columns}
    dx_blocks = [(h, dx_short[h], dx_cost[h]) for h in direct_heads]
    dx_blocks.append(("Total Direct Expenses", "Total Exp", dx_total_cost))
    for h, short, cost_by_p in dx_blocks:
        d_cost, d_pu, d_pct = dx_tables(cost_by_p, sel_dx)
        st.subheader(f"{h} : Forecast (Rs in Lacs)")
        st.dataframe(d_cost.style.format(fmt_l), use_container_width=True, hide_index=True)
        st.markdown(f"##### {short} / p.u. (Rs/Kg)")
        st.dataframe(d_pu.style.format(fmt_n), use_container_width=True, hide_index=True)
        st.markdown(f"##### {short} Turnover %")
        st.dataframe(d_pct.style.format(fmt_p), use_container_width=True, hide_index=True)
        st.markdown("---")

with page_tab_ix:
    sel_ix = title_with_slicer("Indirect Expenses Forecast", "slicer_ix")
    fmt_l = {c: "{:,.2f} L" for c in display_columns}
    fmt_n = {c: "{:,.2f}" for c in display_columns}
    fmt_p = {c: "{:,.2f}%" for c in display_columns}
    ix_blocks = [(h, ix_short[h], ix_cost[h]) for h in indirect_heads]
    ix_blocks.append(("Total Indirect Expenses", "Total Exp", ix_total_cost))
    for h, short, cost_by_p in ix_blocks:
        d_cost, d_pu, d_pct = ix_tables(cost_by_p, sel_ix)
        st.subheader(f"{h} : Forecast (Rs in Lacs)")
        if h in ix_type: st.caption("Basis : " + ("Rate p.u. x Sale Qt" if ix_type[h] == "p.u" else "% x Sale Value"))
        else: st.caption("Basis : sum of all 8 indirect expense heads")
        st.dataframe(d_cost.style.format(fmt_l), use_container_width=True, hide_index=True)
        st.markdown(f"##### {short} / p.u. (Rs/Kg)")
        st.dataframe(d_pu.style.format(fmt_n), use_container_width=True, hide_index=True)
        st.markdown(f"##### {short} Turnover %")
        st.dataframe(d_pct.style.format(fmt_p), use_container_width=True, hide_index=True)
        st.markdown("---")

with page_tab_cost:
    sel_cost = title_with_slicer("Costing : COGS Per Unit", "slicer_cost")
    st.caption("Rs per Kg. RM consumption and Direct Expenses = cost / Production Qt; Indirect Expenses = cost / Sale Qt; Year columns = annual cost / annual Qt. "
               "Travelling Expenses and Carriage Outward are not included (not yet incurred, so not part of FG valuation).")
    for p in (products if sel_cost == "All" else [sel_cost]):
        _cdf = build_costing_df(p)
        _sty = (_cdf.style.format({c: "{:,.2f}" for c in display_columns}, na_rep="")
                .apply(lambda r: ["font-weight: bold" if r["Sl No"] != "" else ""] * len(r), axis=1))
        st.dataframe(_sty, use_container_width=True, hide_index=True, height=35 * (len(_cdf) + 1) + 3)

with page_tab5:
    sel_pl = title_with_slicer("PL Forecast", "slicer_pl")
    st.caption("Tick / untick the checkbox in the '+/-' column on any heading row to expand or collapse it. "
               "[+] = collapsed, [-] = expanded. Each heading (and each RM inside 'RM Consumption') opens independently.")

    # ---- 1. Describe the tree: for every master row -> node key, parent chain, has-children ----
    master_pl = (df_pl_master_raw if sel_pl == "All" else df_pl_by_prod[sel_pl]).reset_index(drop=True)
    node_info = []                       # same order as master_pl
    cur_l1, cur_l2, cur_l3 = None, None, None
    for i in range(len(master_pl)):
        b_id, depth = str(master_pl.at[i, "BlockID"]), master_pl.at[i, "Depth"]
        if depth == "L1":
            node, ancestors = f"L1|{b_id}", []
            cur_l1, cur_l2, cur_l3 = node, None, None
        elif depth == "L2":
            node, ancestors = f"L2|{b_id}|{i}", [cur_l1]
            cur_l2, cur_l3 = node, None
        elif depth == "L3":
            node, ancestors = f"L3|{b_id}|{i}", [cur_l1, cur_l2]
            cur_l3 = node
        else:
            node, ancestors = f"L4|{b_id}|{i}", [cur_l1, cur_l2, cur_l3]
        child_depth = {"L1": "L2", "L2": "L3", "L3": "L4"}.get(depth)
        has_children = (
            child_depth is not None and i + 1 < len(master_pl)
            and master_pl.at[i + 1, "Depth"] == child_depth
            and str(master_pl.at[i + 1, "BlockID"]) == b_id
        )
        node_info.append({"node": node, "ancestors": ancestors, "has_children": has_children})

    open_nodes = st.session_state.pl_open_nodes
    visible_idx = [i for i, n in enumerate(node_info) if all(a in open_nodes for a in n["ancestors"])]

    # row position in the grid -> (node, has_children); used by the click handler below
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
        st.session_state.pl_editor_ver = ver + 1     # fresh editor state after every click

    # ---- 2. Build the visible table ----
    df_pl_filtered = master_pl.loc[visible_idx].copy() if visible_idx else pd.DataFrame(columns=master_pl.columns)

    if not df_pl_filtered.empty:
        def add_tree_prefix(r):
            info = node_info[r.name]
            mark = ("[-] " if info["node"] in open_nodes else "[+] ") if info["has_children"] else ""
            d, l1, l2, l3, l4 = r["Depth"], r["Level 1"], r["Level 2"], r["Level 3"], r["Level 4"]
            if d == "L1": return f"{mark}{l1}", l2, l3, l4
            elif d == "L2": return l1, f"{mark}{l2}", l3, l4
            elif d == "L3": return l1, l2, f"{mark}{l3}", l4
            else: return l1, l2, l3, l4

        prefixed_tuples = [add_tree_prefix(r) for _, r in df_pl_filtered.iterrows()]
        df_pl_filtered["Level 1"] = [t[0] for t in prefixed_tuples]
        df_pl_filtered["Level 2"] = [t[1] for t in prefixed_tuples]
        df_pl_filtered["Level 3"] = [t[2] for t in prefixed_tuples]
        df_pl_filtered["Level 4"] = [t[3] for t in prefixed_tuples]

        display_pl_df = df_pl_filtered.drop(columns=["_fmt", "BlockID", "Depth"])

        def format_pl_dataframe(row):
            fmt = df_pl_filtered.loc[row.name, "_fmt"]
            formatted_row = row.copy()
            for col in display_columns:
                val = safe_float(row[col])
                if fmt == "pct": formatted_row[col] = f"{val:.2f}%"
                elif fmt == "qt": formatted_row[col] = f"{val:,.0f}"
                elif fmt == "rate": formatted_row[col] = f"{val:,.2f}"
                else: formatted_row[col] = f"{val:,.2f} L"
            return formatted_row

        styled_pl_df = display_pl_df.apply(format_pl_dataframe, axis=1).reset_index(drop=True)

        # '+/-' checkbox column (first column). Blank for rows that have nothing to expand.
        toggle_vals = [((node_info[i]["node"] in open_nodes) if node_info[i]["has_children"] else None) for i in visible_idx]
        styled_pl_df.insert(0, "+/-", pd.array(toggle_vals, dtype="boolean"))

        # Fixed pixel widths (never auto-sized) and pinned (frozen) left columns, so the heads stay visible while scrolling right
        _pl_px = {"+/-": 48, "Si No": 52, "Level 1": 215, "Level 2": 175, "Level 3": 115, "Level 4": 100}
        def _pl_cfg(modern):
            cfg = {}
            for _c, _w in _pl_px.items():
                _kw = dict(width=_w, pinned=True) if modern else dict(width=("small" if _w < 100 else "medium"))
                if _c == "+/-": cfg[_c] = st.column_config.CheckboxColumn("+/-", help="Tick to expand, untick to collapse", **_kw)
                else: cfg[_c] = st.column_config.TextColumn(_c, **_kw)
            return cfg
        _pl_args = dict(
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            disabled=[c for c in styled_pl_df.columns if c != "+/-"],
            height=min(35 * (len(styled_pl_df) + 1) + 5, 1100),
            key=f"pl_tree_editor_{st.session_state.pl_editor_ver}",
            on_change=pl_tree_toggle_cb,
        )
        try:
            st.data_editor(styled_pl_df, column_config=_pl_cfg(True), **_pl_args)
        except Exception:      # older Streamlit without pixel widths / pinned columns
            st.data_editor(styled_pl_df, column_config=_pl_cfg(False), **_pl_args)
    else:
        st.warning("No structural P&L rows selected.")

with page_tab_wc:
    st.title("Working Capital Forecast")
    st.caption("Company level (all products, all RMs) - the Product slicer does not apply.  Rs in Lacs.")
    st.subheader("1. Working Capital Requirement (Rs in Lacs)")
    st.caption("Cash Outflow - Cash Inflow - Cash & Bank Balance.  RM advance and payment to creditors come from the RM Val page, Power / labour / other mfg expenses from Direct Expenses, "
               "Selling and admn OH from Indirect Expenses, sale receipts from the Debtors cash flow (Revenue page).  Cash & Bank Balance = opening feed in M1, then the previous period's closing cash.")
    show_wc_df(wc_req_df())
    st.subheader("2. Drawing Power, Borrowing & Interest on Working Capital (Rs in Lacs)")
    st.caption(f"Margin {_mpct * 100:g}% on Working Capital Gap; DP = maximum permissible borrowing.  Total Proposed Borrowing = Working Capital Requirement + Opening OD/CC (M1 = feed, then previous month's Final Borrowing).  "
               f"Final Borrowing = Proposed Borrowing if DP covers it, else DP.  Interest = Final Borrowing x {safe_float(wc_roi):g}% / 12 (Year 1 = sum of months; Year 2-5 = rate x average of opening and closing borrowing); it flows to the PL page below EBIDTA.")
    _short = [display_columns[i] for i in range(17) if wc_sur[i] < 0]
    if _short:
        st.warning("DP shortfall (borrowing needed is above Drawing Power) in: " + ", ".join(_short) + ".  The unfunded gap is carried forward as negative cash.")
    show_wc_df(wc_dp_df())

# -----------------------------------------------------------------------------
# CHAPTER 6: GLOBAL EXCEL PIPELINE COMPILER DOWNSTREAM EXPORTER
# -----------------------------------------------------------------------------
st.markdown("---")
_xl_engine = None
for _cand in ("openpyxl", "xlsxwriter"):
    try:
        __import__(_cand)
        _xl_engine = _cand
        break
    except ImportError:
        pass
if _xl_engine is None:
    st.info("Excel download is switched off because the 'openpyxl' library is missing. "
            "Add a line 'openpyxl' to requirements.txt and reboot the app.")
else:
    output_buffer = BytesIO()
    with pd.ExcelWriter(output_buffer, engine=_xl_engine) as writer:
        df_rev_final.to_excel(writer, sheet_name="Revenue (Lacs)", index=False)
        df_qty_final.to_excel(writer, sheet_name="Quantity Volumes", index=False)
        master_prod_flow_df.to_excel(writer, sheet_name="FG Flow Ledger", index=False)
        df_summary_prod.to_excel(writer, sheet_name="Summary Production", index=False)
        master_rm_flow_df.to_excel(writer, sheet_name="RM Flow Ledger", index=False)
        df_rm_consumption_final.to_excel(writer, sheet_name="RM Consumption Vol", index=False)
        df_scrap_final.to_excel(writer, sheet_name="Visible Scrap Report", index=False)
        df_pl_master_raw.to_excel(writer, sheet_name="Master Financial P&L Statement", index=False)
        _dx_sheets = {"Direct Exp (Rs Lacs)": [], "Direct Exp (Rs per Kg)": [], "Direct Exp (% Turnover)": []}
        for _h, _cost_by_p in [(h, dx_cost[h]) for h in direct_heads] + [("Total Direct Expenses", dx_total_cost)]:
            for _name, _df in zip(_dx_sheets, dx_tables(_cost_by_p, "All")):
                _df.insert(0, "Expense Head", _h)
                _dx_sheets[_name].append(_df)
        for _name, _dfs in _dx_sheets.items():
            pd.concat(_dfs, ignore_index=True).to_excel(writer, sheet_name=_name, index=False)
        _ix_sheets = {"Indirect Exp (Rs Lacs)": [], "Indirect Exp (Rs per Kg)": [], "Indirect Exp (% Turnover)": []}
        for _h, _cost_by_p in [(h, ix_cost[h]) for h in indirect_heads] + [("Total Indirect Expenses", ix_total_cost)]:
            for _name, _df in zip(_ix_sheets, ix_tables(_cost_by_p, "All")):
                _df.insert(0, "Expense Head", _h)
                _ix_sheets[_name].append(_df)
        for _name, _dfs in _ix_sheets.items():
            pd.concat(_dfs, ignore_index=True).to_excel(writer, sheet_name=_name, index=False)
        for _p in products:
            build_costing_df(_p).to_excel(writer, sheet_name=f"Costing {_p}", index=False)
        debtor_due_df(products).to_excel(writer, sheet_name="Due Forecast Sales", index=False)
        debtor_flow_df(products).to_excel(writer, sheet_name="Debtors & Cash Flow", index=False)
        creditor_due_df().to_excel(writer, sheet_name="Due to Suppliers", index=False)
        creditor_flow_df().to_excel(writer, sheet_name="Creditors & Cash Outflow", index=False)
        wc_req_df()[0].to_excel(writer, sheet_name="WC Requirement", index=False)
        wc_dp_df()[0].to_excel(writer, sheet_name="WC Borrowing & Interest", index=False)

    st.download_button(
        label="📥 Download Updated Comprehensive Interconnected Workbook",
        data=output_buffer.getvalue(),
        file_name="Sales_Production_And_PL_Valuation_Forecasting_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# -----------------------------------------------------------------------------
# CHAPTER 7: AUTO-SYNC SIDEBAR FEED RADIO WITH THE TOP TAB THE USER CLICKS
# -----------------------------------------------------------------------------
# Streamlit does not tell Python which tab is open, so a tiny browser-side script
# watches tab clicks and selects the matching sidebar radio button.
import streamlit.components.v1 as components
components.html(r"""
<script>
(function () {
    try {
        const P = window.parent, doc = P.document;
        const MAP = {"Revenue": "Sales / FG Feed", "FG": "Sales / FG Feed",
                     "RM Qt": "RM Qt Feed", "RM Val": "RM Val Feed", "Direct Expenses": "Direct Expenses Feed",
                     "Indirect Expenses": "Indirect Expenses Feed", "WC": "WC Feed", "PL": "RM Val Feed"};
        const norm = s => (s || "").replace(/\s+/g, " ").trim();
        const selectedTab = () => {
            const t = doc.querySelector('[role="tab"][aria-selected="true"]');
            return t ? norm(t.innerText) : null;
        };
        // click the matching radio option in the cockpit (label first, then the input itself as a fallback)
        const setRadio = (want) => {
            const scope = doc.querySelector('[data-testid="stSidebar"]') || doc;
            for (const lb of scope.querySelectorAll("label")) {
                if (norm(lb.innerText) !== want) continue;
                const inp = lb.querySelector('input[type="radio"]');
                if (inp && inp.checked) return true;
                lb.click();
                setTimeout(() => { const i = lb.querySelector('input[type="radio"]'); if (i && !i.checked) i.click(); }, 300);
                return true;
            }
            return false;
        };
        // paint the navigation tabs inline: gold text + gold left bar (default), red text + red left bar (selected); no underline
        const paintTabs = () => {
            const S = (el, p, v) => el.style.setProperty(p, v, "important");
            doc.querySelectorAll('[role="tablist"]').forEach(l => {
                S(l, "background", "#00294A"); S(l, "border", "none");
                l.querySelectorAll("*").forEach(e => {      // hide the thin highlight / border bars (anything that is not a tab)
                    if (e.closest('[role="tab"]') || e.querySelector('[role="tab"]')) return;
                    if (e.offsetHeight > 0 && e.offsetHeight <= 6) S(e, "display", "none");
                });
            });
            doc.querySelectorAll('[role="tab"]').forEach(b => {
                const sel = b.getAttribute("aria-selected") === "true";
                const col = sel ? "#FF5252" : "#FFD24C";
                S(b, "color", col); S(b, "font-weight", "700");
                S(b, "background", sel ? "#0B3D6B" : "transparent");
                S(b, "border", "none");
                S(b, "border-left", "4px solid " + (sel ? "#E53935" : "#D4AF37"));
                S(b, "box-shadow", "none");
                b.querySelectorAll("*").forEach(c => { S(c, "color", col); S(c, "font-weight", "700"); });
            });
        };
        if (P.__tabRadioSyncHandler) { doc.removeEventListener("click", P.__tabRadioSyncHandler, true); P.__tabRadioSyncHandler = null; }
        if (P.__tabSyncTimer) P.clearInterval(P.__tabSyncTimer);
        paintTabs();
        let last = selectedTab();
        // watch which top tab is selected (works for mouse, keyboard and touch) and follow it with the cockpit radio
        P.__tabSyncTimer = P.setInterval(function () {
            paintTabs();
            const cur = selectedTab();
            if (!cur || cur === last) return;
            const want = MAP[cur];
            if (!want || setRadio(want)) last = cur;      // radio not rendered yet -> retry on the next tick
        }, 250);
    } catch (err) { console.warn("tab / cockpit sync unavailable", err); }
})();
</script>
""", height=0)
