import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import urllib.parse

# --- 1. DATA ENGINE (Profit-Ready) ---
DB_FILE = 'negosyo_pro_master.json'

def load_data():
    # Default Starting Data
    default_data = {
        'sales': [], 
        'inventory': {
            "4800016644801": {"name": "Lucky Me", "stock": 20, "min_alert": 5, "cost": 12.0, "srp": 15.0},
            "12345": {"name": "Rice (1kg)", "stock": 50, "min_alert": 10, "cost": 45.0, "srp": 55.0}
        }, 
        'purchase_receipts': [], 
        'debts': []
    }
    
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
                # Migration: Ensure all items have cost/srp to prevent KeyErrors
                for k, v in data['inventory'].items():
                    if 'cost' not in v: v['cost'] = v.get('price', 0)
                    if 'srp' not in v: v['srp'] = v.get('price', 0)
                return data
        except:
            return default_data
    return default_data

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def save_data():
    with open(DB_FILE, 'w') as f:
        json.dump(st.session_state.db, f)

# --- 2. MULTI-LANGUAGE DICTIONARY ---
st.set_page_config(page_title="Negosyo Pro MVP", layout="wide", page_icon="🏪")
lang = st.sidebar.radio("Wika / Language", ["English", "Tagalog"])

D = {
    "English": {
        "tabs": ["⚡ Sale", "📦 Inventory", "🧾 Expenses", "📊 Reports", "💳 Utang"],
        "cost": "Cost Price", "srp": "Selling Price (SRP)", "stock": "Stock",
        "btn_reg": "Register Product", "btn_sell": "Complete Sale",
        "rev": "Revenue", "prof": "Profit", "exp": "Expenses",
        "sms": "Send SMS Reminder", "low": "⚠️ LOW STOCK!"
    },
    "Tagalog": {
        "tabs": ["⚡ Benta", "📦 Imbentaryo", "🧾 Gasto", "📊 Ulat", "💳 Utang"],
        "cost": "Puhunan", "srp": "Presyong Tinda", "stock": "Bilang",
        "btn_reg": "I-rehistro", "btn_sell": "Itala ang Benta",
        "rev": "Kabuuang Benta", "prof": "Kita", "exp": "Gasto",
        "sms": "Mag-SMS Paalala", "low": "⚠️ KONTI NA LANG!"
    }
}[lang]

st.title("🏪 Negosyo Pro")
tabs = st.tabs(D["tabs"])

# --- TAB 1: QUICK SALE ---
with tabs[0]:
    st.subheader(D["tabs"][0])
    b_in = st.text_input("Barcode / Code", key="sale_input")
    if b_in in st.session_state.db['inventory']:
        item = st.session_state.db['inventory'][b_in]
        st.info(f"**{item['name']}** | SRP: ₱{item['srp']:.2f} | {D['stock']}: {item['stock']}")
        if st.button(D["btn_sell"]):
            if item['stock'] > 0:
                st.session_state.db['inventory'][b_in]['stock'] -= 1
                st.session_state.db['sales'].append({
                    "date": str(datetime.now().date()), 
                    "item": item['name'], "cost": item['cost'], "srp": item['srp']
                })
                save_data(); st.success("Success!"); st.rerun()
            else: st.error("No Stock!")

# --- TAB 2: INVENTORY (Profit Margin Focus) ---
with tabs[1]:
    st.subheader(D["tabs"][1])
    # Alerts
    for k, v in st.session_state.db['inventory'].items():
        if v['stock'] <= v['min_alert']: st.warning(f"{D['low
