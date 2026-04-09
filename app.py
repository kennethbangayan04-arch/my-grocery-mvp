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

# --- OWNER MANAGEMENT ---
st.sidebar.write("---")
st.sidebar.subheader("Owner Controls" if lang == "English" else "Control sa May-ari")

if st.sidebar.button("🗑️ Reset for New Owner" if lang == "English" else "🗑️ Reset para sa Bagong Owner"):
    # Clear the memory
    st.session_state.db = {'sales': [], 'inventory': {}, 'purchase_receipts': [], 'debts': []}
    
    # Overwrite the file with empty data
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE) 
        
    st.sidebar.success("System Reset!")
    st.rerun()
   
# --- 3. MODERN UI CSS (Ensure this is in your code) ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {background: rgba(0,0,0,0);}
    .metric-card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #FFC0CB;
    }
    .metric-title { font-size: 13px; color: #757575; font-weight: bold; text-transform: uppercase; }
    .metric-value { font-size: 22px; font-weight: bold; color: #212121; margin-top: 5px; }
    /* This hides the redundant spacing at the top of tabs */
    .block-container { padding-top: 2rem; }
    </style>
""", unsafe_allow_html=True)

# --- DASHBOARD METRICS (The 4 Colored Boxes) ---
s_df = pd.DataFrame(st.session_state.db['sales'])
p_df = pd.DataFrame(st.session_state.db['purchase_receipts'])
today_str = datetime.now().strftime("%Y-%m-%d")

today_sales = s_df[s_df['date'].str.contains(today_str)]['total'].sum() if not s_df.empty else 0
total_products = len(st.session_state.db['inventory'])
weekly_expenses = p_df['total'].sum() if not p_df.empty else 0
low_stock_count = sum(1 for v in st.session_state.db['inventory'].values() if v['stock'] <= v['min_alert'])

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card" style="border-left-color: #fce4ec;"><div class="metric-title">🛒 {D["rev"]} Today</div><div class="metric-value">₱{today_sales:,.2f}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card" style="border-left-color: #e3f2fd;"><div class="metric-title">📦 {D["inv_h"]}</div><div class="metric-value">{total_products}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card" style="border-left-color: #fff3e0;"><div class="metric-title">🧾 {D["exp"]} This Week</div><div class="metric-value">₱{weekly_expenses:,.2f}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card" style="border-left-color: #e0f2f1;"><div class="metric-title">📉 {D["low_stock"]}</div><div class="metric-value">{low_stock_count}</div></div>', unsafe_allow_html=True)

st.write("---")

# --- NAVIGATION TABS ---
# We use emojis in the tab names to match the photo's icons
t1, t2, t3, t4, t5 = st.tabs(["⚡ Quick Sale", "📦 Inventory", "🧾 Expenses", "📊 Reports", "💳 Utang"])

# --- TAB 1: QUICK SALE (Redundancy Removed) ---
with t1:
    # Notice: No st.subheader here anymore!
    if 'cart' not in st.session_state: st.session_state.cart = []
    
    st.markdown("### Register a Sale") # Matches the photo's bold text
    col_in, col_qty = st.columns([3, 1])
    b_in = col_in.text_input(D["input_c"], placeholder="Scan/Type Barcode", key="sale_in", label_visibility="collapsed")
    q_in = col_qty.number_input(D["qty"], min_value=1, value=1, label_visibility="collapsed")
    
    # Rest of your Sale logic...

# --- TAB 2: INVENTORY (Redundancy Removed) ---
with t2:
    # Subheader removed, directly to alerts or registration
    for k, v in st.session_state.db['inventory'].items():
        if v['stock'] <= v['min_alert']: 
            st.warning(f"{D['low_stock']} {v['name']} ({v['stock']})")
    
    # Rest of Inventory logic...# --- 4. NAVIGATION BAR (The Tabbed View) ---
# Replace your current st.tabs line with this:
tabs = st.tabs([f"🎴 {t}" for t in D["tabs"]])
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

# --- TAB 2: INVENTORY  ---
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
            b_i = col_b.number_input(D["bought"], min_value=0.0)
            p_i = col_p.number_input(D["srp"], min_value=0.0)
            
            if st.form_submit_button(D["btn_reg"]):
                if c_i and n_i:
                    st.session_state.db['inventory'][c_i] = {
                        "name": n_i, 
                        "stock": s_i, 
                        "bought": b_i,
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
        h4.write(f"**BOUGHT**") 
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
# --- TAB 3: ---
with tabs[2]:
    st.subheader(D["rec_h"])
    
    # 1. Input Form
    with st.form("p_form", clear_on_submit=True):
        s_n = st.text_input(D["store"])
        a_p = st.number_input(D["amt"], min_value=0.0)
        u_p = st.file_uploader(D["photo"], type=['jpg', 'png', 'jpeg'])
        
        if st.form_submit_button(D["btn_save"]):
            if s_n and a_p > 0:
                st.session_state.db['purchase_receipts'].append({
                    "date": str(datetime.now().strftime("%Y-%m-%d")), 
                    "store": s_n.upper(), 
                    "total": a_p
                })
                save_data()
                st.success("Saved!" if lang == "English" else "Naitabi na!")
                st.rerun()

    # 2. Monthly Filter & History
    if st.session_state.db['purchase_receipts']:
        st.write("---")
        p_df = pd.DataFrame(st.session_state.db['purchase_receipts'])
        
        # Convert date column to datetime objects
        p_df['date'] = pd.to_datetime(p_df['date'])
        # Create a display column for the month (e.g., "April 2026")
        p_df['month_year'] = p_df['date'].dt.strftime('%B %Y')
        
        # MONTH SELECTOR DROPDOWN
        available_exp_months = p_df['month_year'].unique()
        sel_exp_month = st.selectbox(
            "Tingnan ang Gasto sa Buwan ng:" if lang == "Tagalog" else "View Expenses For:", 
            options=available_exp_months,
            key="exp_month_sel"
        )
        
        # Filter the data
        filtered_exp = p_df[p_df['month_year'] == sel_exp_month]
        
        # Display Summary for the month
        monthly_total = filtered_exp['total'].sum()
        st.metric(f"{sel_exp_month} {D['exp']}", f"₱{monthly_total:,.2f}")
        
        # Display Table
        display_df = filtered_exp[['date', 'store', 'total']].copy()
        display_df.columns = ["DATE", "STORE", "AMOUNT"]
        st.dataframe(display_df, use_container_width=True)
        
    else:
        st.info("Walang nakatalang gasto." if lang == "Tagalog" else "No recorded expenses.")
# --- TAB 4: REPORTS  ---
with tabs[3]:
    st.subheader(D["rep_h"])
    
    rev, total_expenses, gross_markup, net_prof = 0.0, 0.0, 0.0, 0.0
    selected_month = datetime.now().strftime('%B %Y')
    
    if st.session_state.db['sales']:
        s_df = pd.DataFrame(st.session_state.db['sales'])
        s_df['date'] = pd.to_datetime(s_df['date'])
        s_df['month_year'] = s_df['date'].dt.strftime('%B %Y')
        
        available_months = s_df['month_year'].unique()
        selected_month = st.selectbox(
            "Piliin ang Buwan" if lang == "Tagalog" else "Select Month", 
            options=available_months,
            index=len(available_months)-1
        )
        
        # Filter sales for the selected month
        m_sales = s_df[s_df['month_year'] == selected_month]
        
        # 1. TOTAL REVENUE (Total cash from customers)
        rev = m_sales['total'].sum()
        
        # 2. GROSS MARKUP (Profit from items alone: SRP - Cost)
        if 'srp' in m_sales.columns and 'bought' in m_sales.columns:
            # We calculate: (Selling Price - Cost Price) * Quantity
            gross_markup = ((m_sales['srp'] - m_sales['bought']) * m_sales['qty']).sum()
        else:
            gross_markup = rev * 0.20 # Fallback estimate
            
        # 3. OPERATING EXPENSES 
        p_df = pd.DataFrame(st.session_state.db['purchase_receipts'])
        if not p_df.empty:
            p_df['date'] = pd.to_datetime(p_df['date'])
            p_df['month_year'] = p_df['date'].dt.strftime('%B %Y')
            total_expenses = p_df[p_df['month_year'] == selected_month]['total'].sum()

        # 4. NET PROFIT 
        net_prof = gross_markup - total_expenses

    # --- DISPLAY METRICS ---
    st.info(f"📅 {selected_month}")
    c1, c2, c3 = st.columns(3)
    c1.metric(D["rev"], f"₱{rev:,.2f}")
    c2.metric(D["exp"], f"₱{total_expenses:,.2f}")
    c3.metric(D["prof"], f"₱{net_prof:,.2f}")
    
    if rev > 0:
        st.write("---")
        st.subheader("Daily Sales Trend" if lang == "English" else "Daloy ng Benta")
        daily_sales = m_sales.groupby(m_sales['date'].dt.date)['total'].sum()
        st.line_chart(daily_sales)
        
# --- TAB 5: UTANG ---
with tabs[4]:
    st.subheader(D["ut_h"])
    
    # 1. Entry Form
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
                    "date": str(datetime.now().date()) 
                })
                save_data(); st.rerun()

    # 2. List and Actions
    if st.session_state.db['debts']:
        st.write("---")
        d_df = pd.DataFrame(st.session_state.db['debts'])
        
        # Header Fix
        if len(d_df.columns) == 4:
            d_df.columns = ["NAME", "PHONE", "AMOUNT", "DATE"]
        elif len(d_df.columns) == 3:
            d_df.columns = ["NAME", "PHONE", "AMOUNT"]
        st.table(d_df)
        
        st.markdown("### 🛠️ " + D["action"])
        
        # THE SELECTOR (Crucial: Must have a unique key)
        sel_idx = st.selectbox(
            "Piliin ang Customer" if lang == "Tagalog" else "Select Customer", 
            range(len(st.session_state.db['debts'])), 
            format_func=lambda x: st.session_state.db['debts'][x]['name'],
            key="active_debtor_selection"
        )
        
        # Get the EXACT person currently selected
        current_pers = st.session_state.db['debts'][sel_idx]
        
        col_rem, col_del = st.columns(2)
        
        with col_rem:
            # Re-calculating the message every time the selection changes
            store_name = "NEGOSYO PRO"
            if lang == "Tagalog":
                msg = f"Magandang araw {current_pers['name']}! Paalala mula sa {store_name} tungkol sa utang na ₱{current_pers['amount']:,.2f}. Salamat!"
            else:
                msg = f"Good day {current_pers['name']}! Reminder from {store_name} regarding your balance of ₱{current_pers['amount']:,.2f}. Thanks!"
            
            # The URL-encoded link
            sms_link = f"sms:{current_pers['phone']}?body={urllib.parse.quote(msg)}"
            
            # THE BUTTON: Now it is explicitly tied to the current selection
            st.link_button(f"📲 {D['btn_sms']}", sms_link, use_container_width=True)
            st.caption(f"Will send to: **{current_pers['name']}**")

        with col_del:
            if st.button(D["btn_paid"], type="primary", use_container_width=True, key="pay_btn"):
                st.session_state.db['debts'].pop(sel_idx)
                save_data()
                st.success("Record Updated!")
                st.rerun()
