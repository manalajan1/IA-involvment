import streamlit as st
import time
import os

st.set_page_config(page_title="Suivi de l'attention", page_icon="🧠")
st.title("Suivi de l'attention étudiante")
st.markdown("Interface connectée au modèle IA en local 📡")

placeholder = st.empty()

while True:
    if os.path.exists("score.txt"):
        with open("score.txt", "r") as f:
            score = f.read().strip()
    else:
        score = "En attente..."

    with placeholder.container():
        st.metric("Score d’attention", f"{score} %")
    time.sleep(2)
