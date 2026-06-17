"""
AI-Powered Supply Chain System — Stage 1: Core Skeleton
Wolaita Sodo University | Department of ECE

This is the foundational version with NO AI yet:
- User registration/login (Producer, Merchant, Customer roles)
- Producers can list products manually
- Merchants/Customers can browse listings with simple filters
- Orders can be placed

AI features (matching, pricing, fraud, demand forecasting) are added
in later stages on top of this skeleton.
"""
import streamlit as st
from src.db import get_supabase_client

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="Ethiopian AI Supply Chain",
    page_icon="🌾",
    layout="wide"
)

# ── SESSION STATE INIT ───────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
if "profile" not in st.session_state:
    st.session_state.profile = None

try:
    supabase = get_supabase_client()
except ValueError as e:
    st.error(str(e))
    st.stop()


# ── HELPER FUNCTIONS ──────────────────────────────────────────
def get_profile(user_id: str):
    res = supabase.table("profiles").select("*").eq("id", user_id).execute()
    return res.data[0] if res.data else None


def sign_up(email, password, full_name, role, region, phone):
    auth_res = supabase.auth.sign_up({"email": email, "password": password})
    if auth_res.user is None:
        return False, "Sign up failed. Email may already be registered."
    user_id = auth_res.user.id
    supabase.table("profiles").insert({
        "id": user_id,
        "full_name": full_name,
        "role": role,
        "region": region,
        "phone": phone
    }).execute()
    return True, "Account created! Please check your email to confirm, then log in."


def sign_in(email, password):
    try:
        auth_res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if auth_res.user:
            st.session_state.user = auth_res.user
            st.session_state.profile = get_profile(auth_res.user.id)
            return True, "Logged in successfully."
        return False, "Invalid credentials."
    except Exception as e:
        return False, f"Login failed: {e}"


def sign_out():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.profile = None


REGIONS = ["Addis Ababa", "Oromia", "SNNPR", "Amhara", "Tigray", "Sidama", "Dire Dawa", "Harari"]
SECTORS = ["Agriculture", "Manufacturing", "Handicrafts", "Livestock", "Food Processing", "Textiles", "Services"]


# ── SIDEBAR: AUTH ────────────────────────────────────────────
with st.sidebar:
    st.title("🌾 AI Supply Chain")
    st.caption("Ethiopian Multi-Sector Commerce")
    st.divider()

    if st.session_state.user is None:
        tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])

        with tab_login:
            login_email = st.text_input("Email", key="login_email")
            login_pass = st.text_input("Password", type="password", key="login_pass")
            if st.button("Log In", use_container_width=True):
                ok, msg = sign_in(login_email, login_pass)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        with tab_signup:
            su_name = st.text_input("Full Name", key="su_name")
            su_email = st.text_input("Email", key="su_email")
            su_pass = st.text_input("Password", type="password", key="su_pass")
            su_role = st.selectbox("I am a...", ["producer", "merchant", "customer"], key="su_role")
            su_region = st.selectbox("Region", REGIONS, key="su_region")
            su_phone = st.text_input("Phone Number", key="su_phone")
            if st.button("Create Account", use_container_width=True):
                if not su_name or not su_email or not su_pass:
                    st.warning("Please fill in all required fields.")
                else:
                    ok, msg = sign_up(su_email, su_pass, su_name, su_role, su_region, su_phone)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
    else:
        profile = st.session_state.profile
        st.success(f"Welcome, {profile['full_name'] if profile else 'User'}")
        st.caption(f"Role: {profile['role'].capitalize() if profile else 'N/A'}")
        st.caption(f"Region: {profile['region'] if profile else 'N/A'}")
        if st.button("Log Out", use_container_width=True):
            sign_out()
            st.rerun()


# ── MAIN AREA ─────────────────────────────────────────────────
if st.session_state.user is None:
    st.title("Welcome to the Ethiopian AI Supply Chain Platform")
    st.write(
        "A unified marketplace connecting **producers**, **merchants**, and **customers** "
        "across Ethiopia's agriculture, manufacturing, handicrafts, livestock, and service sectors."
    )
    st.info("Please log in or sign up using the sidebar to get started.")

