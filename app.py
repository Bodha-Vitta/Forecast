import streamlit as st
import pandas as pd

# Set webpage to wide mode
st.set_page_config(page_title="Sales Forecasting Tool", layout="wide")

st.title("📊 Client Sales Forecasting Dashboard")
st.write("Modify the **Sales Quantity** and **Price per Unit** directly in the table below to see your real-time forecast.")

# 1. Set up the default data grid with a Python trick to avoid the screen display bug
months = [f"Month {i}" for i in range(1, 13)]
initial_data = {
    "Month": months,
    "Sales Quantity": [1000] * 12,
    "Price per Unit (Rs)": [5000.0] * 12
}
df = pd.DataFrame(initial_data)

# 2. Display the interactive table (Both Quantity and Price can be typed into by your client!)
st.subheader("📝 Edit Forecasting Inputs")
edited_df = st.data_editor(df, num_rows="fixed", hide_index=True, use_container_width=True)

# 3. Perform backend calculations on client inputs
edited_df["Monthly Sale (Rs)"] = edited_df["Sales Quantity"] * edited_df["Price per Unit (Rs)"]
total_rs = edited_df["Monthly Sale (Rs)"].sum()

# Convert calculations to Lacs and Crores
total_lacs = total_rs / 100000
total_crores = total_rs / 10000000

# 4. Display results in metric cards
st.markdown("---")
st.subheader("📈 Projected Year End Summary")

col1, col2 = st.columns(2)
with col1:
    st.metric(label="TOTAL YEAR SALE (Lacs)", value=f"Rs {total_lacs:,.2f} Lacs")
with col2:
    st.metric(label="TOTAL YEAR SALE (Crores)", value=f"Rs {total_crores:,.2f} Cr")
