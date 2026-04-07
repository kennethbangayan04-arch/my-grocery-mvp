import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import urllib.parse

# --- 1. DATA ENGINE (With Migration Logic) ---
DB_FILE = 'negosyo_pro_master.json'

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: 
                data = json.load(f)
                # Ensure all items have BOUGHT and PRICE keys to prevent KeyErrors
                for k, v in data['inventory'].items():
                    if "bought" not in v: v["bought"] = v.get("price", 0) * 0.8
                    if "price" not in v: v["price"] = 0
                return data
        except: pass
    # Default Clean Slate
    return {'sales': [], 'inventory': {}, 'purchase_receipts': [], 'debts': []}

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def save_data():
    with open(DB_FILE, 'w') as f: json.dump(st.session_state.db, f)

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
        "success": "Transaction Complete!", "rem_msg": "Reminder from store: Balance of"
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
        "success": "Tapos na ang benta!", "rem_msg": "Paalala mula sa tindahan: Utang na"
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
                    "bought": item.get('bought', 0), "price": item['price'], "subtotal": item['price'] * q_in
                })
                st.rerun()
            else: st.error("Hindi sapat ang stock!" if lang == "Tagalog" else "Insufficient stock!")

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
                    "item": entry['name'], "bought": entry['bought'], 
                    "srp": entry['price'], "total": entry['subtotal']
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
            col_s, col_b, col_p = st.columns(3)
            s_i = col_s.number_input(D["stock"], min_value=0)
            b_i = col_b.number_input(D["bought"], min_value=0.0)
            p_i = col_p.number_input(D["srp"], min_value=0.0)
            if st.form_submit_button(D["btn_reg"]):
                st.session_state.db['inventory'][c_i] = {"name": n_i, "stock": s_i, "bought": b_i, "price": p_i, "min_alert": 5}
                save_data(); st.rerun()

    if st.session_state.db['inventory']:
        st.write("---")
        h1, h2, h3, h4, h5, h6, h7 = st.columns([1.5, 2, 1, 1, 1, 1.5, 1])
        h1.write(f"**{D['code']}**"); h2.write(f"**{D['name'].upper()}**"); h3.write(f"**{D['stock'].upper()}**")
        h4.write(f"**{D['bought'].split(' ')[0].upper()}**"); h5.write("**SRP**"); h6.write(f"**{D['add_stock']}**"); h7.write(f"**{D['action']}**")
        st.divider()

        for code, det in list(st.session_state.db['inventory'].items()):
            r1, r2, r3, r4, r5, r6, r7 = st.columns([1.5, 2, 1, 1, 1, 1.5, 1])
            r1.write(f"`{code}`"); r2.write(det['name']); r3.write(f"**{det['stock']}**")
            r4.write(f"₱{det.get('bought',0):.2f}"); r5.write(f"₱{det['price']:.2f}")
            with r6:
                with st.popover("➕"):
                    add_amt = st.number_input(D["qty"], min_value=1, key=f"a_{code}")
                    if st.button(D["btn_save"], key=f"b_{code}"):
                        st.session_state.db['inventory'][code]['stock'] += add_amt
                        save_data(); st.rerun()
            if r7.button("🗑️", key=f"d_{code}"):
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
    exp = sum([p['total'] for p in st.session_state.db['purchase_receipts']])
    if not s_df.empty:
        rev = s_df['total'].sum()
        prof = (s_df['srp'] - s_df['bought']).sum()
        c1, c2, c3 = st.columns(3)
        c1.metric(D["rev"], f"₱{rev:,.2f}")
        c2.metric(D["exp"], f"₱{exp:,.2f}")
        c3.metric(D["prof"], f"₱{prof:,.2f}")
    else: st.info("Walang benta." if lang == "Tagalog" else "No sales yet.")

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
            full_msg = f"{D['rem_msg']} ₱{pers['amount']:,.2f}. Salamat!"
            st.link_button(D["btn_sms"], f"sms:{pers['phone']}?body={urllib.parse.quote(full_msg)}")
        with col_del:
            if st.button(D["btn_paid"], type="primary", use_container_width=True):
                st.session_state.db['debts'].pop(sel); save_data(); st.rerun()
# --- TAB 1: QUICK SALE (With Multi-Item Cart) ---
with tabs[0]:
    st.subheader(D["sale_header"])
    
    # Initialize an empty cart in the session if it doesn't exist
    if 'cart' not in st.session_state:
        st.session_state.cart = []

    col_input, col_qty = st.columns([3, 1])
    b_in = col_input.text_input(D["input_code"], key="sale_in")
    q_in = col_qty.number_input("Qty", min_value=1, value=1)
    
    if b_in in st.session_state.db['inventory']:
        item = st.session_state.db['inventory'][b_in]
        st.info(f"✨ **{item['name']}** | ₱{item['price']} | Stock: {item['stock']}")
        
        if st.button("➕ Add to Cart" if lang == "English" else "➕ Idagdag sa Cart"):
            if item['stock'] >= q_in:
                # Add to temporary cart
                st.session_state.cart.append({
                    "code": b_in,
                    "name": item['name'],
                    "qty": q_in,
                    "price": item['price'],
                    "subtotal": item['price'] * q_in
                })
                st.success(f"Added {q_in}x {item['name']}")
            else:
                st.error("Insufficient Stock!")

    # --- DISPLAY CART ---
    if st.session_state.cart:
        st.write("---")
        st.markdown("### 🛒 Current Cart / Mga Bibilhin")
        cart_df = pd.DataFrame(st.session_state.cart)
        # Capitalize headers for the cart as well
        cart_df.columns = ["CODE", "ITEM", "QTY", "PRICE", "SUBTOTAL"]
        st.table(cart_df)
        
        total_bill = cart_df['SUBTOTAL'].sum()
        st.header(f"TOTAL: ₱{total_bill:,.2f}")
        
        c_pay, c_clear = st.columns(2)
        
        # FINAL CHECKOUT BUTTON
        if c_pay.button("🏁 " + D["btn_sell"], type="primary", use_container_width=True):
            for entry in st.session_state.cart:
                # 1. Deduct from inventory
                st.session_state.db['inventory'][entry['code']]['stock'] -= entry['qty']
                # 2. Record in Sales History
                st.session_state.db['sales'].append({
                    "date": str(datetime.now().strftime("%Y-%m-%d %H:%M")),
                    "item": entry['name'],
                    "total": entry['subtotal']
                })
            
            # Save data and clear cart
            save_data()
            st.session_state.cart = []
            st.balloons()
            st.success("Transaction Complete!")
            st.rerun()

        if c_clear.button("🗑️ Clear Cart", use_container_width=True):
            st.session_state.cart = []
            st.rerun()