else:
    profile = st.session_state.profile
    role = profile["role"] if profile else None

    page = st.tabs(["📦 Browse Products", "🛒 My Orders"] + (["➕ List a Product", "📋 My Listings"] if role == "producer" else []))

    # ── BROWSE PRODUCTS (everyone can see this) ──────────────
    with page[0]:
        st.subheader("Browse Available Products")

        col1, col2, col3 = st.columns(3)
        with col1:
            filter_sector = st.selectbox("Filter by Sector", ["All"] + SECTORS)
        with col2:
            filter_region = st.selectbox("Filter by Region", ["All"] + REGIONS)
        with col3:
            search_term = st.text_input("Search product name")

        query = supabase.table("products").select("*, profiles(full_name, region)").eq("is_available", True)
        if filter_sector != "All":
            query = query.eq("sector", filter_sector)
        if filter_region != "All":
            query = query.eq("region", filter_region)

        products = query.execute().data

        if search_term:
            products = [p for p in products if search_term.lower() in p["product_name"].lower()]

        if not products:
            st.info("No products found matching your filters.")
        else:
            for p in products:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 2, 2])
                    with c1:
                        st.markdown(f"**{p['product_name']}** · {p['sector']}")
                        st.caption(p.get("description", "") or "No description")
                    with c2:
                        st.metric("Price", f"{p['price_birr']:,.0f} Birr")
                        st.caption(f"Qty: {p['quantity']} {p['unit']} | Grade {p['quality_grade']}")
                    with c3:
                        st.caption(f"📍 {p['region']}")
                        if role in ("merchant", "customer"):
                            qty_to_order = st.number_input(
                                "Quantity", min_value=1.0, max_value=float(p["quantity"]),
                                value=1.0, key=f"qty_{p['id']}"
                            )
                            if st.button("Place Order", key=f"order_{p['id']}"):
                                total = qty_to_order * p["price_birr"]
                                supabase.table("orders").insert({
                                    "product_id": p["id"],
                                    "buyer_id": st.session_state.user.id,
                                    "quantity_ordered": qty_to_order,
                                    "total_price_birr": total,
                                    "status": "pending"
                                }).execute()
                                st.success(f"Order placed for {qty_to_order} {p['unit']} — {total:,.0f} Birr")
                                st.rerun()

    # ── MY ORDERS ──────────────────────────────────────────────
    with page[1]:
        st.subheader("My Orders")
        orders = supabase.table("orders").select("*, products(product_name, region)") \
            .eq("buyer_id", st.session_state.user.id).order("created_at", desc=True).execute().data
        if not orders:
            st.info("You haven't placed any orders yet.")
        else:
            for o in orders:
                with st.container(border=True):
                    pname = o["products"]["product_name"] if o.get("products") else "Unknown product"
                    st.markdown(f"**{pname}** — {o['quantity_ordered']} units")
                    st.caption(f"Total: {o['total_price_birr']:,.0f} Birr | Status: `{o['status']}`")

    # ── PRODUCER-ONLY: LIST A PRODUCT ───────────────────────────
    if role == "producer":
        with page[2]:
            st.subheader("List a New Product")
            with st.form("new_product_form"):
                p_sector = st.selectbox("Sector", SECTORS)
                p_name = st.text_input("Product Name")
                p_qty = st.number_input("Quantity Available", min_value=0.0, step=1.0)
                p_unit = st.selectbox("Unit", ["quintal", "kg", "piece", "head", "unit", "meter", "service"])
                p_price = st.number_input("Price per Unit (Birr)", min_value=0.0, step=10.0)
                p_quality = st.selectbox("Quality Grade", ["A", "B", "C"])
                p_region = st.selectbox("Region", REGIONS, index=REGIONS.index(profile["region"]) if profile["region"] in REGIONS else 0)
                p_desc = st.text_area("Description (optional)")
                submitted = st.form_submit_button("Submit Listing")

                if submitted:
                    if not p_name or p_qty <= 0 or p_price <= 0:
                        st.warning("Please fill in product name, quantity, and price.")
                    else:
                        supabase.table("products").insert({
                            "producer_id": st.session_state.user.id,
                            "sector": p_sector,
                            "product_name": p_name,
                            "quantity": p_qty,
                            "unit": p_unit,
                            "price_birr": p_price,
                            "quality_grade": p_quality,
                            "region": p_region,
                            "description": p_desc,
                            "is_available": True
                        }).execute()
                        st.success(f"'{p_name}' listed successfully!")
                        st.rerun()

        # ── PRODUCER-ONLY: MY LISTINGS ──────────────────────────
        with page[3]:
            st.subheader("My Listings")
            my_products = supabase.table("products").select("*") \
                .eq("producer_id", st.session_state.user.id).order("created_at", desc=True).execute().data
            if not my_products:
                st.info("You haven't listed any products yet.")
            else:
                for p in my_products:
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.markdown(f"**{p['product_name']}** · {p['sector']} · Grade {p['quality_grade']}")
                            st.caption(f"{p['quantity']} {p['unit']} @ {p['price_birr']:,.0f} Birr | {p['region']}")
                        with c2:
                            status = "🟢 Active" if p["is_available"] else "🔴 Inactive"
                            st.caption(status)
                            if st.button("Toggle Status", key=f"toggle_{p['id']}"):
                                supabase.table("products").update(
                                    {"is_available": not p["is_available"]}
                                ).eq("id", p["id"]).execute()
                                st.rerun()
