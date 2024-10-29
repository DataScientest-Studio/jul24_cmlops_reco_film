import streamlit as st
from supabase_auth import sign_out

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Veuillez vous connecter pour accéder à cette page.")
    st.stop()

st.title("Profil Utilisateur")
st.write(f"Email : {st.session_state.user.email}")
# st.write(f"infos : {st.session_state.user}")

if st.button("Se déconnecter"):
    sign_out(st.session_state.user)
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()
