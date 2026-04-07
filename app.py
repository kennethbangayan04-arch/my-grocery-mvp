%%writefile app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# --- 1. DATA ENGINE ---
DB_FILE = 'negosyo_pro_master.json'
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: return json.load(f)
    return {'sales': [], 'inventory': {"4800016644801": {"name": "Lucky Me", "stock": 20, "min_alert": 10, "price": 15}, "12345": {"name": "Rice (1kg)", "stock": 50, "min_alert": 15, "price": 55}}, 'purchase_receipts': [], 'debts': []}

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def save_data():
    with open(DB_FILE, 'w') as f: json.dump(st.session_state.db, f)

# --- 2. UI & LANGUAGE ---
st.set_page_config(page_title="Negosyo Pro MVP", layout="wide")
lang = st.sidebar.radio("Language / Wika", ["English", "Tagalog"])
T = {"English": ["Quick Sale", "Inventory Hub", "Purchase Receipts", "Financial Reports", "Utang Tracker", "Add Sale", "Low Stock!", "Register Product"],
     "Tagalog": ["Mabilisang Benta", "Sentro ng Imbentaryo", "Resibo ng Binili", "Ulat ng Pananalapi", "Listahan ng Utang", "Itala ang Benta", "Mababa ang Stock!", "I-rehistro ang Produkto"]}[lang]

st.title(f"🏪 Negosyo Pro: {T[3]}")
tabs = st.tabs([T[0], T[1], T[2], T[3], T[4]])

# --- TAB 1: QUICK SALE ---
with tabs[0]:
    st.subheader(T[0])
    b_in = st.text_input("Scan/Type Code", key="sale_in")
    if b_in in st.session_state.db['inventory']:
        item = st.session_state.db['inventory'][b_in]
        st.info(f"**{item['name']}** | ₱{item['price']} | Stock: {item['stock']}")
        if st.button(T[5]):
            if item['stock'] > 0:
                st.session_state.db['inventory'][b_in]['stock'] -= 1
                st.session_state.db['sales'].append({"date": str(datetime.now().strftime("%Y-%m-%d")), "item": item['name'], "total": item['price']})
                save_data(); st.success("Sold!"); st.rerun()
            else: st.error("Out of Stock!")

# --- TAB 2: INVENTORY ---
with tabs[1]:
    with st.expander(f"➕ {T[7]}"):
        with st.form("manual_add"):
            c_in = st.text_input("Code"); n_in = st.text_input("Name")
            s_in = st.number_input("Stock", min_value=0); p_in = st.number_input("Price", min_value=0.0)
            if st.form_submit_button(T[7]):
                st.session_state.db['inventory'][c_in] = {"name": n_in, "stock": s_in, "price": p_in, "min_alert": 5}
                save_data(); st.rerun()
    st.dataframe(pd.DataFrame.from_dict(st.session_state.db['inventory'], orient='index'), use_container_width=True)

# --- TAB 3: PURCHASE RECEIPTS (Expenses) ---
with tabs[2]:
    st.subheader(T[2])
    with st.form("p_form"):
        store = st.text_input("Store Name"); cost = st.number_input("Amount Paid (Expense)", min_value=0.0)
        if st.form_submit_button("Archive Receipt"):
            st.session_state.db['purchase_receipts'].append({"date": str(datetime.now().date()), "store": store, "total": cost})
            save_data(); st.success("Expense Recorded!"); st.rerun()
    if st.session_state.db['purchase_receipts']:
        st.dataframe(pd.DataFrame(st.session_state.db['purchase_receipts']), use_container_width=True)

# --- TAB 4: FINANCIAL REPORTS (Revenue vs Expenses) ---
with tabs[3]:
    st.header(T[3])
    
    # Calculate Totals
    total_revenue = sum([s['total'] for s in st.session_state.db['sales']])
    total_expenses = sum([p['total'] for p in st.session_state.db['purchase_receipts']])
    net_profit = total_revenue - total_expenses
    
    # Display Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Sales (Revenue)", f"₱{total_revenue:,.2f}")
    c2.metric("Total Expenses", f"₱{total_expenses:,.2f}", delta_color="inverse")
    
    # Profit Color Logic
    if net_profit >= 0:
        c3.metric("Net Profit", f"₱{net_profit:,.2f}", delta=f"₱{net_profit:,.2f}")
    else:
        c3.metric("Net Loss", f"₱{net_profit:,.2f}", delta=f"₱{net_profit:,.2f}", delta_color="normal")

    st.markdown("---")
    st.subheader("Transaction Breakdown")
    col_left, col_right = st.columns(2)
    with col_left:
        st.write("**Recent Sales**")
        if st.session_state.db['sales']: st.dataframe(pd.DataFrame(st.session_state.db['sales']), use_container_width=True)
    with col_right:
        st.write("**Recent Expenses**")
        if st.session_state.db['purchase_receipts']: st.dataframe(pd.DataFrame(st.session_state.db['purchase_receipts']), use_container_width=True)

# --- TAB 5: UTANG ---
with tabs[4]:
    u_n = st.text_input("Customer"); u_p = st.text_input("Phone"); u_a = st.number_input("Amount")
    if st.button("Save Utang"):
        st.session_state.db['debts'].append({"name": u_n, "phone": u_p, "amount": u_a})
        save_data(); st.success("Saved!"); st.rerun()
    if st.session_state.db['debts']: st.table(pd.DataFrame(st.session_state.db['debts']))
