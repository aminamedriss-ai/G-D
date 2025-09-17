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

st.header("💰 Gestion des paies")

    # Choisir employé
# Upload du fichier CSV
uploaded_file = st.file_uploader("📂 Charger un fichier CSV", type=["csv"])

if uploaded_file:
    # Charger CSV
    df = pd.read_csv(uploaded_file , skiprows=2,
                sep=",",
                decimal=",",
                thousands=" ")

    st.write("✅ Aperçu du fichier importé :")
    st.dataframe(df.head())

    # Vérifier colonnes nécessaires
    if "N°" in df.columns:
    col_matricule = "N°"
elif "Matricule" in df.columns:
    col_matricule = "Matricule"
else:
    st.error("❌ Le fichier doit contenir une colonne 'N°' ou 'Matricule'")
    st.stop()

# Vérifier colonnes nécessaires
    colonnes_requises = [col_matricule, "Mois", "Prime exeptionnelle (10%) (DZD)"]
    if not all(col in df.columns for col in colonnes_requises):
        st.error(f"❌ Le fichier doit contenir les colonnes : {colonnes_requises}")
        st.stop()
    
    if st.button("🚀 Mettre à jour Supabase"):
        for _, row in df.iterrows():
            # ⚡ Utiliser col_matricule dynamique
            matricule = str(row[col_matricule]).strip()
            mois = str(row["Mois"]).strip()
            allowance = float(row["Prime exeptionnelle (10%) (DZD)"] or 0)
    
            data = {
                "Allowance": allowance,
                "ispaye": True
            }
    
            # Mise à jour Supabase
            supabase.table("Paie") \
                .update(data) \
                .eq("matricule", matricule) \
                .eq("Mois", mois) \
                .execute()
    
            print(f"✅ Mise à jour : {matricule} - {mois} → {allowance} DZD")
    
        st.success("🎉 Toutes les lignes ont été mises à jour dans Supabase.")



