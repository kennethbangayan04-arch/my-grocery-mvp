import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import urllib.parse

# --- 1. DATA ENGINE (The "Reactor" Logic) ---
DB_FILE = 'negosyo_pro_master.json'

def load_data():
    # Default data if the file is missing
    default_data = {
        'sales': [], 
        'inventory': {
            "4800016644801": {"NAME": "LUCKY ME", "STOCK": 20, "ALERT": 5, "BOUGHT": 12.0, "SRP": 15.0},
            "12345": {"NAME": "RICE (1KG)", "STOCK": 50, "ALERT": 10, "BOUGHT": 45.0, "SRP": 55.0}
        }, 
        'purchase_receipts': [], 
        'debts': []
    }
    
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: 
                data = json.load(f)
                # MIGRATION: Auto-fix old data to include BOUGHT and SRP
                for k, v in data['inventory'].items():
                    if "BOUGHT" not in v: v["BOUGHT"] = v.get("cost", v.get("price", 0))
                    if "SRP" not in v: v["SRP"] = v.get("price", 0)
                    if "NAME" not in v: v["NAME"] = v.get("name", "Unknown").upper()
                    if "STOCK" not in v: v["STOCK"] = v.get("stock", 0)
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
        "tabs": ["⚡ QUICK SALE", "📦 INVENTORY", "🧾 EXPENSES", "📊 REPORTS", "💳 UTANG"],
        "cost_label": "BOUGHT PRICE (COST)", "srp_label": "SELLING PRICE (SRP)",
        "btn_reg": "REGISTER PRODUCT", "btn_sell": "COMPLETE SALE", "markup": "MARKUP (PROFIT/UNIT)"
    },
    "Tagalog": {
        "tabs": ["⚡ BENTA", "📦 IMBENTARYO", "🧾 GASTO", "📊 ULAT", "💳 UTANG"],
        "cost_label": "PRESYONG BILI (PUHUNAN)", "srp_label": "PRESYONG TINDA (SRP)",
        "btn_reg": "I-REHISTRO ANG PRODUKTO", "btn_sell": "TAPUSIN ANG BENTA", "markup": "TUBO BAWAT ISA"
    }
}[lang]

st.title("🏪 Negosyo Pro")
tabs = st.tabs(D["tabs"])

# --- TAB 1: QUICK SALE (The Checkout) ---
with tabs[0]:
    st.subheader(D["tabs"][0])
    if 'cart' not in st.session_state: st.session_state.cart = []
    
    c_in, q_in = st.columns([3, 1])
    barcode = c_in.text_input("SCAN / TYPE BARCODE", key="sale_scan")
    qty = q_in.number_input("QTY", min_value=1, value=1)
    
    if barcode in st.session_state.db['inventory']:
        item = st.session_state.db['inventory'][barcode]
        st.info(f"✨ **{item['NAME']}** | SRP: ₱{item['SRP']:.2f} | STOCK: {item['STOCK']}")
        if st.button("➕ ADD TO CART"):
            if item['STOCK'] >= qty:
                st.session_state.cart.append({
                    "CODE": barcode, "ITEM": item['NAME'], "QTY": qty, 
                    "BOUGHT": item['BOUGHT'], "SRP": item['SRP'], "SUBTOTAL": item['SRP'] * qty
                })
                st.rerun()
            else: st.error("No Stock!")

    if st.session_state.cart:
        st.write("---")
        df_cart = pd.DataFrame(st.session_state.cart)
        st.table(df_cart[["ITEM", "QTY", "SRP", "SUBTOTAL"]])
        total = df_cart["SUBTOTAL"].sum()
        st.header(f"TOTAL: ₱{total:,.2f}")
        
        if st.button("🏁 " + D["btn_sell"], type="primary"):
            for entry in st.session_state.cart:
                st.session_state.db['inventory'][entry['CODE']]['STOCK']
