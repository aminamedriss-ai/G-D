import streamlit as st
import pandas as pd
from supabase import create_client, Client
import re
import os 
st.set_page_config(
    page_title="Page Admin",
    page_icon="logo3.jpg",  # chemin local ou URL
    layout="wide"
)
# 🔑 Config connexion Supabase
SUPABASE_URL = "https://ddvgplwwukhwdexhwaxc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRkdmdwbHd3dWtod2RleGh3YXhjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTQxNTg0MiwiZXhwIjoyMDcwOTkxODQyfQ.Y3vpaXcq7_R88Z2l3IKHOTrL6NeuVRWT3mcSRiOVAHE"
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("⚙️ Interface Admin - Gestion des Paies")
def signup(nom, prenom, user_name, password):
    # Vérifier si l'utilisateur existe déjà
    existing = supabase.table("authentification").select("*").eq("user_name", user_name).execute()
    if existing.data:
        return {"error": "❌ Ce nom d'utilisateur existe déjà."}

    # Ajouter le nouvel utilisateur
    response = supabase.table("authentification").insert({
        "nom": nom,
        "prenom": prenom,
        "user_name": user_name,
        "mdp": password
    }).execute()
    return response

def login(user_name, password):
    # Vérifier si l'utilisateur existe avec le bon mdp
    response = supabase.table("authentification").select("*").eq("user_name", user_name).eq("mdp", password).execute()
    if response.data:
        return response.data[0]  # Retourne les infos user
    return None

def logout():
    st.session_state["authenticated"] = False
    st.session_state["user"] = None

# --- Interface ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    mode = st.radio("Choisissez :", ["Connexion", "Créer un compte"])

    if mode == "Créer un compte":
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        user_name = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")

        if st.button("Créer un compte"):
            res = signup(nom, prenom, user_name, password)
            if "error" in res:
                st.error(res["error"])
            else:
                st.success("✅ Compte créé avec succès ! Vous pouvez vous connecter.")

    else:  # Connexion
        user_name = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")

        if st.button("Connexion"):
            user = login(user_name, password)
            if user:
                st.session_state["authenticated"] = True
                st.session_state["user"] = user
                st.rerun()
            else:
                st.error("❌ Nom d'utilisateur ou mot de passe incorrect.")

else:
    with st.sidebar:
        st.success(f"Bienvenue {st.session_state['user']['prenom']} {st.session_state['user']['nom']} 👋")
        if st.button("Se déconnecter"):
            logout()
            st.rerun()

    st.header("💰 Gestion des paies")
    def nettoyer_nombre(val):
        """
        Nettoie et convertit une chaîne en float.
        Exemples :
        "6 000,00 Brut" → 6000.0
        "4 500,50" → 4500.5
        "NaN" → 0.0
        """
        if pd.isna(val):
            return 0.0
        val = str(val)
        # Supprimer tout sauf chiffres, virgules, points et tirets
        val = re.sub(r"[^0-9,.\-]", "", val)
        # Remplacer virgule par point
        val = val.replace(",", ".")
        try:
            return float(val)
        except ValueError:
            return 0.0

    uploaded_file = st.file_uploader("📂 Charger un fichier CSV", type=["csv"])

    if uploaded_file:
        # Charger CSV
        df = pd.read_csv(uploaded_file , skiprows=2,
                    sep=",",
                    decimal=",",
                    thousands=" ")

        # st.write("✅ Aperçu du fichier importé :")
        # st.dataframe(df.head())
        if "Etablissement" in df.columns:
            df = df[df["Etablissement"].astype(str).str.strip() == "G+D"]

            if df.empty:
                st.warning("⚠️ Aucune ligne trouvée avec Etablissement = G+D")
                st.stop()
            else:
                st.write("Aperçu du fichier :")
                st.dataframe(df.head())
        else:
            st.error("❌ La colonne 'Etablissement' est absente du fichier.")
            st.stop()
        # Harmoniser les noms de colonnes
        df.rename(columns={"N°": "matricule"}, inplace=True)
        
        # st.write("✅ Aperçu du fichier importé :")
        # st.dataframe(df.head())
        
        # Vérifier colonnes nécessaires
        colonnes_requises = ["matricule", "Mois", "Prime exeptionnelle (10%) (DZD)"]
        if not all(col in df.columns for col in colonnes_requises):
            st.error(f"❌ Le fichier doit contenir les colonnes : {colonnes_requises}")
            st.stop()
        
        import math
        ispaye_state = st.toggle("✅ Activer paiement ?", value=False)
        if st.button("🚀 Mettre à jour Supabase"):
            for _, row in df.iterrows():
                matricule = str(row["matricule"]).strip()
                mois = str(row["Mois"]).strip()
                allowance = row["Prime exeptionnelle (10%) (DZD)"]

                print("🔎 RAW:", matricule, mois, allowance, type(allowance))
                # Gérer NaN ou valeurs vides
                allowance = nettoyer_nombre(row["Prime exeptionnelle (10%) (DZD)"])

                data = {
                    "Allowance": allowance,
                    "ispaye": ispaye_state   # 👈 valeur unique appliquée à tout le monde
                }

                
                if not data:
                    print(f"⚠️ Ligne ignorée car data vide → {matricule}, {mois}")
                    continue

                # Mise à jour Supabase pour l'allowance
                resp = supabase.table("Paie") \
                    .update(data) \
                    .eq("matricule", matricule) \
                    .eq("Mois", mois) \
                    .execute()

                print(f"✅ Mise à jour : {matricule} - {mois} → {allowance} DZD | Réponse: {resp}")

            st.success("🎉 Toutes les lignes ont été mises à jour dans Supabase.")
