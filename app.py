import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import urllib.parse

# --- 1. DATA ENGINE (Fixed Clean Slate) ---
DB_FILE = 'negosyo_pro_master.json'

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: 
                data = json.load(f)
                return data
        except: pass
    return {'sales': [], 'inventory': {}, 'purchase_receipts': [], 'debts': []}

# --- IMPORTANT: FORCING 0.00 FOR YOUR DEMO ---
# To see 0.00, we ensure the session starts empty if no file exists
if 'db' not in st.session_state:
    st.session_state.db = load_data()

def save_data():
    with open(DB_FILE, 'w') as f:
        json.dump(st.session_state.db, f)

# --- 2. BILINGUAL DICTIONARY ---
st.set_page_config(page_title="Negosyo Pro", layout="wide", page_icon="🏪")
lang = st.sidebar.radio("Wika / Language", ["English", "Tagalog"])

D = {
    "English": {
        "tabs": ["⚡ Quick Sale", "📦 Inventory", "🧾 Expenses", "📊 Reports", "💳 Utang"],
        "sale_h": "Register a Sale", "input_c": "Scan/Type Barcode", "qty": "Qty", "add_cart": "➕ Add to Cart",
        "cart_h": "🛒 Current Cart", "total": "TOTAL", "btn_sell": "🏁 Complete Sale", "btn_clear": "🗑️ Clear Cart",
        "inv_h": "Stock Management", "btn_reg": "Register New Product", "name": "Product Name", 
        "stock": "Current Stock", "bought": "Bought Price", "srp": "SRP",
        "code": "CODE", "action": "ACTION", "add_stock": "ADD STOCK",
        "rec_h": "Log Expenses", "store": "Store Name", "amt": "Amount Spent", "photo": "Upload Photo", "btn_save": "Save",
        "rep_h": "Financial Summary", "rev": "Total Sales", "exp": "Total Expenses", "prof": "Net Profit",
        "ut_h": "Debt Management", "cust": "Customer Name", "phone": "Mobile Number", "debt_amt": "Debt Amount",
        "btn_sms": "Send SMS Reminder", "btn_paid": "✅ Mark as Paid", "low_stock": "⚠️ LOW STOCK!"
    },
    "Tagalog": {
        "tabs": ["⚡ Benta", "📦 Imbentaryo", "🧾 Gasto", "📊 Ulat", "💳 Utang"],
        "sale_h": "Itala ang Benta", "input_c": "I-scan ang Barcode", "qty": "Dami", "add_cart": "➕ Idagdag sa Cart",
        "cart_h": "🛒 Mga Bibilhin", "total": "KABUUAN", "btn_sell": "🏁 Tapusin ang Benta", "btn_clear": "🗑️ Burahin ang Cart",
        "inv_h": "Pamamahala ng Stock", "btn_reg": "I-rehistro ang Produkto", "name": "Pangalan ng Produkto",
        "stock": "Bilang ng Stock", "bought": "Puhunan", "srp": "SRP",
        "code": "KODIGO", "action": "AKSYON", "add_stock": "DAGDAG STOCK",
        "rec_h": "Itala ang Gasto", "store": "Tindahan", "amt": "Halaga", "photo": "I-upload ang Resibo", "btn_save": "I-save",
        "rep_h": "Ulat ng Kita", "rev": "Kabuuang Benta", "exp": "Kabuuang Gasto", "prof": "Netong Kita",
        "ut_h": "Listahan ng Utang", "cust": "Customer", "phone": "Numero", "debt_amt": "Utang",
        "btn_sms": "Magpadala ng SMS", "btn_paid": "✅ Bayad na", "low_stock": "⚠️ KONTI NA LANG!"
    }
}[lang]

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
                    "bought": item.get('bought', 0), "price": item['price'], "subtotal": item['price'] * q_in
                })
                st.rerun()
            else: st.error("Out of stock!" if lang == "English" else "Wala ng stock!")

    if st.session_state.cart:
        st.write("---")
        st.markdown(f"### {D['cart_h']}")
        cart_df = pd.DataFrame(st.session_state.cart)
        st.table(cart_df)
        total_bill = cart_df['subtotal'].sum()
        st.header(f"{D['total']}: ₱{total_bill:,.2f}")
        
        c_pay, c_clear = st.columns(2)
        if c_pay.button(D["btn_sell"], type="primary", use_container_width=True):
            for entry in st.session_state.cart:
                st.session_state.db['inventory'][entry['code']]['stock'] -= entry['qty']
                st.session_state.db['sales'].append({
                    "date": str(datetime.now().strftime("%Y-%m-%d %H:%M")), 
                    "item": entry['name'], "qty": entry['qty'],
                    "bought": entry['bought'], "srp": entry['price'], "total": entry['subtotal']
                })
            save_data(); st.session_state.cart = []; st.balloons(); st.rerun()
        if c_clear.button(D["btn_clear"], use_container_width=True): st.session_state.cart = []; st.rerun()

