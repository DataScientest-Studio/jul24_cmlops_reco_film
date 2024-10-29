import streamlit as st
from supabase_auth import sign_up, sign_in, sign_out

st.set_page_config(
    page_title="Système de Recommandation de Films",
    page_icon=":movie_camera:",
    layout="wide",
)


def main():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("Bienvenue sur le Système de Recommandation de Films")

        tab1, tab2 = st.tabs(["Connexion", "Inscription"])

        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Mot de passe", type="password")
                submit = st.form_submit_button("Se connecter")

                if submit:
                    try:
                        response = sign_in(email, password)
                        st.session_state.authenticated = True
                        st.session_state.user = response.user
                        st.rerun()
                    except Exception as e:
                        st.error(f"{str(e)}")

        with tab2:
            with st.form("signup_form"):
                email = st.text_input("Email")
                password = st.text_input("Mot de passe", type="password")
                submit = st.form_submit_button("S'inscrire")

                if submit:
                    try:
                        sign_up(email, password)
                        st.success(
                            "Inscription réussie ! Veuillez vérifier votre email."
                        )
                    except Exception as e:
                        st.error(f"{str(e)}")
    else:
        st.switch_page("pages/1_🎬_Recommandations.py")


if __name__ == "__main__":
    main()
