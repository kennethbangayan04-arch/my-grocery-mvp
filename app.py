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

lang = st.sidebar.radio("Wika / Language", ["English", "Tagalog"])

D = {
    "English": {
        "tabs": ["⚡ Quick Sale", "📦 Inventory", "🧾 Expenses", "📊 Reports", "💳 Utang"],
        "rev": "Total Sales Today", "inv": "Total Products", "exp": "Total Expenses", "low": "Low Stock",
        "sale_h": "Register a Sale", "input_c": "Scan/Type Barcode", "qty": "Quantity", "total": "TOTAL",
        "btn_sell": "🏁 Complete Sale", "btn_clear": "🗑️ Clear Cart", "low_stock": "⚠️ LOW STOCK!",
        "action": "Actions", "add_stock": "Add Stock", "btn_paid": "Mark as Paid", "btn_sms": "Send SMS Reminder"
    },
    "Tagalog": {
        "tabs": ["⚡ Benta", "📦 Imbentaryo", "🧾 Gasto", "📊 Ulat", "💳 Utang"],
        "rev": "Benta Ngayon", "inv": "Produkto", "exp": "Kabuuang Gasto", "low": "Konti na lang",
        "sale_h": "Itala ang Benta", "input_c": "I-scan ang Barcode", "qty": "Dami", "total": "KABUUAN",
        "btn_sell": "🏁 Tapusin ang Benta", "btn_clear": "🗑️ Burahin ang Cart", "low_stock": "⚠️ KONTI NA LANG!",
        "action": "Aksyon", "add_stock": "Dagdag Stock", "btn_paid": "Bayad na", "btn_sms": "Mag-SMS Paalala"
    }
}[lang]

# --- SIDEBAR ---
st.sidebar.title("🏪 Bentamate")
st.sidebar.caption("Smart Business Companion")
st.sidebar.write("---")

if st.sidebar.button("🗑️ Reset for New Owner", key="reset_button"):
    st.session_state.db = {'sales': [], 'inventory': {}, 'purchase_receipts': [], 'debts': []}
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.rerun()

st.title("🏪 Bentamate")
st.markdown("##### Smart Business Companion")
st.write("")

# --- TOP DASHBOARD CALCULATIONS ---
s_df = pd.DataFrame(st.session_state.db['sales'])
p_df = pd.DataFrame(st.session_state.db['purchase_receipts'])
today_str = datetime.now().strftime("%Y-%m-%d")

today_sales = s_df[s_df['date'].str.contains(today_str)]['total'].sum() if not s_df.empty else 0
total_products = len(st.session_state.db['inventory'])
total_expenses = p_df['total'].sum() if not p_df.empty else 0
low_stock_threshold = 5 
low_stock_count = sum(1 for v in st.session_state.db['inventory'].values() if v['stock'] <= low_stock_threshold)

# --- TOP DASHBOARD DISPLAY ---
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
    b_in = col_in.text_input(D["input_c"], placeholder="Scan/Type Barcode", key="barcode_input", label_visibility="collapsed")
    q_in = col_qty.number_input(D["qty"], min_value=1, value=1, key="qty_input", label_visibility="collapsed")
    
    if b_in in st.session_state.db['inventory']:
        item = st.session_state.db['inventory'][b_in]
        st.info(f"✨ **{item['name']}** | ₱{item['price']:.2f} | Stock: {item['stock']}")
        if st.button("➕ Add to Cart", use_container_width=True, key="add_to_cart"):
            if item['stock'] >= q_in:
                st.session_state.cart.append({"code": b_in, "name": item['name'], "qty": q_in, "bought": item.get('bought', 0), "price": item['price'], "subtotal": item['price'] * q_in})
                st.rerun()
            else: st.error("Out of stock!")

    if st.session_state.cart:
        st.write("---")
        cart_df = pd.DataFrame(st.session_state.cart)
        display_cart = cart_df[['name', 'qty', 'price', 'subtotal']].copy()
        display_cart.columns = ["NAME", "QUANTITY", "PRICE", "SUBTOTAL"] 
        formatted_cart = display_cart.style.format({"PRICE": "₱{:,.2f}", "SUBTOTAL": "₱{:,.2f}"})
        
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
    st.markdown("### 📦 Stock Management")
    with st.expander("Register New Product"):
        with st.form("reg_form", clear_on_submit=True):
            c_i = st.text_input("Code")
            n_i = st.text_input("Name").upper()
            cs, cb, cp = st.columns(3)
            s_i = cs.number_input("Stock", min_value=0)
            b_i = cb.number_input("Bought Price", min_value=0.0)
            p_i = cp.number_input("SRP", min_value=0.0)
            if st.form_submit_button("Save"):
                st.session_state.db['inventory'][c_i] = {"name": n_i, "stock": s_i, "bought": b_i, "price": p_i, "min_alert": 5}
                save_data(); st.rerun()

    st.write("---")
    search_query = st.text_input("🔍 Search Product", key="inv_search").upper()

    if st.session_state.db['inventory']:
        h1, h2, h3, h4, h5, h6 = st.columns([1.5, 2.5, 1, 1, 1.5, 1])
        h1.write("**CODE**"); h2.write("**NAME**"); h3.write("**STOCK**"); h4.write("**SRP**"); h5.write("**ADD**"); h6.write("**DEL**")
        for code, det in list(st.session_state.db['inventory'].items()):
            if search_query == "" or search_query in code.upper() or search_query in det['name'].upper():
                r1, r2, r3, r4, r5, r6 = st.columns([1.5, 2.5, 1, 1, 1.5, 1])
                r1.write(f"`{code}`"); r2.write(det['name'])
                if det['stock'] <= low_stock_threshold: r3.write(f"🔴 **{det['stock']}**")
                else: r3.write(f"🟢 {det['stock']}")
                r4.write(f"₱{det['price']:.2f}")
                with r5:
                    with st.popover("➕"):
                        amt = st.number_input("Quantity", min_value=1, key=f"add_inv_{code}")
                        if st.button("Save", key=f"btn_inv_{code}"):
                            st.session_state.db['inventory'][code]['stock'] += amt
                            save_data(); st.rerun()
                if r6.button("🗑️", key=f"del_inv_{code}"):
                    del st.session_state.db['inventory'][code]; save_data(); st.rerun()