# --- TAB 2: INVENTORY (With Bought Price & SRP) ---
with tabs[1]:
    st.subheader(D["inv_h"])
    
    # 1. Low Stock Alerts
    for k, v in st.session_state.db['inventory'].items():
        if v['stock'] <= v['min_alert']: 
            st.warning(f"{D['low_stock']} {v['name']} ({v['stock']})")
    
    # 2. Registration Form (Updated with 3 columns)
    with st.expander(D["btn_reg"]):
        with st.form("reg_form", clear_on_submit=True):
            c_i = st.text_input(D["code"])
            n_i = st.text_input(D["name"]).upper()
            
            # Create 3 columns: Stock, Bought Price, and SRP
            col_s, col_b, col_p = st.columns(3)
            s_i = col_s.number_input(D["stock"], min_value=0)
            b_i = col_b.number_input(D["bought"], min_value=0.0) # <--- ADDED BOUGHT PRICE
            p_i = col_p.number_input(D["srp"], min_value=0.0)
            
            if st.form_submit_button(D["btn_reg"]):
                if c_i and n_i:
                    st.session_state.db['inventory'][c_i] = {
                        "name": n_i, 
                        "stock": s_i, 
                        "bought": b_i, # <--- SAVING BOUGHT PRICE
                        "price": p_i, 
                        "min_alert": 5
                    }
                    save_data()
                    st.rerun()

    # 3. Dynamic Inventory List
    if st.session_state.db['inventory']:
        st.write("---")
        # Added a column for BOUGHT (Headers)
        h1, h2, h3, h4, h5, h6, h7 = st.columns([1.5, 2, 1, 1, 1, 1.5, 1])
        h1.write(f"**{D['code']}**")
        h2.write(f"**{D['name'].upper()}**")
        h3.write(f"**STOCK**")
        h4.write(f"**BOUGHT**") # <--- NEW HEADER
        h5.write(f"**SRP**")
        h6.write(f"**{D['add_stock']}**")
        h7.write(f"**{D['action']}**")
        st.divider()

        for code, det in list(st.session_state.db['inventory'].items()):
            r1, r2, r3, r4, r5, r6, r7 = st.columns([1.5, 2, 1, 1, 1, 1.5, 1])
            
            r1.write(f"`{code}`")
            r2.write(det['name'])
            r3.write(f"**{det['stock']}**")
            
            # Displaying the Money values
            # .get() is used here so old items without a 'bought' price won't crash the app
            r4.write(f"₱{det.get('bought', 0.0):.2f}") 
            r5.write(f"₱{det['price']:.2f}")
            
            with r6:
                with st.popover("➕"):
                    add_amt = st.number_input(D["qty"], min_value=1, key=f"a_{code}")
                    if st.button(D["btn_save"], key=f"b_{code}"):
                        st.session_state.db['inventory'][code]['stock'] += add_amt
                        save_data()
                        st.rerun()
                        
            if r7.button("🗑️", key=f"d_{code}"):
                del st.session_state.db['inventory'][code]
                save_data()
                st.rerun()
    else:
        st.info("Inventory is empty.")
