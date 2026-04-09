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

# Account Access Section
with st.sidebar.popover("👤 Account Access", use_container_width=True):
    auth_mode = st.radio("Choose Action", ["Sign In", "Create Account"])
    if auth_mode == "Sign In":
        st.text_input("Email or Username", placeholder="juan@email.com")
        st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            st.success("Logged in successfully!")
    else:
        st.text_input("Full Name")
        st.text_input("Email", placeholder="juan@email.com")
        st.text_input("Create Password", type="password")
        st.text_input("Confirm Password", type="password")
        if st.button("Register", use_container_width=True):
            st.toast("Account created (Demo Mode)!", icon="🎉")

# Language Selection (Must be BEFORE dictionary mapping)
lang_choice = st.sidebar.radio("Wika / Language", ["English", "Tagalog"])

# Dictionary mapping
translations = {
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
}
D = translations[lang_choice]

# Vertical Spacing for Reset
for _ in range(15):
    st.sidebar.write("")

# Reset Button at the bottom
st.sidebar.write("---")
if st.sidebar.button("🗑️ Reset for New Owner", key="reset_button", use_container_width=True):
    st.session_state.db = {'sales': [], 'inventory': {}, 'purchase_receipts': [], 'debts': []}
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.rerun()

# --- 4. DASHBOARD CALCULATIONS ---
st.title("🏪 Bentamate")
st.markdown("##### Smart Business Companion")

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
                st.session_state.db['inventory'][c_i] = {"name": n_i, "stock": s_i, "bought": b_i, "price": p_i}
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

# --- TAB 3: EXPENSES ---
with t3:
    st.markdown(f"### {D['exp']}")
    with st.form("exp_form", clear_on_submit=True):
        store_ex = st.text_input("Store Name")
        amt_ex = st.number_input("Amount", min_value=0.0)
        uploaded_file = st.file_uploader("Upload Receipt", type=['jpg', 'png', 'jpeg', 'pdf'])
        if st.form_submit_button("Log Expense"):
            if store_ex and amt_ex > 0:
                receipt_name = uploaded_file.name if uploaded_file else "No Receipt"
                if uploaded_file:
                    if not os.path.exists("receipts"): os.makedirs("receipts")
                    with open(os.path.join("receipts", receipt_name), "wb") as f:
                        f.write(uploaded_file.getbuffer())
                st.session_state.db['purchase_receipts'].append({"date": str(datetime.now().strftime("%Y-%m-%d")), "store": store_ex.upper(), "total": amt_ex, "receipt": receipt_name})
                save_data(); st.success("Expense Recorded!"); st.rerun()

    if st.session_state.db['purchase_receipts']:
        st.write("---")
        df_p_view = pd.DataFrame(st.session_state.db['purchase_receipts'])
        df_p_view['date_dt'] = pd.to_datetime(df_p_view['date'])
        df_p_view['month_year'] = df_p_view['date_dt'].dt.strftime('%B %Y')
        sel_month_ex = st.selectbox("Filter Month", df_p_view['month_year'].unique(), key="ex_month_sel")
        f_df_ex = df_p_view[df_p_view['month_year'] == sel_month_ex].copy()
        
        h1, h2, h3, h4 = st.columns([1, 2, 1, 1])
        h1.write("**DATE**"); h2.write("**STORE**"); h3.write("**AMOUNT**"); h4.write("**FILE**")
        for idx, row in f_df_ex.iterrows():
            c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
            c1.write(row['date'])
            c2.write(row['store'])
            c3.write(f"₱{row['total']:,.2f}")
            if row['receipt'] != "No Receipt":
                f_path = os.path.join("receipts", row['receipt'])
                if os.path.exists(f_path):
                    with open(f_path, "rb") as f:
                        c4.download_button("👁️ View", f, file_name=row['receipt'], key=f"ex_btn_{idx}")
                else: c4.write("Missing")
            else: c4.write("None")

