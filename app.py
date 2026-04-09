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

# --- SIDEBAR (Clean & Optimized) ---
st.sidebar.title("🏪 Bentamate")

# 1. Account Access at the Top
with st.sidebar.popover("👤 Account Access", use_container_width=True):
    auth_mode = st.radio("Action", ["Sign In", "Create Account"])
    if auth_mode == "Sign In":
        st.text_input("Username")
        st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            st.success("Welcome back!")
    else:
        st.text_input("Full Name")
        st.text_input("Email")
        st.text_input("Password", type="password")
        if st.button("Create Account", use_container_width=True):
            st.toast("Registered!", icon="🎉")

st.sidebar.write("---")

# 2. Language Selection
lang = st.sidebar.radio("Wika / Language", ["English", "Tagalog"])

D = {
    "English": {
        "tabs": ["⚡ Quick Sale", "📦 Inventory", "🧾 Expenses", "📊 Reports", "💳 Utang"],
        "rev": "Total Sales Today", "inv": "Total Products", "exp": "Total Expenses", "low": "Low Stock",
        "sale_h": "Register a Sale", "input_c": "Scan/Type Barcode", "qty": "Quantity", "total": "TOTAL"
    },
    "Tagalog": {
        "tabs": ["⚡ Benta", "📦 Imbentaryo", "🧾 Gasto", "📊 Ulat", "💳 Utang"],
        "rev": "Benta Ngayon", "inv": "Produkto", "exp": "Kabuuang Gasto", "low": "Konti na lang",
        "sale_h": "Itala ang Benta", "input_c": "I-scan ang Barcode", "qty": "Dami", "total": "KABUUAN"
    }
}[lang]

# Spacing to push reset to bottom
for _ in range(10): st.sidebar.write("")

# 3. Danger Zone / Reset at the Bottom
st.sidebar.write("---")
with st.sidebar.expander("⚠️ Danger Zone"):
    if st.sidebar.button("🗑️ Reset for New Owner", use_container_width=True, key="reset_button"):
        st.session_state.db = {'sales': [], 'inventory': {}, 'purchase_receipts': [], 'debts': []}
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()

st.title("🏪 Bentamate")
st.write("")

# --- CALCULATIONS ---
s_df = pd.DataFrame(st.session_state.db['sales'])
p_df = pd.DataFrame(st.session_state.db['purchase_receipts'])
today_str = datetime.now().strftime("%Y-%m-%d")

today_sales = s_df[s_df['date'].str.contains(today_str)]['total'].sum() if not s_df.empty else 0
total_products = len(st.session_state.db['inventory'])
total_expenses = p_df['total'].sum() if not p_df.empty else 0
low_stock_count = sum(1 for v in st.session_state.db['inventory'].values() if v['stock'] <= 5)

# --- DASHBOARD ---
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="metric-card" style="border-left-color: #fce4ec;"><div class="metric-title">{D["rev"]}</div><div class="metric-value">₱{today_sales:,.2f}</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-card" style="border-left-color: #e3f2fd;"><div class="metric-title">{D["inv"]}</div><div class="metric-value">{total_products}</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="metric-card" style="border-left-color: #fff3e0;"><div class="metric-title">{D["exp"]}</div><div class="metric-value">₱{total_expenses:,.2f}</div></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="metric-card" style="border-left-color: #e0f2f1;"><div class="metric-title">{D["low"]}</div><div class="metric-value">{low_stock_count}</div></div>', unsafe_allow_html=True)

st.write("---")
t1, t2, t3, t4, t5 = st.tabs(D["tabs"])

# --- TAB 1: QUICK SALE ---
with t1:
    st.markdown(f"### {D['sale_h']}")
    if 'cart' not in st.session_state: st.session_state.cart = []
    col_in, col_qty = st.columns([3, 1])
    b_in = col_in.text_input(D["input_c"], key="barcode_input", label_visibility="collapsed")
    q_in = col_qty.number_input(D["qty"], min_value=1, value=1, key="qty_input", label_visibility="collapsed")
    
    if b_in in st.session_state.db['inventory']:
        item = st.session_state.db['inventory'][b_in]
        st.info(f"✨ **{item['name']}** | ₱{item['price']:.2f} | Stock: {item['stock']}")
        if st.button("➕ Add to Cart", use_container_width=True):
            if item['stock'] >= q_in:
                st.session_state.cart.append({"code": b_in, "name": item['name'], "qty": q_in, "bought": item.get('bought', 0), "price": item['price'], "subtotal": item['price'] * q_in})
                st.rerun()
            else: st.error("Out of stock!")

    if st.session_state.cart:
        cart_df = pd.DataFrame(st.session_state.cart)
        st.table(cart_df[['name', 'qty', 'price', 'subtotal']].style.format({"price": "{:.2f}", "subtotal": "{:.2f}"}))
        if st.button("🏁 Complete Sale", type="primary"):
            tid = datetime.now().strftime("%H%M%S")
            for e in st.session_state.cart:
                st.session_state.db['inventory'][e['code']]['stock'] -= e['qty']
                st.session_state.db['sales'].append({"trans_id": tid, "date": datetime.now().strftime("%Y-%m-%d %H:%M"), "item": e['name'], "qty": e['qty'], "bought": e['bought'], "srp": e['price'], "total": e['subtotal']})
            save_data(); st.session_state.cart = []; st.rerun()

