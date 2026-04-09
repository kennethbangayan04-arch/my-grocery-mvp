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

# --- 2. CONFIG & MODERN UI CSS ---
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
    .block-container { padding-top: 1.5rem; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR (Fixed Order) ---
st.sidebar.title("🏪 Bentamate")
st.sidebar.markdown("##### Smart Business Companion")
st.sidebar.write("---")

# Language Selection (Must be BEFORE dictionary mapping)
lang_choice = st.sidebar.radio("Wika / Language", ["English", "Tagalog"])

# Fully Translated Dictionary
translations = {
    "English": {
        "tabs": ["⚡ Quick Sale", "📦 Inventory", "🧾 Expenses", "📊 Reports", "💳 Debt"],
        "rev": "Total Sales Today", "inv": "Total Products", "exp": "Total Expenses", "low": "Low Stock",
        "sale_h": "Register a Sale", "input_c": "Scan/Type Barcode", "qty": "Quantity", "total": "TOTAL",
        "btn_sell": "🏁 Complete Sale", "btn_clear": "🗑️ Clear Cart", "low_stock": "⚠️ LOW STOCK!",
        "auth_title": "👤 Account Access", "auth_choice": "Choose Action", "sign_in": "Sign In", 
        "create_acc": "Create Account", "login_btn": "Login", "reg_btn": "Register",
        "inv_code": "CODE", "inv_name": "NAME", "inv_stock": "STOCK", "inv_srp": "SRP", 
        "inv_add": "ADD", "inv_del": "DEL", "search_p": "🔍 Search Product"
    },
    "Tagalog": {
        "tabs": ["⚡ Benta", "📦 Imbentaryo", "🧾 Gasto", "📊 Ulat", "💳 Utang"],
        "rev": "Benta Ngayon", "inv": "Mga Produkto", "exp": "Kabuuang Gasto", "low": "Konti na lang",
        "sale_h": "Itala ang Benta", "input_c": "I-scan ang Barcode", "qty": "Dami", "total": "KABUUAN",
        "btn_sell": "🏁 Tapusin ang Benta", "btn_clear": "🗑️ Burahin ang Cart", "low_stock": "⚠️ KONTI NA LANG!",
        "auth_title": "👤 Access sa Account", "auth_choice": "Pumili ng Aksyon", "sign_in": "Mag-log In", 
        "create_acc": "Gumawa ng Account", "login_btn": "Pumasok", "reg_btn": "I-rehistro",
        "inv_code": "KODIGO", "inv_name": "PANGALAN", "inv_stock": "STOK", "inv_srp": "PRESYO", 
        "inv_add": "DAGDAG", "inv_del": "BURA", "search_p": "🔍 Maghanap ng Produkto"
    }
}
D = translations[lang_choice]

# Account Access Section
with st.sidebar.popover(D["auth_title"], use_container_width=True):
    auth_mode = st.radio(D["auth_choice"], [D["sign_in"], D["create_acc"]])
    if auth_mode == D["sign_in"]:
        st.text_input("Username", placeholder="Username")
        st.text_input("Password", type="password")
        if st.button(D["login_btn"], use_container_width=True):
            st.success("Tagumpay ang pag-log in!")
    else:
        st.text_input("Full Name")
        st.text_input("Email", placeholder="juan@email.com")
        st.text_input("Password", type="password")
        if st.button(D["reg_btn"], use_container_width=True):
            st.toast("Account created (Demo Mode)!", icon="🎉")

# Vertical Spacing for Reset
for _ in range(15):
    st.sidebar.write("")

st.sidebar.write("---")
if st.sidebar.button("🗑️ Reset for New Owner", key="reset_button", use_container_width=True):
    st.session_state.db = {'sales': [], 'inventory': {}, 'purchase_receipts': [], 'debts': []}
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.rerun()

# --- 4. DASHBOARD CALCULATIONS ---
st.title("🏪 Bentamate")
st.markdown(f"##### {D['sale_h'] if lang_choice == 'Tagalog' else 'Smart Business Companion'}")

s_df = pd.DataFrame(st.session_state.db['sales'])
p_df = pd.DataFrame(st.session_state.db['purchase_receipts'])
today_str = datetime.now().strftime("%Y-%m-%d")

today_sales = s_df[s_df['date'].str.contains(today_str)]['total'].sum() if not s_df.empty else 0
total_products = len(st.session_state.db['inventory'])
total_expenses = p_df['total'].sum() if not p_df.empty else 0
low_stock_threshold = 5 
low_stock_count = sum(1 for v in st.session_state.db['inventory'].values() if v['stock'] <= low_stock_threshold)

# --- 5. TOP DASHBOARD DISPLAY ---
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="metric-card" style="border-left-color: #fce4ec;"><div class="metric-title">{D["rev"]}</div><div class="metric-value">₱{today_sales:,.2f}</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-card" style="border-left-color: #e3f2fd;"><div class="metric-title">{D["inv"]}</div><div class="metric-value">{total_products}</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="metric-card" style="border-left-color: #fff3e0;"><div class="metric-title">{D["exp"]}</div><div class="metric-value">₱{total_expenses:,.2f}</div></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="metric-card" style="border-left-color: #e0f2f1;"><div class="metric-title">{D["low"]}</div><div class="metric-value">{low_stock_count}</div></div>', unsafe_allow_html=True)

if low_stock_count > 0:
    st.error(f"**{D['low_stock']}** {low_stock_count} items are below the safety limit!")

st.write("---")

t1, t2, t3, t4, t5 = st.tabs(D["tabs"])

# --- TAB 1: QUICK SALE ---
with t1:
    st.markdown(f"### {D['sale_h']}")
    if 'cart' not in st.session_state: st.session_state.cart = []
    col_in, col_qty = st.columns([3, 1])
    b_in = col_in.text_input(D["input_c"], placeholder=D["input_c"], key="barcode_input", label_visibility="collapsed")
    q_in = col_qty.number_input(D["qty"], min_value=1, value=1, key="qty_input", label_visibility="collapsed")
    
    if b_in in st.session_state.db['inventory']:
        item = st.session_state.db['inventory'][b_in]
        st.info(f"✨ **{item['name']}** | ₱{item['price']:.2f} | Stock: {item['stock']}")
        if st.button("➕ Add to Cart", use_container_width=True, key="add_to_cart"):
            if item['stock'] >= q_in:
                st.session_state.cart.append({"code": b_in, "name": item['name'], "qty": q_in, "bought": item.get('bought', 0), "price": item['price'], "subtotal": item['price'] * q_in})
                st.rerun()
            else: st.error("Out of stock!" if lang_choice == "English" else "Walang stock!")

    if st.session_state.cart:
        st.write("---")
        cart_df = pd.DataFrame(st.session_state.cart)
        display_cart = cart_df[['name', 'qty', 'price', 'subtotal']].copy()
        display_cart.columns = [D["inv_name"], D["qty"], D["inv_srp"], D["total"]] 
        formatted_cart = display_cart.style.format({D["inv_srp"]: "₱{:,.2f}", D["total"]: "₱{:,.2f}"})
        st.table(formatted_cart)
        total_bill = cart_df['subtotal'].sum()
        st.header(f"{D['total']}: ₱{total_bill:,.2f}")
        
        cp, cc = st.columns(2)
        if cp.button(D["btn_sell"], type="primary", use_container_width=True):
            trans_id = datetime.now().strftime("%H%M%S") 
            for entry in st.session_state.cart:
                st.session_state.db['inventory'][entry['code']]['stock'] -= entry['qty']
                st.session_state.db['sales'].append({
                    "trans_id": trans_id,
                    "date": str(datetime.now().strftime("%Y-%m-%d %H:%M")), 
                    "item": entry['name'], "qty": entry['qty'], 
                    "bought": entry['bought'], "srp": entry['price'], "total": entry['subtotal']
                })
            save_data(); st.session_state.cart = []; st.balloons(); st.rerun()
        if cc.button(D["btn_clear"], use_container_width=True): st.session_state.cart = []; st.rerun()

# --- TAB 2: INVENTORY ---
with t2:
    st.markdown(f"### 📦 {D['tabs'][1]}")
    with st.expander(D["sale_h"] if lang_choice == "Tagalog" else "Register New Product"):
        with st.form("reg_form", clear_on_submit=True):
            c_i = st.text_input(D["inv_code"])
            n_i = st.text_input(D["inv_name"]).upper()
            cs, cb, cp = st.columns(3)
            s_i = cs.number_input(D["inv_stock"], min_value=0)
            b_i = cb.number_input("Cost" if lang_choice == "English" else "Puhunan", min_value=0.0)
            p_i = cp.number_input(D["inv_srp"], min_value=0.0)
            if st.form_submit_button("Save" if lang_choice == "English" else "I-save"):
                st.session_state.db['inventory'][c_i] = {"name": n_i, "stock": s_i, "bought": b_i, "price": p_i}
                save_data(); st.rerun()

    st.write("---")
    search_query = st.text_input(D["search_p"], key="inv_search").upper()

    if st.session_state.db['inventory']:
        h1, h2, h3, h4, h5, h6 = st.columns([1.5, 2.5, 1, 1, 1.5, 1])
        h1.write(f"**{D['inv_code']}**"); h2.write(f"**{D['inv_name']}**"); h3.write(f"**{D['inv_stock']}**"); h4.write(f"**{D['inv_srp']}**"); h5.write(f"**{D['inv_add']}**"); h6.write(f"**{D['inv_del']}**")
        for code, det in list(st.session_state.db['inventory'].items()):
            if search_query == "" or search_query in code.upper() or search_query in det['name'].upper():
                r1, r2, r3, r4, r5, r6 = st.columns([1.5, 2.5, 1, 1, 1.5, 1])
                r1.write(f"`{code}`"); r2.write(det['name'])
                if det['stock'] <= low_stock_threshold: r3.write(f"🔴 **{det['stock']}**")
                else: r3.write(f"🟢 {det['stock']}")
                r4.write(f"₱{det['price']:.2f}")
                with r5:
                    with st.popover("➕"):
                        amt = st.number_input(D["qty"], min_value=1, key=f"add_inv_{code}")
                        if st.button("Save", key=f"btn_inv_{code}"):
                            st.session_state.db['inventory'][code]['stock'] += amt
                            save_data(); st.rerun()
                if r6.button("🗑️", key=f"del_inv_{code}"):
                    del st.session_state.db['inventory'][code]; save_data(); st.rerun()

# Remaining tabs (Gasto, Ulat, Utang) follow the same D[key] logic...
