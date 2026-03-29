import streamlit as st
import pandas as pd
import joblib

# 1. Page Configuration
st.set_page_config(page_title="GJU Major Recommender", page_icon="🎓", layout="centered")

# 2. Load the 83% Accuracy Model
@st.cache_resource
def get_model():
    # Make sure this matches your filename on GitHub exactly!
    return joblib.load('top 15.pkl')

model = get_model()

# 3. UI and Questions
st.title("🎓 GJU Major Recommendation Engine")
st.info("Find your academic path based on the profiles of successful graduates.")

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
    'R3': "I like building things with my hands (wood, metal, or electronics).",
    'I8': "I enjoy using scientific equipment like microscopes.",
    'S4': "I like helping people solve their daily problems."
}

with st.form("gju_survey"):
    st.subheader("Rate your interest (1 = Low, 5 = High)")
    user_answers = {}
    for q_id, q_text in questions.items():
        user_answers[q_id] = st.select_slider(q_text, options=[1, 2, 3, 4, 5], value=3)
    
    submit = st.form_submit_button("Predict My GJU Major", use_container_width=True)

if submit:
    input_df = pd.DataFrame([user_answers])
    prediction = model.predict(input_df)[0]
    st.success(f"## Your Recommended School: \n # **{prediction}**")
    st.balloons()
    
    st.markdown("---")
    st.write("### Was this recommendation accurate?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, this fits me! ✅"):
            st.toast("Thanks for the feedback! This helps validate our model.")
            # In a real app, we would save this to a database
    with col2:
        if st.button("No, I expected something else ❌"):
            st.toast("Interesting! We will use this to improve the AI.")
