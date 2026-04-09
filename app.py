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
        "sale_h": "Register a Sale", "input_c": "Scan/Type Barcode", "qty": "Qty", "total": "TOTAL",
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
if st.sidebar.button("🗑️ Reset for New Owner", key="owner_reset"):
    st.session_state.db = {'sales': [], 'inventory': {}, 'purchase_receipts': [], 'debts': []}
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.rerun()

# --- TOP DASHBOARD ---
s_df = pd.DataFrame(st.session_state.db['sales'])
p_df = pd.DataFrame(st.session_state.db['purchase_receipts'])
today_str = datetime.now().strftime("%Y-%m-%d")

today_sales = s_df[s_df['date'].str.contains(today_str)]['total'].sum() if not s_df.empty else 0
total_products = len(st.session_state.db['inventory'])
total_expenses = p_df['total'].sum() if not p_df.empty else 0
low_stock_count = sum(1 for v in st.session_state.db['inventory'].values() if v['stock'] <= 5)

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="metric-card" style="border-left-color: #fce4ec;"><div class="metric-title">{D["rev"]}</div><div class="metric-value">₱{today_sales:,.2f}</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-card" style="border-left-color: #e3f2fd;"><div class="metric-title">{D["inv"]}</div><div class="metric-value">{total_products}</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="metric-card" style="border-left-color: #fff3e0;"><div class="metric-title">{D["exp"]}</div><div class="metric-value">₱{total_expenses:,.2f}</div></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="metric-card" style="border-left-color: #e0f2f1;"><div class="metric-title">{D["low"]}</div><div class="metric-value">{low_stock_count}</div></div>', unsafe_allow_html=True)

st.write("---")

# --- NAVIGATION TABS ---
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
        st.table(cart_df[['name', 'qty', 'price', 'subtotal']])
        total_bill = cart_df['subtotal'].sum()
        st.header(f"{D['total']}: ₱{total_bill:,.2f}")
        cp, cc = st.columns(2)
        if cp.button(D["btn_sell"], type="primary", use_container_width=True):
            for entry in st.session_state.cart:
                st.session_state.db['inventory'][entry['code']]['stock'] -= entry['qty']
                st.session_state.db['sales'].append({"date": str(datetime.now().strftime("%Y-%m-%d %H:%M")), "item": entry['name'], "qty": entry['qty'], "bought": entry['bought'], "srp": entry['price'], "total": entry['subtotal']})
            save_data(); st.session_state.cart = []; st.balloons(); st.rerun()
        if cc.button(D["btn_clear"], use_container_width=True): st.session_state.cart = []; st.rerun()

# --- TAB 2: INVENTORY ---
with t2:
    st.markdown(f"### {D['inv']}")
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

    if st.session_state.db['inventory']:
        h1, h2, h3, h4, h5, h6 = st.columns([1.5, 2.5, 1, 1, 1.5, 1])
        h1.write("**CODE**"); h2.write("**NAME**"); h3.write("**STOCK**"); h4.write("**SRP**"); h5.write("**ADD**"); h6.write("**DEL**")
        for code, det in list(st.session_state.db['inventory'].items()):
            r1, r2, r3, r4, r5, r6 = st.columns([1.5, 2.5, 1, 1, 1.5, 1])
            r1.write(f"`{code}`"); r2.write(det['name']); r3.write(str(det['stock'])); r4.write(f"₱{det['price']:.2f}")
            with r5:
                with st.popover("➕"):
                    amt = st.number_input("Qty", min_value=1, key=f"add_{code}")
                    if st.button("Save", key=f"btn_{code}"):
                        st.session_state.db['inventory'][code]['stock'] += amt
                        save_data(); st.rerun()
            if r6.button("🗑️", key=f"del_{code}"):
                del st.session_state.db['inventory'][code]; save_data(); st.rerun()

# --- TAB 3: EXPENSES ---
with t3:
    st.markdown(f"### {D['exp']}")
    with st.form("exp_form", clear_on_submit=True):
        store = st.text_input("Store Name")
        amt = st.number_input("Amount", min_value=0.0)
        if st.form_submit_button("Log Expense"):
            st.session_state.db['purchase_receipts'].append({"date": str(datetime.now().strftime("%Y-%m-%d")), "store": store.upper(), "total": amt})
            save_data(); st.rerun()
    if st.session_state.db['purchase_receipts']:
        df_p = pd.DataFrame(st.session_state.db['purchase_receipts'])
        df_p['date'] = pd.to_datetime(df_p['date'])
        df_p['month_year'] = df_p['date'].dt.strftime('%B %Y')
        sel_month = st.selectbox("Filter Month", df_p['month_year'].unique())
        st.table(df_p[df_p['month_year'] == sel_month][['date', 'store', 'total']])

# --- TAB 4: REPORTS ---
with t4:
    st.markdown("### Financial Analysis")
    if not s_df.empty:
        s_df['date'] = pd.to_datetime(s_df['date'])
        s_df['month_year'] = s_df['date'].dt.strftime('%B %Y')
        sel_m = st.selectbox("Select Report Month", s_df['month_year'].unique())
        m_sales = s_df[s_df['month_year'] == sel_m]
        rev = m_sales['total'].sum()
        markup = ((m_sales['srp'] - m_sales['bought']) * m_sales['qty']).sum()
        m_exp = pd.DataFrame(st.session_state.db['purchase_receipts'])
        exp_total = 0
        if not m_exp.empty:
            m_exp['date'] = pd.to_datetime(m_exp['date'])
            exp_total = m_exp[m_exp['date'].dt.strftime('%B %Y') == sel_m]['total'].sum()
        
        st.metric("Net Profit", f"₱{markup - exp_total:,.2f}")
        st.write("---")
        st.subheader("Daily Sales Trend")
        m_sales['day'] = m_sales['date'].dt.date
        st.line_chart(m_sales.groupby('day')['total'].sum())

# --- TAB 5: UTANG ---
with t5:
    st.markdown("### Debt Registry")
    with st.form("u_form", clear_on_submit=True):
        un, up, ua = st.text_input("Name"), st.text_input("Phone"), st.number_input("Amount", min_value=0.0)
        if st.form_submit_button("Add Debt"):
            st.session_state.db['debts'].append({"name": un.upper(), "phone": up, "amount": ua, "date": str(datetime.now().date())})
            save_data(); st.rerun()
    if st.session_state.db['debts']:
        st.table(pd.DataFrame(st.session_state.db['debts']))
        idx = st.selectbox("Select Debtor", range(len(st.session_state.db['debts'])), format_func=lambda x: st.session_state.db['debts'][x]['name'], key="sms_sel")
        pers = st.session_state.db['debts'][idx]
        msg = f"Good day {pers['name']}! Friendly reminder of your balance: ₱{pers['amount']:,.2f}."
        st.link_button("Send SMS", f"sms:{pers['phone']}?body={urllib.parse.quote(msg)}")
        if st.button("Mark as Paid", type="primary"):
            st.session_state.db['debts'].pop(idx); save_data(); st.rerun()
