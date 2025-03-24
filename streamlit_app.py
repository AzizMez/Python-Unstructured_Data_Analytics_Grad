import streamlit as st
import qrcode
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

df_final = pd.read_csv("C:\\Users\\azizm\\Documents\\Uni\\Spring 2025\\UDA\\data\\all_laws.csv")

# Google Form & Sheet URLs (for QR Code Implementation for Presentation)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdB7exmWrMhwhjufAwubY4HRTad4HSjG55tTLZJoCwCyVz4ng/viewform"
SHEET_URL = "https://docs.google.com/spreadsheets/d/11NEGdpRFubObmm66fraGt74AtVpI4g4YI3LadBVHgN4/gviz/tq?tqx=out:csv"

df_game = df_final.sample(frac=1).reset_index(drop=True)

if "score" not in st.session_state:
    st.session_state.score = 0
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "reveal_location" not in st.session_state:
    st.session_state.reveal_location = False

st.title("Dumb Law or Fake Dumb Law?")
st.subheader("Can you guess if the law is real or fake?")

if "current_law" not in st.session_state:
    st.session_state.current_law = df_game.iloc[st.session_state.current_index]

current_law = st.session_state.current_law

st.write(f"**Law:** {current_law['Law']}")


#Including Scoring System and Live Results of Voting
col1, col2, col3 = st.columns([1, 1, 2])

# Voting Buttons
with col1:
    if st.button("Real"):
        if not st.session_state.reveal_location:
            st.session_state.reveal_location = True
            if current_law["Type"] == "Real":
                st.success("Correct! This law is real.")
                st.session_state.score += 1
            else:
                st.error("Wrong! This law is fake.")

with col2:
    if st.button("Fake"):
        if not st.session_state.reveal_location:
            st.session_state.reveal_location = True
            if current_law["Type"] == "Fake":
                st.success("Correct! This law is fake.")
                st.session_state.score += 1
            else:
                st.error("Wrong! This law is real.")

# Live Results
with col3:
    st.subheader("Live Results")

    def fetch_votes():
        try:
            df_votes = pd.read_csv(SHEET_URL)
            real_votes = df_votes[df_votes.iloc[:, 1] == "Real"].shape[0]
            fake_votes = df_votes[df_votes.iloc[:, 1] == "Fake"].shape[0]
            return real_votes, fake_votes
        except Exception:
            return None, None

    if st.button("Update Live Results"):
        real_votes, fake_votes = fetch_votes()

        if real_votes is not None and fake_votes is not None:
            st.write(f"**Real Votes:** {real_votes}")
            st.write(f"**Fake Votes:** {fake_votes}")
        else:
            st.error("Failed to fetch voting results. Make sure the sheet is public.")

# Show location after if Law is Real
if st.session_state.reveal_location:
    if current_law["Type"] == "Real":
        city = current_law["City"] if pd.notna(current_law["City"]) and current_law["City"].strip() else None
        location_display = f"{city}, {current_law['state']}" if city else current_law["state"]
        st.write(f"**Location:** {location_display}")

    if st.button("Next Law"):
        st.session_state.current_index += 1
        st.session_state.current_law = df_game.iloc[st.session_state.current_index]  # Load new law
        st.session_state.reveal_location = False
        st.rerun()


st.write(f"**Score:** {st.session_state.score}")


if st.session_state.current_index >= len(df_game):
    st.write("Game Over!")
    if st.button("Play Again"):
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.reveal_location = False
        st.rerun()


# QR Code
st.subheader("Scan the QR Code to Vote")
qr = qrcode.make(FORM_URL)

# Making it fit on the same page (no scrolling)
qr_bytes = BytesIO()
qr.thumbnail((150, 150))
qr.save(qr_bytes, format="PNG")
qr_bytes.seek(0)

st.image(qr_bytes, caption="Scan to Vote!", width=150)


