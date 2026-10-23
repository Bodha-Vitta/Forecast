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
    header[data-testid="stHeader"] { z-index: 99 !important; background: #F6F4EC !important; height: 2rem !important; min-height: 2rem !important; }
    .block-container { padding-top: 2.4rem !important; padding-bottom: 1rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; max-width: 100% !important; }
    div[data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    hr { border-color: #D4AF37 !important; margin: 0.5rem 0 !important; }

    /* Navigation tabs: same blue as the cockpit, bright-gold text + gold left accent bar (default); red text + red left bar (selected). No underline */
    /* FROZEN navigation bar: only the tab strip is sticky (the old rule stuck the whole tab block, which is as tall as the page, so it never froze).
       It sits just below Streamlit's 2rem top header, which is opaque cream so content never shows through. */
    div[data-testid="stTabs"], div[data-baseweb="tabs"] { overflow: visible !important; }
    .stApp div[role="tablist"], .stApp div[data-baseweb="tab-list"] {
        position: sticky !important; top: 2rem !important; z-index: 98 !important;
        background: #00294A !important; border: none !important; border-radius: 8px !important;
        padding: 6px 10px !important; gap: 10px !important;
        box-shadow: 0 -6px 0 0 #F6F4EC, 0 4px 8px rgba(0,41,74,0.35) !important;
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
    div[data-testid="stDataFrame"] { border: 1.5px solid #00294A; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,41,74,0.18); margin-top: 0.35rem; }
    /* output tables on the pages : outer border in the same dark blue as the cells (cockpit feed boxes keep their gold frame - rule below) */
    [data-testid="stMain"] div[data-testid="stDataFrame"], [data-testid="stMain"] div[data-testid="stDataEditor"],
    section.main div[data-testid="stDataFrame"], section.main div[data-testid="stDataEditor"] { border: 1.5px solid #00294A !important; }

    /* Sidebar cockpit */
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #00294A, #001B33) !important; border-right: 2px solid #D4AF37; }
    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] { height: 2.2rem !important; min-height: 0 !important; padding-top: 0.4rem !important; margin-bottom: 0 !important; }
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] { padding-top: 0.2rem !important; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { color: #D4AF37 !important; border-left: none !important; padding-left: 0 !important; }
    section[data-testid="stSidebar"] label p, section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: #F1DE9C !important; }
    section[data-testid="stSidebar"] hr { border-color: #D4AF37 !important; }
    section[data-testid="stSidebar"] h2 { margin-top: 0.9rem !important; }
    section[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] { margin: 0.3rem 0 0.5rem 0 !important; }
    /* read-only total capex boxes (Add Product desk) */
    .capex-row { display: flex; gap: 14px; margin: 0.3rem 0 1rem 0; flex-wrap: wrap; }
    .capex-box { flex: 1 1 220px; background: #FFF6D6; border: 2px solid #D4AF37; border-radius: 8px; padding: 6px 12px; }
    .capex-box span { display: block; color: #0B3D6B; font-size: 0.78rem; font-weight: 600; }
    .capex-box b { color: #00294A; font-size: 1.15rem; }
    .capex-box.tot { background: #D4AF37; } .capex-box.tot span, .capex-box.tot b { color: #00294A; }
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
    /* Add Product desk : form frame, text box, expanders, Add button */
    section[data-testid="stSidebar"] div[data-testid="stForm"] { border: 2px solid #D4AF37 !important; border-radius: 10px !important; padding: 0.6rem 0.8rem !important; }
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] div[data-baseweb="input"] { background: #FFF6D6 !important; border: 2px solid #D4AF37 !important; border-radius: 8px !important; }
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] input { color: #00294A !important; font-weight: 700 !important; background: transparent !important; }
    section[data-testid="stSidebar"] div[data-testid="stFormSubmitButton"] button { background: #D4AF37 !important; border: 2px solid #F1DE9C !important; min-height: 2.4rem !important; padding: 0 1.2rem !important; }
    section[data-testid="stSidebar"] div[data-testid="stFormSubmitButton"] button, section[data-testid="stSidebar"] div[data-testid="stFormSubmitButton"] button * { color: #00294A !important; font-weight: 800 !important; }
    section[data-testid="stSidebar"] div[data-testid="stExpander"] { border: 1.5px solid #D4AF37 !important; border-radius: 8px !important; }
    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary p { color: #FFD24C !important; font-weight: 700 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* ===== ONE font for every page + the cockpit : Segoe UI Light, no bold anywhere ===== */
    .stApp.stApp.stApp.stApp :is(p, span, div, label, li, a, h1, h2, h3, h4, h5, h6, button, input, textarea, select, summary, th, td, b, strong, em, small, code, caption) {
        font-family: "Segoe UI Light", "Segoe UI", sans-serif !important; font-weight: 400 !important;
    }
    .stApp.stApp.stApp.stApp [data-testid="stIconMaterial"], .stApp.stApp.stApp.stApp span[class*="material-symbols"], .stApp.stApp.stApp.stApp span[class*="material-icons"] {
        font-family: "Material Symbols Rounded", "Material Icons" !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---- Products added through the "Add Product" cockpit desk (kept in the session; every page / slicer / calculation reads this list) ----
if "added_products" not in st.session_state: st.session_state.added_products = []     # list of {uid, name, feed_df, sc, rm_df}
if "ap_uid" not in st.session_state: st.session_state.ap_uid = 0
if "ap_form_ver" not in st.session_state: st.session_state.ap_form_ver = 0
if "ap_flash" not in st.session_state: st.session_state.ap_flash = []
added_products = st.session_state.added_products
added_names = [c["name"] for c in added_products]
products = ["P1", "P2", "P3", "P4"] + added_names          # P4 = new product on the new capex project ; then every added product
new_prods = ["P4"] + added_names                           # products that run on their own capex / timing feed
products_base = ["P1", "P2", "P3"]                         # products fed through the original Sales / FG feed tables
p4_rms = ["RM13", "RM14", "RM15"]
rm_base = [f"RM{i}" for i in range(1, 13)]                # RM1-RM12 : fed through the original RM feed tables
raw_materials = rm_base + p4_rms                           # extended in CHAPTER 3 with the RMs of added products

def safe_float(val):
    try:
        if isinstance(val, (list, np.ndarray, pd.Series)):
            val = val[0] if len(val) > 0 else None
        if val is None or pd.isna(val) or val == "": return 0.0
        return float(val)
    except: return 0.0

# RM table of an added product : column names, and a cleaner that returns one dict per filled row
AP_RM_COLS = ["RM Name", "Consumption Ratio (%)", "Normal Loss - Scrap (%)", "Invisible Loss (%)", "Default Price (Rs/Kg)",
              "Days Hold of Inventory", "Supplier Advance (%)", "Supplier Credit Days", "M1 Op Stock (Kg)", "Opening Creditors (Rs Lacs)"]
def _ap_rm_rows(df):
    rows = []
    for _, r in df.iterrows():
        nm = r[AP_RM_COLS[0]]
        if nm is None or pd.isna(nm) or str(nm).strip() == "": continue
        rows.append({"name": str(nm).strip(), "con": safe_float(r[AP_RM_COLS[1]]), "vloss": safe_float(r[AP_RM_COLS[2]]), "iloss": safe_float(r[AP_RM_COLS[3]]),
                     "price": safe_float(r[AP_RM_COLS[4]]), "hold": safe_float(r[AP_RM_COLS[5]]), "adv": safe_float(r[AP_RM_COLS[6]]),
                     "credit": safe_float(r[AP_RM_COLS[7]]), "opstock": safe_float(r[AP_RM_COLS[8]]), "opcred": safe_float(r[AP_RM_COLS[9]])})
    return rows
def _rm_universe():
    out = rm_base + p4_rms
    for c in added_products:
        for r in _ap_rm_rows(c["rm_df"]):
            if r["name"] not in out: out = out + [r["name"]]
    return out
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
        "RM Name": ["RM1", "RM2", "RM3", "RM4", "RM5", "RM6", "RM1", "RM7", "RM8", "RM9", "RM10", "RM1", "RM11", "RM12", "RM13", "RM14", "RM15"],
        "Target FG": ["P1", "P1", "P1", "P1", "P1", "P1", "P2", "P2", "P2", "P2", "P2", "P3", "P3", "P3", "P4", "P4", "P4"],
        "Con%": [0.70, 0.15, 0.05, 0.04, 0.03, 0.03, 0.70, 0.20, 0.03, 0.04, 0.03, 0.70, 0.20, 0.10, 0.60, 0.30, 0.10],
        "Visible Loss": [0.04] * 17, "Invisible Loss": [0.01] * 17
    }
    st.session_state.sidebar_bom_df = pd.DataFrame(bom_data)

# 6. Initialize Raw Material Logistics Inventory parameters
if "sidebar_rm_logistics_df" not in st.session_state:
    logistics_data = {
        "Raw Material": rm_base,
        "M1 Initial Op Stock Qty": [13000.0, 1658.0, 553.0, 442.0, 332.0, 332.0, 1700.0, 250.0, 350.0, 250.0, 100.0, 50.0],
        "Days Hold": [45.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0]
    }
    st.session_state.sidebar_rm_logistics_df = pd.DataFrame(logistics_data)

# 7. Initialize Raw Material Base Unit Commercial Procurement Price Feeder
if "sidebar_rm_price_df" not in st.session_state:
    st.session_state.sidebar_rm_price_df = pd.DataFrame({
        "Raw Material": rm_base,
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
        "Raw Material": rm_base,
        "Opening Creditors (Rs Lacs)": [21.613, 4.098, 0.068, 0.683, 0.409, 0.511, 4.434, 0.846, 0.086, 0.338, 0.783, 0.261]
    })

# ---- NEW: advance payment on RM orders (RM Val feed) ----
if "adv_pct_saved" not in st.session_state:
    st.session_state.adv_pct_saved = 20.0

# ---- NEW: WC (Working Capital) page feeds ----
if "wc_cash_saved" not in st.session_state:
    st.session_state.wc_cash_saved = 1.5          # opening bank / cash balance (Rs lacs)
if "wc_roi_saved" not in st.session_state:
    st.session_state.wc_roi_saved = 9.0           # rate of interest (% p.a.)
if "wc_od_saved" not in st.session_state:
    st.session_state.wc_od_saved = 15.0           # opening bank OD / CC balance (Rs lacs)
if "wc_limit_saved" not in st.session_state:
    st.session_state.wc_limit_saved = 20.0        # NEW : OD / CC sanction limit (Rs lacs) - CF page
if "wc_margin_saved" not in st.session_state:
    st.session_state.wc_margin_saved = 25.0       # margin on working capital gap (%)
wc_flow_cols = ["FD Increment", "Tax Payment Provision", "Other Contingency Requirement"]   # TL Interest & Bank Charges now comes from the TL page
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
        "P1": [7.0, 5.0, 1.0], "P2": [8.0, 6.0, 1.5], "P3": [9.0, 7.0, 2.0], "P4": [9.0, 7.0, 2.0]
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
# ---- Sessions opened before P4 existed: add the P4 BOM rows / P4 Direct Expense rates once ----
if "P4" not in set(st.session_state.sidebar_bom_df["Target FG"]):
    st.session_state.sidebar_bom_df = pd.concat([st.session_state.sidebar_bom_df, pd.DataFrame({
        "RM Name": p4_rms, "Target FG": ["P4"] * 3, "Con%": [0.60, 0.30, 0.10], "Visible Loss": [0.04] * 3, "Invisible Loss": [0.01] * 3})], ignore_index=True)
if "P4" not in st.session_state.sidebar_dx_rate_df.columns:
    st.session_state.sidebar_dx_rate_df = st.session_state.sidebar_dx_rate_df.assign(P4=[9.0, 7.0, 2.0])

# ---- NEW: P4 / NEW CAPEX FEED (P4 cockpit feed & default figures) ----
p4_cols = months + ["Year 2", "Year 3", "Year 4", "Year 5"]
P4_ROWS = ["Sale Qt Projection (Kg)", "Growth % : Sale", "Selling Rate (Rs/Kg)", "Selling Rate Inflation %",
           "FG Inventory Hold Days", "New Capex Payment (Rs Lacs)", "New Capex Installation Cost (Rs Lacs)"]
def _feed_getter(df):
    """Returns f(row name) -> 16 values (M1-M12, Year 2-5) of one new-capex product feed table (P4 table or the table of an added product)."""
    t = df.set_index(df.columns[0])
    return lambda name: [safe_float(t.at[name, c]) if (name in t.index and c in t.columns) else 0.0 for c in p4_cols]

def _np_timing(pay, inst, sc, is_p4):
    """Capex completion month and start of capitalisation / production / sale (0-based month index) of a new-capex product.
    P4 : completion = Auto (month after the last capex payment) or the month chosen ; start = completion + 1.
    Added product with capex : same.  Added product without capex : start = month chosen (Auto = M1)."""
    has = (sum(pay) + sum(inst)) > 0
    last = max([i for i in range(12) if pay[i] > 0] or [-1])
    warn, sel_c = "", sc.get("completion", "Auto")
    if sel_c in months[:11]:
        comp = months.index(sel_c)
        if comp < last:
            warn = f"Completion month {months[comp]} is before the last capex payment ({months[last]}); {months[last]} is used."
            comp = last
    else:
        comp = min(last + 1, 10)
    start = comp + 1
    if not is_p4:
        sel_s = sc.get("start", "Auto")
        if not has:
            start = months.index(sel_s) if sel_s in months else 0
            comp = start - 1
        elif sel_s in months:
            if months.index(sel_s) >= start: start = months.index(sel_s)
            else: warn = (warn + " " if warn else "") + f"Start month {sel_s} is before the month after completion; {months[min(start, 11)]} is used."
    return has, last, comp, min(start, 11), warn

if "sidebar_p4_df" not in st.session_state:
    _z = [0.0] * 16
    _rows = {
        "Sale Qt Projection (Kg)":               [0.0] * 8 + [100.0, 500.0, 600.0, 800.0] + [0.0] * 4,
        "Growth % : Sale":                       [0.0] * 12 + [20.0, 10.0, 5.0, 5.0],
        "Selling Rate (Rs/Kg)":                  [600.0] * 12 + [0.0] * 4,
        "Selling Rate Inflation %":              [0.0] * 12 + [5.0, 5.0, 5.0, 5.0],
        "FG Inventory Hold Days":                [45.0] * 16,
        "New Capex Payment (Rs Lacs)":           [0.0, 20.0, 20.0, 20.0, 0.0, 0.0, 40.0, 0.0, 0.0, 0.0, 0.0, 0.0] + [0.0] * 4,
        "New Capex Installation Cost (Rs Lacs)": [0.0] * 7 + [2.0] + [0.0] * 8,
    }
    st.session_state.sidebar_p4_df = pd.DataFrame([{"P4 Assumption": k, **dict(zip(p4_cols, v))} for k, v in _rows.items()])
if "p4_scalars" not in st.session_state:
    st.session_state.p4_scalars = {"op_fg": 0.0, "op_dbt": 0.0, "dbt_days": 30.0, "adv_pct": 10.0, "crd_days": 35.0, "tl_pct": 85.0, "completion": "Auto"}
if "sidebar_p4_rm_df" not in st.session_state:
    st.session_state.sidebar_p4_rm_df = pd.DataFrame({
        "Raw Material": p4_rms, "Initial Price": [100.0, 300.0, 400.0], "Days Hold": [30.0, 30.0, 30.0],
        "M1 Initial Op Stock Qty": [0.0, 0.0, 0.0], "Opening Creditors (Rs Lacs)": [0.0, 0.0, 0.0]})

# ---- NEW: FAR FEED (opening assets + asset additions) ----
asset_classes = ["Plant & Machinery", "Electrical Equipments", "Furniture", "Vehicles", "Computers", "Building", "Land",
                 "Brand Rights & Trade Mark", "Computer Software"]
if "sidebar_far_open_df" not in st.session_state:
    st.session_state.sidebar_far_open_df = pd.DataFrame({
        "Asset": asset_classes,
        "Gross Block (Rs Lacs)": [300.0, 20.0, 10.0, 10.0, 15.0, 30.0, 50.0, 5.0, 5.0],
        "Gross Dep (Rs Lacs)":   [70.0, 5.0, 2.0, 3.0, 5.0, 9.0, 0.0, 1.0, 1.0],
        "Rate of Dep (%)":       [5.0, 10.0, 7.0, 10.0, 10.0, 5.0, 0.0, 20.0, 20.0]})
add_rows = ["Plant & Machinery (Regular)"] + asset_classes[1:]          # P&M (New Capex Project) is added automatically
if "sidebar_far_add_df" not in st.session_state:
    _a = {r: [0.0] * 16 for r in add_rows}
    def _put(r, pos, v): _a[r][pos] = v                                    # pos 0-11 = M1-M12, 12-15 = Year 2-5
    _put("Plant & Machinery (Regular)", 5, 1.0)
    for k, v in zip(range(12, 16), [5.0, 10.0, 15.0, 10.0]): _put("Plant & Machinery (Regular)", k, v)
    _put("Electrical Equipments", 3, 3.0)
    _put("Furniture", 2, 2.0)
    for r in ("Electrical Equipments", "Furniture"):
        for k in range(12, 16): _put(r, k, 2.0)
    _put("Vehicles", 11, 5.0); _put("Vehicles", 13, 5.0); _put("Vehicles", 15, 10.0)
    for k in (1, 4, 7, 11): _put("Computers", k, 1.0)
    for k in range(12, 16): _put("Computers", k, 3.0)
    for k in (0, 2, 6, 9): _put("Building", k, 1.0)
    for k in range(12, 16): _put("Building", k, 2.0)
    _put("Land", 12, 10.0)
    st.session_state.sidebar_far_add_df = pd.DataFrame([{"Asset Addition (Rs Lacs)": r, **dict(zip(p4_cols, v))} for r, v in _a.items()])

# ---- NEW: TL FEED (term loans + bank charges) ----
tl_names = ["TL1", "TL2", "TL3", "TL New"]
if "sidebar_tl_df" not in st.session_state:
    st.session_state.sidebar_tl_df = pd.DataFrame({
        "Term Loan": tl_names,
        "Opening O/s M1 (Rs Lacs)": [10.0, 20.0, 5.0, 0.0],
        "Interest Rate (% p.a.)":    [9.0, 8.0, 7.0, 8.0],
        "Life Left (Months)":        [24.0, 35.0, 36.0, 48.0]})
if "bank_chg_saved" not in st.session_state:
    st.session_state.bank_chg_saved = 0.05            # % per month on month-end outstanding (WC borrowing and TL)

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
def _on_ctx_change():
    """Opening the Add Product desk spreads the cockpit once; the Squeeze / Spread buttons stay fully usable afterwards."""
    if st.session_state.get("synchronized_sidebar_context_radio_widget") == "Add Product":
        st.session_state.cockpit_wide = True
COCKPIT_WIDE = st.session_state.cockpit_wide          # re-evaluated after the radio below (the Add Product desk always opens spread)
WIDE_CSS = """
    <style>
    section[data-testid="stSidebar"]:not([aria-expanded="false"]) { width: min(78vw, 1150px) !important; min-width: min(78vw, 1150px) !important; max-width: min(78vw, 1150px) !important; }
    section[data-testid="stSidebar"]:not([aria-expanded="false"]) > div { width: 100% !important; }
    section[data-testid="stSidebar"] div[data-testid="stNumberInput"] { max-width: 260px !important; }
    section[data-testid="stSidebar"] div[data-testid="stButton"] { justify-content: flex-start !important; }
    </style>"""

def _col_px(df, c):
    """Column width in pixels from the longest text in the column (header or cell)."""
    head = len(str(c)) * 7.2 + 44                       # header text + sort / menu icons
    cells = max([len(str(v)) for v in df[c].tolist()] + [1]) * 8 + 24
    return int(min(max(head, cells, 64), 300))

def sb_editor(df, **kw):
    """Cockpit feed table. Every key-in column gets a red marker in its heading (fixed columns have none).
    Spread cockpit: each column is also sized to its data, so the box stays compact."""
    wide = COCKPIT_WIDE
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

# ---- Output-table theme : navy cells, bright-gold text, deeper band on heading / total rows, light-coral negatives ----
T_NAVY, T_GOLD, T_ROWHDR, T_NEG = "#00294A", "#FFD24C", "#FFF0A0", "#FF8A80"     # cell blue (= cockpit / navigation bar), number gold, row-header light gold, negative coral
T_BAND, T_GOLD_SOFT = T_NAVY, T_ROWHDR
def navy(obj):
    """Styler with the dark-blue / gold theme : text columns (row headers) light golden yellow, numbers bright gold, nothing bold."""
    sty = obj if hasattr(obj, "set_properties") else obj.style
    sty = sty.set_properties(**{"background-color": T_NAVY, "color": T_GOLD, "font-weight": "400"})
    _hdr = [c for c in sty.data.columns if not pd.api.types.is_numeric_dtype(sty.data[c])]
    if _hdr: sty = sty.set_properties(subset=_hdr, **{"color": T_ROWHDR})
    _m = getattr(sty, "map", None) or getattr(sty, "applymap")
    return _m(lambda v: f"color: {T_NEG};" if isinstance(v, (int, float, np.floating)) and not isinstance(v, bool) and v < 0 else "")
def gdf(obj, **kw):
    """st.dataframe in the navy / gold theme (falls back to the plain table if styling is not possible)."""
    try:
        return st.dataframe(navy(obj), **kw)
    except Exception:
        return st.dataframe(obj, **kw)

# ---- ADD PRODUCT desk : helpers ----
def _nz(v):
    """Number box value : an empty box stays None."""
    try:
        return None if (v is None or pd.isna(v)) else float(v)
    except Exception:
        return None

AP_SC_DEFAULT = {"op_fg": None, "op_dbt": None, "cust_adv": None, "dbt_days": None, "tl_pct": None, "tl_rate": None, "tl_life": None,
                 "completion": "Auto", "start": "Auto"}
def _ap_blank_feed():
    return pd.DataFrame({"Assumption": P4_ROWS, **{c: [np.nan] * len(P4_ROWS) for c in p4_cols}})
AP_DX_RATE = "Rate p.u. (Rs/Kg production)"
AP_INFL = [f"Year {y} (%)" for y in (2, 3, 4, 5)]
def _ap_blank_dx():
    return pd.DataFrame({"Expense Head": direct_heads, "Against": ["p.u (Production Qt)"] * len(direct_heads),
                         AP_DX_RATE: [np.nan] * len(direct_heads), **{c: [np.nan] * len(direct_heads) for c in AP_INFL}})
def _ap_blank_ix():
    return pd.DataFrame({"Expense Head": indirect_heads, "Against Sale": [ix_type[h] for h in indirect_heads],
                         IX_RATE_COL: [np.nan] * len(indirect_heads), **{c: [np.nan] * len(indirect_heads) for c in AP_INFL}})
# products added before this version have no own expense feeds : give them empty boxes ; added products no longer share the P1-P4 Direct Expenses desk
for _c0 in st.session_state.added_products:
    if "dx_df" not in _c0: _c0["dx_df"] = _ap_blank_dx()
    if "ix_df" not in _c0: _c0["ix_df"] = _ap_blank_ix()
    if _c0["name"] in st.session_state.sidebar_dx_rate_df.columns:
        st.session_state.sidebar_dx_rate_df = st.session_state.sidebar_dx_rate_df.drop(columns=[_c0["name"]])

def _capex_boxes(feed_df):
    """Read-only totals under the capex rows of the feed table (update as the user keys in)."""
    g = _feed_getter(feed_df)
    pay, inst = sum(g("New Capex Payment (Rs Lacs)")[0:12]), sum(g("New Capex Installation Cost (Rs Lacs)")[0:12])
    st.markdown(f'<div class="capex-row"><div class="capex-box"><span>Total New Capex Payment (Rs Lacs)</span><b>{pay:,.2f}</b></div>'
                f'<div class="capex-box"><span>Total Installation Cost (Rs Lacs)</span><b>{inst:,.2f}</b></div>'
                f'<div class="capex-box tot"><span>TOTAL NEW CAPEX (Rs Lacs) - auto</span><b>{pay + inst:,.2f}</b></div></div>', unsafe_allow_html=True)

def _ap_blank_rm(n=3):
    return pd.DataFrame({AP_RM_COLS[0]: [None] * n, **{c: [np.nan] * n for c in AP_RM_COLS[1:]}})

def _ap_inputs(feed_df, sc, rm_df, kp, dx_df, ix_df):
    """Input boxes of one product, in the layout of the 'Add product' sheet. Returns (feed table, scalars, RM table)."""
    feed_title("New Product : Cockpit feed & default figures - M1 to M12 and Year 2-5")
    st.caption("Sale Qt (Kg) and Selling Rate (Rs/Kg) : M1-M12.  Growth % : Sale and Selling Rate Inflation % : Year 2-5.  FG Inventory Hold Days : M1-M12 and Year 2-5.  "
               "New Capex Payment and Installation Cost (Rs Lacs) : in the month they are paid.  Sale Qt before the start month is ignored; "
               "Year 2 Sale = M12 Sale x 12 x (1 + Year 2 growth); Year 2-5 Selling Rate = M12 rate compounded by the yearly inflation.")
    feed_df = sb_editor(feed_df, hide_index=True, key=f"{kp}_feed", column_config={"Assumption": st.column_config.TextColumn(disabled=True)})
    _capex_boxes(feed_df)
    sc = dict(sc)
    feed_title("Opening position, credit terms, capex funding and timing")
    c1, c2, c3 = st.columns(3)
    with c1:
        sc["op_fg"] = st.number_input("Opening FG Stock (Kg, M1)", value=_nz(sc.get("op_fg")), min_value=0.0, key=f"{kp}_opfg")
        sc["op_dbt"] = st.number_input("Opening Debtors (Rs Lacs)", value=_nz(sc.get("op_dbt")), min_value=0.0, key=f"{kp}_opdbt")
        sc["cust_adv"] = st.number_input("Customer Advance (%)", value=_nz(sc.get("cust_adv")), min_value=0.0, max_value=100.0, key=f"{kp}_cadv")
    with c2:
        sc["dbt_days"] = st.number_input("Credit Days : Debtors", value=_nz(sc.get("dbt_days")), min_value=0.0, key=f"{kp}_dbtd")
        sc["tl_pct"] = st.number_input("TL Sanction & Disbursement (% of capex)", value=_nz(sc.get("tl_pct")), min_value=0.0, max_value=100.0, key=f"{kp}_tlpct")
        sc["tl_rate"] = st.number_input("TL Interest Rate (% p.a.)", value=_nz(sc.get("tl_rate")), min_value=0.0, key=f"{kp}_tlrate")
    with c3:
        sc["tl_life"] = st.number_input("TL Repayment Period (Months)", value=_nz(sc.get("tl_life")), min_value=0.0, key=f"{kp}_tllife")
        _oc, _os = ["Auto"] + months[:11], ["Auto"] + months
        sc["completion"] = st.selectbox("Capex Installation & Commercial Run (month)", _oc, index=_oc.index(sc["completion"]) if sc.get("completion") in _oc else 0, key=f"{kp}_comp",
                                        help="Auto = month after the last capex payment. Ignored when there is no capex.")
        sc["start"] = st.selectbox("Start of Sale & Production (month)", _os, index=_os.index(sc["start"]) if sc.get("start") in _os else 0, key=f"{kp}_start",
                                   help="Auto = month after completion (with capex) or M1 (no capex). Production and sale never start before the month after completion.")
    feed_title("RM Cockpit feed - one row per raw material (use the + row at the bottom of the box to add more RMs)")
    st.caption("Consumption Ratio (%) = share of this product's production (normally totals 100%).  Normal Loss (scrap) and Invisible Loss are % of gross RM consumption.  "
               "Default Price = Rs/Kg.  If an RM name already exists in the model (e.g. RM1) the product shares that RM : only its ratio and losses are used here, "
               "price / stock / credit terms stay as already fed.")
    rm_df = sb_editor(rm_df, hide_index=True, num_rows="dynamic", key=f"{kp}_rm", column_config={AP_RM_COLS[0]: st.column_config.TextColumn(AP_RM_COLS[0])})
    feed_title("Direct Expenses of this product - key in the rate per Kg of production (Rs) and YoY inflation % for Year 2-5 (empty box = nil)")
    st.caption("Fed separately for every new product - nothing is borrowed from P1-P4.")
    dx_df = sb_editor(dx_df, hide_index=True, key=f"{kp}_dx", column_config={"Expense Head": st.column_config.TextColumn(disabled=True), "Against": st.column_config.TextColumn(disabled=True)})
    feed_title("Indirect Expenses of this product - key in the rate (Rs/Kg for p.u, % of sale value for %) and YoY inflation % for Year 2-5 (empty box = nil)")
    ix_df = sb_editor(ix_df, hide_index=True, key=f"{kp}_ix", column_config={"Expense Head": st.column_config.TextColumn(disabled=True), "Against Sale": st.column_config.TextColumn(disabled=True)})
    return feed_df, sc, rm_df, dx_df, ix_df

def _ap_validate(name, feed_df, sc, rm_df, dx_df, ix_df):
    """Returns (errors, warnings). Errors stop the Add; warnings are shown after it."""
    errs, warns, nm = [], [], (name or "").strip()
    reserved = {p.lower() for p in products} | {"all", "total", "product", "timeline"} | {c.lower() for c in display_columns}
    if not nm: errs.append("Key in the name of the new product.")
    elif any(ch in nm for ch in "[]:*?/\\"): errs.append("The product name cannot contain any of  [ ] : * ? / \\")
    elif nm.lower() in reserved: errs.append(f"'{nm}' is already used (P1-P4 / added products) or reserved - choose a different name.")
    g = _feed_getter(feed_df)
    pay, inst = g("New Capex Payment (Rs Lacs)")[0:12], g("New Capex Installation Cost (Rs Lacs)")[0:12]
    q, r = g("Sale Qt Projection (Kg)")[0:12], g("Selling Rate (Rs/Kg)")[0:12]
    has, _last, _comp, start, tw = _np_timing(pay, inst, sc, False)
    if tw: warns.append(tw)
    if any(v < 0 for v in q + r + pay + inst): errs.append("Negative figures are not allowed in the feed table.")
    if sum(q[start:]) <= 0: errs.append(f"No Sale Qt from the start month ({months[start]}) onwards - key in the monthly Sale Qt Projection.")
    else:
        if any(q[i] > 0 and r[i] <= 0 for i in range(start, 12)): warns.append("Some months have Sale Qt but no Selling Rate - they will show nil revenue.")
        if q[11] <= 0: warns.append("M12 Sale Qt is blank / nil - Year 2-5 sales are projected from the M12 run rate, so they will be nil.")
    if sum(q[:start]) > 0: warns.append(f"Sale Qt keyed before the start month ({months[start]}) is ignored.")
    if start > 0 and (_nz(sc.get("op_fg")) or 0) > 0: errs.append(f"Opening FG Stock must be blank / nil when sale starts only in {months[start]} - a product that is not yet launched has no stock (it would give negative production).")
    if has and (_nz(sc.get("tl_pct")) or 0) > 0:
        if (_nz(sc.get("tl_life")) or 0) <= 0: errs.append("Key in the TL Repayment Period (months) - TL sanction is above nil.")
        if (_nz(sc.get("tl_rate")) or 0) <= 0: warns.append("TL interest rate is blank - TL interest will be nil.")
    rows = _ap_rm_rows(rm_df)
    for _, rr in rm_df.iterrows():
        _nm = rr[AP_RM_COLS[0]]
        if (_nm is None or pd.isna(_nm) or str(_nm).strip() == "") and any(not pd.isna(rr[c]) for c in AP_RM_COLS[1:]):
            errs.append("An RM row has figures but no RM name."); break
    if not rows: errs.append("Key in at least one raw material (RM name and consumption ratio).")
    else:
        if len({x["name"].lower() for x in rows}) != len(rows): errs.append("An RM name is repeated within this product - use one row per RM.")
        if any(min(x["con"], x["vloss"], x["iloss"], x["price"], x["hold"], x["adv"], x["credit"], x["opstock"], x["opcred"]) < 0 for x in rows): errs.append("Negative figures are not allowed in the RM feed.")
        if any(x["vloss"] + x["iloss"] >= 100 for x in rows): errs.append("Normal Loss + Invisible Loss must be below 100% for every RM.")
        tot = sum(x["con"] for x in rows)
        if abs(tot - 100.0) > 0.5: warns.append(f"RM consumption ratios total {tot:g}% (normally 100%).")
        known = {x.lower(): x for x in _rm_universe()}
        _sh = [known[x["name"].lower()] for x in rows if x["name"].lower() in known]
        if _sh: warns.append("Shared with existing RM(s) : " + ", ".join(_sh) + " - existing price, stock and credit terms are used.")
    for _lbl, _d, _rc in (("Direct Expenses", dx_df, AP_DX_RATE), ("Indirect Expenses", ix_df, IX_RATE_COL)):
        if (pd.to_numeric(_d[[_rc] + AP_INFL].stack(), errors="coerce") < 0).any(): errs.append(f"Negative figures are not allowed in the {_lbl} feed.")
        _br = [h for h, v in zip(_d["Expense Head"], _d[_rc]) if pd.isna(v)]
        _bi = [h for h, row in zip(_d["Expense Head"], _d[AP_INFL].isna().any(axis=1)) if row]
        if _br: warns.append(f"{_lbl} rate blank for : {', '.join(_br)} - treated as nil.")
        if _bi: warns.append(f"{_lbl} inflation blank (Year 2-5) for : {', '.join(_bi)} - treated as 0%.")
    return errs, warns

def _ap_remove(uid):
    lst = st.session_state.added_products
    for c in list(lst):
        if c["uid"] == uid:
            lst.remove(c)
            for _k in ("slicer_rev", "slicer_fg", "slicer_rmqt", "slicer_rmval", "slicer_dx", "slicer_ix", "slicer_cost", "slicer_pl"):
                if st.session_state.get(_k) == c["name"]: st.session_state[_k] = "All"       # a slicer must not point at a removed product
            d = st.session_state.sidebar_dx_rate_df
            if c["name"] in d.columns: st.session_state.sidebar_dx_rate_df = d.drop(columns=[c["name"]])
            st.session_state.ap_flash = [("info", f"Product {c['name']} removed from the model.")]

with st.sidebar:
    # top line: Spread (top-right) when squeezed, Squeeze (top-left) when spread; heading sits below it
    _ap_open = (st.session_state.get("synchronized_sidebar_context_radio_widget") == "Add Product")
    st.button("❮  Squeeze" if st.session_state.cockpit_wide else "Spread  ❯", on_click=_toggle_cockpit, key="cockpit_toggle_top",
              help=("Click to squeeze the cockpit back" if st.session_state.cockpit_wide else "Click to spread the cockpit so the feed tables are fully visible"))
    st.header("⚙️ Cockpit Feed")
    st.caption("🔴 = key-in column  |  heading without 🔴 = fixed, not editable")
    sidebar_context = st.radio(
        "Cockpit Feed",
        options=["Sales / FG Feed", "RM Qt Feed", "RM Val Feed", "Direct Expenses Feed", "Indirect Expenses Feed", "WC Feed",
                 "P4 / New Capex Feed", "FAR Feed", "TL Feed", "Add Product"],
        key="synchronized_sidebar_context_radio_widget",
        on_change=_on_ctx_change,
        label_visibility="collapsed"
    )
    st.markdown("---")
    _p4_cockpit_auto = False
    _ap_cockpit_auto = False
    COCKPIT_WIDE = st.session_state.cockpit_wide
    if COCKPIT_WIDE: st.markdown(WIDE_CSS, unsafe_allow_html=True)

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
    wc_od_limit = st.session_state.wc_limit_saved
    edited_wc_flow_df, edited_wc_bal_df = st.session_state.sidebar_wc_flow_df, st.session_state.sidebar_wc_bal_df
    # All other feeds default to their saved values; the desk that is open below overwrites its own ones
    edited_qty_df, edited_rate_df, edited_fg_inflation_df, edited_prod_params_df = st.session_state.sidebar_qty_df, st.session_state.sidebar_rate_df, st.session_state.sidebar_fg_inflation_df, st.session_state.sidebar_prod_params_df
    edited_bom_df, edited_rm_logistics_df, edited_rm_price_df, edited_rm_inflation_df = st.session_state.sidebar_bom_df, st.session_state.sidebar_rm_logistics_df, st.session_state.sidebar_rm_price_df, st.session_state.sidebar_rm_inflation_df
    g_y2, g_y3, g_y4, g_y5 = [x / 100.0 for x in st.session_state.growth_saved]
    # P4 / FAR / TL feeds (new)
    edited_p4_df, edited_p4_rm_df, p4s = st.session_state.sidebar_p4_df, st.session_state.sidebar_p4_rm_df, dict(st.session_state.p4_scalars)
    edited_far_open_df, edited_far_add_df = st.session_state.sidebar_far_open_df, st.session_state.sidebar_far_add_df
    edited_tl_df, bank_chg_pct = st.session_state.sidebar_tl_df, st.session_state.bank_chg_saved

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
        st.caption("Rate per unit of production (Rs) - applied to Production Qt. Added products have their own Direct Expenses feed inside the Add Product desk (not here).")
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
        st.caption("Initial rate - Rs per Kg sold (p.u.) or % of Sale Value, as per 'Against Sale'. Same rate for all products (P1-P4 and added products)")
        edited_ix_df = sb_editor(st.session_state.sidebar_ix_df, hide_index=True, column_config={"Expense Head": st.column_config.TextColumn(disabled=True), "Against Sale": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_ix_df = edited_ix_df
        st.caption("YoY inflation (%) on rate / % - Year 2 to Year 5")
        edited_ix_infl_df = sb_editor(st.session_state.sidebar_ix_infl_df, hide_index=True, column_config={"Expense Head": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_ix_infl_df = edited_ix_infl_df
        edited_qty_df, edited_rate_df, edited_fg_inflation_df, edited_prod_params_df, edited_bom_df, edited_rm_logistics_df, edited_rm_price_df, edited_rm_inflation_df = st.session_state.sidebar_qty_df, st.session_state.sidebar_rate_df, st.session_state.sidebar_fg_inflation_df, st.session_state.sidebar_prod_params_df, st.session_state.sidebar_bom_df, st.session_state.sidebar_rm_logistics_df, st.session_state.sidebar_rm_price_df, st.session_state.sidebar_rm_inflation_df
        g_y2, g_y3, g_y4, g_y5 = [x / 100.0 for x in st.session_state.growth_saved]
    elif sidebar_context == "WC Feed":
        st.header("🏦 6. WC Feed Desk")
        wc_cash_open = st.number_input("Opening Bank / Cash Balance (Rs Lacs)", value=st.session_state.wc_cash_saved)
        st.session_state.wc_cash_saved = wc_cash_open
        wc_roi = st.number_input("Rate of Interest on Working Capital (% p.a.)", value=st.session_state.wc_roi_saved)
        st.session_state.wc_roi_saved = wc_roi
        wc_od_open = st.number_input("Opening Bank OD / CC Balance (Rs Lacs)", value=st.session_state.wc_od_saved)
        st.session_state.wc_od_saved = wc_od_open
        wc_od_limit = st.number_input("OD / CC Sanction Limit (Rs Lacs)", value=float(st.session_state.wc_limit_saved))
        st.session_state.wc_limit_saved = wc_od_limit
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
    elif sidebar_context == "P4 / New Capex Feed":
        st.header("🆕 7. P4 / New Capex Feed Desk")
        feed_title("P4 : Cockpit Feed & Default Figures - M1 to M12 and Year 2-5")
        st.caption("Sale Qt before the start month is ignored. Year 2 Sale = M12 Sale x 12 x (1 + Year 2 growth). "
                   "Year 2-5 Selling Rate = M12 rate compounded by the yearly inflation. Capex payment / installation cost: M1-M12 only.")
        edited_p4_df = sb_editor(st.session_state.sidebar_p4_df, hide_index=True, column_config={"P4 Assumption": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_p4_df = edited_p4_df
        _ps = st.session_state.p4_scalars
        _ps["completion"] = st.selectbox("Capex Installation & Commercial Run (completion month)", ["Auto"] + months[:11],
                                         index=(["Auto"] + months[:11]).index(_ps["completion"]) if _ps["completion"] in ["Auto"] + months[:11] else 0,
                                         help="Auto = month after the last capex payment. Capitalisation, production and sale start the month after completion.")
        _ps["tl_pct"] = st.number_input("TL Sanction & Disbursement (% of capex payment)", value=float(_ps["tl_pct"]))
        _ps["op_fg"] = st.number_input("P4 Opening FG Stock Qt (M1)", value=float(_ps["op_fg"]))
        _ps["op_dbt"] = st.number_input("P4 Opening Debtors (Rs Lacs)", value=float(_ps["op_dbt"]))
        _ps["dbt_days"] = st.number_input("P4 Credit Days : Debtors", value=float(_ps["dbt_days"]))
        _ps["adv_pct"] = st.number_input("Advance to Supplier (%) - RM13-RM15", value=float(_ps["adv_pct"]))
        _ps["crd_days"] = st.number_input("Credit Days : Creditors net of Advance - RM13-RM15", value=float(_ps["crd_days"]))
        p4s = dict(_ps)
        feed_title("P4 Raw Materials (RM13-RM15) - Price, Days Hold, M1 Opening Stock, Opening Creditors")
        edited_p4_rm_df = sb_editor(st.session_state.sidebar_p4_rm_df, hide_index=True, column_config={"Raw Material": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_p4_rm_df = edited_p4_rm_df
        _p4_cockpit_auto = True                       # the Auto table (TL disbursement / own contribution) is drawn after the calculation below
    elif sidebar_context == "FAR Feed":
        st.header("🏗️ 8. FAR Feed Desk")
        feed_title("Opening Asset Feed - Gross Block, Gross Dep (Rs Lacs) and Rate of Dep (% p.a.)")
        st.caption("Opening WDV = Gross Block - Gross Dep. Depreciation is charged on closing gross block, never below nil WDV.")
        edited_far_open_df = sb_editor(st.session_state.sidebar_far_open_df, hide_index=True, column_config={"Asset": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_far_open_df = edited_far_open_df
        feed_title("Asset Addition (Rs Lacs) - M1 to M12 and Year 2-5")
        st.caption("Plant & Machinery (New Capex Project) is added automatically: capex + installation + interest during construction, in the start month.")
        edited_far_add_df = sb_editor(st.session_state.sidebar_far_add_df, hide_index=True, column_config={"Asset Addition (Rs Lacs)": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_far_add_df = edited_far_add_df
    elif sidebar_context == "TL Feed":
        st.header("🏦 9. TL Feed Desk")
        feed_title("Term Loans - Opening O/s (M1), Interest Rate and Life Left")
        st.caption("Life left = months from M1 (TL1-TL3) or from the start of repayment (TL New, repaid from the start month after completion). "
                   "TL New disbursement is automatic (P4 / New Capex Feed). Loans for added products (TL New - <product>) are fed in the Add Product desk.")
        edited_tl_df = sb_editor(st.session_state.sidebar_tl_df, hide_index=True, column_config={"Term Loan": st.column_config.TextColumn(disabled=True)})
        st.session_state.sidebar_tl_df = edited_tl_df
        bank_chg_pct = st.number_input("Rate of Bank Charges (% per month, on month-end O/s of WC borrowing and TL)", value=float(st.session_state.bank_chg_saved), format="%.3f")
        st.session_state.bank_chg_saved = bank_chg_pct
    elif sidebar_context == "Add Product":
        st.header("➕ 10. Add Product Desk")
        st.caption("Key in the feeds of a new product (every box starts empty) and click Add. The whole model - all pages and every Product slicer - then includes the product. "
                   "You can add as many products as you need, one after the other. Sales, RM, debtors / creditors, capex and TL follow the same logic as P4; direct and indirect expenses are fed separately for the new product; finance cost, working capital and depreciation are shared as per COGS unless an asset is exclusive to the product.")
        for _kind, _msg in st.session_state.get("ap_flash", []):
            {"success": st.success, "warning": st.warning, "info": st.info}.get(_kind, st.info)(_msg)
        st.session_state.ap_flash = []
        _ver = st.session_state.ap_form_ver
        if f"ap_blank_{_ver}" not in st.session_state:
            st.session_state[f"ap_blank_{_ver}"] = (_ap_blank_feed(), dict(AP_SC_DEFAULT), _ap_blank_rm(), _ap_blank_dx(), _ap_blank_ix())
        _b_feed, _b_sc, _b_rm, _b_dx, _b_ix = st.session_state[f"ap_blank_{_ver}"]
        with st.container(border=True):
            _ap_name = st.text_input("Name of the New Product (e.g. A1)", value="", max_chars=15, key=f"ap_name_{_ver}")
            _f_feed, _f_sc, _f_rm, _f_dx, _f_ix = _ap_inputs(_b_feed, _b_sc, _b_rm, f"ap{_ver}", _b_dx, _b_ix)
            _ap_go = st.button("➕  Add Product to the Model", key=f"ap_go_{_ver}")
        if _ap_go:
            _errs, _warns = _ap_validate(_ap_name, _f_feed, _f_sc, _f_rm, _f_dx, _f_ix)
            if _errs:
                for _e in _errs: st.error(_e)
                for _w in _warns: st.warning(_w)
            else:
                _known = {x.lower(): x for x in _rm_universe()}
                _rmc = _f_rm[_f_rm[AP_RM_COLS[0]].notna() & (_f_rm[AP_RM_COLS[0]].astype(str).str.strip() != "")].copy().reset_index(drop=True)
                _rmc[AP_RM_COLS[0]] = [_known.get(str(x).strip().lower(), str(x).strip()) for x in _rmc[AP_RM_COLS[0]]]      # same RM spelling as the model
                _nm = _ap_name.strip()
                st.session_state.ap_uid += 1
                st.session_state.added_products.append({"uid": st.session_state.ap_uid, "name": _nm, "feed_df": _f_feed.reset_index(drop=True), "sc": dict(_f_sc), "rm_df": _rmc,
                                                         "dx_df": _f_dx.reset_index(drop=True), "ix_df": _f_ix.reset_index(drop=True)})
                st.session_state.ap_form_ver = _ver + 1                 # fresh empty form
                st.session_state.ap_flash = [("success", f"Product {_nm} added - it is now in every page and in every Product slicer.")] + [("warning", w) for w in _warns]
                st.rerun()
        if added_products:
            feed_title("Products already added - open to change the feeds, or remove the product")
            for _c in list(added_products):
                with st.expander(f"✏️ {_c['name']}"):
                    _kp = f"apx{_c['uid']}"
                    _c["feed_df"], _c["sc"], _c["rm_df"], _c["dx_df"], _c["ix_df"] = _ap_inputs(_c["feed_df"], _c["sc"], _c["rm_df"], _kp, _c["dx_df"], _c["ix_df"])
                    st.caption("All feeds of this product (sales, RM, capex, direct and indirect expenses) are edited here.")
                    st.button(f"🗑 Remove {_c['name']} from the model", key=f"{_kp}_del", on_click=_ap_remove, args=(_c["uid"],))
        _ap_cockpit_auto = True                       # the timing / funding summary is drawn after the calculation below
    # bottom-left Squeeze / Spread button (same action as the top one)
    st.markdown("---")
    st.button("❮  Squeeze" if st.session_state.cockpit_wide else "Spread  ❯", on_click=_toggle_cockpit, key="cockpit_toggle_bottom",
              help=("Click to squeeze the cockpit back" if st.session_state.cockpit_wide else "Click to spread the cockpit so the feed tables are fully visible"))
# -----------------------------------------------------------------------------
# CHAPTER 3: ANALYTICAL COMPUTATION LAYER
# -----------------------------------------------------------------------------
qty_matrix, rate_matrix, rev_matrix = {}, {}, {}

prod_sales_matrix, fg_cl_matrix, fg_op_matrix, fg_prod_matrix = {}, {}, {}, {}


# ---- RM13-RM15 (P4) and the RMs of every product added in the Add Product desk join the RM feed tables used by the calculations ----
raw_materials = _rm_universe()                                  # RM1-RM15 + RMs introduced by added products (a name already in the model, e.g. RM1, is shared)
rm_added = [r for r in raw_materials if r not in rm_base + p4_rms]
edited_rm_logistics_df = pd.concat([edited_rm_logistics_df[edited_rm_logistics_df["Raw Material"].isin(rm_base)],
                                    edited_p4_rm_df[["Raw Material", "M1 Initial Op Stock Qty", "Days Hold"]]], ignore_index=True)
edited_rm_price_df = pd.concat([edited_rm_price_df[edited_rm_price_df["Raw Material"].isin(rm_base)],
                                edited_p4_rm_df[["Raw Material", "Initial Price"]]], ignore_index=True)
edited_op_cred_df = pd.concat([edited_op_cred_df[edited_op_cred_df["Raw Material"].isin(rm_base)],
                               edited_p4_rm_df[["Raw Material", "Opening Creditors (Rs Lacs)"]]], ignore_index=True)
# RMs / BOM rows of the added products (feeds keyed in the Add Product desk)
rm_new_info, bom_add_rows = {}, []
for _c in added_products:
    for _r in _ap_rm_rows(_c["rm_df"]):
        bom_add_rows.append({"RM Name": _r["name"], "Target FG": _c["name"], "Con%": _r["con"] / 100.0,
                             "Visible Loss": _r["vloss"] / 100.0, "Invisible Loss": _r["iloss"] / 100.0})
        if _r["name"] in rm_added and _r["name"] not in rm_new_info: rm_new_info[_r["name"]] = _r       # first definition of a new RM is used
if rm_new_info:
    _nr = list(rm_new_info.values())
    edited_rm_logistics_df = pd.concat([edited_rm_logistics_df, pd.DataFrame({"Raw Material": [r["name"] for r in _nr],
        "M1 Initial Op Stock Qty": [r["opstock"] for r in _nr], "Days Hold": [r["hold"] for r in _nr]})], ignore_index=True)
    edited_rm_price_df = pd.concat([edited_rm_price_df, pd.DataFrame({"Raw Material": [r["name"] for r in _nr], "Initial Price": [r["price"] for r in _nr]})], ignore_index=True)
    edited_op_cred_df = pd.concat([edited_op_cred_df, pd.DataFrame({"Raw Material": [r["name"] for r in _nr], "Opening Creditors (Rs Lacs)": [r["opcred"] for r in _nr]})], ignore_index=True)
if bom_add_rows:
    edited_bom_df = pd.concat([edited_bom_df, pd.DataFrame(bom_add_rows)], ignore_index=True)
edited_dx_rate_df = edited_dx_rate_df.copy()                    # direct expense rates : every product needs a column
for _p in products:
    if _p not in edited_dx_rate_df.columns: edited_dx_rate_df[_p] = 0.0

# ---- New-capex products : P4 (P4 / New Capex Feed desk) + every product added in the Add Product desk ----
# Each one has its own timing (completion month, start of capitalisation / production / sale), capex funding, FG / debtors / RM feeds.
_added_by_name = {c["name"]: c for c in added_products}
NPD = {}
for _p in new_prods:
    _grow = _feed_getter(edited_p4_df if _p == "P4" else _added_by_name[_p]["feed_df"])
    _sc = p4s if _p == "P4" else _added_by_name[_p]["sc"]
    _pay, _inst = _grow("New Capex Payment (Rs Lacs)")[0:12], _grow("New Capex Installation Cost (Rs Lacs)")[0:12]
    _has, _last, _comp, _start, _warn = _np_timing(_pay, _inst, _sc, _p == "P4")
    _frac = min(max(safe_float(_sc.get("tl_pct", 85.0 if _p == "P4" else 0.0)), 0.0), 100.0) / 100.0
    _disb = [(_pay[i] + _inst[i]) * _frac for i in range(12)]                                      # TL disbursement (Auto)
    NPD[_p] = {"row": _grow, "sc": _sc, "comp": _comp, "start": _start, "warn": _warn, "capex_total": sum(_pay) + sum(_inst),
               "tl_frac": _frac, "tl_disb": _disb, "own": [(_pay[i] + _inst[i]) - _disb[i] for i in range(12)]}   # own = capex margin & own cash contribution (Auto)
p4_row = NPD["P4"]["row"]
p4_completion, p4_start, p4_completion_warn = NPD["P4"]["comp"], NPD["P4"]["start"], NPD["P4"]["warn"]
p4_capex_total, p4_tl_disb, p4_own = NPD["P4"]["capex_total"], NPD["P4"]["tl_disb"], NPD["P4"]["own"]

# debtors : credit days and opening debtors of every new-capex product join the debtors feed
edited_debtor_df = edited_debtor_df.copy()
for _p in NPD:
    edited_debtor_df[_p] = [safe_float(NPD[_p]["sc"].get("dbt_days", 30.0 if _p == "P4" else 0.0)) if r == "Days Credit" else safe_float(NPD[_p]["sc"].get("op_dbt", 0.0))
                            for r in edited_debtor_df["Parameters"]]

for p in products:
    if p in NPD:
        # new-capex products come from their own feed: monthly sale from the start month only, own growth, M12 run rate as the Year 2 base
        _d = NPD[p]
        q_months = [v if i >= _d["start"] else 0.0 for i, v in enumerate(_d["row"]("Sale Qt Projection (Kg)")[0:12])]
        r_months = _d["row"]("Selling Rate (Rs/Kg)")[0:12]
        v_months = [q * r for q, r in zip(q_months, r_months)]
        _g = [v / 100.0 for v in _d["row"]("Growth % : Sale")[12:16]]
        _inf = [v / 100.0 for v in _d["row"]("Selling Rate Inflation %")[12:16]]
        y1_q_total, y1_v_total = sum(q_months), sum(v_months)
        y_q, y_r, _q, _r = [], [], q_months[11] * 12.0, r_months[11]
        for k in range(4):
            _q, _r = _q * (1 + _g[k]), _r * (1 + _inf[k])
            y_q.append(_q); y_r.append(_r)
        qty_matrix[p] = q_months + [y1_q_total] + y_q
        rate_matrix[p] = r_months + [(y1_v_total / y1_q_total) if y1_q_total > 0 else 0.0] + y_r
        rev_matrix[p] = v_months + [y1_v_total] + [a * b for a, b in zip(y_q, y_r)]
        m1_op_input = safe_float(_d["sc"].get("op_fg", 0.0))
        _hd = _d["row"]("FG Inventory Hold Days")
        hold = _hd[0:12] + [0.0] + _hd[12:16]                                    # per period (M1-M12, -, Year 2-5)
    else:
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
        hold = [hold_days] * 17
    
    p_sales = qty_matrix[p]
    p_op, p_cl, p_prod = [0.0] * 17, [0.0] * 17, [0.0] * 17
    for idx in range(12): p_cl[idx] = (hold[idx] / 30.0) * p_sales[idx]
    
    # Secure arrays from assignment type breaks
    p_op_list = [0.0] * 17
    p_op_list[0] = m1_op_input
    for idx in range(1, 12): p_op_list[idx] = p_cl[idx - 1]
    for idx in range(12): p_prod[idx] = p_sales[idx] + p_cl[idx] - p_op_list[idx]
    p_op_list[12], p_cl[12], p_prod[12] = p_op_list[0], p_cl[11], sum(p_prod[0:12])
    
    horizon_map, prev_map = {"Year 2": 13, "Year 3": 14, "Year 4": 15, "Year 5": 16}, {"Year 2": 12, "Year 3": 13, "Year 4": 14, "Year 5": 15}
    for yr, idx in horizon_map.items():
        p_op_list[idx] = p_cl[prev_map[yr]]
        p_cl[idx] = (hold[idx] / 30.0) * (p_sales[idx] / 12.0)
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
_added_dx = {c["name"]: c["dx_df"] for c in added_products}      # added products : their own direct expense feed (nothing shared with P1-P4)
_added_ix = {c["name"]: c["ix_df"] for c in added_products}
def _own(df, head, col):
    r = df.loc[df["Expense Head"] == head, col]
    return safe_float(r.values) if len(r) else 0.0
for h in direct_heads:
    infl0 = [safe_float(edited_dx_infl_df.loc[edited_dx_infl_df["Expense Head"] == h, f"Year {y} (%)"].values) / 100.0 for y in (2, 3, 4, 5)]
    for p in products:
        infl = infl0
        if p in _added_dx:
            base = _own(_added_dx[p], h, AP_DX_RATE)
            infl = [_own(_added_dx[p], h, f"Year {y} (%)") / 100.0 for y in (2, 3, 4, 5)]
        elif h in dx_common_heads:
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
df_scrap_final.insert(0, "Scrap (Qt)", [f"Scrap {p} (S{p})" for p in products])
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
    base0 = safe_float(ix_row[IX_RATE_COL].values)
    infl0 = [safe_float(edited_ix_infl_df.loc[edited_ix_infl_df["Expense Head"] == h, f"Year {y} (%)"].values) / 100.0 for y in (2, 3, 4, 5)]
    for p in products:
        base, infl = base0, infl0
        if p in _added_ix:                                    # added product : its own rate / % and inflation
            base = _own(_added_ix[p], h, IX_RATE_COL)
            infl = [_own(_added_ix[p], h, f"Year {y} (%)") / 100.0 for y in (2, 3, 4, 5)]
        yr_rates, running = [], base
        for k in range(4):
            running = running * (1.0 + infl[k])
            yr_rates.append(running)
        if p == products[0]: ix_rate[h] = [base0] * 13 + yr_rates
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
    gdf(sty, width="stretch", hide_index=True, height=min(35 * (len(df) + 1) + 3, 1300))

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
_adv_frac_p4 = min(max(safe_float(p4s.get("adv_pct", 10.0)), 0.0), 100.0) / 100.0        # RM13-RM15 (P4) have their own advance % and credit days
crd_adv_frac = {rm: (_adv_frac_p4 if rm in p4_rms else _adv_frac) for rm in raw_materials}
crd_days_rm = {rm: (safe_float(p4s.get("crd_days", 35.0)) if rm in p4_rms else safe_float(rm_credit_days)) for rm in raw_materials}
for _rm, _r in rm_new_info.items():              # RMs of added products carry their own advance % and credit days
    crd_adv_frac[_rm] = min(max(_r["adv"], 0.0), 100.0) / 100.0
    crd_days_rm[_rm] = _r["credit"]
crd_adv = {rm: [v * crd_adv_frac[rm] for v in crd_gross[rm]] for rm in raw_materials}                       # Advance paid at order = Adv % x Gross Due
crd_due = {rm: [g - a for g, a in zip(crd_gross[rm], crd_adv[rm])] for rm in raw_materials}                  # Net Due to Suppliers = Gross Due - Advance (credit days apply on this)
crd_open = {rm: safe_float(edited_op_cred_df.loc[edited_op_cred_df["Raw Material"] == rm, "Opening Creditors (Rs Lacs)"].values) for rm in raw_materials}
crd = {rm: credit_schedule(crd_due[rm], crd_days_rm[rm], crd_open[rm]) for rm in raw_materials}
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

# ---- NEW: TERM LOANS (TL page) : run month by month for 60 months (M1-M60), then rolled up to M1-M12, Year 1-5 (Rs lacs) ----
# Repayment = equal principal : opening O/s / months of life remaining (so each loan is fully repaid at the end of its life).
# TL1-TL3 repay from M1 ; TL New is interest-only until completion and repays from the start month (after completion) over its life.
# Interest = opening O/s x rate / 12. Bank charges = month-end (closing) O/s x rate of bank charges (% per month).
# Interest on TL New up to the completion month = interest during construction : capitalised into the new Plant & Machinery, not charged to PL.
_bc_rate = safe_float(bank_chg_pct) / 100.0                                  # per month
# Loans of the new-capex products : "TL New" = P4 ; "TL New - <product>" = every added product that has capex and a TL share
tl_prod = {"TL New": "P4"}
_tl_extra = []
for _p in added_names:
    _d = NPD[_p]
    if _d["capex_total"] > 0 and _d["tl_frac"] > 0:
        tl_prod[f"TL New - {_p}"] = _p
        _tl_extra.append({"Term Loan": f"TL New - {_p}", "Opening O/s M1 (Rs Lacs)": 0.0,
                          "Interest Rate (% p.a.)": safe_float(_d["sc"].get("tl_rate")), "Life Left (Months)": safe_float(_d["sc"].get("tl_life"))})
tl_names = ["TL1", "TL2", "TL3"] + list(tl_prod)
_tl_all = pd.concat([edited_tl_df, pd.DataFrame(_tl_extra)], ignore_index=True) if _tl_extra else edited_tl_df
_tlf = _tl_all.set_index("Term Loan")
def _tl_feed(n, c): return safe_float(_tlf.at[n, c]) if (n in _tlf.index and c in _tlf.columns) else 0.0
TLH = 60
tl_m = {}
for n in tl_names:
    disb = [0.0] * TLH
    if n in tl_prod: disb[0:12] = NPD[tl_prod[n]]["tl_disb"]
    rate, life = _tl_feed(n, "Interest Rate (% p.a.)") / 100.0, int(round(_tl_feed(n, "Life Left (Months)")))
    rep_start = NPD[tl_prod[n]]["start"] if n in tl_prod else 0
    bal = _tl_feed(n, "Opening O/s M1 (Rs Lacs)")
    rec = {k: [0.0] * TLH for k in ("op", "disb", "rep", "int", "cl", "bc")}
    for m in range(TLH):
        op = bal
        intr = op * rate / 12.0
        rep = 0.0
        if m >= rep_start and op > 0:
            remaining = life - (m - rep_start)
            rep = op / remaining if remaining > 0 else op
        rep = min(rep, op)
        cl = op + disb[m] - rep
        rec["op"][m], rec["disb"][m], rec["rep"][m], rec["int"][m], rec["cl"][m], rec["bc"][m] = op, disb[m], rep, intr, cl, cl * _bc_rate
        bal = cl
    tl_m[n] = rec

def _roll(series, kind):
    """60 monthly values -> 17 columns. flow : Year = sum of its 12 months ; op : Year = first month ; cl : Year = last month."""
    out = series[0:12]
    for y in range(5):
        blk = series[12 * y: 12 * y + 12]
        out = out + [sum(blk) if kind == "flow" else (blk[0] if kind == "op" else blk[-1])]
    return out[0:12] + [out[12]] + out[13:17]
tl = {n: {"op": _roll(tl_m[n]["op"], "op"), "disb": _roll(tl_m[n]["disb"], "flow"), "rep": _roll(tl_m[n]["rep"], "flow"),
          "int": _roll(tl_m[n]["int"], "flow"), "cl": _roll(tl_m[n]["cl"], "cl"), "bc": _roll(tl_m[n]["bc"], "flow")} for n in tl_names}
for n in tl_names: tl[n]["inst"] = [a + b for a, b in zip(tl[n]["rep"], tl[n]["int"])]          # TL instalment (repay + interest) = cash outflow
_idc_by = {}                                                                  # interest during construction (capitalised), by product
for _n, _p in tl_prod.items():
    _m = [tl_m[_n]["int"][m] if m <= NPD[_p]["comp"] else 0.0 for m in range(TLH)]
    _idc_by[_p] = {"series": _roll(_m, "flow"), "total": sum(_m)}
tl_idc_series = [sum(_idc_by[p]["series"][i] for p in _idc_by) for i in range(17)]
tl_idc = sum(_idc_by[p]["total"] for p in _idc_by)
tl_int_pl = {n: ([a - b for a, b in zip(tl[n]["int"], _idc_by[tl_prod[n]]["series"])] if n in tl_prod else tl[n]["int"]) for n in tl_names}   # charged to PL
tl_int_tot = [sum(tl[n]["int"][i] for n in tl_names) for i in range(17)]
tl_bc_tot = [sum(tl[n]["bc"][i] for n in tl_names) for i in range(17)]

def tl_tables():
    """The TL page tables: (heading, dataframe) - one row per loan plus Total, as in the TL sheet."""
    out = []
    for head, key in (("1. Opening O/s", "op"), ("2. Disbursement", "disb"), ("3. Repayment", "rep"), ("4. TL Interest", "int"),
                      ("5. Bank Charges on TL", "bc"), ("6. TL Closing O/s", "cl"), ("7. TL Total Instalment (Repay + Int) : Cash Outflow", "inst")):
        d = compile_report({n: tl[n][key] for n in tl_names}, "Term Loan")
        if key == "int":
            memo = [{"Term Loan": "of which : Interest during Construction (TL New, capitalised)", **dict(zip(display_columns, tl_idc_series))},
                    {"Term Loan": "Interest on TL charged to PL", **dict(zip(display_columns, [sum(tl_int_pl[n][i] for n in tl_names) for i in range(17)]))}]
            d = pd.concat([d, pd.DataFrame(memo)], ignore_index=True)
        out.append((head, d))
    return out

# ---- NEW: FIXED ASSET REGISTER (FAR page) (Rs lacs) ----
# Closing gross = opening + addition ; depreciation (straight line) = closing gross x rate / 12 per month (a full month in the month of addition),
# Year 2-5 = closing gross x rate ; Year 1 = sum of months ; depreciation stops once WDV reaches nil.
# Plant & Machinery is shown as one row; the new capex project (P4) is run as its own ledger so that its depreciation can be charged to P4.
_fo = edited_far_open_df.set_index("Asset")
_fa = edited_far_add_df.set_index("Asset Addition (Rs Lacs)")
def _far_feed(a, c): return safe_float(_fo.at[a, c]) if (a in _fo.index and c in _fo.columns) else 0.0
def _add_series(row):
    v = [safe_float(_fa.at[row, c]) if (row in _fa.index and c in _fa.columns) else 0.0 for c in p4_cols]
    return v[0:12] + [sum(v[0:12])] + v[12:16]
asset_val = {p: NPD[p]["capex_total"] + (_idc_by[p]["total"] if p in _idc_by else 0.0) for p in NPD}      # new P&M capitalised = capex + installation + interest during construction
_new_add = {}
for _p in NPD:
    _new_add[_p] = [0.0] * 17
    _new_add[_p][NPD[_p]["start"]] = asset_val[_p]
    _new_add[_p][12] = asset_val[_p]
p4_asset_value, p4_idc = asset_val["P4"], _idc_by["P4"]["total"]

def _ledger(g0, a0, rate, add):
    r = {k: [0.0] * 17 for k in ("op_g", "add", "cl_g", "op_a", "dep", "cl_a")}
    g, a = g0, a0
    for t in range(12):
        r["op_g"][t], r["op_a"][t], r["add"][t] = g, a, add[t]
        cg = g + add[t]
        dep = max(0.0, min(cg * rate / 12.0, cg - a))
        r["cl_g"][t], r["dep"][t], r["cl_a"][t] = cg, dep, a + dep
        g, a = cg, a + dep
    r["op_g"][12], r["op_a"][12], r["add"][12] = g0, a0, sum(add[0:12])
    r["cl_g"][12], r["dep"][12], r["cl_a"][12] = r["cl_g"][11], sum(r["dep"][0:12]), r["cl_a"][11]
    g, a = r["cl_g"][11], r["cl_a"][11]
    for t in range(13, 17):
        r["op_g"][t], r["op_a"][t], r["add"][t] = g, a, add[t]
        cg = g + add[t]
        dep = max(0.0, min(cg * rate, cg - a))
        r["cl_g"][t], r["dep"][t], r["cl_a"][t] = cg, dep, a + dep
        g, a = cg, a + dep
    r["op_w"] = [x - y for x, y in zip(r["op_g"], r["op_a"])]
    r["cl_w"] = [x - y for x, y in zip(r["cl_g"], r["cl_a"])]
    return r

far = {}
for a in asset_classes:
    rate = _far_feed(a, "Rate of Dep (%)") / 100.0
    add = _add_series("Plant & Machinery (Regular)" if a == "Plant & Machinery" else a)
    far[a] = _ledger(_far_feed(a, "Gross Block (Rs Lacs)"), _far_feed(a, "Gross Dep (Rs Lacs)"), rate, add)
_pm_rate = _far_feed("Plant & Machinery", "Rate of Dep (%)") / 100.0
far_new_p = {p: _ledger(0.0, 0.0, _pm_rate, _new_add[p]) for p in NPD}            # P&M (New Capex Project) : one ledger per new-capex product (P4 + added products)
far_new = {k: [sum(far_new_p[p][k][i] for p in NPD) for i in range(17)] for k in far_new_p["P4"]}
far_show = {a: ({k: [x + y for x, y in zip(far[a][k], far_new[k])] for k in far[a]} if a == "Plant & Machinery" else far[a]) for a in asset_classes}
dep_total = [sum(far_show[a]["dep"][i] for a in asset_classes) for i in range(17)]
dep_new_p = {p: far_new_p[p]["dep"] for p in NPD}                                  # each charged to its own product only
dep_new = far_new["dep"]
dep_other = [a - b for a, b in zip(dep_total, dep_new)]                         # shared by all products on COGS

def far_tables():
    out = []
    for head, key in (("1. Opening Gross Block", "op_g"), ("2. Addition", "add"), ("3. Closing Gross Block", "cl_g"),
                      ("4. Depreciation : Opening (Accumulated)", "op_a"), ("5. Depreciation : Current", "dep"),
                      ("6. Depreciation : Closing (Accumulated)", "cl_a"), ("7. Opening WDV", "op_w"), ("8. Closing WDV", "cl_w")):
        d = compile_report({a: far_show[a][key] for a in asset_classes}, "Asset")
        if key in ("add", "dep"):
            _memo = [{"Asset": f"of which : Plant & Machinery (New Capex Project - {p})", **dict(zip(display_columns, far_new_p[p][key]))} for p in NPD if p == "P4" or NPD[p]["capex_total"] > 0]
            d = pd.concat([d, pd.DataFrame(_memo)], ignore_index=True)
        out.append((head, d))
    return out

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
wc_tlint  = [tl_int_tot[i] + tl_bc_tot[i] for i in _I]                                            # TL interest (incl. during construction) + TL bank charges : TL page
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
# NEW: bank charges on WC = month-end borrowing x rate of bank charges (% per month) ; Year 1 = sum ; Year 2-5 = 12 x rate x average of opening and closing borrowing
wc_bc = [max(wc_fin[t], 0.0) * _bc_rate for t in range(12)]
wc_bc.append(sum(wc_bc[0:12]))
for _i in range(13, 17): wc_bc.append(max((wc_od_op[_i] + wc_fin[_i]) / 2.0, 0.0) * _bc_rate * 12.0)

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
            ("10", "Bank Charges on WC", wc_bc, True),
            ("", "Memo : Closing Cash / (Unfunded Gap)", wc_cash_cl, False)]
    return _wc_df(spec, "Drawing Power, Borrowing & Interest on Working Capital")

def show_wc_df(df_bold):
    df, bold = df_bold
    sty = (df.style.format({c: "{:,.2f} L" for c in display_columns}, na_rep="")
           .apply(lambda r: ["font-weight: bold" if bold[r.name] else ""] * len(r), axis=1))
    gdf(sty, width="stretch", hide_index=True, height=35 * (len(df) + 1) + 3)

# ---- Hierarchical P&L compiler (16 Sl Nos, Level 1 - Level 4). Same function serves "All" and a single product ----
pct_of = lambda n, d: [(a / b * 100.0 if b > 0 else 0.0) for a, b in zip(n, d)]
per_unit = lambda n, d: [(a * 100000.0 / b if b > 0 else 0.0) for a, b in zip(n, d)]       # Rs lacs / Qt -> Rs per Kg

# ---- NEW: interest on working capital shared between P1-P4 on each product's COGS (monthly; Year 1 = sum of months) ----
_cogs_glob = {p: [rm_cons_val_p_total[p][i] + fg_adj[p][i] + dx_total_cost[p][i] + ix_total_cost[p][i] for i in range(17)] for p in products}
wc_int_p = {p: [0.0] * 17 for p in products}
for _i in list(range(12)) + [13, 14, 15, 16]:
    _tot = sum(_cogs_glob[p][_i] for p in products)
    for p in products: wc_int_p[p][_i] = (wc_int[_i] * _cogs_glob[p][_i] / _tot) if _tot > 0 else 0.0
for p in products: wc_int_p[p][12] = sum(wc_int_p[p][0:12])

def alloc_on_cogs(series):
    """Share a company-level series between P1-P4 on each product's COGS (monthly; Year 1 = sum of months; equal split if no COGS)."""
    out = {p: [0.0] * 17 for p in products}
    for i in list(range(12)) + [13, 14, 15, 16]:
        tot = sum(_cogs_glob[p][i] for p in products)
        for p in products: out[p][i] = (series[i] * _cogs_glob[p][i] / tot) if tot > 0 else series[i] / len(products)
    for p in products: out[p][12] = sum(out[p][0:12])
    return out
def only_prod(series, prod):
    return {p: (list(series) if p == prod else [0.0] * 17) for p in products}
def _add_p(a, b): return {p: [x + y for x, y in zip(a[p], b[p])] for p in products}

# ---- NEW: Depreciation (FAR page) : new P&M -> P4 ; rest shared on COGS.  Finance costs : TL New interest / bank charges -> P4 ; rest on COGS ----
dep_p = alloc_on_cogs(dep_other)
for _p in NPD: dep_p = _add_p(dep_p, only_prod(dep_new_p[_p], _p))
_tl_old = [n for n in tl_names if n not in tl_prod]                              # TL1-TL3 : shared by all products on COGS
tl_int_p = alloc_on_cogs([sum(tl_int_pl[n][i] for n in _tl_old) for i in range(17)])
for _n, _p in tl_prod.items(): tl_int_p = _add_p(tl_int_p, only_prod(tl_int_pl[_n], _p))
bc_p = alloc_on_cogs([wc_bc[i] + sum(tl[n]["bc"][i] for n in _tl_old) for i in range(17)])
for _n, _p in tl_prod.items(): bc_p = _add_p(bc_p, only_prod(tl[_n]["bc"], _p))
fin_p = {p: [wc_int_p[p][i] + tl_int_p[p][i] + bc_p[p][i] for i in range(17)] for p in products}

def build_pl(sel):
    """Value table of the PL (Rs lacs / Qt). Each row also carries _prod (product the row belongs to, for the % and per-Kg tables) and
    _dv (False = detail row not repeated in the % / per-Kg tables)."""
    prods = products if sel == "All" else [sel]
    allsel = (sel == "All")
    rows = []
    def add(si, blk, depth, l1, l2, l3, l4, series, fmt="lac", prod=None, dv=True):
        d = {"Si No": si, "BlockID": blk, "Depth": depth, "Level 1": l1, "Level 2": l2, "Level 3": l3, "Level 4": l4}
        for i, c in enumerate(display_columns): d[c] = series[i]
        d["_fmt"], d["_prod"], d["_dv"] = fmt, prod, dv      # qt / lac / rate / pct = display format of the row
        rows.append(d)
    S = lambda f: [sum(f(p)[i] for p in prods) for i in range(17)]
    def head(si, label, f, fmt="lac"):                    # L1 = total, L2 = product(s)
        add(si, si, "L1", label, "", "", "", S(f), fmt)
        for p in prods: add("", si, "L2", "", p, "", "", f(p), fmt, prod=p)

    # RM helpers (All = original total matrices, single product = product-wise split)
    rms = raw_materials if allsel else used_rms[sel]
    q_src = ({"op": rm_op_matrix, "pur": rm_purch_matrix, "con": rm_gross_cons_matrix, "cl": rm_cl_matrix} if allsel
             else {"op": rm_op_p[sel], "pur": rm_purch_p[sel], "con": rm_cons_p[sel], "cl": rm_cl_p[sel]})
    v_src = ({"op": rm_op_val_matrix, "pur": rm_purch_val_matrix, "con": rm_cons_val_matrix, "cl": rm_cl_val_matrix} if allsel
             else {"op": rm_op_val_p[sel], "pur": rm_purch_val_p[sel], "con": rm_cons_val_p[sel], "cl": rm_cl_val_p[sel]})

    sale_t = S(lambda p: qty_matrix[p])
    rev_t = S(lambda p: rev_lacs_p[p])
    cons_t = [sum(v_src["con"][rm][i] for rm in rms) for i in range(17)]

    # 1, 2 : Sale / Production Qt
    head("1", "Sale (Qt) :", lambda p: qty_matrix[p], "qt")
    head("2", "Production (Qt) :", lambda p: fg_prod_matrix[p], "qt")

    # 3 : Revenue  (L2 product -> L3 Qt / Rate)
    add("3", "3", "L1", "Revenue (Rs) :", "", "", "", rev_t)
    for p in prods:
        add("", "3", "L2", "", p, "", "", rev_lacs_p[p], prod=p)
        add("", "3", "L3", "", "", "Qt", "", qty_matrix[p], "qt", prod=p, dv=False)
        add("", "3", "L3", "", "", "Rate", "", rate_matrix[p], "rate", prod=p, dv=False)

    # 4 : RM Consumption  (L2 Total + each RM -> L3 Opening stk / Purchase / Consumption / Cl stock -> L4 Qt / Rate)
    add("4", "4", "L1", "RM Consumption (Rs) :", "", "", "", cons_t)
    add("", "4", "L2", "", "Total", "", "", cons_t)
    for lbl, k in (("Opening stk", "op"), ("Purchase", "pur"), ("Consumption", "con"), ("Cl stock", "cl")):
        vv = [sum(v_src[k][rm][i] for rm in rms) for i in range(17)]
        qq = [sum(q_src[k][rm][i] for rm in rms) for i in range(17)]
        add("", "4", "L3", "", "", lbl, "", vv, dv=False)
        add("", "4", "L4", "", "", "", "Qt", qq, "qt", dv=False)
        add("", "4", "L4", "", "", "", "Rate", per_unit(vv, qq), "rate", dv=False)
    for rm in rms:
        add("", "4", "L2", "", rm, "", "", v_src["con"][rm])
        for lbl, k in (("Opening stk", "op"), ("Purchase", "pur"), ("Consumption", "con"), ("Cl stock", "cl")):
            add("", "4", "L3", "", "", lbl, "", v_src[k][rm], dv=False)
            add("", "4", "L4", "", "", "", "Qt", q_src[k][rm], "qt", dv=False)
            add("", "4", "L4", "", "", "", "Rate", rm_price_horizon[rm], "rate", dv=False)

    # 5 : FG Decrease / (Increase) = 5a - 5b  (L2 5a / 5b -> L3 product -> L4 Qt / Rate = COGS per unit)
    add("5", "5", "L1", "FG : Decrease / (Increase) of FG (5a-5b)", "", "", "", S(lambda p: fg_adj[p]))
    for _lbl, _val, _qty, _rate in (("5a  FG : Opening stock", fg_op_val, fg_op_matrix, fg_op_rate),
                                    ("5b  Less : FG : Closing stock", fg_cl_val, fg_cl_matrix, fg_cl_rate)):
        add("", "5", "L2", "", _lbl, "", "", S(lambda p: _val[p]), dv=False)
        for p in prods:
            add("", "5", "L3", "", "", p, "", _val[p], prod=p, dv=False)
            add("", "5", "L4", "", "", "", "Qt", _qty[p], "qt", prod=p, dv=False)
            add("", "5", "L4", "", "", "", "Rate", _rate[p], "rate", prod=p, dv=False)

    # 6 : sub-total RM consumption + FG adjustment (4+5)
    sub_p = {p: [rm_cons_val_p_total[p][i] + fg_adj[p][i] for i in range(17)] for p in products}
    head("6", "RM Consumption + FG Adj. (4+5)", lambda p: sub_p[p])

    # exp blocks : L2 Total + heads -> L3 product -> L4 Qt / Rate
    def exp_block(si, label, total_f, head_f, heads, qty_f, short_pct_heads=()):
        add(si, si, "L1", label, "", "", "", S(total_f))
        add("", si, "L2", "", "Total", "", "", S(total_f))
        for p in prods:
            add("", si, "L3", "", "", p, "", total_f(p), prod=p)
            add("", si, "L4", "", "", "", "Qt", qty_f(p), "qt", prod=p, dv=False)
            add("", si, "L4", "", "", "", "Rate", per_unit(total_f(p), qty_f(p)), "rate", prod=p, dv=False)
        for h in heads:
            add("", si, "L2", "", h, "", "", S(lambda p: head_f(h, p)))
            for p in prods:
                add("", si, "L3", "", "", p, "", head_f(h, p), prod=p)
                if h in short_pct_heads:      # % of sale value heads: Sale Value x Rate (%)
                    add("", si, "L4", "", "", "", "Sale Value", rev_lacs_p[p], prod=p, dv=False)
                    add("", si, "L4", "", "", "", "Rate (%)", pct_of(head_f(h, p), rev_lacs_p[p]), "pct", prod=p, dv=False)
                else:
                    add("", si, "L4", "", "", "", "Qt", qty_f(p), "qt", prod=p, dv=False)
                    add("", si, "L4", "", "", "", "Rate", per_unit(head_f(h, p), qty_f(p)), "rate", prod=p, dv=False)
    exp_block("7", "Direct Expenses", lambda p: dx_total_cost[p], lambda h, p: dx_cost[h][p], direct_heads, lambda p: fg_prod_matrix[p])

    # 8-9 : COP (6+7), Gross Profit (3-8)
    cop_p = {p: [sub_p[p][i] + dx_total_cost[p][i] for i in range(17)] for p in products}
    gp_p = {p: [rev_lacs_p[p][i] - cop_p[p][i] for i in range(17)] for p in products}
    head("8", "COP (6+7)", lambda p: cop_p[p])
    head("9", "Gross Profit (3-8)", lambda p: gp_p[p])

    # 10 : Indirect Expenses
    exp_block("10", "Indirect Expenses", lambda p: ix_total_cost[p], lambda h, p: ix_cost[h][p], indirect_heads,
              lambda p: qty_matrix[p], short_pct_heads=[h for h in indirect_heads if ix_type[h] == "%"])

    # 11-14 : COGS (8+10), EBIDTA (3-11), Interest on Working Capital (shared on COGS), PBT (12-13)
    cogs_p = {p: [cop_p[p][i] + ix_total_cost[p][i] for i in range(17)] for p in products}
    eb_p = {p: [rev_lacs_p[p][i] - cogs_p[p][i] for i in range(17)] for p in products}
    head("11", "COGS (8+10)", lambda p: cogs_p[p])
    head("12", "EBIDTA (3-11)", lambda p: eb_p[p])
    # 13-16 (NEW) : Depreciation (FAR page), EBIT (12-13), Finance Costs (WC interest + TL interest + bank charges), PBT (14-15)
    ebit_p = {p: [eb_p[p][i] - dep_p[p][i] for i in range(17)] for p in products}
    head("13", "Depreciation (FAR page)", lambda p: dep_p[p])
    head("14", "EBIT (12-13)", lambda p: ebit_p[p])
    add("15", "15", "L1", "Finance Costs", "", "", "", S(lambda p: fin_p[p]))
    for _lbl, _src in (("Interest on Working Capital (WC page)", wc_int_p), ("Interest on Term Loan (TL page)", tl_int_p),
                       ("Bank Charges (WC + TL)", bc_p)):
        add("", "15", "L2", "", _lbl, "", "", S(lambda p: _src[p]))
        for p in prods: add("", "15", "L3", "", "", p, "", _src[p], prod=p)
    head("16", "PBT (14-15)", lambda p: [ebit_p[p][i] - fin_p[p][i] for i in range(17)])
    return pd.DataFrame(rows)

def derive_pl(df, sel, kind):
    """% against Sales (kind 'pct') or cost per Kg against Sale Qt (kind 'pu') : every value row of the PL (except stock-movement detail) divided by the
    Revenue / Sale Qt of its own product (or of the selected products for total rows). Same Level 1-4 tree as the value table."""
    prods = products if sel == "All" else [sel]
    rev_s = [sum(rev_lacs_p[p][i] for p in prods) for i in range(17)]
    qty_s = [sum(qty_matrix[p][i] for p in prods) for i in range(17)]
    out = df[(df["_fmt"] == "lac") & (df["_dv"])].copy().reset_index(drop=True)
    for r in range(len(out)):
        p = out.at[r, "_prod"]
        den = (rev_lacs_p[p] if isinstance(p, str) else rev_s) if kind == "pct" else (qty_matrix[p] if isinstance(p, str) else qty_s)
        for i, c in enumerate(display_columns):
            v = safe_float(out.at[r, c])
            out.at[r, c] = (v / den[i] * 100.0 if kind == "pct" else v * 100000.0 / den[i]) if den[i] > 0 else 0.0
    out["_fmt"] = "pct" if kind == "pct" else "rate"
    return out

df_pl_master_raw = build_pl("All")
df_pl_by_prod = {p: build_pl(p) for p in products}
PL_VAL = {"All": df_pl_master_raw, **df_pl_by_prod}
PL_PCT = {s: derive_pl(d, s, "pct") for s, d in PL_VAL.items()}
PL_PU = {s: derive_pl(d, s, "pu") for s, d in PL_VAL.items()}

# -----------------------------------------------------------------------------
# CHAPTER 4A (NEW): CASH FLOW (CF page) - company level, Rs in Lacs. Every figure is linked from the pages above.
# Flows : Year 1 = sum of M1-M12.  Balances : Year 1 = M12 (closing) / M1 (opening).  Headings not yet in the model = 0.
# -----------------------------------------------------------------------------
_Z = [0.0] * 17
def _vsum(*series): return [sum(s[i] for s in series) for i in range(17)]
def _flow17(m12, y25=None):                        # 12 monthly values (+ optional Year 2-5) -> 17 columns, Year 1 = sum
    return list(m12) + [sum(m12)] + (list(y25) if y25 is not None else [0.0] * 4)

# Inflow
cf_tl_rec = _vsum(*[tl[n]["disb"] for n in tl_names])                                       # TL page : disbursement
cf_bor = [wc_fin[i] for i in range(12)] + [wc_fin[11]] + [wc_fin[i] for i in range(13, 17)]   # month-end bank borrowing O/s (WC page Final Borrowing) ; Year 1 = M12
_bor_prev = [safe_float(wc_od_open)] + cf_bor[0:11] + [safe_float(wc_od_open)] + [cf_bor[12]] + cf_bor[13:16]
cf_wc_rec = [cf_bor[i] - _bor_prev[i] for i in range(17)]                                    # increase over previous period's O/s (negative = repayment)
cf_coll = {p: dbt[p]["flow"] for p in products}                                              # Revenue page : debtors cash inflow
cf_in = _vsum(cf_tl_rec, cf_wc_rec, *cf_coll.values())

# Outflow : CAPEX
cf_cap_sup = _flow17([sum(NPD[p]["row"]("New Capex Payment (Rs Lacs)")[i] + NPD[p]["row"]("New Capex Installation Cost (Rs Lacs)")[i] for p in NPD) for i in range(12)])
cf_cap_dir = _vsum(*[_add_series(r) for r in add_rows])                                      # FAR feed : asset additions
cf_tl_rep = _vsum(*[tl[n]["rep"] for n in tl_names])                                         # TL page : repayment
cf_capex = _vsum(cf_cap_sup, cf_cap_dir, cf_tl_rep, wc_fd)
# Outflow : RM (RM Val page)
cf_rm_pay = {rm: crd[rm]["flow"] for rm in raw_materials}
cf_rm_adv = {rm: crd_adv[rm] for rm in raw_materials}
cf_rm = _vsum(*cf_rm_pay.values(), *cf_rm_adv.values())
# Outflow : Finance cost (cash) - TL interest includes interest during construction (capitalised in FAR, but paid in cash)
cf_tl_int_p = {p: [tl_int_p[p][i] + (_idc_by[p]["series"][i] if p in _idc_by else 0.0) for i in range(17)] for p in products}
cf_fin = _vsum(*wc_int_p.values(), *cf_tl_int_p.values(), *bc_p.values())
# Outflow : Taxes / other
cf_tax = _vsum(wc_tax)
cf_oth_out = _vsum(wc_cont)
cf_dx = _vsum(*dx_total_cost.values())
cf_ix = _vsum(*ix_total_cost.values())
cf_out = _vsum(cf_capex, cf_dx, cf_ix, cf_rm, cf_fin, cf_tax, cf_oth_out)

# Opening / closing cash chain
cf_open, cf_close = [0.0] * 17, [0.0] * 17
_c = safe_float(wc_cash_open)
for _t in range(12):
    cf_open[_t] = _c
    cf_close[_t] = _c + cf_in[_t] - cf_out[_t]
    _c = cf_close[_t]
cf_open[12] = cf_open[0]
cf_close[12] = cf_open[12] + cf_in[12] - cf_out[12]
for _i in range(13, 17):
    cf_open[_i] = cf_close[_i - 1]
    cf_close[_i] = cf_open[_i] + cf_in[_i] - cf_out[_i]
cf_limit = [safe_float(wc_od_limit)] * 17
cf_free = [a - b for a, b in zip(cf_limit, cf_bor)]
cf_avail = [a + b for a, b in zip(cf_free, cf_close)]

def build_cf():
    """CF table in the 'CF' sheet layout, Level 1-4 tree (same columns / +/- expansion as the PL)."""
    rows = []
    def add(si, blk, depth, l1, l2, l3, l4, series):
        d = {"Si No": si, "BlockID": blk, "Depth": depth, "Level 1": l1, "Level 2": l2, "Level 3": l3, "Level 4": l4}
        for i, c in enumerate(display_columns): d[c] = series[i]
        d["_fmt"], d["_prod"], d["_dv"] = "lac", None, True
        rows.append(d)
    def by_key(blk, label, dct, keys, depth_lbl, depth_key):
        add("", blk, depth_lbl, "", label if depth_lbl == "L2" else "", label if depth_lbl == "L3" else "", "", _vsum(*[dct[k] for k in keys]))
        for k in keys:
            add("", blk, depth_key, "", k if depth_key == "L2" else "", k if depth_key == "L3" else "", k if depth_key == "L4" else "", dct[k])

    add("1", "1", "L1", "Opening Cash Balance", "", "", "", cf_open)

    add("2", "2", "L1", "(+) Total Cash Inflow", "", "", "", cf_in)
    add("", "2", "L2", "", "New Term Loan Receipt", "", "", cf_tl_rec)
    add("", "2", "L2", "", "Loan from Management", "", "", _Z)
    add("", "2", "L2", "", "Working Capital Receipt", "", "", cf_wc_rec)
    by_key("2", "Collection", cf_coll, products, "L2", "L3")
    add("", "2", "L2", "", "Tax Refund", "", "", _Z)
    add("", "2", "L2", "", "Fixed Deposit discount", "", "", _Z)
    add("", "2", "L2", "", "Others", "", "", _Z)

    add("3", "3", "L1", "(-) Cash Outflow", "", "", "", cf_out)
    add("", "3", "L2", "", "CAPEX", "", "", cf_capex)
    for _lbl, _s in (("Payment to Capex supplier", cf_cap_sup), ("Capex : Direct Purchase", cf_cap_dir), ("TL repayment", cf_tl_rep),
                     ("FIXED DEPOSIT/ Margin", wc_fd), ("Investment In Subsidiary", _Z), ("RENT ADVANCE", _Z), ("Other", _Z)):
        add("", "3", "L3", "", "", _lbl, "", _s)
    add("", "3", "L2", "", "Direct Expenses", "", "", cf_dx)
    for h in direct_heads: by_key("3", h, dx_cost[h], products, "L3", "L4")
    add("", "3", "L2", "", "Indirect Expenses", "", "", cf_ix)
    for h in indirect_heads: by_key("3", h, ix_cost[h], products, "L3", "L4")
    add("", "3", "L2", "", "RM", "", "", cf_rm)
    by_key("3", "Payment to Suppliers/ Creditors", cf_rm_pay, raw_materials, "L3", "L4")
    by_key("3", "Advance payment to suppliers", cf_rm_adv, raw_materials, "L3", "L4")
    add("", "3", "L3", "", "", "Duty", "", _Z)
    add("", "3", "L3", "", "", "Other", "", _Z)
    add("", "3", "L2", "", "Finance Cost", "", "", cf_fin)
    by_key("3", "Interest on WC", wc_int_p, products, "L3", "L4")
    by_key("3", "Interest on TL", cf_tl_int_p, products, "L3", "L4")
    by_key("3", "Other (Bank Charges)", bc_p, products, "L3", "L4")
    add("", "3", "L2", "", "Taxes", "", "", cf_tax)
    for _lbl, _s in (("GST", _Z), ("Adv Tax", wc_tax), ("Income Tax", _Z), ("Other Admin charges", _Z)):
        add("", "3", "L3", "", "", _lbl, "", _s)
    add("", "3", "L2", "", "Other Outflow", "", "", cf_oth_out)
    add("", "3", "L3", "", "", "Other Contingency (WC feed)", "", wc_cont)

    add("4", "4", "L1", "Closing Cash Balance (1+2-3)", "", "", "", cf_close)
    add("5", "5", "L1", "Bank Sanction Limit", "", "", "", cf_limit)
    add("6", "6", "L1", "Bank Borrowing O/s", "", "", "", cf_bor)
    add("7", "7", "L1", "Free Limit (5-6)", "", "", "", cf_free)
    add("8", "8", "L1", "Closing Cash Balance (4)", "", "", "", cf_close)
    add("9", "9", "L1", "Total Cash Available (7+8)", "", "", "", cf_avail)
    return pd.DataFrame(rows)

df_cf = build_cf()

# -----------------------------------------------------------------------------
# CHAPTER 4B (NEW): PRODUCT SLICER HELPERS (view-only filters; "All" returns the original tables)
# -----------------------------------------------------------------------------
def title_with_slicer(title, key):
    c_title, c_slicer = st.columns([6, 1.3], vertical_alignment="center")
    with c_title: st.title(title)
    with c_slicer: return st.selectbox("Product", ["All"] + products, key=key, label_visibility="collapsed", format_func=lambda x: f"Product : {x}")

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
page_tab5, page_tab1, page_tab2, page_tab3, page_tab4, page_tab_dx, page_tab_ix, page_tab_cost, page_tab_wc, page_tab_far, page_tab_tl, page_tab_cf = st.tabs(["PL", "Revenue", "FG", "RM Qt", "RM Val", "Direct Expenses", "Indirect Expenses", "Costing", "WC", "FAR", "TL", "CF"])

# (Streamlit tabs are client-side only, so the sidebar radio is synced by the script in CHAPTER 7.)

with page_tab1:
    sel1 = title_with_slicer("Sales Forecasting", "slicer_rev")
    st.subheader("1. Revenue (Rs in Lacs)")
    gdf(pick_rev(sel1).style.format({col: "{:,.2f} L" for col in display_columns if col != "Product"}), width="stretch", hide_index=True)
    st.subheader("2. Sale (Qt)")
    gdf(pick_matrix(df_qty_final, qty_matrix, sel1).style.format({col: "{:,.0f}" for col in display_columns if col != "Product"}), width="stretch", hide_index=True)
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
    gdf(pick_fg_flow(sel2).style.format({col: "{:,.0f}" for col in display_columns if col not in ["Product", "FG Inventory Metrics"]}), width="stretch", hide_index=True)
    st.subheader("2. Production (Qt)")
    gdf(pick_matrix(df_summary_prod, fg_prod_matrix, sel2).style.format({col: "{:,.0f}" for col in display_columns if col != "Product"}), width="stretch", hide_index=True)
    st.subheader("3. FG Closing Stock (Qt)")
    gdf(pick_matrix(df_summary_cl, fg_cl_matrix, sel2).style.format({col: "{:,.0f}" for col in display_columns if col != "Product"}), width="stretch", hide_index=True)
    st.subheader("4. FG Opening Stock (Qt)")
    gdf(pick_matrix(df_summary_op, fg_op_matrix, sel2).style.format({col: "{:,.0f}" for col in display_columns if col != "Product"}), width="stretch", hide_index=True)
    st.subheader("5. FG Closing Stock (Value)")
    st.caption("Rs in Lacs = FG Closing Stock Qt x COGS per unit (Costing page)")
    gdf(pick_matrix(df_fg_cl_val_final, fg_cl_val, sel2).style.format({col: "{:,.2f} L" for col in display_columns if col != "Product"}), width="stretch", hide_index=True)
    st.subheader("6. FG Opening Stock (Value)")
    st.caption("Rs in Lacs = M1 Opening Qt x M1 COGS per unit; M2 onward = previous month's closing value; Year 2-5 = previous year's closing value")
    gdf(pick_matrix(df_fg_op_val_final, fg_op_val, sel2).style.format({col: "{:,.2f} L" for col in display_columns if col != "Product"}), width="stretch", hide_index=True)

with page_tab3:
    sel3 = title_with_slicer("Material Forecasting", "slicer_rmqt")
    st.subheader("1. RM Flow (Qt)")
    gdf(pick_rm_flow(sel3, master_rm_flow_df, rm_op_p, rm_purch_p, rm_cons_p, rm_cl_p, "RM Flow(Qt) Metrics").style.format({col: "{:,.0f}" for col in display_columns if col not in ["Raw Material", "RM Flow(Qt) Metrics"]}), width="stretch", hide_index=True)
    st.subheader("2. RM Consumption (Qt)")
    gdf(pick_rm(sel3, df_rm_consumption_final, rm_cons_p).style.format({col: "{:,.0f}" for col in display_columns if col != "Raw Material"}), width="stretch", hide_index=True)
    st.subheader("3. RM Purchase (Qt)")
    gdf(pick_rm(sel3, df_rm_purchase_final, rm_purch_p).style.format({col: "{:,.0f}" for col in display_columns if col != "Raw Material"}), width="stretch", hide_index=True)
    st.subheader("4. RM Loss (Qt)")
    gdf(pick_rm(sel3, df_rm_loss_final, rm_loss_p).style.format({col: "{:,.0f}" for col in display_columns if col != "Raw Material"}), width="stretch", hide_index=True)
    st.subheader("5. Scrap (Qt)")
    gdf(pick_scrap(sel3).style.format({col: "{:,.0f}" for col in display_columns if col != "Scrap (Qt)"}), width="stretch", hide_index=True)

with page_tab4:
    sel4 = title_with_slicer("Material Forecasting", "slicer_rmval")
    st.subheader("1. RM Flow (Rs in Lacs)")
    gdf(pick_rm_flow(sel4, master_rm_val_flow_df, rm_op_val_p, rm_purch_val_p, rm_cons_val_p, rm_cl_val_p, "RM Flow(Rs) Metrics").style.format({col: "{:,.2f} L" for col in display_columns if col not in ["Raw Material", "RM Flow(Rs) Metrics"]}), width="stretch", hide_index=True)
    st.subheader("2. RM Purchase (Rs in Lacs)")
    gdf(pick_rm(sel4, df_rm_purchase_val_final, rm_purch_val_p).style.format({col: "{:,.2f} L" for col in display_columns if col != "Raw Material"}), width="stretch", hide_index=True)
    st.subheader("3. RM Consumption (Rs in Lacs)")
    gdf(pick_rm(sel4, df_rm_consumption_val_final, rm_cons_val_p).style.format({col: "{:,.2f} L" for col in display_columns if col != "Raw Material"}), width="stretch", hide_index=True)
    st.subheader("4. RM Loss (Rs in Lacs)")
    gdf(pick_rm(sel4, df_rm_loss_val_final, rm_loss_p).style.format({col: "{:,.2f} L" for col in display_columns if col != "Raw Material"}), width="stretch", hide_index=True)
    st.subheader("5. RM Opening Stock (Rs in Lacs)")
    gdf(pick_rm(sel4, df_rm_op_val_final, rm_op_val_p).style.format({col: "{:,.2f} L" for col in display_columns if col != "Raw Material"}), width="stretch", hide_index=True)
    st.subheader("6. RM Closing Stock (Rs in Lacs)")
    gdf(pick_rm(sel4, df_rm_cl_val_final, rm_cl_val_p).style.format({col: "{:,.2f} L" for col in display_columns if col != "Raw Material"}), width="stretch", hide_index=True)
    st.subheader("7. Due to Suppliers (Rs in Lacs)")
    st.caption(f"RM-wise, all products combined (the Product slicer does not apply).  Gross Due = Purchase + Purchase x GST ({safe_float(gst_pur_pct):g}% on purchases).  "
               f"Advance {_adv_frac * 100:g}% of Gross Due is paid at order (RM13-RM15 / P4 : {_adv_frac_p4 * 100:g}%; RMs of added products : their own advance %); Net Due to Suppliers = Gross Due - Advance")
    show_block_df(creditor_due_df())
    st.subheader("8. Creditors Flow & Cash Outflow Movement Forecast (Rs in Lacs)")
    st.caption(f"RM-wise, all products combined.  Credit period {safe_float(rm_credit_days):g} days for RM1-RM12 and {crd_days_rm['RM13']:g} days for RM13-RM15 (P4), and the credit days keyed for the RMs of added products, applied on Net Due.  "
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
        gdf(d_cost.style.format(fmt_l), width="stretch", hide_index=True)
        st.markdown(f"##### {short} / p.u. (Rs/Kg)")
        gdf(d_pu.style.format(fmt_n), width="stretch", hide_index=True)
        st.markdown(f"##### {short} Turnover %")
        gdf(d_pct.style.format(fmt_p), width="stretch", hide_index=True)
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
        gdf(d_cost.style.format(fmt_l), width="stretch", hide_index=True)
        st.markdown(f"##### {short} / p.u. (Rs/Kg)")
        gdf(d_pu.style.format(fmt_n), width="stretch", hide_index=True)
        st.markdown(f"##### {short} Turnover %")
        gdf(d_pct.style.format(fmt_p), width="stretch", hide_index=True)
        st.markdown("---")

with page_tab_cost:
    sel_cost = title_with_slicer("Costing : COGS Per Unit", "slicer_cost")
    st.caption("Rs per Kg. RM consumption and Direct Expenses = cost / Production Qt; Indirect Expenses = cost / Sale Qt; Year columns = annual cost / annual Qt. "
               "Travelling Expenses and Carriage Outward are not included (not yet incurred, so not part of FG valuation).")
    for p in (products if sel_cost == "All" else [sel_cost]):
        _cdf = build_costing_df(p)
        _sty = (_cdf.style.format({c: "{:,.2f}" for c in display_columns}, na_rep="")
                .apply(lambda r: ["font-weight: bold" if r["Sl No"] != "" else ""] * len(r), axis=1))
        gdf(_sty, width="stretch", hide_index=True, height=35 * (len(_cdf) + 1) + 3)

def render_pl_tree(master_pl, sfx="", px=None):
    """One PL tree table with its own +/- expansion state (sfx keeps the three PL tables independent; px = optional column widths)."""
    # ---- 1. Describe the tree: for every master row -> node key, parent chain, has-children ----
    # (FIX: the table passed in is used as it is - Value, % against Sales or Cost per Kg; it was previously overwritten by the Value table)
    master_pl = master_pl.reset_index(drop=True)
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

    open_nodes = st.session_state.setdefault(f"pl_open_nodes{sfx}", set())
    visible_idx = [i for i, n in enumerate(node_info) if all(a in open_nodes for a in n["ancestors"])]

    # row position in the grid -> (node, has_children); used by the click handler below
    st.session_state[f"pl_row_map{sfx}"] = [(node_info[i]["node"], node_info[i]["has_children"]) for i in visible_idx]

    def pl_tree_toggle_cb():
        ver = st.session_state.get(f"pl_editor_ver{sfx}", 0)
        editor_state = st.session_state.get(f"pl_tree_editor{sfx}_{ver}", {})
        row_map = st.session_state.get(f"pl_row_map{sfx}", [])
        for r_pos, changes in editor_state.get("edited_rows", {}).items():
            r_pos = int(r_pos)
            if "+/-" in changes and 0 <= r_pos < len(row_map) and row_map[r_pos][1]:
                if changes["+/-"]: st.session_state[f"pl_open_nodes{sfx}"].add(row_map[r_pos][0])
                else: st.session_state[f"pl_open_nodes{sfx}"].discard(row_map[r_pos][0])
        st.session_state[f"pl_editor_ver{sfx}"] = ver + 1     # fresh editor state after every click

    _click_cols = ("+/-", "Si No", "Level 1", "Level 2", "Level 3", "Level 4")
    def pl_tree_click_cb():
        """NEW : a click on the [+] / [-] cell (or on the heading text) of a heading row expands / collapses it."""
        ver = st.session_state.get(f"pl_editor_ver{sfx}", 0)
        ev = st.session_state.get(f"pl_tree_view{sfx}_{ver}")
        row_map = st.session_state.get(f"pl_row_map{sfx}", [])
        try:
            cells = ev["selection"]["cells"]
        except Exception:
            cells = []
        for cell in cells or []:
            try:
                r_pos, col = int(cell[0]), str(cell[1])
            except Exception:
                continue
            if col in _click_cols and 0 <= r_pos < len(row_map) and row_map[r_pos][1]:
                _open = st.session_state[f"pl_open_nodes{sfx}"]
                if row_map[r_pos][0] in _open: _open.discard(row_map[r_pos][0])
                else: _open.add(row_map[r_pos][0])
        st.session_state[f"pl_editor_ver{sfx}"] = ver + 1     # fresh table (no selection left behind) after every click

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

        display_pl_df = df_pl_filtered.drop(columns=["_fmt", "BlockID", "Depth", "_prod", "_dv"])

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

        # '+/-' first column : clickable [+] / [-] cell (navy, like the rest of the table). Blank for rows that have nothing to expand.
        # (the old checkbox stays as an automatic fallback when this Streamlit version has no cell-click selection)
        toggle_vals = [((node_info[i]["node"] in open_nodes) if node_info[i]["has_children"] else None) for i in visible_idx]
        click_vals = [("" if v is None else ("[-]" if v else "[+]")) for v in toggle_vals]
        styled_cb_df = styled_pl_df.copy()
        styled_cb_df.insert(0, "+/-", pd.array(toggle_vals, dtype="boolean"))
        styled_pl_df.insert(0, "+/-", click_vals)
        _pl_depth = df_pl_filtered["Depth"].tolist()          # same row order as styled_pl_df
        def _pl_row_css(r):
            out = []
            for c in r.index:
                css = f"background-color: {T_NAVY}; font-weight: 400; color: {T_ROWHDR if c not in display_columns else T_GOLD};"
                if c in display_columns and isinstance(r[c], str) and r[c].startswith("-"): css += f" color: {T_NEG};"
                out.append(css)
            return out
        _pl_view = styled_pl_df.style.apply(_pl_row_css, axis=1)
        _cb_view = styled_cb_df.style.apply(_pl_row_css, axis=1)

        # Fixed pixel widths (never auto-sized) and pinned (frozen) left columns, so the heads stay visible while scrolling right
        _pl_px = px or {"+/-": 48, "Si No": 52, "Level 1": 215, "Level 2": 175, "Level 3": 115, "Level 4": 100}
        def _pl_cfg(modern, checkbox):
            cfg = {}
            for _c, _w in _pl_px.items():
                _kw = dict(width=_w, pinned=True) if modern else dict(width=("small" if _w < 100 else "medium"))
                if _c == "+/-" and checkbox: cfg[_c] = st.column_config.CheckboxColumn("+/-", help="Tick to expand, untick to collapse", **_kw)
                elif _c == "+/-": cfg[_c] = st.column_config.TextColumn("+/-", help="Click [+] to expand, [-] to collapse", **_kw)
                else: cfg[_c] = st.column_config.TextColumn(_c, **_kw)
            return cfg
        _ver_now = st.session_state.get(f'pl_editor_ver{sfx}', 0)
        _h = min(35 * (len(styled_pl_df) + 1) + 5, 1100)
        _done = False
        if st.session_state.get("pl_click_mode", True):
            # clickable-cell table (st.dataframe with single-cell selection)
            for _data, _modern in ((_pl_view, True), (_pl_view, False), (styled_pl_df, True), (styled_pl_df, False)):
                try:
                    st.dataframe(_data, column_config=_pl_cfg(_modern, False), width="stretch", hide_index=True, height=_h,
                                 key=f"pl_tree_view{sfx}_{_ver_now}", on_select=pl_tree_click_cb, selection_mode="single-cell")
                    _done = True
                    break
                except Exception:
                    continue
            if not _done: st.session_state["pl_click_mode"] = False       # this Streamlit version has no cell-click : use the checkbox from now on
        if not _done:
            _pl_args = dict(
                width="stretch",
                hide_index=True,
                num_rows="fixed",
                disabled=[c for c in styled_cb_df.columns if c != "+/-"],
                height=_h,
                key=f"pl_tree_editor{sfx}_{_ver_now}",
                on_change=pl_tree_toggle_cb,
            )
            for _data, _modern in ((_cb_view, True), (_cb_view, False), (styled_cb_df, True), (styled_cb_df, False)):   # navy / gold view first, plain table as fallback
                try:
                    st.data_editor(_data, column_config=_pl_cfg(_modern, True), **_pl_args)
                    break
                except Exception:
                    continue
    else:
        st.warning("No structural P&L rows selected.")

with page_tab5:
    sel_pl = title_with_slicer("PL Forecast", "slicer_pl")
    st.caption(("Click the [+] / [-] cell in the '+/-' column (or the heading text) on any heading row to expand or collapse it. "
                if st.session_state.get("pl_click_mode", True) else
                "Tick / untick the checkbox in the '+/-' column on any heading row to expand or collapse it. ") +
               "[+] = collapsed, [-] = expanded. Each heading opens independently; the three tables below have the same rows and the same expansion.")
    st.subheader("1. PL : Value (Rs in Lacs)")
    render_pl_tree(PL_VAL[sel_pl].reset_index(drop=True), "")
    st.subheader("2. PL : % against Sales")
    st.caption("Every line (and expense head / sub-head) as % of Revenue - product rows against that product's Revenue.")
    render_pl_tree(PL_PCT[sel_pl].reset_index(drop=True), "_pct")
    st.subheader("3. PL : Cost per Kg against Sale Qt (Rs/Kg)")
    st.caption("Every line (and expense head / sub-head) divided by Sale Qt - product rows against that product's Sale Qt.")
    render_pl_tree(PL_PU[sel_pl].reset_index(drop=True), "_pu")

with page_tab_wc:
    st.title("Working Capital Forecast")
    st.caption("Company level (all products, all RMs) - the Product slicer does not apply.  Rs in Lacs.")
    st.subheader("1. Working Capital Requirement (Rs in Lacs)")
    st.caption("Cash Outflow - Cash Inflow - Cash & Bank Balance.  RM advance and payment to creditors come from the RM Val page, Power / labour / other mfg expenses from Direct Expenses, "
               "Selling and admn OH from Indirect Expenses, TL interest & bank charges from the TL page, sale receipts from the Debtors cash flow (Revenue page).  Cash & Bank Balance = opening feed in M1, then the previous period's closing cash.")
    show_wc_df(wc_req_df())
    st.subheader("2. Drawing Power, Borrowing & Interest on Working Capital (Rs in Lacs)")
    st.caption(f"Margin {_mpct * 100:g}% on Working Capital Gap; DP = maximum permissible borrowing.  Total Proposed Borrowing = Working Capital Requirement + Opening OD/CC (M1 = feed, then previous month's Final Borrowing).  "
               f"Final Borrowing = Proposed Borrowing if DP covers it, else DP.  Interest = Final Borrowing x {safe_float(wc_roi):g}% / 12 (Year 1 = sum of months; Year 2-5 = rate x average of opening and closing borrowing).  Bank Charges on WC = month-end Final Borrowing x {safe_float(bank_chg_pct):g}% per month (TL Feed).  "
               "Both flow to the PL page under Finance Costs, below EBIT.")
    _short = [display_columns[i] for i in range(17) if wc_sur[i] < 0]
    if _short:
        st.warning("DP shortfall (borrowing needed is above Drawing Power) in: " + ", ".join(_short) + ".  The unfunded gap is carried forward as negative cash.")
    show_wc_df(wc_dp_df())


with page_tab_far:
    st.title("Fixed Asset Register (FAR)")
    _far_note = "; ".join(f"{p} capitalised in {display_columns[NPD[p]['start']]} at {asset_val[p]:,.2f} L (capex {NPD[p]['capex_total']:,.2f} L + interest during construction {(_idc_by[p]['total'] if p in _idc_by else 0.0):,.2f} L)" for p in NPD if p == "P4" or NPD[p]["capex_total"] > 0)
    st.caption(f"Company level - Rs in Lacs.  Depreciation (straight line) = closing gross block x rate / 12 per month (Year 2-5 : x rate), never below nil WDV.  "
               f"Plant & Machinery includes the new capex projects : {_far_note}.  "
               "Depreciation on each new P&M is charged to its own product; the rest is shared by all products on COGS (PL page, below EBIDTA).")
    _fmt_far = {c: "{:,.2f} L" for c in display_columns}
    for _h, _d in far_tables():
        st.subheader(_h)
        gdf(_d.style.format(_fmt_far).apply(lambda r: ["font-weight: bold" if r["Asset"] == "Total" else ""] * len(r), axis=1),
                     width="stretch", hide_index=True, height=35 * (len(_d) + 1) + 3)

with page_tab_tl:
    st.title("Term Loan (TL)")
    _tl_note = "; ".join(f"{n} : disbursed {NPD[p]['tl_frac'] * 100:g}% of each capex payment, interest only up to completion ({months[NPD[p]['comp']]}), repaid from {display_columns[NPD[p]['start']]}" for n, p in tl_prod.items())
    st.caption(f"Rs in Lacs.  Repayment = opening O/s / months of life remaining (equal principal).  Interest = opening O/s x rate / 12.  "
               f"{_tl_note}.  Interest up to completion (total {tl_idc:,.2f} L) is capitalised into the respective new Plant & Machinery.  "
               f"Bank charges = month-end O/s x {safe_float(bank_chg_pct):g}% per month.  Year 1 = M1-M12; Year 2-5 = sum of their 12 months.")
    _fmt_tl = {c: "{:,.2f} L" for c in display_columns}
    for _h, _d in tl_tables():
        st.subheader(_h)
        gdf(_d.style.format(_fmt_tl).apply(lambda r: ["font-weight: bold" if r["Term Loan"] == "Total" else ""] * len(r), axis=1),
                     width="stretch", hide_index=True, height=35 * (len(_d) + 1) + 3)

with page_tab_cf:
    st.title("Cash Flow : Forecast")
    st.caption(("Click the [+] / [-] cell" if st.session_state.get("pl_click_mode", True) else "Tick / untick the '+/-' checkbox") +
               " on any heading row to expand or collapse it.  Company level (all products, all RMs) - the Product slicer does not apply.  Rs in Lacs.  "
               "Opening Cash = WC feed in M1, then the previous period's closing.  Working Capital Receipt = increase in month-end bank borrowing O/s (WC page Final Borrowing; negative = repayment).  "
               "Collection = debtors cash inflow (Revenue page); RM payments / advances = RM Val page; expenses = Direct / Indirect Expenses pages; TL receipt, repayment and interest = TL page "
               "(interest incl. interest during construction, paid in cash); capex = P4 / added-product capex payments + FAR asset additions; FD, tax and contingency = WC feed.  "
               "Year 1 = M1-M12.  Headings not yet in the model show 0.")
    if any(v < 0 for v in cf_free):
        st.warning("Bank borrowing O/s is above the OD / CC Sanction Limit (Free Limit negative) in: " + ", ".join(display_columns[i] for i in range(17) if cf_free[i] < 0) + ".")
    render_pl_tree(df_cf, "_cf", px={"+/-": 48, "Si No": 52, "Level 1": 230, "Level 2": 185, "Level 3": 225, "Level 4": 80})

# P4 / New Capex Feed desk : Auto rows (calculated, not editable) and timing, shown under the P4 feed boxes
if _p4_cockpit_auto:
    with st.sidebar:
        feed_title("Auto : TL Disbursement & Own Contribution (Rs Lacs), M1-M12")
        gdf(pd.DataFrame([{"Auto": "TL Sanction & Disbursement", **dict(zip(months, p4_tl_disb))},
                                   {"Auto": "Capex Margin & Own Cash Contribution", **dict(zip(months, p4_own))}]).style.format({m: "{:,.2f}" for m in months}),
                     hide_index=True, width="stretch")
        st.caption(f"Completion : {months[p4_completion]} {'(Auto)' if p4s.get('completion', 'Auto') == 'Auto' else ''}  |  "
                   f"Capitalisation, production & sale start : {display_columns[p4_start]}  |  New P&M capitalised : {p4_asset_value:,.2f} L "
                   f"(incl. interest during construction {p4_idc:,.2f} L)")
        if p4_completion_warn: st.warning(p4_completion_warn)

# Add Product desk : timing and capex funding of every added product (calculated, not editable)
if _ap_cockpit_auto and added_products:
    with st.sidebar:
        feed_title("Added products - timing & capex funding (Auto)")
        _sum_rows = [{"Product": _p, "Capex Completion": (months[NPD[_p]["comp"]] if NPD[_p]["capex_total"] > 0 else "-"),
                      "Sale & Production Start": display_columns[NPD[_p]["start"]], "Capex + Installation (Rs Lacs)": NPD[_p]["capex_total"],
                      "TL Disbursed": sum(NPD[_p]["tl_disb"]), "Own Contribution": sum(NPD[_p]["own"]),
                      "New P&M Capitalised (Rs Lacs)": asset_val[_p]} for _p in added_names]
        gdf(pd.DataFrame(_sum_rows).style.format({c: "{:,.2f}" for c in ["Capex + Installation (Rs Lacs)", "TL Disbursed", "Own Contribution", "New P&M Capitalised (Rs Lacs)"]}),
                     hide_index=True, width="stretch")
        for _p in added_names:
            if NPD[_p]["warn"]: st.warning(f"{_p} : {NPD[_p]['warn']}")

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
        df_pl_master_raw.drop(columns=["_prod", "_dv"]).to_excel(writer, sheet_name="Master Financial P&L Statement", index=False)
        PL_PCT["All"].drop(columns=["_prod", "_dv"]).to_excel(writer, sheet_name="PL % against Sales", index=False)
        PL_PU["All"].drop(columns=["_prod", "_dv"]).to_excel(writer, sheet_name="PL Cost per Kg", index=False)
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
            build_costing_df(_p).to_excel(writer, sheet_name=f"Costing {_p}"[:31], index=False)
        debtor_due_df(products).to_excel(writer, sheet_name="Due Forecast Sales", index=False)
        debtor_flow_df(products).to_excel(writer, sheet_name="Debtors & Cash Flow", index=False)
        creditor_due_df().to_excel(writer, sheet_name="Due to Suppliers", index=False)
        creditor_flow_df().to_excel(writer, sheet_name="Creditors & Cash Outflow", index=False)
        wc_req_df()[0].to_excel(writer, sheet_name="WC Requirement", index=False)
        wc_dp_df()[0].to_excel(writer, sheet_name="WC Borrowing & Interest", index=False)
        _r = 0
        for _h, _d in far_tables():
            pd.DataFrame([{"Asset": _h}]).to_excel(writer, sheet_name="FAR", index=False, header=False, startrow=_r)
            _d.to_excel(writer, sheet_name="FAR", index=False, startrow=_r + 1)
            _r += len(_d) + 4
        _r = 0
        for _h, _d in tl_tables():
            pd.DataFrame([{"Term Loan": _h}]).to_excel(writer, sheet_name="TL", index=False, header=False, startrow=_r)
            _d.to_excel(writer, sheet_name="TL", index=False, startrow=_r + 1)
            _r += len(_d) + 4
        df_cf.drop(columns=["_fmt", "_prod", "_dv"]).to_excel(writer, sheet_name="Cash Flow", index=False)

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
                     "Indirect Expenses": "Indirect Expenses Feed", "WC": "WC Feed", "PL": "RM Val Feed",
                     "FAR": "FAR Feed", "TL": "TL Feed", "CF": "WC Feed"};
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
                S(b, "color", col); S(b, "font-weight", "400");
                S(b, "background", sel ? "#0B3D6B" : "transparent");
                S(b, "border", "none");
                S(b, "border-left", "4px solid " + (sel ? "#E53935" : "#D4AF37"));
                S(b, "box-shadow", "none");
                b.querySelectorAll("*").forEach(c => { S(c, "color", col); S(c, "font-weight", "400"); });
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
