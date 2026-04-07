import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import urllib.parse

# --- 1. DATA ENGINE (Clean Slate Version) ---
DB_FILE = 'negosyo_pro_master.json'

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: 
                data = json.load(f)
                # Migration: Ensure existing items have all necessary keys
                for k, v in data['inventory'].items():
                    if "bought" not in v: v["bought"] = v.get("price", 0) * 0.8
                return data
        except: 
            pass
    
    # START WITH EMPTY DATA (No Lucky Me, No Rice)
    return {
        'sales': [], 
        'inventory': {}, 
        'purchase_receipts': [], 
        'debts': []
    }

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def save_data():
    with open(DB_FILE, 'w') as f:
        json.dump(st.session_state.db, f)

# --- 2. THE BILINGUAL DICTIONARY ---
st.set_page_config(page_title="Negosyo Pro", layout="wide", page_icon="🏪")
lang = st.sidebar.radio("Wika / Language", ["English", "Tagalog"])

D = {
    "English": {
        "tabs": ["⚡ Quick Sale", "📦 Inventory", "🧾 Expenses", "📊 Reports", "💳 Utang"],
        "sale_h": "Register a Sale", "input_c": "Scan/Type Barcode", "qty": "Qty", "add_cart": "➕ Add to Cart",
        "cart_h": "🛒 Current Cart", "total": "TOTAL", "btn_checkout": "🏁 Complete Sale", "btn_clear": "🗑️ Clear Cart",
        "inv_h": "Stock Management", "btn_reg": "Register New Product", "name": "Product Name", 
        "stock": "Current Stock", "bought": "Bought Price (Cost)", "srp": "SRP (Selling Price)",
        "code": "CODE", "action": "ACTION", "add_stock": "ADD STOCK",
        "rec_h": "Log Expenses", "store": "Store Name", "amt": "Amount Spent", "photo": "Upload Photo", "btn_save": "Save",
        "rep_h": "Financial Summary", "rev": "Total Sales", "exp": "Total Expenses", "prof": "Net Profit",
        "ut_h": "Debt Management", "cust": "Customer Name", "phone": "Mobile Number", "debt_amt": "Debt Amount",
        "btn_sms": "Send SMS Reminder", "btn_paid": "✅ Mark as Paid", "low_stock": "⚠️ LOW STOCK!",
        "success": "Transaction Complete!"
    },
    "Tagalog": {
        "tabs": ["⚡ Benta", "📦 Imbentaryo", "🧾 Gasto", "📊 Ulat", "💳 Utang"],
        "sale_h": "Itala ang Benta", "input_c": "I-scan/I-type ang Barcode", "qty": "Dami", "add_cart": "➕ Idagdag sa Cart",
        "cart_h": "🛒 Mga Bibilhin", "total": "KABUUAN", "btn_checkout": "🏁 Tapusin ang Benta", "btn_clear": "🗑️ Burahin ang Cart",
        "inv_h": "Pamamahala ng Stock", "btn_reg": "I-rehistro ang Produkto", "name": "Pangalan ng Produkto",
        "stock": "Bilang ng Stock", "bought": "Puhunan (Presyong Bili)", "srp": "SRP (Presyong Tinda)",
        "code": "KODIGO", "action": "AKSYON", "add_stock": "DAGDAG STOCK",
        "rec_h": "Itala ang Gasto", "store": "Pangalan ng Tindahan", "amt": "Halagang Nagastos", "photo": "I-upload ang Larawan", "btn_save": "I-save",
        "rep_h": "Ulat ng Kita at Gasto", "rev": "Kabuuang Benta", "exp": "Kabuuang Gasto", "prof": "Netong Kita",
        "ut_h": "Listahan ng Utang", "cust": "Pangalan ng Customer", "phone": "Numero ng Telepono", "debt_amt": "Halaga ng Utang",
        "btn_sms": "Magpadala ng SMS Paalala", "btn_paid": "✅ Bayad na / Burahin", "low_stock": "⚠️ KONTI NA LANG!",
        "success": "Tapos na ang benta!"
    }
}[lang]

# --- 3. UI LAYOUT ---
st.title("🏪 Negosyo Pro")
tabs = st.tabs(D["tabs"])

# --- TAB 1: QUICK SALE ---
with tabs[0]:
    st.subheader(D["sale_h"])
    if 'cart' not in st.session_state: st.session_state.cart = []
    
    col_in, col_qty = st.columns([3, 1])
    b_in = col_in.text_input(D["input_c"], key="sale_in")
    q_in = col_qty.number_input(D["qty"], min_value=1, value=1)
    
    if b_in in st.session_state.db['inventory']:
        item = st.session_state.db['inventory'][b_in]
        st.info(f"✨ **{item['name']}** | ₱{item['price']:.2f} | {D['stock']}: {item['stock']}")
        if st.button(D["add_cart"]):
            if item['stock'] >= q_in:
                st.session_state.cart.append({
                    "code": b_in, "name": item['name'], "qty": q_in, 
                    "price": item['price'], "subtotal": item['price'] * q_in
                })
                st.rerun()
            else: st.error("Out of stock!" if lang == "English" else "Wala ng stock!")

    if st.session_state.cart:
        st.write("---")
        st.markdown(f"### {D['cart_h']}")
        cart_df = pd.DataFrame(st.session_state.cart)
        cart_df.columns = [D["code"], D["name"].upper(), D["qty"].upper(), "PRICE", "SUBTOTAL"]
        st.table(cart_df)
        total_bill = cart_df['SUBTOTAL'].sum()
        st.header(f"{D['total']}: ₱{total_bill:,.2f}")
        
        c_pay, c_clear = st.columns(2)
        if c_pay.button(D["btn_checkout"], type="primary", use_container_width=True):
            for entry in st.session_state.cart:
                st.session_state.db['inventory'][entry['code']]['stock'] -= entry['qty']
                st.session_state.db['sales'].append({
                    "date": str(datetime.now().strftime("%Y-%m-%d %H:%M")), 
                    "item": entry['name'], "total": entry['subtotal']
                })
            save_data(); st.session_state.cart = []; st.balloons(); st.rerun()
        if c_clear.button(D["btn_clear"], use_container_width=True): st.session_state.cart = []; st.rerun()

