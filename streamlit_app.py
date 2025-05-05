# Import required libraries for web interface, QR code generation, and data handling
import streamlit as st
import qrcode
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

# Load the final dataset containing both real and fake laws
df_final = pd.read_csv("all_laws.csv")

# URLs for Google Form (voting) and linked Google Sheet (live result updates)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdB7exmWrMhwhjufAwubY4HRTad4HSjG55tTLZJoCwCyVz4ng/viewform"
SHEET_URL = "https://docs.google.com/spreadsheets/d/11NEGdpRFubObmm66fraGt74AtVpI4g4YI3LadBVHgN4/gviz/tq?tqx=out:csv"

# Shuffle the laws to randomize their presentation order
df_game = df_final.sample(frac=1).reset_index(drop=True)

# Initialize session state for game logic and UI tracking
if "score" not in st.session_state:
    st.session_state.score = 0
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "reveal_location" not in st.session_state:
    st.session_state.reveal_location = False

# Set page title and subtitle
st.title("Dumb Law or Fake Dumb Law?")
st.subheader("Can you guess if the law is real or fake?")

# Load the first law if not already in session state
if "current_law" not in st.session_state:
    st.session_state.current_law = df_game.iloc[st.session_state.current_index]

# Fetch the current law for display
current_law = st.session_state.current_law
st.write(f"**Law:** {current_law['Law']}")

# Create three columns for layout: Real button, Fake button, Live Results
col1, col2, col3 = st.columns([1, 1, 2])

# --- Voting Buttons ---
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

# --- Live Voting Results ---
with col3:
    st.subheader("Live Results")

    # Helper function to fetch and count votes from the linked Google Sheet
    def fetch_votes():
        try:
            df_votes = pd.read_csv(SHEET_URL)
            real_votes = df_votes[df_votes.iloc[:, 1] == "Real"].shape[0]
            fake_votes = df_votes[df_votes.iloc[:, 1] == "Fake"].shape[0]
            return real_votes, fake_votes
        except Exception:
            return None, None

    # Update vote counts if button is clicked
    if st.button("Update Live Results"):
        real_votes, fake_votes = fetch_votes()

        if real_votes is not None and fake_votes is not None:
            st.write(f"**Real Votes:** {real_votes}")
            st.write(f"**Fake Votes:** {fake_votes}")
        else:
            st.error("Failed to fetch voting results. Make sure the sheet is public.")

# --- Location Reveal (only for real laws) ---
if st.session_state.reveal_location:
    if current_law["Type"] == "Real":
        city = current_law["City"] if pd.notna(current_law["City"]) and current_law["City"].strip() else None
        location_display = f"{city}, {current_law['state']}" if city else current_law["state"]
        st.write(f"**Location:** {location_display}")

    # Button to go to the next law
    if st.button("Next Law"):
        st.session_state.current_index += 1
        st.session_state.current_law = df_game.iloc[st.session_state.current_index]
        st.session_state.reveal_location = False
        st.rerun()

# Display the user's score
st.write(f"**Score:** {st.session_state.score}")

# Handle end-of-game logic
if st.session_state.current_index >= len(df_game):
    st.write("Game Over!")
    if st.button("Play Again"):
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.reveal_location = False
        st.rerun()

# --- QR Code for Audience Voting ---
st.subheader("Scan the QR Code to Vote")

# Generate the QR code image based on the Google Form URL
qr = qrcode.make(FORM_URL)

# Convert QR code image to a format suitable for embedding in Streamlit
qr_bytes = BytesIO()
qr.thumbnail((150, 150))  # Resize for display
qr.save(qr_bytes, format="PNG")
qr_bytes.seek(0)

# Display the QR code in the sidebar or page
st.image(qr_bytes, caption="Scan to Vote!", width=150)



