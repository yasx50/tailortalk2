import streamlit as st
import requests

st.title("🗓️ AI Appointment Scheduler")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("You:", key="input")

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    response = requests.post("http://localhost:8000/chat", json={"message": user_input})
    reply = response.json()["reply"]
    st.session_state.chat_history.append(("bot", reply))

for sender, msg in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"**You**: {msg}")
    else:
        st.markdown(f"**Assistant**: {msg}")