# --- TAB 2: INVENTORY ---
with tabs[1]:
    st.subheader(D["inv_h"])
    for k, v in st.session_state.db['inventory'].items():
        if v['stock'] <= v['min_alert']: st.warning(f"{D['low_stock']} {v['name']} ({v['stock']})")
    
    with st.expander(D["btn_reg"]):
        with st.form("reg_form", clear_on_submit=True):
            c_i = st.text_input(D["code"])
            n_i = st.text_input(D["name"]).upper()
            col_s, col_p = st.columns(2)
            s_i = col_s.number_input(D["stock"], min_value=0)
            p_i = col_p.number_input(D["srp"], min_value=0.0)
            if st.form_submit_button(D["btn_reg"]):
                st.session_state.db['inventory'][c_i] = {"name": n_i, "stock": s_i, "price": p_i, "min_alert": 5}
                save_data(); st.rerun()

    if st.session_state.db['inventory']:
        st.write("---")
        h1, h2, h3, h4, h5, h6 = st.columns([1.5, 2.5, 1, 1, 1.5, 1])
        h1.write(f"**{D['code']}**"); h2.write(f"**{D['name'].upper()}**"); h3.write(f"**{D['stock'].upper()}**")
        h4.write(f"**PRICE**"); h5.write(f"**{D['add_stock']}**"); h6.write(f"**{D['action']}**")
        st.divider()

        for code, det in list(st.session_state.db['inventory'].items()):
            r1, r2, r3, r4, r5, r6 = st.columns([1.5, 2.5, 1, 1, 1.5, 1])
            r1.write(f"`{code}`"); r2.write(det['name']); r3.write(f"**{det['stock']}**")
            r4.write(f"₱{det['price']:.2f}")
            with r5:
                with st.popover("➕"):
                    add_amt = st.number_input(D["qty"], min_value=1, key=f"a_{code}")
                    if st.button(D["btn_save"], key=f"b_{code}"):
                        st.session_state.db['inventory'][code]['stock'] += add_amt
                        save_data(); st.rerun()
            if r6.button("🗑️", key=f"d_{code}"):
                del st.session_state.db['inventory'][code]; save_data(); st.rerun()

# --- TAB 3: EXPENSES ---
with tabs[2]:
    st.subheader(D["rec_h"])
    with st.form("p_form"):
        s_n = st.text_input(D["store"]); a_p = st.number_input(D["amt"])
        if st.form_submit_button(D["btn_save"]):
            st.session_state.db['purchase_receipts'].append({"date": str(datetime.now().date()), "store": s_n, "total": a_p})
            save_data(); st.rerun()
    st.dataframe(pd.DataFrame(st.session_state.db['purchase_receipts']), use_container_width=True)

# --- TAB 4: REPORTS ---
with tabs[3]:
    st.subheader(D["rep_h"])
    s_df = pd.DataFrame(st.session_state.db['sales'])
    p_df = pd.DataFrame(st.session_state.db['purchase_receipts'])
    rev = s_df['total'].sum() if not s_df.empty else 0
    exp = p_df['total'].sum() if not p_df.empty else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric(D["rev"], f"₱{rev:,.2f}")
    c2.metric(D["exp"], f"₱{exp:,.2f}")
    c3.metric(D["prof"], f"₱{rev-exp:,.2f}")

# --- TAB 5: UTANG ---
with tabs[4]:
    st.subheader(D["ut_h"])
    with st.form("u_form", clear_on_submit=True):
        u_n = st.text_input(D["cust"]); u_p = st.text_input(D["phone"]); u_a = st.number_input(D["debt_amt"])
        if st.form_submit_button(f"➕ {D['ut_h']}"):
            if u_n and u_p:
                st.session_state.db['debts'].append({"name": u_n.upper(), "phone": u_p, "amount": u_a})
                save_data(); st.rerun()

    if st.session_state.db['debts']:
        d_df = pd.DataFrame(st.session_state.db['debts'])
        st.table(d_df)
        col_rem, col_del = st.columns(2)
        with col_rem:
            sel = st.selectbox(D["cust"], range(len(st.session_state.db['debts'])), format_func=lambda x: st.session_state.db['debts'][x]['name'])
            pers = st.session_state.db['debts'][sel]
            msg = f"Paalala: Balance of ₱{pers['amount']:,.2f}."
            st.link_button(D["btn_sms"], f"sms:{pers['phone']}?body={urllib.parse.quote(msg)}")
        with col_del:
            if st.button(D["btn_paid"], type="primary"):
                st.session_state.db['debts'].pop(sel); save_data(); st.rerun()
