"""pages/products.py  —  Producer listing management"""
import streamlit as st
from utils.db import get_products, create_product, delete_product

SECTORS = ["Agriculture", "Manufacturing", "Handicrafts", "Livestock", "Food Processing", "Textiles", "Services"]
PRODUCTS_BY_SECTOR = {
    "Agriculture":     ["Teff", "Wheat", "Maize", "Barley", "Sorghum", "Millet", "Coffee", "Tea", "Sesame", "Sunflower"],
    "Livestock":       ["Cattle", "Sheep", "Goat", "Camel", "Poultry", "Honey", "Dairy", "Eggs"],
    "Handicrafts":     ["Pottery", "Basket Weaving", "Jewelry", "Leather Goods", "Wood Carving", "Paintings"],
    "Manufacturing":   ["Metal Parts", "Furniture", "Bricks", "Cement Products", "Plastic Goods", "Paper Products"],
    "Food Processing": ["Injera", "Spices", "Edible Oil", "Sugar", "Salt", "Flour", "Dried Fruit"],
    "Textiles":        ["Cotton Fabric", "Silk", "Wool", "Traditional Clothing", "Carpets", "Thread"],
    "Services":        ["Transport", "Storage", "Logistics", "Cold Chain", "Packaging", "Consulting"],
}
REGIONS = ["Addis Ababa", "Oromia", "Amhara", "Tigray", "SNNPR", "Somali", "Afar", "Benishangul-Gumuz"]
UNITS   = ["kg", "ton", "liter", "pcs", "bag", "bale", "box", "sack"]


def show_my_listings():
    user     = st.session_state["user"]
    listings = get_products(user_id=user["id"])

    st.markdown("## 📦 My Listings")
    if not listings:
        st.info("You have no active listings yet. Use **➕ Add Product** to create one.")
        return

    for p in listings:
        with st.expander(f"📌 {p['title']}  —  {p['quantity']} {p['unit']} @ {p['price']} ETB"):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(f"**Sector:** {p['sector']}  |  **Product:** {p['product']}")
                st.write(f"**Region:** {p['region']}  |  **Quality:** Grade {p['quality']}")
                st.write(f"**Delivery:** {'Yes 🚚' if p['can_deliver'] else 'No — pickup only'}")
                st.write(f"**Description:** {p['description'] or '—'}")
                st.caption(f"Listed on {p['created_at'][:10]}")
            with c2:
                if st.button("🗑️ Remove", key=f"del_{p['id']}"):
                    delete_product(p["id"], user["id"])
                    st.success("Listing removed.")
                    st.rerun()


def show_add_product():
    user = st.session_state["user"]
    st.markdown("## ➕ Add New Product Listing")

    with st.form("add_product_form"):
        title  = st.text_input("Listing Title *", placeholder="e.g. Premium White Teff — 500 kg")
        sector = st.selectbox("Sector *", SECTORS)
        product_options = PRODUCTS_BY_SECTOR.get(sector, ["Other"])
        product = st.selectbox("Product *", product_options + ["Other"])
        if product == "Other":
            product = st.text_input("Specify product name *")

        c1, c2, c3 = st.columns(3)
        quantity = c1.number_input("Quantity *", min_value=0.1, value=100.0, step=0.1)
        unit     = c2.selectbox("Unit *", UNITS)
        price    = c3.number_input("Price per unit (ETB) *", min_value=1.0, value=50.0, step=0.5)

        c4, c5 = st.columns(2)
        quality    = c4.selectbox("Quality Grade *", ["A", "B", "C"])
        region     = c5.selectbox("Region *", REGIONS, index=REGIONS.index(user.get("region", REGIONS[0])) if user.get("region") in REGIONS else 0)
        can_deliver = st.checkbox("I can deliver this product 🚚")
        description = st.text_area("Description (optional)", placeholder="Freshly harvested, organic, sun-dried…")

        submitted = st.form_submit_button("📤 Publish Listing", use_container_width=True, type="primary")

    if submitted:
        if not all([title, sector, product, quantity, unit, price, quality, region]):
            st.error("Please fill all required fields (*).")
        else:
            create_product(user["id"], title, sector, product, quantity, unit, price, quality, region, description, can_deliver)
            st.success(f"✅ '{title}' published successfully!")
            st.balloons()
