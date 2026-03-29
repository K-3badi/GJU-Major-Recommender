import streamlit as st
import pandas as pd
import joblib
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="GJU Major Recommender", 
    page_icon="🎓", 
    layout="centered"
)

# --- 2. DATABASE CONNECTION ---
# This connects to the [connections.gsheets] section in your Streamlit Secrets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Database connection failed. Please check your Streamlit Secrets formatting.")
    st.stop()

# --- 3. LOAD THE AI MODEL ---
@st.cache_resource
def load_gju_model():
    # Ensure 'top 15.pkl' is uploaded to the same folder on GitHub
    return joblib.load('top 15.pkl')

model = load_gju_model()

# --- 4. USER INTERFACE ---
st.title("🎓 GJU Major Recommendation Engine")
st.markdown("### Find your academic path at German Jordanian University")
st.info("Input your interests below. Our AI (83% accuracy) will predict which GJU school matches your profile based on historical data.")

# Define RIASEC-based questions
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

# Survey Form
with st.form("gju_survey"):
    st.subheader("Rate your interest (1 = Low, 5 = High)")
    user_answers = {}
    
    # Generate sliders for each question
    for q_id, q_text in questions.items():
        user_answers[q_id] = st.select_slider(q_text, options=[1, 2, 3, 4, 5], value=3)
    
    submit = st.form_submit_button("Predict My GJU Major", use_container_width=True)

# --- 5. PREDICTION & FEEDBACK ---
if submit:
    # Prepare data for model
    input_df = pd.DataFrame([user_answers])
    
    # Generate Prediction
    prediction = model.predict(input_df)[0]
    
    # Visual Result
    st.success(f"## Your Recommended School: \n # **{prediction}**")
    st.balloons()
    
    st.markdown("---")
    st.subheader("Help us improve: Was this recommendation accurate?")
    
    # Feedback Buttons
    col1, col2 = st.columns(2)
    
    # Current timestamp for the database
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with col1:
        if st.button("Yes, fits me! ✅", use_container_width=True):
            feedback_row = pd.DataFrame([{
                "Timestamp": current_time,
                "Major_Recommended": prediction,
                "User_Feedback": "Correct"
            }])
            conn.create(data=feedback_row)
            st.toast("Success! Feedback saved to GJU Database.")

    with col2:
        if st.button("No, expected something else ❌", use_container_width=True):
            feedback_row = pd.DataFrame([{
                "Timestamp": current_time,
                "Major_Recommended": prediction,
                "User_Feedback": "Incorrect"
            }])
            conn.create(data=feedback_row)
            st.toast("Feedback recorded. Thank you!")
