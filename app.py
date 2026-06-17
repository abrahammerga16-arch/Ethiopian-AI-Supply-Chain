import streamlit as st
from utils.auth import init_session, login_user, register_user, logout_user
from utils.db import init_db

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ethiopian Trade Hub",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  :root {
    --teal: #009688;
    --mint: #4DB6AC;
    --dark: #1a1a2e;
    --card: #16213e;
  }
  .stApp { background: #f0f4f8; }
  .hero {
    background: linear-gradient(135deg, #009688, #26a69a);
    border-radius: 16px;
    padding: 40px 32px;
    color: white;
    margin-bottom: 24px;
  }
  .hero h1 { font-size: 2.2rem; margin: 0 0 8px; }
  .hero p  { font-size: 1.05rem; opacity: 0.9; margin: 0; }
  .role-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    border: 2px solid transparent;
    transition: all .2s;
  }
  .role-card:hover { border-color: #009688; }
  .stat-box {
    background: white;
    border-radius: 10px;
    padding: 18px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,.06);
  }
  .stat-num { font-size: 2rem; font-weight: 700; color: #009688; }
  .stat-lbl { color: #666; font-size: .9rem; }
  .badge-producer  { background:#e8f5e9; color:#2e7d32; padding:3px 10px; border-radius:20px; font-size:.8rem; font-weight:600; }
  .badge-merchant  { background:#e3f2fd; color:#1565c0; padding:3px 10px; border-radius:20px; font-size:.8rem; font-weight:600; }
  .badge-customer  { background:#fff3e0; color:#e65100; padding:3px 10px; border-radius:20px; font-size:.8rem; font-weight:600; }
  .badge-admin     { background:#f3e5f5; color:#6a1b9a; padding:3px 10px; border-radius:20px; font-size:.8rem; font-weight:600; }
  .product-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 12px;
    border-left: 4px solid #009688;
    box-shadow: 0 2px 6px rgba(0,0,0,.06);
  }
  .sidebar-logo { font-size: 1.4rem; font-weight: 700; color: #009688; }
</style>
""", unsafe_allow_html=True)

# ── Init ──────────────────────────────────────────────────────────────────────
init_db()
init_session()

# ── Router ────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.get("logged_in"):
        show_landing()
    else:
        show_dashboard()

# ═════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ═════════════════════════════════════════════════════════════════════════════
def show_landing():
    st.markdown("""
    <div class="hero">
      <h1>🌍 Ethiopian Trade Hub</h1>
      <p>AI-Powered Supply Chain & Smart Matching System<br>
         Connecting Producers · Merchants · Customers across Ethiopia</p>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Register"])

    with tab_login:
        _login_form()

    with tab_register:
        _register_form()

    # Stats row
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    for col, num, lbl in [
        (c1, "10,000+", "Producers"),
        (c2, "10,000+", "Merchants"),
        (c3, "8", "Ethiopian Regions"),
        (c4, "7", "Sectors Covered"),
    ]:
        col.markdown(f"""
        <div class="stat-box">
          <div class="stat-num">{num}</div>
          <div class="stat-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)


def _login_form():
    st.subheader("Welcome back")
    email    = st.text_input("Email", key="li_email")
    password = st.text_input("Password", type="password", key="li_pw")
    if st.button("Sign In", use_container_width=True, type="primary"):
        ok, msg = login_user(email, password)
        if ok:
            st.success(f"Welcome, {st.session_state['user']['name']}!")
            st.rerun()
        else:
            st.error(msg)
    st.caption("Demo accounts — producer@test.com / merchant@test.com / customer@test.com / admin@test.com (password: test123)")


def _register_form():
    st.subheader("Create your account")
    c1, c2 = st.columns(2)
    name  = c1.text_input("Full Name")
    email = c2.text_input("Email", key="reg_email")
    role  = st.selectbox("I am a…", ["Producer", "Merchant", "Customer"])
    region = st.selectbox("Region", [
        "Addis Ababa", "Oromia", "Amhara", "Tigray",
        "SNNPR", "Somali", "Afar", "Benishangul-Gumuz",
    ])
    phone = st.text_input("Phone (optional)")
    pw  = st.text_input("Password", type="password", key="reg_pw")
    pw2 = st.text_input("Confirm Password", type="password", key="reg_pw2")
    if st.button("Create Account", use_container_width=True, type="primary"):
        if pw != pw2:
            st.error("Passwords do not match.")
        elif not all([name, email, pw]):
            st.error("Name, email, and password are required.")
        else:
            ok, msg = register_user(name, email, pw, role, region, phone)
            if ok:
                st.success("Account created! Please sign in.")
            else:
                st.error(msg)


# ═════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
def show_dashboard():
    user = st.session_state["user"]
    role = user["role"]

    # Sidebar
    with st.sidebar:
        st.markdown(f'<div class="sidebar-logo">🌍 Trade Hub</div>', unsafe_allow_html=True)
        st.markdown(f"**{user['name']}**")
        badge = f'<span class="badge-{role.lower()}">{role}</span>'
        st.markdown(badge, unsafe_allow_html=True)
        st.markdown(f"📍 {user.get('region','')}")
        st.divider()

        pages = _get_pages(role)
        page  = st.radio("Navigation", list(pages.keys()), label_visibility="collapsed")
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()

    pages[page]()


def _get_pages(role):
    from pages import home, products, browse, profile, admin_panel
    base = {"🏠 Home": home.show, "👤 Profile": profile.show}
    if role == "Producer":
        base["📦 My Listings"] = products.show_my_listings
        base["➕ Add Product"]  = products.show_add_product
    elif role == "Merchant":
        base["🔍 Browse Products"] = browse.show
        base["📋 My Orders"]       = browse.show_orders
    elif role == "Customer":
        base["🛒 Shop"]       = browse.show
        base["📦 My Purchases"] = browse.show_orders
    elif role == "Admin":
        base["👥 Users"]    = admin_panel.show_users
        base["📊 Products"] = admin_panel.show_all_products
    return base


if __name__ == "__main__":
    main()
