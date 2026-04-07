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
    return {'sales': [], 'inventory': {"4800016644801": {"name": "Lucky Me", "stock": 20, "min_alert": 5, "price": 15}, "12345": {"name": "Rice (1kg)", "stock": 50, "min_alert": 10, "price": 55}}, 'purchase_receipts': [], 'debts': []}

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def save_data():
    with open(DB_FILE, 'w') as f: json.dump(st.session_state.db, f)

# --- 2. THE DICTIONARY (Every Word is Here) ---
st.set_page_config(page_title="Negosyo Pro MVP", layout="wide")
lang = st.sidebar.radio("Wika / Language", ["English", "Tagalog"])

D = {
    "English": {
        "tabs": ["⚡ Quick Sale", "📦 Inventory", "🧾 Purchase Receipts", "📊 Reports", "💳 Utang Tracker"],
        "sale_header": "Register a Sale",
        "input_code": "Scan/Type Barcode",
        "btn_sell": "Complete Sale",
        "inv_header": "Stock Management",
        "btn_reg": "Register New Product",
        "name": "Product Name", "stock": "Current Stock", "price": "Price",
        "receipt_header": "Log Grocery Receipts",
        "store": "Store Name", "amt": "Amount Spent", "photo": "Upload Photo",
        "btn_save": "Save to Archive",
        "rep_header": "Financial Summary",
        "rev": "Total Sales", "exp": "Total Expenses", "prof": "Net Profit",
        "utang_header": "Debt Management",
        "cust": "Customer Name", "phone": "Mobile Number", "debt_amt": "Debt Amount",
        "btn_sms": "Send SMS Reminder",
        "low_stock": "⚠️ LOW STOCK!"
    },
    "Tagalog": {
        "tabs": ["⚡ Mabilisang Benta", "📦 Imbentaryo", "🧾 Resibo ng Binili", "📊 Mga Ulat", "💳 Listahan ng Utang"],
        "sale_header": "Itala ang Benta",
        "input_code": "I-scan/I-type ang Barcode",
        "btn_sell": "Tapusin ang Benta",
        "inv_header": "Pamamahala ng Stock",
        "btn_reg": "I-rehistro ang Produkto",
        "name": "Pangalan ng Produkto", "stock": "Bilang ng Stock", "price": "Presyo",
        "receipt_header": "Itala ang mga Resibo",
        "store": "Pangalan ng Tindahan", "amt": "Halagang Nagastos", "photo": "I-upload ang Larawan",
        "btn_save": "I-save sa Archive",
        "rep_header": "Ulat ng Kita at Gasto",
        "rev": "Kabuuang Benta", "exp": "Kabuuang Gasto", "prof": "Netong Kita",
        "utang_header": "Listahan ng mga Utang",
        "cust": "Pangalan ng Customer", "phone": "Numero ng Telepono", "debt_amt": "Halaga ng Utang",
        "btn_sms": "Magpadala ng SMS",
        "low_stock": "⚠️ MABABA ANG STOCK!"
    }
}[lang]

# --- 3. UI LAYOUT ---
st.title(f"🏪 Negosyo Pro")
tabs = st.tabs(D["tabs"])

# TAB 1: QUICK SALE
with tabs[0]:
    st.subheader(D["sale_header"])
    b_in = st.text_input(D["input_code"], key="sale_in")
    if b_in in st.session_state.db['inventory']:
        item = st.session_state.db['inventory'][b_in]
        st.info(f"**{item['name']}** | ₱{item['price']}")
        if st.button(D["btn_sell"]):
            st.session_state.db['inventory'][b_in]['stock'] -= 1
            st.session_state.db['sales'].append({"date": str(datetime.now().date()), "item": item['name'], "total": item['price']})
            save_data(); st.rerun()

# TAB 2: INVENTORY
with tabs[1]:
    st.subheader(D["inv_header"])
    for k, v in st.session_state.db['inventory'].items():
        if v['stock'] <= v['min_alert']: st.warning(f"{D['low_stock']} {v['name']} ({v['stock']})")
    
    with st.expander(D["btn_reg"]):
        with st.form("add_form"):
            c_i = st.text_input("Code"); n_i = st.text_input(D["name"])
            s_i = st.number_input(D["stock"], min_value=0); p_i = st.number_input(D["price"], min_value=0.0)
            if st.form_submit_button(D["btn_reg"]):
                st.session_state.db['inventory'][c_i] = {"name": n_i, "stock": s_i, "price": p_i, "min_alert": 5}
                save_data(); st.rerun()
    st.dataframe(pd.DataFrame.from_dict(st.session_state.db['inventory'], orient='index'))

# TAB 3: RECEIPTS (Expense)
with tabs[2]:
    st.subheader(D["receipt_header"])
    with st.form("p_form"):
        s_n = st.text_input(D["store"]); a_p = st.number_input(D["amt"])
        u_p = st.file_uploader(D["photo"], type=['jpg','png'])
        if st.form_submit_button(D["btn_save"]):
            st.session_state.db['purchase_receipts'].append({"date": str(datetime.now().date()), "store": s_n, "total": a_p})
            save_data(); st.success("Saved!"); st.rerun()
    st.dataframe(pd.DataFrame(st.session_state.db['purchase_receipts']))

# TAB 4: REPORTS
with tabs[3]:
    st.subheader(D["rep_header"])
    rev = sum([s['total'] for s in st.session_state.db['sales']])
    exp = sum([p['total'] for p in st.session_state.db['purchase_receipts']])
    c1, c2, c3 = st.columns(3)
    c1.metric(D["rev"], f"₱{rev:,.2f}")
    c2.metric(D["exp"], f"₱{exp:,.2f}")
    c3.metric(D["prof"], f"₱{rev-exp:,.2f}")

# TAB 5: UTANG
with tabs[4]:
    st.subheader(D["utang_header"])
    u_n = st.text_input(D["cust"]); u_p = st.text_input(D["phone"]); u_a = st.number_input(D["debt_amt"])
    if st.button(f"➕ {D['utang_header']}"):
        st.session_state.db['debts'].append({"name": u_n, "phone": u_p, "amount": u_a})
        save_data(); st.rerun()
    if st.session_state.db['debts']:
        d_df = pd.DataFrame(st.session_state.db['debts'])
        st.table(d_df)
        sel = st.selectbox(D["cust"], d_df['name'])
        pers = next(i for i in st.session_state.db['debts'] if i['name'] == sel)
        msg = f"Paalala sa utang: ₱{pers['amount']}"
        st.link_button(D["btn_sms"], f"sms:{pers['phone']}?body={urllib.parse.quote(msg)}")