# --- TAB 2: INVENTORY ---
with t2:
    with st.expander("Register New"):
        with st.form("reg_form", clear_on_submit=True):
            c, n = st.text_input("Code"), st.text_input("Name").upper()
            s, b, p = st.number_input("Stock"), st.number_input("Cost"), st.number_input("SRP")
            if st.form_submit_button("Save"):
                st.session_state.db['inventory'][c] = {"name": n, "stock": s, "bought": b, "price": p}
                save_data(); st.rerun()
    
    search = st.text_input("🔍 Search Product").upper()
    for code, d in list(st.session_state.db['inventory'].items()):
        if search == "" or search in code or search in d['name']:
            r1, r2, r3, r4 = st.columns([2,1,1,1])
            r1.write(f"**{d['name']}**")
            r2.write(f"Stock: {d['stock']}")
            r3.write(f"₱{d['price']:.2f}")
            if r4.button("🗑️", key=f"del_{code}"):
                del st.session_state.db['inventory'][code]; save_data(); st.rerun()

# --- TAB 3: EXPENSES ---
with t3:
    with st.form("ex_form", clear_on_submit=True):
        store_ex, amt_ex = st.text_input("Store"), st.number_input("Amount")
        up_f = st.file_uploader("Receipt", type=['jpg','png','pdf'])
        if st.form_submit_button("Log Expense"):
            fname = up_f.name if up_f else "No Receipt"
            if up_f:
                if not os.path.exists("receipts"): os.makedirs("receipts")
                with open(os.path.join("receipts", fname), "wb") as f: f.write(up_f.getbuffer())
            st.session_state.db['purchase_receipts'].append({"date": datetime.now().strftime("%Y-%m-%d"), "store": store_ex.upper(), "total": amt_ex, "receipt": fname})
            save_data(); st.rerun()

    if st.session_state.db['purchase_receipts']:
        ex_df = pd.DataFrame(st.session_state.db['purchase_receipts'])
        st.table(ex_df[['date', 'store', 'total', 'receipt']].style.format({"total": "{:.2f}"}))

# --- TAB 4: REPORTS ---
with t4:
    if not s_df.empty:
        s_df['date_dt'] = pd.to_datetime(s_df['date'])
        s_df['month_year'] = s_df['date_dt'].dt.strftime('%B %Y')
        sel_m = st.selectbox("Select Month", s_df['month_year'].unique())
        
        m_sales = s_df[s_df['month_year'] == sel_m].copy()
        p_df['date_dt'] = pd.to_datetime(p_df['date'])
        m_exp = p_df[p_df['date_dt'].dt.strftime('%B %Y') == sel_m]['total'].sum() if not p_df.empty else 0
        
        gross_sales = m_sales['total'].sum()
        earnings = ((m_sales['srp'] - m_sales['bought']) * m_sales['qty']).sum()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Gross Sales", f"₱{gross_sales:,.2f}")
        c2.metric("Gross Earnings", f"₱{earnings:,.2f}")
        c3.metric("Expenses", f"₱{m_exp:,.2f}")
        c4.metric("Net Profit", f"₱{earnings - m_exp:,.2f}")

        st.write("---")
        st.subheader("📝 Daily Transaction Log")
        m_sales['just_date'] = m_sales['date_dt'].dt.date
        day_logs = m_sales[m_sales['just_date'] == st.date_input("Select Day", value=m_sales['just_date'].max())]
        
        if not day_logs.empty:
            receipts = day_logs.groupby('trans_id').agg({'date_dt': 'first', 'item': lambda x: ", ".join(x), 'total': 'sum'})
            receipts['TIME'] = receipts['date_dt'].dt.strftime('%I:%M %p')
            log_view = receipts.reset_index()[['trans_id', 'TIME', 'item', 'total']]
            log_view.columns = ["TRANS ID", "TIME", "ITEMS BOUGHT", "TOTAL"]
            st.table(log_view.style.format({"TOTAL": "{:.2f}"}))
            
            st.write("---")
            st.subheader("📈 DAILY SALES TREND")
            st.line_chart(m_sales.groupby('just_date')['total'].sum())

# --- TAB 5: UTANG ---
with t5:
    st.markdown("### Debt Registry")
    with st.form("u_form", clear_on_submit=True):
        un, up, ua = st.text_input("NAME").upper(), st.text_input("PHONE"), st.number_input("AMOUNT")
        ud = st.date_input("DUE DATE")
        if st.form_submit_button("ADD DEBT"):
            if sum(d['amount'] for d in st.session_state.db['debts'] if d['name'] == un) + ua > 500: st.error("Limit ₱500!")
            else:
                st.session_state.db['debts'].append({"name": un, "phone": up, "amount": ua, "date": str(datetime.now().date()), "due_date": str(ud)})
                save_data(); st.rerun()

    if st.session_state.db['debts']:
        u_df = pd.DataFrame(st.session_state.db['debts'])
        st.table(u_df[['name', 'phone', 'amount', 'due_date']].style.format({"amount": "{:.2f}"}))
        
        sel = st.selectbox("Select Debtor", range(len(st.session_state.db['debts'])), format_func=lambda x: st.session_state.db['debts'][x]['name'])
        pers = st.session_state.db['debts'][sel]
        
        c_sms, c_paid = st.columns(2)
        sms_url = f"sms:{pers['phone']}?body={urllib.parse.quote(f'Hi {pers['name']}, reminder of your ₱{pers['amount']:.2f} balance.')}"
        c_sms.link_button("SEND SMS", sms_url, use_container_width=True)
        if c_paid.button("MARK PAID", type="primary", use_container_width=True):
            st.session_state.db['debts'].pop(sel); save_data(); st.rerun()