# --- TAB 3: EXPENSES ---
with tabs[2]:
    st.subheader(D["rec_h"])
    with st.form("p_form", clear_on_submit=True):
        s_n = st.text_input(D["store"])
        a_p = st.number_input(D["amt"], min_value=0.0)
        u_p = st.file_uploader(D["photo"], type=['jpg', 'png', 'jpeg'])
        if st.form_submit_button(D["btn_save"]):
            if s_n and a_p > 0:
                st.session_state.db['purchase_receipts'].append({"date": str(datetime.now().date()), "store": s_n.upper(), "total": a_p})
                save_data(); st.success("Saved!"); st.rerun()

# --- TAB 4: REPORTS (Clean 0.00 Start) ---
with tabs[3]:
    st.subheader(D["rep_h"])
    rev, exp, prof = 0.0, 0.0, 0.0
    
    if st.session_state.db['sales']:
        s_df = pd.DataFrame(st.session_state.db['sales'])
        s_df['date'] = pd.to_datetime(s_df['date'])
        s_df['month_year'] = s_df['date'].dt.strftime('%B %Y')
        
        available_months = s_df['month_year'].unique()
        selected_month = st.selectbox("Month", options=available_months)
        
        m_data = s_df[s_df['month_year'] == selected_month]
        rev = m_data['total'].sum()
        if 'srp' in m_data.columns and 'bought' in m_data.columns:
            prof = (m_data['srp'] - m_data['bought']).sum()
        
        p_df = pd.DataFrame(st.session_state.db['purchase_receipts'])
        if not p_df.empty:
            p_df['date'] = pd.to_datetime(p_df['date'])
            p_df['month_year'] = p_df['date'].dt.strftime('%B %Y')
            exp = p_df[p_df['month_year'] == selected_month]['total'].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric(D["rev"], f"₱{rev:,.2f}")
    c2.metric(D["exp"], f"₱{exp:,.2f}")
    c3.metric(D["prof"], f"₱{prof:,.2f}")

# --- TAB 5: UTANG (With Dynamic Column Fix) ---
with tabs[4]:
    st.subheader(D["ut_h"])
    with st.form("u_form", clear_on_submit=True):
        u_n = st.text_input(D["cust"])
        u_p = st.text_input(D["phone"])
        u_a = st.number_input(D["debt_amt"], min_value=0.0)
        if st.form_submit_button(f"➕ {D['ut_h']}"):
            if u_n and u_p:
                st.session_state.db['debts'].append({
                    "name": u_n.upper(), 
                    "phone": u_p, 
                    "amount": u_a,
                    "date": str(datetime.now().date()) # The 4th column
                })
                save_data(); st.rerun()

    # --- THIS IS WHERE YOU ADD THE FIX ---
    if st.session_state.db['debts']:
        st.write("---")
        d_df = pd.DataFrame(st.session_state.db['debts'])
        
        # --- DYNAMIC COLUMN FIX ---
        # This prevents the "ValueError" if some rows are missing the Date
        if len(d_df.columns) == 4:
            d_df.columns = ["NAME", "PHONE", "AMOUNT", "DATE"]
        elif len(d_df.columns) == 3:
            d_df.columns = ["NAME", "PHONE", "AMOUNT"]
            
        st.table(d_df)
        
        col_rem, col_del = st.columns(2)
        
        with col_rem:
            st.markdown(f"### 📱 {D['btn_sms']}")
            sel = st.selectbox(
                "Piliin ang Customer" if lang == "Tagalog" else "Select Customer", 
                range(len(st.session_state.db['debts'])), 
                format_func=lambda x: st.session_state.db['debts'][x]['name']
            )
            pers = st.session_state.db['debts'][sel]
            
            # Bilingual Message Logic
            store_name = "NEGOSYO PRO"
            if lang == "Tagalog":
                msg = f"Magandang araw {pers['name']}! Paalala mula sa {store_name} tungkol sa utang na ₱{pers['amount']:,.2f}."
            else:
                msg = f"Good day {pers['name']}! Reminder from {store_name} regarding your balance of ₱{pers['amount']:,.2f}."
            
            st.link_button(D["btn_sms"], f"sms:{pers['phone']}?body={urllib.parse.quote(msg)}")

        with col_del:
            st.markdown(f"### ✅ {D['btn_paid']}")
            if st.button(D["btn_paid"], type="primary", use_container_width=True):
                st.session_state.db['debts'].pop(sel)
                save_data()
                st.rerun()
