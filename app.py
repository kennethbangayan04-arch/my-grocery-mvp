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
            with open(DB_FILE, 'r') as f: return json.load(f)
        except: pass
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
            save
