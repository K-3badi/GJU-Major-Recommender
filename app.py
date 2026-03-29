import streamlit as st
import pandas as pd
import joblib
from streamlit_gsheets import GSheetsConnection

# 1. Page Setup & Connection
st.set_page_config(page_title="GJU Major Recommender", page_icon="🎓")
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Load your 83% Accuracy Model
@st.cache_resource
def get_model():
    return joblib.load('top 15.pkl')

model = get_model()

# 3. UI Styling
st.title("🎓 GJU Major Recommendation Engine")
st.markdown("### Find your path at the German Jordanian University")
st.info("This AI uses historical student data to predict which school fits your personality.")

# 4. The 15 Survey Questions
questions = {
    'A3': "I enjoy playing a musical instrument.", 'I1': "I like to study and help solve world problems.",
    'I4': "I enjoy working in a research lab.", 'A8': "I like writing creative stories or poetry.",
    'A5': "I enjoy performing in front of an audience.", 'R4': "I like to work on or repair machinery.",
    'E5': "I enjoy giving speeches or leading meetings.", 'S8': "I like helping people with personal problems.",
    'C5': "I like keeping detailed records of data.", 'S3': "I enjoy teaching or training people.",
    'E3': "I like to lead teams or manage projects.", 'A2': "I enjoy sketching, drawing, or painting.",
    'R3': "I like building things with my hands.", 'I8': "I enjoy using scientific equipment.",
    'S4': "I like helping people solve daily problems."
}

with st.form("gju_survey"):
    user_answers = {}
    for q_id, q_text in questions.items():
        user_answers[q_id] = st.select_slider(q_text, options=[1, 2, 3, 4, 5], value=3)
    
    submit = st.form_submit_button("Predict My GJU Major", use_container_width=True)

# 5. Prediction & Database Shipping
if submit:
    input_df = pd.DataFrame([user_answers])
    prediction = model.predict(input_df)[0]
    
    st.success(f"## Your Recommended School: \n # **{prediction}**")
    st.balloons()
    
    st.markdown("---")
    st.subheader("Was this recommendation accurate?")
    
    col1, col2 = st.columns(2)
    
    if col1.button("Yes, fits me! ✅", use_container_width=True):
        new_row = pd.DataFrame([{
            "Timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"), 
            "Major_Recommended": prediction, 
            "User_Feedback": "Correct"
        }])
        conn.create(data=new_row)
        st.toast("Saved to the GJU Database!")

    if col2.button("No, not for me ❌", use_container_width=True):
        new_row = pd.DataFrame([{
            "Timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"), 
            "Major_Recommended": prediction, 
            "User_Feedback": "Incorrect"
        }])
        conn.create(data=new_row)
        st.toast("Feedback recorded for AI retraining.")
