"""pages/home.py"""
import streamlit as st
from utils.db import get_products, get_orders


def show():
    user = st.session_state["user"]
    role = user["role"]

    st.markdown(f"## 👋 Hello, {user['name'].split()[0]}!")

    if role == "Producer":
        _producer_home(user)
    elif role == "Merchant":
        _merchant_home(user)
    elif role == "Customer":
        _customer_home(user)
    elif role == "Admin":
        _admin_home()


def _producer_home(user):
    listings = get_products(user_id=user["id"])
    orders   = get_orders(user["id"], as_buyer=False)
    active   = [p for p in listings if p["status"] == "Active"]
    pending  = [o for o in orders if o["status"] == "Pending"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Active Listings",  len(active))
    c2.metric("Total Orders",     len(orders))
    c3.metric("Pending Orders",   len(pending))

    st.markdown("---")
    st.markdown("### 📢 Quick Tips for Producers")
    st.info("💡 **Stage 2 (coming soon):** AI Smart Matching will automatically find the best merchants for your products.")
    st.success("✅ Add your products now so they appear in merchant searches.")
    st.warning("📈 **Stage 3 (coming soon):** Price Recommendation AI will suggest fair market prices based on region and season.")

    if listings:
        st.markdown("### 📦 Your Recent Listings")
        for p in listings[:3]:
            _mini_product_card(p)


def _merchant_home(user):
    products = get_products()
    orders   = get_orders(user["id"], as_buyer=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Products Available", len(products))
    c2.metric("My Orders",          len(orders))
    c3.metric("Pending Orders",     len([o for o in orders if o["status"] == "Pending"]))

    st.markdown("---")
    st.info("💡 **Stage 2 (coming soon):** AI Smart Matching will recommend producers that match your preferred product, region, budget, and quality grade.")

    st.markdown("### 🆕 Latest Listings")
    for p in products[:4]:
        _mini_product_card(p)


def _customer_home(user):
    products = get_products()
    orders   = get_orders(user["id"], as_buyer=True)

    c1, c2 = st.columns(2)
    c1.metric("Products Available", len(products))
    c2.metric("My Purchases",       len(orders))

    st.markdown("---")
    st.markdown("### 🛒 Featured Products")
    for p in products[:3]:
        _mini_product_card(p)


def _admin_home():
    from utils.db import get_all_users, get_conn
    conn = get_all_users()
    c = __import__("utils.db", fromlist=["get_conn"]).get_conn()
    users    = c.execute("SELECT COUNT(*) as n FROM users").fetchone()["n"]
    products = c.execute("SELECT COUNT(*) as n FROM products WHERE status='Active'").fetchone()["n"]
    orders   = c.execute("SELECT COUNT(*) as n FROM orders").fetchone()["n"]
    c.close()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Users",    users)
    c2.metric("Active Products", products)
    c3.metric("Total Orders",   orders)

    st.markdown("---")
    st.info("🔐 Admin Panel: Manage users and products from the sidebar.")


def _mini_product_card(p):
    verified = "✅ Verified" if p.get("seller_verified") else "⬜ Unverified"
    deliver  = "🚚 Delivery" if p.get("can_deliver") else "🏪 Pickup only"
    st.markdown(f"""
    <div class="product-card">
      <strong>{p['title']}</strong><br>
      <span style="color:#666;font-size:.9rem;">
        📍 {p['region']} &nbsp;|&nbsp; 🏷️ {p['sector']} &nbsp;|&nbsp;
        ⭐ Grade {p['quality']} &nbsp;|&nbsp; {deliver} &nbsp;|&nbsp; {verified}
      </span><br>
      <span style="color:#009688;font-weight:700;font-size:1.05rem;">
        {p['quantity']} {p['unit']} @ {p['price']} ETB/{p['unit']}
      </span>
    </div>
    """, unsafe_allow_html=True)
