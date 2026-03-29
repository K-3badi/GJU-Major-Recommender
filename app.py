import streamlit as st
import pandas as pd
import joblib
import time
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- 1. PAGE CONFIG & CUSTOM CSS ---
st.set_page_config(page_title="GJU Major Recommender", page_icon="🎓", layout="centered", initial_sidebar_state="expanded")

# Inject Custom CSS to make it look professional
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} /* Hides the top-right menu */
    footer {visibility: hidden;}    /* Hides the Streamlit watermark */
    header {visibility: hidden;}    /* Hides the top header bar */
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        border-color: #004b87; /* GJU Blue-ish hover */
        color: #004b87;
    }
    .survey-container {
        padding: 2rem;
        border-radius: 10px;
        background-color: #f8f9fa;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. INITIALIZE MEMORY (SESSION STATE) ---
if 'prediction' not in st.session_state:
    st.session_state.prediction = None
if 'survey_submitted' not in st.session_state:
    st.session_state.survey_submitted = False

# --- 3. DATABASE & MODEL SETUP ---
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_resource(show_spinner=False)
def load_model():
    return joblib.load('top 15.pkl')

model = load_model()

# --- 4. SIDEBAR (PROFESSIONAL CONTEXT) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/5/52/German_Jordanian_University_logo.png/220px-German_Jordanian_University_logo.png", width=150)
    st.markdown("### About This Tool")
    st.write("This AI-driven recommendation engine is designed to help prospective students find their ideal academic path at GJU.")
    st.write("By analyzing personal interests and mapping them against historical student success data, the system predicts the most suitable major.")
    st.markdown("---")
    st.caption("Powered by Machine Learning | Business Intelligence & Data Analytics")

# --- 5. MAIN UI HEADER ---
st.title("🎓 GJU Major Recommendation Engine")
st.markdown("Discover your future at the German Jordanian University. Answer the 15 questions below to receive an AI-powered major prediction.")
st.markdown("---")

# --- 6. SURVEY FORM ---
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

# Only show the form if they haven't submitted yet
if not st.session_state.survey_submitted:
    with st.form("survey_form"):
        st.subheader("Rate your interest (1 = Low, 5 = High)")
        answers = {}
        for q_id, q_text in questions.items():
            answers[q_id] = st.select_slider(q_text, options=[1, 2, 3, 4, 5], value=3)
        
        submitted = st.form_submit_button("Predict My GJU Major", use_container_width=True)

    if submitted:
        # UX: Fake processing time for professional feel
        with st.spinner('Analyzing profile against GJU historical data...'):
            time.sleep(1.2)
            input_df = pd.DataFrame([answers])
            st.session_state.prediction = model.predict(input_df)[0]
            st.session_state.survey_submitted = True
            st.rerun() # Refresh to hide the form and show the result

# --- 7. RESULT & FEEDBACK LOOP ---
if st.session_state.survey_submitted and st.session_state.prediction:
    st.success("### Analysis Complete!")
    st.markdown(f"<h1 style='text-align: center; color: #004b87;'>{st.session_state.prediction}</h1>", unsafe_allow_html=True)
    st.balloons()
    
    st.markdown("---")
    st.subheader("Help us improve the algorithm:")
    st.write("Does this major align with your expectations and interests?")
    
    col1, col2 = st.columns(2)
    
    # Function to handle database save and reset
    def save_and_reset(feedback_type):
        try:
            existing_data = conn.read(usecols=[0, 1, 2], ttl=5).dropna(how="all")
            new_row = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Major_Recommended": st.session_state.prediction,
                "User_Feedback": feedback_type
            }])
            updated_data = pd.concat([existing_data, new_row], ignore_index=True)
            conn.update(data=updated_data)
            
            st.toast("✅ Feedback saved to database!")
            time.sleep(1.5) # Let the user read the success message
            
            # Reset the app for the next user
            st.session_state.prediction = None
            st.session_state.survey_submitted = False
            st.rerun()
            
        except Exception as e:
            st.error("Could not save to database. Please try again.")

    if col1.button("Yes, fits me perfectly! ✅", use_container_width=True):
        save_and_reset("Correct")

    if col2.button("No, I expected something else ❌", use_container_width=True):
        save_and_reset("Incorrect")
