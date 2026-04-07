import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import urllib.parse

# --- 1. DATA ENGINE ---
DB_FILE = 'negosyo_pro_master.json'
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: 
                data = json.load(f)
                # This line ensures 'cost' exists even in old data
                for item in data['inventory'].values():
                    if 'cost' not in item: item['cost'] = item.get('price', 0)
                    if 'srp' not in item: item['srp'] = item.get('price', 0)
                return data
        except:
            pass
    return {
        'sales': [], 
        'inventory': {
            "4800016644801": {"name": "Lucky Me", "stock": 20, "min_alert": 5, "cost": 12.0, "srp": 15.0},
            "12345": {"name": "Rice (1kg)", "stock": 50, "min_alert": 10, "cost": 45.0, "srp": 55.0}
        }, 
        'purchase_receipts': [], 
        'debts': []
    }

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def save_data():
    with open(DB_FILE, 'w') as f: json.dump(st.session_state.db, f)

# --- 2. LANGUAGE DICTIONARY ---
st.set_page_config(page_title="Negosyo Pro MVP", layout="wide")
lang = st.sidebar.radio("Wika / Language", ["English", "Tagalog"])

D = {
    "English": {
        "tabs": ["⚡ Quick Sale", "📦 Inventory", "🧾 Purchase Receipts", "📊 Reports", "💳 Utang Tracker"],
        "cost": "Price Bought (Cost)", "srp": "Selling Price (SRP)", "markup": "Profit/Unit",
        "btn_reg": "Register Product", "name": "Product Name", "stock": "Stock",
        "rev": "Total Revenue", "exp": "Total Expenses", "prof": "Estimated Profit"
    },
    "Tagalog": {
        "tabs": ["⚡ Mabilisang Benta", "📦 Imbentaryo", "🧾 Resibo ng Binili", "📊 Mga Ulat", "💳 Listahan ng Utang"],
        "cost": "Presyong Bili (Puhunan)", "srp": "Presyong Tinda (SRP)", "markup": "Tubo Bawat Isa",
        "btn_reg": "I-rehistro ang Produkto", "name": "Pangalan ng Produkto", "stock": "Bilang ng Stock",
        "rev": "Kabuuang Benta", "exp": "Kabuuang Gasto", "prof": "Inaasahang Kita"
    }
}[lang]

st.title(f"🏪 Negosyo Pro")
tabs = st.tabs(D["tabs"])

# --- TAB 1: QUICK SALE ---
with tabs[0]:
    b_in = st.text_input("Barcode", key="sale_in")
    if b_in in st.session_state.db['inventory']:
        item = st.session_state.db['inventory'][b_in]
        st.info(f"**{item['name']}** | SRP: ₱{item['srp']}")
        if st.button("Sold"):
            st.session_state.db['inventory'][b_in]['stock'] -= 1
            st.session_state.db['sales'].append({
                "date": str(datetime.now().date()), 
                "item": item['name'], 
                "cost": item['cost'], 
                "srp": item['srp']
            })
            save_data(); st.rerun()

# --- TAB 2: INVENTORY (Cost vs SRP) ---
with tabs[1]:
    with st.expander(D["btn_reg"]):
        with st.form("add_item"):
            c_i = st.text_input("Barcode")
            n_i = st.text_input(D["name"])
            col1, col2, col3 = st.columns(3)
            s_i = col1.number_input(D["stock"], min_value=0)
            cost_i = col2.number_input(D["cost"], min_value=0.0)
            srp_i = col3.number_input(D["srp"], min_value=0.0)
            if st.form_submit_button(D["btn_reg"]):
                st.session_state.db['inventory'][c_i] = {"name": n_i, "stock": s_i, "cost": cost_i, "srp": srp_i, "min_alert": 5}
                save_data(); st.rerun()
    
    # Display Table with Markup calculation
    df_inv = pd.DataFrame.from_dict(st.session_state.db['inventory'], orient='index').reset_index()
    df_inv['Markup'] = df_inv['srp'] - df_inv['cost']
    st.dataframe(df_inv, use_container_width=True)

# --- TAB 3: RECEIPTS ---
with tabs[2]:
    with st.form("exp"):
        s_n = st.text_input("Store"); a_p = st.number_input("Amount")
        if st.form_submit_button("Save"):
            st.session_state.db['purchase_receipts'].append({"date": str(datetime.now().date()), "store": s_n, "total": a_p})
            save_data(); st.rerun()

# --- TAB 4: REPORTS (True Profit) ---
with tabs[3]:
    st.subheader(D["rep_header"] if "rep_header" in D else "Summary")
    sales_df = pd.DataFrame(st.session_state.db['sales'])
    if not sales_df.empty:
        total_rev = sales_df['srp'].sum()
        # True Profit is SRP - Cost of items sold
        true_profit = (sales_df['srp'] - sales_df['cost']).sum()
        
        c1, c2 = st.columns(2)
        c1.metric(D["rev"], f"₱{total_rev:,.2f}")
        c2.metric(D["prof"], f"₱{true_profit:,.2f}")
        st.write("Recent Sales History:")
        st.dataframe(sales_df)
    else:
        st.info("No sales data.")

# --- TAB 5: UTANG TRACKER ---
with tabs[4]:
    st.subheader(T[4]) # "Utang Tracker" or "Listahan ng Utang"
    
    # 1. Input Form for New Debt
    with st.expander("➕ Register New Utang", expanded=True):
        u_col1, u_col2, u_col3 = st.columns(3)
        u_name = u_col1.text_input("Customer Name")
        u_phone = u_col2.text_input("Mobile Number (e.g. 0917...)")
        u_amt = u_col3.number_input("Amount Owed (₱)", min_value=0.0)
        
        if st.button("📝 Save Debt Record"):
            if u_name and u_phone:
                st.session_state.db['debts'].append({
                    "name": u_name, 
                    "phone": u_phone, 
                    "amount": u_amt, 
                    "date": str(datetime.now().date())
                })
                save_data()
                st.success(f"Recorded debt for {u_name}!")
                st.rerun()
            else:
                st.error("Please provide Name and Mobile Number.")

    # 2. Display Table of Active Debts
    if st.session_state.db['debts']:
        st.markdown("### Active Debts")
        debt_df = pd.DataFrame(st.session_state.db['debts'])
        # Rename columns for the display table
        debt_df.columns = ["Customer Name", "Mobile Number", "Amount (₱)", "Date Issued"]
        st.dataframe(debt_df, use_container_width=True)
        
        st.markdown("---")
        
        # 3. Automated Reminder Logic
        st.subheader("📲 Send SMS Reminder")
        target = st.selectbox("Select Customer to Remind", [d['name'] for d in st.session_state.db['debts']])
        
        # Find the specific data for the selected customer
        customer_data = next(item for item in st.session_state.db['debts'] if item['name'] == target)
        
        # Format the reminder message
        msg = "Good day {}, paalala lang po sa inyong utang na ₱{:,.2f}. Salamat!".format(
            customer_data['name'], 
            customer_data['amount']
        )
        
        st.code(msg, language="text")
        st.caption("Copy the text above to send via SMS or Messenger.")
    else:
        st.info("No credit records found.")