# --- TAB 3: EXPENSES (With File Viewing) ---
with t3:
    st.markdown(f"### {D['exp']}")
    with st.form("exp_form", clear_on_submit=True):
        store = st.text_input("Store Name")
        amt = st.number_input("Amount", min_value=0.0)
        uploaded_file = st.file_uploader("Upload Receipt", type=['jpg', 'png', 'jpeg', 'pdf'])
        
        if st.form_submit_button("Log Expense"):
            if store and amt > 0:
                # If a file is uploaded, we save it locally so we can view it later
                receipt_name = "No Receipt"
                if uploaded_file:
                    receipt_name = uploaded_file.name
                    # Create a 'receipts' folder if it doesn't exist
                    if not os.path.exists("receipts"):
                        os.makedirs("receipts")
                    # Save the file into that folder
                    with open(os.path.join("receipts", receipt_name), "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                st.session_state.db['purchase_receipts'].append({
                    "date": str(datetime.now().strftime("%Y-%m-%d")), 
                    "store": store.upper(), 
                    "total": amt, 
                    "receipt": receipt_name
                })
                save_data(); st.success("Expense Recorded!"); st.rerun()

    if st.session_state.db['purchase_receipts']:
        st.write("---")
        df_p = pd.DataFrame(st.session_state.db['purchase_receipts'])
        df_p['date_dt'] = pd.to_datetime(df_p['date'])
        df_p['month_year'] = df_p['date_dt'].dt.strftime('%B %Y')
        sel_month = st.selectbox("Filter Month", df_p['month_year'].unique())
        
        # Filter the data
        f_df = df_p[df_p['month_year'] == sel_month].copy()
        
        # Display the Table headers
        h1, h2, h3, h4 = st.columns([1, 2, 1, 1])
        h1.write("**DATE**"); h2.write("**STORE**"); h3.write("**AMOUNT**"); h4.write("**FILE**")
        
        for index, row in f_df.iterrows():
            c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
            c1.write(row['date'])
            c2.write(row['store'])
            c3.write(f"₱{row['total']:,.2f}")
            
            # If there is a receipt, create a download button for it
            if row['receipt'] != "No Receipt":
                file_path = os.path.join("receipts", row['receipt'])
                if os.path.exists(file_path):
                    with open(file_path, "rb") as file:
                        c4.download_button(
                            label="👁️ View",
                            data=file,
                            file_name=row['receipt'],
                            key=f"btn_{index}"
                        )
                else:
                    c4.write("Missing")
            else:
                c4.write("None")
