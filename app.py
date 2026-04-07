import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# --- 1. DATA ENGINE ---
DB_FILE = 'negosyo_pro_master.json'

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: 
                return json.load(f)
        except:
            pass
    return {
        'sales': [], 
        'inventory': {
            "4800016644801": {"name": "Lucky Me", "stock": 20, "min_alert": 10, "price": 15},
            "12345": {"name": "Rice (1kg)", "stock": 50, "min_alert": 15, "price": 55}
        }, 
        'purchase_receipts': [], 
        'debts': []
    }

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def save_data():
    with open(DB_FILE, 'w') as f: 
        json.dump(st.session_state.db, f)

# --- 2. UI & LANGUAGE ---
st.set_page_config(page_title="Negosyo Pro MVP", layout="wide")
lang = st.sidebar.radio("Language / Wika", ["English", "Tagalog"])

T = {
    "English": ["Quick Sale", "Inventory Hub", "Purchase Receipts", "Financial Reports", "Utang Tracker", "Add Sale", "Low Stock!", "Register Product"],
    "Tagalog": ["Mabilisang Benta", "Sentro ng Imbentaryo", "Resibo ng Binili", "Ulat ng Pananalapi", "Listahan ng Utang", "Itala ang Benta", "Mababa ang Stock!", "I-rehistro ang Produkto"]
}[lang]

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
                st.session_state.db['sales'].append({
                    "date": str(datetime.now().strftime("%Y-%m-%d")), 
                    "item": item['name'], 
                    "total": item['price']
                })
                save_data()
                st.success("Sold!")
                st.rerun()
            else:
                st.error("Out of Stock!")

# --- TAB 2: INVENTORY ---
with tabs[1]:
    with st.expander(f"➕ {T[7]}"):
        with st.form("manual_add"):
            c_in = st.text_input("Code")
            n_in = st.text_input("Name")
            s_in = st.number_input("Stock", min_value=0)
            p_in = st.number_input("Price", min_value=0.0)
            if st.form_submit_button(T[7]):
                st.session_state.db['inventory'][c_in] = {"name": n_in, "stock": s_in, "price": p_in, "min_alert": 5}
                save_data()
                st.rerun()
    st.dataframe(pd.DataFrame.from_dict(st.session_state.db['inventory'], orient='index'), use_container_width=True)

# --- TAB 3: PURCHASE RECEIPTS (Expense & Photo Archive) ---
with tabs[2]:
    st.subheader(T[2]) # "Purchase Receipts" or "Resibo ng Binili"
    st.info("Snap a photo of your grocery/wholesaler receipt to track your business expenses.")
    
    # 1. Upload Form
    with st.form("purchase_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        store_name = col_a.text_input("Store Name (e.g. Puregold, Market)")
        total_spent = col_b.number_input("Total Amount Spent (₱)", min_value=0.0)
        
        # This creates the "Browse" or "Take Photo" button
        uploaded_file = st.file_uploader("📸 Upload Receipt Photo", type=['png', 'jpg', 'jpeg'])
        
        notes = st.text_area("Items Bought (e.g. 1 sack Rice, 5 cases Noodles)")
        
        submit_receipt = st.form_submit_button("💾 Save to Digital Archive")
        
        if submit_receipt:
            if store_name and total_spent > 0:
                # Store the data
                receipt_entry = {
                    "date": str(datetime.now().strftime("%Y-%m-%d")),
                    "store": store_name,
                    "amount": total_spent,
                    "items": notes,
                    "photo_id": uploaded_file.name if uploaded_file else "No Photo"
                }
                st.session_state.db['purchase_receipts'].append(receipt_entry)
                save_data()
                st.success(f"Receipt from {store_name} archived successfully!")
                st.rerun()
            else:
                st.error("Please enter the Store Name and Amount.")

    # 2. Display the History Table
    st.markdown("---")
    st.subheader("📜 Expense History")
    if st.session_state.db['purchase_receipts']:
        expense_df = pd.DataFrame(st.session_state.db['purchase_receipts'])
        # Rename for cleaner display
        expense_df.columns = ["Date", "Store", "Amount (₱)", "Details", "Receipt File"]
        st.dataframe(expense_df, use_container_width=True)
    else:
        st.info("No receipts archived yet.")

# --- TAB 4: FINANCIAL REPORTS ---
with tabs[3]:
    st.header(T[3])
    
    # Calculate Totals
    total_revenue = sum([s['total'] for s in st.session_state.db['sales']])
    total_expenses = sum([p['total'] for p in st.session_state.db['purchase_receipts']])
    net_profit = total_revenue - total_expenses
    
    # Display Metrics
    c1, c2, c3 = st.columns(3)
    
    # Using simple strings to avoid f-string formatting errors
    sales_text = "₱{:,.2f}".format(total_revenue)
    exp_text = "₱{:,.2f}".format(total_expenses)
    profit_text = "₱{:,.2f}".format(net_profit)
    
    c1.metric("Total Sales", sales_text)
    c2.metric("Total Expenses", exp_text, delta_color="inverse")
    
    if net_profit >= 0:
        c3.metric("Net Profit", profit_text, delta=profit_text)
    else:
        c3.metric("Net Loss", profit_text, delta=profit_text, delta_color="normal")

# --- TAB 5: UTANG TRACKER ---
with tabs[4]:
    st.subheader(T[4])
    
    # 1. Register New Debt
    with st.expander("➕ Register New Utang", expanded=True):
        u_col1, u_col2, u_col3 = st.columns(3)
        u_name = u_col1.text_input("Customer Name")
        u_phone = u_col2.text_input("Mobile Number (e.g. 09171234567)")
        u_amt = u_col3.number_input("Amount Owed (₱)", min_value=0.0)
        
        if st.button("📝 Save Debt Record"):
            if u_name and u_phone:
                st.session_state.db['debts'].append({
                    "name": u_name, "phone": u_phone, "amount": u_amt, "date": str(datetime.now().date())
                })
                save_data()
                st.success(f"Recorded debt for {u_name}!")
                st.rerun()
            else:
                st.error("Please provide Name and Mobile Number.")

    # 2. Display Table
    if st.session_state.db['debts']:
        st.markdown("### Active Debts")
        debt_df = pd.DataFrame(st.session_state.db['debts'])
        st.dataframe(debt_df, use_container_width=True)
        
        st.markdown("---")
        
        # 3. SMS REMINDER BUTTON (The New Feature)
        st.subheader("📲 Send Reminder")
        selected_name = st.selectbox("Select Customer", [d['name'] for d in st.session_state.db['debts']])
        
        # Get data for selected person
        person = next(item for item in st.session_state.db['debts'] if item['name'] == selected_name)
        
        # Format the Message
        reminder_msg = "Good day {}, paalala lang po sa inyong utang na ₱{:,.2f}. Salamat!".format(
            person['name'], person['amount']
        )
        
        # Create the SMS Link (sms:number?body=message)
        # Note: We use quote to handle spaces and symbols in the URL
        import urllib.parse
        encoded_msg = urllib.parse.quote(reminder_msg)
        sms_link = f"sms:{person['phone']}?body={encoded_msg}"
        
        st.info(f"**Message Preview:** {reminder_msg}")
        
        # The Action Button
        st.link_button(f"✉️ Send SMS to {person['name']}", sms_link)
        
        st.caption("Note: This button will open your phone's Messaging app with the text already typed out.")
    else:
        st.info("No credit records found.")