# --- TAB 2: INVENTORY (Manual Restock & Delete) ---
with tabs[1]:
    st.subheader(D["inv_header"])
    
    # 1. Low Stock Alerts
    for k, v in st.session_state.db['inventory'].items():
        if v['stock'] <= v['min_alert']: 
            st.warning(f"{D['low_stock']} {v['name']} ({v['stock']})")
    
    # 2. Registration Form
    with st.expander(D["btn_reg"]):
        with st.form("add_form", clear_on_submit=True):
            c_i = st.text_input("Barcode/Code")
            n_i = st.text_input(D["name"]).upper()
            col_s, col_p = st.columns(2)
            s_i = col_s.number_input("Initial Stock", min_value=0)
            p_i = col_p.number_input("Price (SRP)", min_value=0.0)
            if st.form_submit_button(D["btn_reg"]):
                if c_i and n_i:
                    st.session_state.db['inventory'][c_i] = {"name": n_i, "stock": s_i, "price": p_i, "min_alert": 5}
                    save_data(); st.rerun()

    # 3. Dynamic Inventory List (With Manual Restock)
    if st.session_state.db['inventory']:
        st.write("---")
        # Layout: Code, Name, Stock, Price, Restock Input, Action
        h1, h2, h3, h4, h5, h6 = st.columns([1.5, 2.5, 1, 1, 2, 1])
        h1.write("**CODE**")
        h2.write("**NAME**")
        h3.write("**STOCK**")
        h4.write("**PRICE**")
        h5.write("**ADD STOCK**") # Header for typing
        h6.write("**ACTION**")
        st.divider()

        for code, details in list(st.session_state.db['inventory'].items()):
            r1, r2, r3, r4, r5, r6 = st.columns([1.5, 2.5, 1, 1, 2, 1])
            
            r1.write(f"`{code}`")
            r2.write(details['name'])
            r3.write(f"**{details['stock']}**")
            r4.write(f"₱{details['price']:.2f}")
            
            # --- MANUAL RESTOCK INPUT ---
            # Using a small form for each row so the user can type and hit 'Enter'
            with r5:
                with st.popover("➕ Add"):
                    add_amt = st.number_input("How many?", min_value=1, key=f"amt_{code}", step=1)
                    if st.button("Confirm", key=f"btn_{code}"):
                        st.session_state.db['inventory'][code]['stock'] += add_amt
                        save_data()
                        st.toast(f"Added {add_amt} to {details['name']}!")
                        st.rerun()
            
            # --- DELETE FEATURE ---
            if r6.button("🗑️", key=f"del_{code}"):
                del st.session_state.db['inventory'][code]
                save_data()
                st.rerun()
    else:
        st.info("Inventory is empty.")        
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

# TAB 5: UTANG (With Delete/Paid Function)
with tabs[4]:
    st.subheader(D["utang_header"])
    
    # 1. Entry Form
    with st.form("utang_form", clear_on_submit=True):
        u_n = st.text_input(D["cust"])
        u_p = st.text_input(D["phone"])
        u_a = st.number_input(D["debt_amt"], min_value=0.0)
        if st.form_submit_button(f"➕ {D['utang_header']}"):
            if u_n and u_p:
                st.session_state.db['debts'].append({"name": u_n, "phone": u_p, "amount": u_a})
                save_data()
                st.rerun()

    # 2. List and Actions
    if st.session_state.db['debts']:
        st.markdown("---")
        
        # Display as a nice table first
        d_df = pd.DataFrame(st.session_state.db['debts'])
        st.table(d_df)
        
        # --- DELETE / PAID SECTION ---
        st.write("---")
        col_remind, col_delete = st.columns(2)
        
        with col_remind:
            st.subheader(D["btn_sms"])
            sel_idx = st.selectbox("Select Customer", range(len(st.session_state.db['debts'])), 
                                   format_func=lambda x: st.session_state.db['debts'][x]['name'])
            
            pers = st.session_state.db['debts'][sel_idx]
            
            # Bilingual Message
            msg = f"Paalala mula sa tindahan: May utang po na ₱{pers['amount']:,.2f}. Salamat!" if lang == "Tagalog" else f"Reminder from the store: Balance of ₱{pers['amount']:,.2f}. Thank you!"
            
            st.link_button(D["btn_sms"], f"sms:{pers['phone']}?body={urllib.parse.quote(msg)}")

        with col_delete:
            st.subheader("Action")
            # The "Delete" button
            delete_label = "✅ Mark as Paid / Delete" if lang == "English" else "✅ Bayad na / Burahin"
            if st.button(delete_label, type="primary"):
                # Remove the selected person using their index
                removed_person = st.session_state.db['debts'].pop(sel_idx)
                save_data()
                st.success(f"Removed {removed_person['name']} from list.")
                st.rerun()