# --- TAB 4: REPORTS ---
with t4:
    st.markdown("### 📊 Business Performance")
    if not s_df.empty:
        s_df['date_dt'] = pd.to_datetime(s_df['date'])
        s_df['month_year'] = s_df['date_dt'].dt.strftime('%B %Y')
        sel_m_rep = st.selectbox("Select Month", s_df['month_year'].unique(), key="rep_month_sel")
        m_sales_rep = s_df[s_df['month_year'] == sel_m_rep].copy()
        
        p_df['date_dt'] = pd.to_datetime(p_df['date'])
        p_df['month_year'] = p_df['date_dt'].dt.strftime('%B %Y')
        m_expenses_rep = p_df[p_df['month_year'] == sel_m_rep]['total'].sum() if not p_df.empty else 0
        
        total_gross_sales = m_sales_rep['total'].sum()
        total_gross_earnings = ((m_sales_rep['srp'] - m_sales_rep['bought']) * m_sales_rep['qty']).sum()
        net_profit = total_gross_earnings - m_expenses_rep

        rc1, rc2, rc3, rc4 = st.columns(4)
        rc1.metric("Gross Sales", f"₱{total_gross_sales:,.2f}")
        rc2.metric("Gross Earnings", f"₱{total_gross_earnings:,.2f}")
        rc3.metric("Expenses", f"₱{m_expenses_rep:,.2f}")
        rc4.metric("Net Profit", f"₱{net_profit:,.2f}")

        st.write("---")
        st.subheader("📝 Daily Transaction Log")
        m_sales_rep['just_date'] = m_sales_rep['date_dt'].dt.date
        available_days = sorted(m_sales_rep['just_date'].unique(), reverse=True)
        sel_day_rep = st.date_input("Select Day", value=available_days[0] if available_days else datetime.now().date())
        
        day_logs_rep = m_sales_rep[m_sales_rep['just_date'] == sel_day_rep].copy()
        if not day_logs_rep.empty:
            receipts_rep = day_logs_rep.groupby('trans_id').agg({'date_dt': 'first', 'item': lambda x: ", ".join(x), 'total': 'sum'}).sort_values(by='date_dt', ascending=False)
            receipts_rep['TIME'] = receipts_rep['date_dt'].dt.strftime('%I:%M %p')
            receipts_rep = receipts_rep.reset_index()
            log_display = receipts_rep[['trans_id', 'TIME', 'item', 'total']]
            log_display.columns = ["TRANS ID", "TIME", "ITEMS BOUGHT", "TOTAL"]
            st.info(f"Total Daily Sales: **₱{receipts_rep['total'].sum():,.2f}**")
            st.table(log_display.style.format({"TOTAL": "₱{:,.2f}"}))
        
        st.write("---")
        st.subheader("📈 DAILY SALES TREND")
        chart_data = m_sales_rep.groupby('just_date')['total'].sum()
        if not chart_data.empty: st.line_chart(chart_data)
        else: st.info("Not enough data to generate a trend yet.")
    else: st.info("No sales data available yet.")

# --- TAB 5: UTANG ---
with t5:
    st.markdown("### Debt Registry (Limit: ₱500)")
    CREDIT_LIMIT = 500.0
    now_dt = datetime.now().date()
    max_due_dt = now_dt + pd.Timedelta(days=7)
    
    with st.form("u_form", clear_on_submit=True):
        un_u = st.text_input("NAME").upper()
        up_u = st.text_input("PHONE")
        ua_u = st.number_input("AMOUNT", min_value=0.0)
        ud_u = st.date_input("DUE DATE (Max 7 Days)", value=max_due_dt, min_value=now_dt, max_value=max_due_dt)
        if st.form_submit_button("ADD DEBT"):
            existing_u = sum(d['amount'] for d in st.session_state.db['debts'] if d['name'] == un_u)
            if existing_u + ua_u > CREDIT_LIMIT: st.error(f"❌ **LIMIT REACHED!** Current: ₱{existing_u:,.2f}")
            else:
                st.session_state.db['debts'].append({"name": un_u, "phone": up_u, "amount": ua_u, "date": str(now_dt), "due_date": str(ud_u)})
                save_data(); st.success("Debt Added!"); st.rerun()

    if st.session_state.db['debts']:
        st.write("---")
        d_df_u = pd.DataFrame(st.session_state.db['debts'])
        d_df_u['DUE_DT'] = pd.to_datetime(d_df_u['due_date']).dt.date
        d_df_u['DAYS_LEFT'] = (d_df_u['DUE_DT'] - now_dt).apply(lambda x: x.days)
        
        display_u = d_df_u[['name', 'phone', 'amount', 'date', 'due_date', 'DAYS_LEFT']].copy()
        display_u.columns = ["NAME", "PHONE", "AMOUNT", "DATE", "DUE DATE", "DAYS_LEFT"]
        
        def style_u(row):
            d = row['DAYS_LEFT']
            if d < 0: return ['background-color: #ffcdd2'] * len(row)
            if d <= 3: return ['background-color: #fff9c4'] * len(row)
            return [''] * len(row)

        st.table(display_u.style.apply(style_u, axis=1).format({"AMOUNT": "₱{:,.2f}"}).hide(axis="columns", subset=["DAYS_LEFT"]))
        
        idx_u = st.selectbox("SELECT DEBTOR", range(len(st.session_state.db['debts'])), format_func=lambda x: st.session_state.db['debts'][x]['name'])
        pers_u = st.session_state.db['debts'][idx_u]
        p_days_u = (pd.to_datetime(pers_u['due_date']).date() - now_dt).days
        
        c_sms, c_paid = st.columns(2)
        with c_sms:
            msg_u = f"Reminder: Your balance ₱{pers_u['amount']:,.2f} is due on {pers_u['due_date']}."
            if p_days_u <= 3: msg_u = f"URGENT: Your balance ₱{pers_u['amount']:,.2f} is due in {p_days_u} days!"
            st.link_button("SEND SMS", f"sms:{pers_u['phone']}?body={urllib.parse.quote(msg_u)}", use_container_width=True)
        with c_paid:
            if st.button("MARK PAID", type="primary", use_container_width=True):
                st.session_state.db['debts'].pop(idx_u); save_data(); st.rerun()
