"""pages/browse.py  —  Product browsing + ordering"""
import streamlit as st
from utils.db import get_products, get_orders, create_order

REGIONS = ["All", "Addis Ababa", "Oromia", "Amhara", "Tigray", "SNNPR", "Somali", "Afar", "Benishangul-Gumuz"]
SECTORS = ["All", "Agriculture", "Manufacturing", "Handicrafts", "Livestock", "Food Processing", "Textiles", "Services"]


def show():
    user = st.session_state["user"]
    st.markdown("## 🔍 Browse Products")

    # Filters
    with st.expander("🎛️ Filters", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        region  = c1.selectbox("Region",  REGIONS,  key="br_region")
        sector  = c2.selectbox("Sector",  SECTORS,  key="br_sector")
        quality = c3.selectbox("Quality", ["All", "A", "B", "C"], key="br_quality")
        search  = c4.text_input("Search", placeholder="teff, coffee…", key="br_search")

    products = get_products(
        region  = region  if region  != "All" else None,
        sector  = sector  if sector  != "All" else None,
        quality = quality if quality != "All" else None,
        search  = search  or None,
    )
    # Hide own listings for producers browsing
    if user["role"] == "Producer":
        products = [p for p in products if p["user_id"] != user["id"]]

    st.markdown(f"**{len(products)} products found**")

    if not products:
        st.info("No products match your filters.")
        return

    for p in products:
        _product_card(p, user)


def _product_card(p, user):
    verified = "✅ Verified Seller" if p.get("seller_verified") else "⬜ Unverified"
    deliver  = "🚚 Can Deliver" if p.get("can_deliver") else "🏪 Pickup Only"
    with st.container():
        st.markdown(f"""
        <div class="product-card">
          <strong style="font-size:1.05rem;">{p['title']}</strong>
          <span style="float:right;color:#009688;font-weight:700;">{p['price']} ETB/{p['unit']}</span><br>
          <span style="color:#666;font-size:.85rem;">
            🏷️ {p['sector']} &nbsp;·&nbsp; 📍 {p['region']} &nbsp;·&nbsp;
            ⭐ Grade {p['quality']} &nbsp;·&nbsp; {deliver} &nbsp;·&nbsp; {verified}
          </span><br>
          <span style="color:#444;font-size:.9rem;">{p['description'] or ''}</span><br>
          <span style="color:#555;font-size:.85rem;">📦 Available: <b>{p['quantity']} {p['unit']}</b> &nbsp;·&nbsp; 👤 {p['seller_name']}</span>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"🛒 Order from this listing"):
            qty = st.number_input(
                f"Quantity ({p['unit']})",
                min_value=0.1,
                max_value=float(p["quantity"]),
                value=min(10.0, float(p["quantity"])),
                step=0.1,
                key=f"qty_{p['id']}",
            )
            total = round(qty * p["price"], 2)
            st.markdown(f"**Total: {total} ETB**")
            if st.button("📨 Place Order", key=f"order_{p['id']}", type="primary"):
                create_order(p["id"], user["id"], p["user_id"], qty, total)
                st.success(f"✅ Order placed! The seller will be notified.")


def show_orders():
    user = st.session_state["user"]
    st.markdown("## 📋 My Orders")

    orders = get_orders(user["id"], as_buyer=True)

    if not orders:
        st.info("You haven't placed any orders yet.")
        return

    # Summary
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Orders",   len(orders))
    c2.metric("Pending",        len([o for o in orders if o["status"] == "Pending"]))
    c3.metric("Total Spent",    f"{sum(o['total_price'] for o in orders):,.0f} ETB")

    st.divider()

    for o in orders:
        status_color = {"Pending": "🟡", "Confirmed": "🟢", "Completed": "✅", "Cancelled": "🔴"}.get(o["status"], "⚪")
        st.markdown(f"""
        <div class="product-card">
          <strong>{o['title']}</strong>
          <span style="float:right">{status_color} {o['status']}</span><br>
          <span style="color:#666;font-size:.9rem;">
            📦 {o['quantity']} {o['unit']} &nbsp;·&nbsp;
            💰 {o['total_price']} ETB &nbsp;·&nbsp;
            👤 Seller: {o['counterpart_name']}
          </span><br>
          <span style="color:#aaa;font-size:.8rem;">Ordered on {o['created_at'][:10]}</span>
        </div>
        """, unsafe_allow_html=True)
