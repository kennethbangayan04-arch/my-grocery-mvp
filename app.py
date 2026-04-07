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
            with open(DB_FILE, 'r') as f: return json.load(f)
        except: pass
    return {'sales': [], 'inventory': {"4800016644801": {"name": "Lucky Me", "stock": 20, "min_alert": 5, "price": 15}, "12345": {"name": "Rice (1kg)", "stock": 50, "min_alert": 10, "price": 55}}, 'purchase_receipts': [], 'debts': []}

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def save_data():
    with open(DB_FILE, 'w') as f: json.dump(st.session_state.db, f)

# --- 2. THE DICTIONARY (Every Word is Here) ---
st.set_page_config(page_title="Negosyo Pro MVP", layout="wide")
lang = st.sidebar.radio("Wika / Language", ["English", "Tagalog"])

D = {
    "English": {
        "tabs": ["⚡ Quick Sale", "📦 Inventory", "🧾 Purchase Receipts", "📊 Reports", "💳 Utang Tracker"],
        "sale_header": "Register a Sale",
        "input_code": "Scan/Type Barcode",
        "btn_sell": "Complete Sale",
        "inv_header": "Stock Management",
        "btn_reg": "Register New Product",
        "name": "Product Name", "stock": "Current Stock", "price": "Price",
        "receipt_header": "Log Grocery Receipts",
        "store": "Store Name", "amt": "Amount Spent", "photo": "Upload Photo",
        "btn_save": "Save to Archive",
        "rep_header": "Financial Summary",
        "rev": "Total Sales", "exp": "Total Expenses", "prof": "Net Profit",
        "utang_header": "Debt Management",
        "cust": "Customer Name", "phone": "Mobile Number", "debt_amt": "Debt Amount",
        "btn_sms": "Send SMS Reminder",
        "low_stock": "⚠️ LOW STOCK!"
    },
    "Tagalog": {
        "tabs": ["⚡ Mabilisang Benta", "📦 Imbentaryo", "🧾 Resibo ng Binili", "📊 Mga Ulat", "💳 Listahan ng Utang"],
        "sale_header": "Itala ang Benta",
        "input_code": "I-scan/I-type ang Barcode",
        "btn_sell": "Tapusin ang Benta",
        "inv_header": "Pamamahala ng Stock",
        "btn_reg": "I-rehistro ang Produkto",
        "name": "Pangalan ng Produkto", "stock": "Bilang ng Stock", "price": "Presyo",
        "receipt_header": "Itala ang mga Resibo",
        "store": "Pangalan ng Tindahan", "amt": "Halagang Nagastos", "photo": "I-upload ang Larawan",
        "btn_save": "I-save sa Archive",
        "rep_header": "Ulat ng Kita at Gasto",
        "rev": "Kabuuang Benta", "exp": "Kabuuang Gasto", "prof": "Netong Kita",
        "utang_header": "Listahan ng mga Utang",
        "cust": "Pangalan ng Customer", "phone": "Numero ng Telepono", "debt_amt": "Halaga ng Utang",
        "btn_sms": "Magpadala ng SMS",
        "low_stock": "⚠️ MABABA ANG STOCK!"
    }
}[lang]

# --- 3. UI LAYOUT ---
st.title(f"🏪 Negosyo Pro")
tabs = st.tabs(D["tabs"])

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

# --- TAB 2: INVENTORY (With Row-by-Row Delete) ---
with tabs[1]:
    st.subheader(D["inv_header"])
    
    # 1. Low Stock Alerts
    for k, v in st.session_state.db['inventory'].items():
        if v['stock'] <= v['min_alert']: 
            st.warning(f"{D['low_stock']} {v['name']} ({v['stock']})")
    
    # 2. Registration Form
    with st.expander(D["btn_reg"]):
        with st.form("add_form", clear_on_submit=True):
            c_i = st.text_input("Code")
            n_i = st.text_input(D["name"]).upper() # Auto-capitalize for professional look
            s_i = st.number_input(D["stock"], min_value=0)
            p_i = st.number_input(D["price"], min_value=0.0)
            if st.form_submit_button(D["btn_reg"]):
                if c_i and n_i:
                    st.session_state.db['inventory'][c_i] = {"name": n_i, "stock": s_i, "price": p_i, "min_alert": 5}
                    save_data()
                    st.rerun()
            
            # The Delete Button in the final column
            if r6.button("🗑️", key=f"del_{code}"):
                del st.session_state.db['inventory'][code]
                save_data()
                st.toast(f"Removed {details['name']}!") # Small feedback popup
                st.rerun()
    else:
        st.info("No products registered yet.")
        
    # 3. Current Inventory Display
    if st.session_state.db['inventory']:
        st.write("---")
        # Capitalized display for professional look
        inv_df = pd.DataFrame.from_dict(st.session_state.db['inventory'], orient='index').reset_index()
        inv_df.columns = ["CODE", "NAME", "STOCK", "PRICE", "ALERT_LEVEL"]
        st.table(inv_df)

        # 4. DELETE / MANAGEMENT SECTION
        st.markdown("### 🛠️ " + ("Manage Inventory" if lang == "English" else "Pamamahala ng Produkto"))
        
        # Create a dropdown to select which item to delete
        # We use a selectbox because a button next to every row in a big inventory makes the screen messy
        items_list = {v['name']: k for k, v in st.session_state.db['inventory'].items()}
        to_delete_name = st.selectbox(
            "Select Product to Remove" if lang == "English" else "Piliin ang Produktong Buburahin", 
            options=list(items_list.keys())
        )
        
        delete_btn_label = "🗑️ Delete Product" if lang == "English" else "🗑️ Burahin ang Produkto"
        if st.button(delete_label if 'delete_label' in locals() else delete_btn_label, type="secondary"):
            # Get the code from the name
            code_to_remove = items_list[to_delete_name]
            # Remove from database
            del st.session_state.db['inventory'][code_to_remove]
            save_data()
            st.success(f"Removed {to_delete_name}!")
            st.rerun()
    else:
        st.info("No products registered yet.")
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
