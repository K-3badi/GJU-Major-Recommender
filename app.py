import streamlit as st
import pandas as pd
import joblib
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="GJU Major Recommender", page_icon="🎓")

# 2. Database Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Load the AI Model
@st.cache_resource
def load_model():
    return joblib.load('top 15.pkl')

model = load_model()

# 4. Give the App "Memory" (Session State)
# This prevents the "Ghost Button" trap!
if 'prediction' not in st.session_state:
    st.session_state.prediction = None

# 5. UI Header
st.title("🎓 GJU Major Recommendation Engine")
st.info("Input your interests below to see which GJU school matches your profile.")

questions = {
    'A3': "I enjoy playing a musical instrument.", 
    'I1': "I like to study and help solve world problems.",
    'I4': "I enjoy working in a research lab or on science projects.", 
    'A8': "I like writing creative stories, plays, or poetry.",
    'A5': "I enjoy performing in front of an audience.", 
    'R4': "I like to work on or repair machinery and cars.",
    'E5': "I enjoy giving speeches or leading meetings.", 
    'S8': "I like helping people with personal or emotional problems.",
    'C5': "I like keeping detailed records of expenses or data.", 
    'S3': "I enjoy teaching or training people how to do things.",
    'E3': "I like to lead teams or manage group projects.", 
    'A2': "I enjoy sketching, drawing, or painting.",
    'R3': "I like building things with my hands.", 
    'I8': "I enjoy using scientific equipment like microscopes.",
    'S4': "I like helping people solve their daily problems."
}

with st.form("survey"):
    answers = {}
    for q_id, q_text in questions.items():
        answers[q_id] = st.select_slider(q_text, options=[1, 2, 3, 4, 5], value=3)
    
    submit = st.form_submit_button("Predict My GJU Major", use_container_width=True)

# 6. Prediction Logic (Saves to Memory)
if submit:
    input_df = pd.DataFrame([answers])
    st.session_state.prediction = model.predict(input_df)[0]

# 7. Feedback & Database Saving
# Because we use memory, this stays visible even after a button click!
if st.session_state.prediction:
    st.success(f"## Your Recommended School: \n # **{st.session_state.prediction}**")
    st.balloons()
    
    st.markdown("---")
    st.subheader("Help improve the AI: Was this accurate?")
    
    col1, col2 = st.columns(2)
    
    if col1.button("Yes, fits me! ✅", use_container_width=True):
        # Read the current sheet, add the new row, and update
        existing_data = conn.read(usecols=[0, 1, 2], ttl=5)
        existing_data = existing_data.dropna(how="all") # Clean empty rows
        
        new_row = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Major_Recommended": st.session_state.prediction,
            "User_Feedback": "Correct"
        }])
        
        updated_data = pd.concat([existing_data, new_row], ignore_index=True)
        conn.update(data=updated_data)
        st.toast("Success! Saved to your Google Sheet.")

    if col2.button("No, expected something else ❌", use_container_width=True):
        existing_data = conn.read(usecols=[0, 1, 2], ttl=5)
        existing_data = existing_data.dropna(how="all")
        
        new_row = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Major_Recommended": st.session_state.prediction,
            "User_Feedback": "Incorrect"
        }])
        
        updated_data = pd.concat([existing_data, new_row], ignore_index=True)
        conn.update(data=updated_data)
        st.toast("Feedback recorded!")