# --- TAB 4: REPORTS (With Exact Input Time) ---
with t4:
    st.markdown("### 📊 Business Performance")
    if not s_df.empty:
        # 1. Convert to datetime and sort
        s_df['date'] = pd.to_datetime(s_df['date'])
        s_df['month_year'] = s_df['date'].dt.strftime('%B %Y')
        
        sel_m = st.selectbox("Select Month", s_df['month_year'].unique(), key="rep_month_sel")
        m_sales = s_df[s_df['month_year'] == sel_m].copy()
        
        # ... (keep your metric columns c1, c2, c3, c4 here) ...

        st.write("---")
        st.subheader("📝 Daily Transaction Log")
        
        # 2. Filter by Day
        m_sales['just_date'] = m_sales['date'].dt.date
        available_days = sorted(m_sales['just_date'].unique(), reverse=True)
        sel_day = st.date_input("Select Day", value=available_days[0] if available_days else datetime.now().date())
        
        day_logs = m_sales[m_sales['just_date'] == sel_day].copy()
        
        if not day_logs.empty:
            # 3. Group by Transaction ID to show merged receipts
            # We take the 'first' date entry to get the exact input time
            receipts = day_logs.groupby('trans_id').agg({
                'date': 'first', 
                'item': lambda x: ", ".join(x),
                'total': 'sum'
            }).sort_values(by='date', ascending=False)

            # 4. Format the TIME to 12-hour format (e.g., 01:45 PM)
            receipts['TIME'] = receipts['date'].dt.strftime('%I:%M %p')
            
            # 5. Clean up the display table
            log_display = receipts[['TIME', 'item', 'total']].copy()
            log_display.columns = ["TIME", "ITEMS BOUGHT", "RECEIPT TOTAL"]
            
            st.info(f"Total Daily Sales: **₱{receipts['total'].sum():,.2f}**")
            # Use 2-decimal formatting for the total column
            st.table(log_display.style.format({"RECEIPT TOTAL": "₱{:,.2f}"}))
        else:
            st.warning("No transactions found for this day.")

# --- TAB 5: UTANG ---
with t5:
    st.markdown("### Debt Registry (Limit: ₱500)")
    CREDIT_LIMIT = 500.0
    today_dt_obj = datetime.now().date()
    max_due = today_dt_obj + pd.Timedelta(days=7)
    
    with st.form("u_form", clear_on_submit=True):
        un = st.text_input("NAME").upper()
        up = st.text_input("PHONE")
        ua = st.number_input("AMOUNT", min_value=0.0)
        ud = st.date_input("DUE DATE (Max 7 Days)", value=max_due, min_value=today_dt_obj, max_value=max_due)
        
        if st.form_submit_button("ADD DEBT"):
            if un and up and ua > 0:
                existing = sum(d['amount'] for d in st.session_state.db['debts'] if d['name'] == un)
                if existing + ua > CREDIT_LIMIT:
                    st.error(f"❌ **LIMIT REACHED!** Current Debt: ₱{existing:,.2f}")
                else:
                    st.session_state.db['debts'].append({
                        "name": un, "phone": up, "amount": ua, 
                        "date": str(today_dt_obj), "due_date": str(ud)
                    })
                    save_data(); st.success("Debt Added Successfully"); st.rerun()

    if st.session_state.db['debts']:
        st.write("---")
        d_df = pd.DataFrame(st.session_state.db['debts'])
        
        # Robust Date Logic
        d_df['DUE_DT'] = pd.to_datetime(d_df['due_date'])
        now_dt = pd.to_datetime(datetime.now().date())
        d_df['DAYS_LEFT'] = (d_df['DUE_DT'] - now_dt).dt.days
        
        display_debt = d_df[['name', 'phone', 'amount', 'date', 'due_date', 'DAYS_LEFT']].copy()
        display_debt.columns = ["NAME", "PHONE", "AMOUNT", "DATE", "DUE DATE", "DAYS_LEFT"]
        
        def apply_row_styles(row):
            days = row['DAYS_LEFT']
            if days < 0: return ['background-color: #ffcdd2'] * len(row) # Red
            if days <= 3: return ['background-color: #fff9c4'] * len(row) # Yellow
            return [''] * len(row)

        st.table(
            display_debt.style.apply(apply_row_styles, axis=1)
            .format({"AMOUNT": "₱{:,.2f}"})
            .hide(axis="columns", subset=["DAYS_LEFT"]) 
        )
        
        upcoming = d_df[(d_df['DAYS_LEFT'] <= 3) & (d_df['DAYS_LEFT'] >= 0)]
        if not upcoming.empty:
            st.warning(f"🔔 **REMINDER:** {len(upcoming)} customer(s) due within 3 days!")

        st.write("---")
        # FIXED INDENTATION: Aligned with the 'if' block (8 spaces)
        idx = st.selectbox("SELECT DEBTOR", range(len(st.session_state.db['debts'])), 
                           format_func=lambda x: st.session_state.db['debts'][x]['name'], key="debt_sel_final")
        pers = st.session_state.db['debts'][idx]
        
        p_due = pd.to_datetime(pers['due_date'])
        p_days = int((p_due - now_dt).days) 

        col_sms, col_pay = st.columns(2)
        with col_sms:
            msg = f"Good day {pers['name']}! Your ₱{pers['amount']:,.2f} balance is due on {pers['due_date']}."
            if p_days <= 3:
                msg = f"URGENT: {pers['name']}, your ₱{pers['amount']:,.2f} balance is due in {p_days} days!"
            
            st.link_button("SEND SMS", f"sms:{pers['phone']}?body={urllib.parse.quote(msg)}", use_container_width=True)
        
        with col_pay:
            if st.button("MARK PAID", type="primary", use_container_width=True, key="pay_debt_final"):
                st.session_state.db['debts'].pop(idx); save_data(); st.rerun()
