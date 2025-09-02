import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import base64
from supabase import create_client

st.set_page_config(
    page_title=" Portail Paie Employé G + D",
    page_icon="g+d2.png",  # chemin local ou URL
    layout="wide"
)
import base64


# Fonction pour convertir une image locale en base64
def get_base64_of_image(img_path):
    with open(img_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Convertir tes logos locaux
logo_gauche = get_base64_of_image("g+d.png")
logo_droite = get_base64_of_image("logo3.jpg")

# Injecter dans le header
st.markdown(f"""
<style>
/* Header Streamlit */
header[data-testid="stHeader"] {{
    background: #ffffff !important;
    border-bottom: 1px solid #ccd6f6 !important;
    height: 70px !important;
    position: relative !important;
}}

/* Supprimer le dégradé par défaut */
header[data-testid="stHeader"]::before {{
    content: none !important;
}}

/* Conteneur custom logos */
.custom-header {{
    position: absolute;
    top: -100px;
    left: 0;
    right: 0;
    height: 70px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;   /* 🔼 Aligne les logos vers le haut */
    padding: 6px 20px 30px 20px;  /* top | right | bottom | left → espace en bas */
    pointer-events: none;
}}

.custom-header img {{
    height: 100px;   /* ajuste la taille si besoin */
    object-fit: contain;
    pointer-events: auto;
}}
</style>

<div class="custom-header">
    <img src="data:image/png;base64,{logo_gauche}" alt="Logo gauche">
    <img src="data:image/png;base64,{logo_droite}" alt="Logo droite">
</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* ====== Base globale (facultatif) ====== */
html, body, .stApp { background: #ffffff !important; font-family: 'Segoe UI', sans-serif; }
h1, h2, h3, h4, h5, h6, p, span, label, div, strong { color: #001749 !important; }

/* ====== CONTRÔLE VISIBLE (select fermé) ====== */
[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #001749 !important;
    border: 1px solid #ccd6f6 !important;
    border-radius: 6px !important;
    min-height: 38px !important;
    padding: 6px 10px !important;
}
[data-baseweb="select"] * { color: #001749 !important; }
[data-baseweb="select"] svg { fill: #001749 !important; }

/* Focus sur le contrôle */
[data-baseweb="select"]:focus-within > div {
    border-color: #001749 !important;
    box-shadow: 0 0 0 3px rgba(0,23,73,0.15) !important;
    outline: none !important;
}
/* ====== TEXTE SELECTBOX (valeur affichée) ====== */
[data-baseweb="select"] > div > div {
    color: #001749 !important;   /* couleur du texte choisi */
    font-weight: 500 !important;
}

/* Placeholder (avant sélection) */
[data-baseweb="select"] [class*="placeholder"] {
    color: #7a869a !important;   /* gris doux pour le placeholder */
    font-style: italic !important;
}
/* ====== CORRECTION ALIGNEMENT TEXTE SELECTBOX ====== */
[data-baseweb="select"] > div {
    display: flex !important;
    align-items: center !important;
    min-height: 40px !important;     /* hauteur cohérente */
    line-height: 1.4 !important;     /* corrige le texte coupé */
    padding: 6px 12px !important;    /* espace intérieur */
}

[data-baseweb="select"] > div > div {
    display: flex !important;
    align-items: center !important;
    color: #001749 !important;
    font-size: 15px !important;
    font-weight: 500 !important;
}

/* ====== MENU DÉROULANT (popover) ====== */
/* Conteneur popover */
[data-baseweb="popover"] { background: transparent !important; }

/* Listbox (couvre ul et div selon versions) */
[data-baseweb="popover"] [role="listbox"],
ul[role="listbox"],
div[role="listbox"] {
    background: #ffffff !important;
    color: #001749 !important;
    border: 1px solid #ccd6f6 !important;
    border-radius: 0 !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.12) !important;
    padding: 4px !important;
}

/* ====== OPTIONS ====== */
/* Couvre li/div selon versions */
[role="option"],
li[role="option"] {
    background: #ffffff !important;
    color: #001749 !important;
    padding: 8px 12px !important;
    border-radius: 0px !important;
    margin: 2px !important;
}

/* Survol */
[role="option"]:hover,
li[role="option"]:hover {
    background: #eef3ff !important;
    color: #001749 !important;
}

/* Option sélectionnée dans la liste */
[aria-selected="true"] {
    background: #dfe9ff !important;
    color: #001749 !important;
}

/* ====== SIDEBAR (si vous avez des selectbox dedans) ====== */
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #001749 !important;
    border: 1px solid #ccd6f6 !important;
    border-radius: 10px !important;
}

/* ====== INPUTS / BOUTONS pour harmonie (optionnel) ====== */
.stTextInput input {
    background: #f9fbff !important;
    color: #001749 !important;
    border: 1px solid #ccd6f6 !important;
    border-radius: 8px !important;
    padding: 6px 10px !important;
}
.stTextInput input:focus {
    border: 1px solid #001749 !important;
    box-shadow: 0 0 4px rgba(0,23,73,0.3) !important;
    outline: none !important;
}
.stButton button {
    background: #ffffff !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    font-weight: 600 !important;
}
.stButton button:hover { background: #003080 !important; }
/* ====== BARRE SUPÉRIEURE (header Streamlit) ====== */
header[data-testid="stHeader"] {
    background: #ffffff !important;
    color: #ffffff !important;
    border-bottom: 1px solid #ccd6f6 !important; /* facultatif, fine séparation */
}

/* Supprimer l’effet dégradé translucide de Streamlit */
header[data-testid="stHeader"]::before {
    content: none !important;
}

/* Icône du menu hamburger (sidebar) */
header[data-testid="stHeader"] button[kind="header"] {
    color: #001749 !important;
}

</style>
""", unsafe_allow_html=True)




with open("g+d.png", "rb") as image_file:
    encoded = base64.b64encode(image_file.read()).decode()

st.title("💼 Portail Paie Employé G + D")


# --- CONNEXION SUPABASE ---
SUPABASE_URL = "https://ddvgplwwukhwdexhwaxc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRkdmdwbHd3dWtod2RleGh3YXhjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0MTU4NDIsImV4cCI6MjA3MDk5MTg0Mn0.z8qKY6xGTwb4Ixd6V9GAHDWc6atFkkpdLGHuGGDh-4g"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Initialiser l'état de session ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.matricule = None
    st.session_state.password_changed = False
    st.session_state.show_change_form = False
    st.session_state.show_paie = False

# --- FORMULAIRE DE LOGIN ---
if not st.session_state.logged_in:
    st.subheader("🔐 Connexion")
    matricule = st.text_input("Entrez votre matricule")
    password = st.text_input("Entrez votre mot de passe", type="password")

    if st.button("Se connecter"):
        if matricule and password:
            res_user = supabase.table("Paie").select("matricule, mdp").eq("matricule", matricule).execute()

            if res_user.data:
                user = res_user.data[0]
                if user["mdp"] == password:
                    st.session_state.logged_in = True
                    st.session_state.matricule = matricule
                    st.success("✅ Connexion réussie !")
                    st.rerun()
                else:
                    st.error("❌ Mot de passe incorrect")
            else:
                st.error("❌ Matricule introuvable")
        else:
            st.warning("⚠️ Veuillez entrer votre matricule et votre mot de passe.")

# --- PAGE APRES CONNEXION ---
if st.session_state.logged_in:
    # st.write(f"👋 Bienvenue, matricule **{st.session_state.matricule}**")

    # --- MENU ---
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 Changer mon mot de passe"):
            st.session_state.show_change_form = True
            st.session_state.show_paie = False

    with col2:
        if st.button("💼 Consulter ma paie"):
            st.session_state.show_paie = True
            st.session_state.show_change_form = False

    # --- FORMULAIRE CHANGEMENT MOT DE PASSE ---
    if st.session_state.show_change_form:
        st.subheader("🔑 Changement du mot de passe")
        new_password = st.text_input("Nouveau mot de passe", type="password")
        confirm_password = st.text_input("Confirmez le mot de passe", type="password")

        if st.button("Valider le changement"):
            if new_password and confirm_password:
                if new_password == confirm_password:
                    response = supabase.table("Paie") \
                        .update({"mdp": new_password}) \
                        .eq("matricule", st.session_state.matricule) \
                        .execute()

                    if response.data:
                        st.success("✅ Mot de passe changé avec succès !")
                        st.session_state.show_change_form = False
                        st.rerun()
                    else:
                        st.error("⚠️ Erreur : aucun enregistrement mis à jour.")
                else:
                    st.error("❌ Les mots de passe ne correspondent pas.")
            else:
                st.error("❌ Veuillez remplir les deux champs.")

    # --- INTERFACE CONSULTATION DE PAIE ---
    if st.session_state.show_paie:
        st.subheader("📊 Consultation de paie")
        matricule = st.session_state.matricule
        ordre_mois = [
            "-janv.-", "-févr.-", "-mars-", "-avr.-", "-mai-", "-juin-",
            "-juil.-", "-août-", "-sept.-", "-oct.-", "-nov.-", "-déc.-"
        ]  

        res = supabase.table("Paie").select("Mois").eq('matricule', matricule).execute() 
        mois_dispo = list({r["Mois"] for r in res.data}) 
        mois_dispo = sorted(mois_dispo, key=lambda x: ordre_mois.index(x) if x in ordre_mois else 999) 

        if mois_dispo: 
            mois_choisi = st.selectbox(
                "📅 Sélectionnez un mois", 
                mois_dispo, 
                index=None, 
                placeholder="— Sélectionnez un mois —"
            )

            if mois_choisi:
                res_all = supabase.table("Paie").select("*").eq('matricule', matricule).execute()    
                df_all = pd.DataFrame(res_all.data)        

                if not df_all.empty:
                    df_all["Mois"] = pd.Categorical(df_all["Mois"], categories=ordre_mois, ordered=True)    
                    df_all = df_all.sort_values("Mois")    
                    df_mois = df_all[df_all["Mois"] == mois_choisi]    

                    if not df_mois.empty:
                        salaire_net = float(df_mois["Salaire net"].iloc[0])
                        travel_expense = float(df_mois["Travel Expense"].iloc[0])
                        travel_allowance = float(df_mois["Travel Allowance"].iloc[0])
                        total_mois = float(df_mois["Total"].iloc[0])

                        trimestre = {
                            "-mars-": ["-janv.-", "-févr.-", "-mars-"],
                            "-juin-": ["-avr.-", "-mai-", "-juin-"],
                            "-sept.-": ["-juil.-", "-août-", "-sept.-"],
                            "-déc.-": ["-oct.-", "-nov.-", "-déc.-"]
                        }

                        cumul_indemnites = 0
                        salaire_affiche = salaire_net

                        st.success(f"Bienvenue {df_mois['Name'].iloc[0]} 👋")
                        st.write("### 📊 Vos informations de paie")

                        st.markdown(f"- **💰 Salaire Net (versé ce mois) :** {salaire_net:,.2f} DZD")

                        st.markdown(f"""
                        - **🧾 Travel Expense :** {travel_expense:,.2f} DZD  
                        - **🚌 Travel Allowance :** {travel_allowance:,.2f} DZD  
                        - **📦 Total Indemnités du mois :** {total_mois:,.2f} DZD  
                        """)

                        if mois_choisi in trimestre:
                            df_trim = df_all[df_all["Mois"].isin(trimestre[mois_choisi])]
                            cumul_indemnites = df_trim["Total"].sum()
                            salaire_affiche = salaire_net + cumul_indemnites

                            st.markdown(f"""
                            ---
                            - **➕ Cumul indemnités du trimestre :** {cumul_indemnites:,.2f} DZD  
                            - **🔢 Salaire final versé :** {salaire_affiche:,.2f} DZD  
                            """)
                        else:
                            st.info("ℹ️ Ce mois, vous êtes payé uniquement avec le **salaire net**. Les indemnités seront versées à la fin du trimestre.")

    # --- BOUTON DECONNEXION ---
    if st.button("🚪 Se déconnecter"):
        st.session_state.logged_in = False
        st.session_state.matricule = None
        st.session_state.password_changed = False
        st.session_state.show_change_form = False
        st.session_state.show_paie = False
        st.rerun()
