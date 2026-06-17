"""pages/profile.py"""
import streamlit as st
from utils.db import update_user_profile

REGIONS = ["Addis Ababa", "Oromia", "Amhara", "Tigray", "SNNPR", "Somali", "Afar", "Benishangul-Gumuz"]


def show():
    user = st.session_state["user"]
    st.markdown("## 👤 My Profile")

    col1, col2 = st.columns([1, 2])

    with col1:
        initials = "".join(w[0].upper() for w in user["name"].split()[:2])
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#009688,#26a69a);
                    width:90px;height:90px;border-radius:50%;
                    display:flex;align-items:center;justify-content:center;
                    color:white;font-size:2rem;font-weight:700;margin:auto;">
          {initials}
        </div>
        """, unsafe_allow_html=True)
        role = user["role"]
        badge_class = f"badge-{role.lower()}"
        st.markdown(f'<div style="text-align:center;margin-top:8px"><span class="{badge_class}">{role}</span></div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f"**Email:** {user['email']}")
        st.markdown(f"**Member since:** {user.get('created_at','')[:10]}")
        verified = "✅ Verified Account" if user.get("is_verified") else "⬜ Not Verified"
        st.markdown(f"**Status:** {verified}")

    st.divider()
    st.markdown("### ✏️ Edit Profile")

    with st.form("profile_form"):
        name   = st.text_input("Full Name",    value=user["name"])
        phone  = st.text_input("Phone",        value=user.get("phone") or "")
        region = st.selectbox("Region", REGIONS,
                              index=REGIONS.index(user["region"]) if user.get("region") in REGIONS else 0)
        if st.form_submit_button("💾 Save Changes", type="primary"):
            update_user_profile(user["id"], name, phone, region)
            st.session_state["user"]["name"]   = name
            st.session_state["user"]["phone"]  = phone
            st.session_state["user"]["region"] = region
            st.success("Profile updated!")
