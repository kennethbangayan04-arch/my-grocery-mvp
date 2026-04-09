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
                return data
        except: pass
    return {'sales': [], 'inventory': {}, 'purchase_receipts': [], 'debts': []}

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def save_data():
    with open(DB_FILE, 'w') as f:
        json.dump(st.session_state.db, f)

# --- 2. CONFIG & UI ---
st.set_page_config(page_title="Bentamate", layout="wide", page_icon="🏪")

st.markdown("""
    <style>
    .metric-card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 6px solid #FFC0CB;
        margin-bottom: 10px;
    }
    .metric-title { font-size: 13px; color: #757575; font-weight: bold; text-transform: uppercase; }
    .metric-value { font-size: 24px; font-weight: bold; color: #212121; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

lang = st.sidebar.radio("Wika / Language", ["English", "Tagalog"])

D = {
    "English": {
        "tabs": ["⚡ Quick Sale", "📦 Inventory", "🧾 Expenses", "📊 Reports", "💳 Utang"],
        "rev": "Total Sales Today", "inv": "Total Products", "exp": "Total Expenses", "low": "Low Stock",
        "sale_h": "Register a Sale", "input_c": "Scan/Type Barcode", "qty": "Quantity", "total": "TOTAL",
        "btn_sell": "🏁 Complete Sale", "btn_clear": "🗑️ Clear Cart", "low_stock": "⚠️ LOW STOCK!"
    },
    "Tagalog": {
        "tabs": ["⚡ Benta", "📦 Imbentaryo", "🧾 Gasto", "📊 Ulat", "💳 Utang"],
        "rev": "Benta Ngayon", "inv": "Produkto", "exp": "Kabuuang Gasto", "low": "Konti na lang",
        "sale_h": "Itala ang Benta", "input_c": "I-scan ang Barcode", "qty": "Dami", "total": "KABUUAN",
        "btn_sell": "🏁 Tapusin ang Benta", "btn_clear": "🗑️ Burahin ang Cart", "low_stock": "⚠️ KONTI NA LANG!"
    }
}[lang]

# --- DASHBOARD LOGIC ---
s_df = pd.DataFrame(st.session_state.db['sales'])
p_df = pd.DataFrame(st.session_state.db['purchase_receipts'])
today_sales = s_df[s_df['date'].str.contains(datetime.now().strftime("%Y-%m-%d"))]['total'].sum() if not s_df.empty else 0
low_stock_count = sum(1 for v in st.session_state.db['inventory'].values() if v['stock'] <= 5)

st.title("🏪 Bentamate")
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="metric-card"><div class="metric-title">{D["rev"]}</div><div class="metric-value">₱{today_sales:,.2f}</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-card"><div class="metric-title">{D["inv"]}</div><div class="metric-value">{len(st.session_state.db["inventory"])}</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="metric-card"><div class="metric-title">{D["exp"]}</div><div class="metric-value">₱{p_df["total"].sum() if not p_df.empty else 0:,.2f}</div></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="metric-card"><div class="metric-title">{D["low"]}</div><div class="metric-value">{low_stock_count}</div></div>', unsafe_allow_html=True)

if low_stock_count > 0: st.error(D['low_stock'])

st.write("---")
t1, t2, t3, t4, t5 = st.tabs(D["tabs"])

# --- TAB 1: QUICK SALE ---
with t1:
    st.markdown(f"### {D['sale_h']}")
    if 'cart' not in st.session_state: st.session_state.cart = []
    col_in, col_qty = st.columns([3, 1])
    b_in = col_in.text_input(D["input_c"], key="barcode_input")
    q_in = col_qty.number_input(D["qty"], min_value=1, value=1)
    
    if b_in in st.session_state.db['inventory']:
        item = st.session_state.db['inventory'][b_in]
        if st.button("➕ Add to Cart"):
            if item['stock'] >= q_in:
                st.session_state.cart.append({"code": b_in, "name": item['name'], "qty": q_in, "bought": item.get('bought', 0), "price": item['price'], "subtotal": item['price'] * q_in})
                st.rerun()
            else: st.error("No stock!")

    if st.session_state.cart:
        df_cart = pd.DataFrame(st.session_state.cart)
        st.table(df_cart[['name', 'qty', 'price', 'subtotal']].style.format({"price": "{:.2f}", "subtotal": "{:.2f}"}))
        if st.button(D["btn_sell"], type="primary"):
            tid = datetime.now().strftime("%H%M%S")
            for e in st.session_state.cart:
                st.session_state.db['inventory'][e['code']]['stock'] -= e['qty']
                st.session_state.db['sales'].append({"trans_id": tid, "date": datetime.now().strftime("%Y-%m-%d %H:%M"), "item": e['name'], "qty": e['qty'], "bought": e['bought'], "srp": e['price'], "total": e['subtotal']})
            save_data(); st.session_state.cart = []; st.rerun()

# --- TAB 2: INVENTORY ---
with t2:
    st.markdown("### 📦 Inventory")
    with st.expander("Register New"):
        with st.form("reg_form"):
            c, n = st.text_input("Code"), st.text_input("Name").upper()
            s, b, p = st.number_input("Stock"), st.number_input("Cost"), st.number_input("SRP")
            if st.form_submit_button("Save"):
                st.session_state.db['inventory'][c] = {"name": n, "stock": s, "bought": b, "price": p}
                save_data(); st.rerun()
    
    sq = st.text_input("🔍 Search").upper()
    for code, d in list(st.session_state.db['inventory'].items()):
        if sq == "" or sq in code or sq in d['name']:
            col1, col2, col3 = st.columns([2,1,1])
            col1.write(f"**{d['name']}** ({code})")
            col2.write(f"Stock: {d['stock']}")
            if col3.button("🗑️", key=code):
                del st.session_state.db['inventory'][code]; save_data(); st.rerun()

# --- TAB 3: EXPENSES ---
with t3:
    with st.form("ex_form"):
        store, amt = st.text_input("Store"), st.number_input("Amount")
        if st.form_submit_button("Log"):
            st.session_state.db['purchase_receipts'].append({"date": datetime.now().strftime("%Y-%m-%d"), "store": store, "total": amt})
            save_data(); st.rerun()

# --- TAB 4: REPORTS ---
with t4:
    if not s_df.empty:
        st.metric("Total Profit (Markup)", f"₱{((s_df['srp'] - s_df['bought']) * s_df['qty']).sum():,.2f}")
        st.dataframe(s_df)

# --- TAB 5: UTANG (No Due Dates) ---
with t5:
    st.markdown("### 💳 Debt Registry")
    with st.form("u_form", clear_on_submit=True):
        un, up, ua = st.text_input("NAME").upper(), st.text_input("PHONE"), st.number_input("AMOUNT")
        if st.form_submit_button("ADD DEBT"):
            if sum(d['amount'] for d in st.session_state.db['debts'] if d['name'] == un) + ua > 500:
                st.error("Limit ₱500 reached!")
            else:
                st.session_state.db['debts'].append({"name": un, "phone": up, "amount": ua, "date": datetime.now().strftime("%Y-%m-%d")})
                save_data(); st.rerun()

    if st.session_state.db['debts']:
        d_df = pd.DataFrame(st.session_state.db['debts'])
        st.table(d_df.style.format({"amount": "{:.2f}"}))
        
        sel_idx = st.selectbox("SELECT CUSTOMER", range(len(st.session_state.db['debts'])), format_func=lambda x: st.session_state.db['debts'][x]['name'])
        pers = st.session_state.db['debts'][sel_idx]
        
        c_sms, c_paid = st.columns(2)
        sms_body = urllib.parse.quote(f"Hi {pers['name']}, reminder of your ₱{pers['amount']:.2f} balance at Bentamate.")
        c_sms.link_button("SEND SMS", f"sms:{pers['phone']}?body={sms_body}", use_container_width=True)
        if c_paid.button("MARK PAID", type="primary", use_container_width=True):
            st.session_state.db['debts'].pop(sel_idx); save_data(); st.rerun()
