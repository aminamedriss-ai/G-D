import streamlit as st
import pandas as pd
from supabase import create_client, Client
st.set_page_config(
    page_title="Page Admin",
    page_icon="logo3.jpg",  # chemin local ou URL
    layout="wide"
)
# 🔑 Config connexion Supabase
SUPABASE_URL = "https://ddvgplwwukhwdexhwaxc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRkdmdwbHd3dWtod2RleGh3YXhjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTQxNTg0MiwiZXhwIjoyMDcwOTkxODQyfQ.Y3vpaXcq7_R88Z2l3IKHOTrL6NeuVRWT3mcSRiOVAHE"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("⚙️ Interface Admin - Gestion des Paies")

# 📌 Onglets
# menu = st.sidebar.radio("Menu", ["💰 Paies"])

# ========================
# 👤 Gestion des employés
# ========================
# if menu == "👤 Employés":
    # st.header("👤 Gestion des employés")

    # # Formulaire ajout employé
    # with st.form("ajout_employe"):
    #     matricule = st.text_input("Matricule")
    #     nom = st.text_input("Nom & Prénom")
    #     poste = st.text_input("Titre du poste")
    #     indemnite = st.text_input("Indémnité de panier")
    #     salaire_base = st.text_input("Salaire de base")
    #     salaire_net = st.text_input("Salaire net")

    #     submitted = st.form_submit_button("➕ Ajouter")
    #     # Récupérer le dernier id
    #     res = supabase.table("Paie").select("id").order("id", desc=True).limit(1).execute()
    #     if res.data:
    #         last_id = res.data[0]["id"]
    #         new_id = last_id + 1
    #     else:
    #         new_id = 1  # si la table est vide

    #     if submitted:
    #         data = {
    #             "id": new_id,
    #             "matricule": matricule,
    #             "Name": nom,
    #             "Titre du poste": poste,
    #         }
    #         supabase.table("Paie").insert(data).execute()
    #         st.success(f"✅ Employé {nom} ajouté.")

    # # Liste employés existants
    # res = supabase.table("Paie").select("*").execute()
    # df_emp = pd.DataFrame(res.data)
    # if not df_emp.empty:
    #     st.subheader("📋 Liste des employés")
    #     st.dataframe(df_emp)

# ========================
# 💰 Gestion des paies
# ========================
# if menu == "💰 Paies":
st.header("💰 Gestion des paies")

    # Choisir employé
res = supabase.table("Paie").select("matricule, Name").execute()
df_emp = pd.DataFrame(res.data)

    # ✅ Garder les matricules uniques (1 ligne par matricule)
df_unique = df_emp.drop_duplicates(subset="matricule")

    # Construire dictionnaire pour le selectbox
employe_dict = {f"{row['Name']} ({row['matricule']})": row["matricule"] for _, row in df_unique.iterrows()}

# Sélecteur
choix_emp = st.selectbox("👤 Sélectionnez un employé", list(employe_dict.keys()))

if choix_emp:
        matricule = employe_dict[choix_emp]

        with st.form("ajout_paie"):
            mois = st.selectbox("📅 Mois", ["-janv.-", "-févr.-", "-mars-", "-avr.-", "-mai-", "-juin-", "-juil.-", "-août-", "-sept.-", "-oct.-", "-nov.-", "-déc.-"])
            
            allowance = st.number_input("🚌 Allowance", min_value=0.0, step=100.0)
            ispaye = st.checkbox("✅ Allownance attribué ?")

            
            submit_paie = st.form_submit_button("➕ Ajouter / Modifier paie")
            if submit_paie:
                data = {
                    "Allowance": allowance,
                    "ispaye": ispaye
                }

                supabase.table("Paie") \
                    .update(data) \
                    .eq("matricule", matricule) \
                    .eq("Mois", mois) \
                    .execute()

                st.success(f"✅ Paie modifiée pour {choix_emp} ({mois})")


        # 📊 Historique paie
        # res_paie = supabase.table("Paie").select("*").eq("matricule", matricule).execute()
        # df_paie = pd.DataFrame(res_paie.data)
        # if not df_paie.empty:
        #     st.subheader("📋 Historique des paies")
        #     st.dataframe(df_paie)
