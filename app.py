import streamlit as st
import pandas as pd
import joblib
import time
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- 1. PAGE CONFIG & CUSTOM CSS ---
st.set_page_config(page_title="GJU Major Recommender", page_icon="🎓", layout="centered", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        border-color: #004b87;
        color: #004b87;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. INITIALIZE MEMORY ---
if 'prediction' not in st.session_state:
    st.session_state.prediction = None
if 'survey_submitted' not in st.session_state:
    st.session_state.survey_submitted = False
if 'final_major' not in st.session_state:
    st.session_state.final_major = None

# --- 3. DATABASE & MODEL SETUP ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    pass 

@st.cache_resource(show_spinner=False)
def load_model():
    return joblib.load('top 15.pkl')

model = load_model()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/5/52/German_Jordanian_University_logo.png/220px-German_Jordanian_University_logo.png", width=150)
    st.markdown("### About This Tool")
    st.write("This 2-Stage Business Intelligence engine helps prospective students find their ideal academic path at GJU.")
    st.write("**Stage 1:** Machine Learning predicts your optimal Faculty based on personality traits.")
    st.write("**Stage 2:** An expert system pinpoints your specific major.")
    st.markdown("---")

# --- 5. MAIN UI ---
st.title("🎓 GJU Major Recommendation Engine")
st.markdown("Discover your future at the German Jordanian University.")
st.markdown("---")

# --- 6. STAGE 1: ML SURVEY ---
if not st.session_state.survey_submitted:
    questions = {
        'A3': "I enjoy playing a musical instrument.", 'I1': "I like to study and help solve world problems.",
        'I4': "I enjoy working in a research lab or on science projects.", 'A8': "I like writing creative stories, plays, or poetry.",
        'A5': "I enjoy performing in front of an audience.", 'R4': "I like to work on or repair machinery and cars.",
        'E5': "I enjoy giving speeches or leading meetings.", 'S8': "I like helping people with personal or emotional problems.",
        'C5': "I like keeping detailed records of expenses or data.", 'S3': "I enjoy teaching or training people how to do things.",
        'E3': "I like to lead teams or manage group projects.", 'A2': "I enjoy sketching, drawing, or painting.",
        'R3': "I like building things with my hands.", 'I8': "I enjoy using scientific equipment like microscopes.",
        'S4': "I like helping people solve their daily problems."
    }

    with st.form("survey_form"):
        st.subheader("Stage 1: Profile Assessment (1 = Low, 5 = High)")
        answers = {}
        for q_id, q_text in questions.items():
            answers[q_id] = st.select_slider(q_text, options=[1, 2, 3, 4, 5], value=3)
        
        submitted = st.form_submit_button("Analyze My Profile", use_container_width=True)

    if submitted:
        with st.spinner('Analyzing profile against GJU historical data...'):
            time.sleep(1.2)
            input_df = pd.DataFrame([answers])
            st.session_state.prediction = model.predict(input_df)[0]
            st.session_state.survey_submitted = True
            st.rerun()

# --- 7. STAGE 2: THE FUNNEL LOGIC ---
if st.session_state.survey_submitted and not st.session_state.final_major:
    school = st.session_state.prediction
    st.success(f"### AI Prediction: **{school}**")
    st.markdown("---")
    st.subheader("Stage 2: Pinpoint Your Major")
    st.info("Answer one final question to find your exact track within this school.")
    
    # SAFETY NET: Initialize variables so it never crashes with a NameError
    focus = None
    mapping = {}

    # 7a. The Logic Tree (Using 'in' makes it crash-proof against slight misspellings)
    if "Management" in school or "Business" in school:
        focus = st.radio("What type of work sounds most appealing to you?",
            ["Analyzing data, building models, and finding trends", 
             "Creating campaigns and understanding consumer behavior",
             "Managing supply chains and global trade",
             "Working with financial records and corporate money",
             "Leading teams and managing general business operations"], index=None)
        mapping = {
            "Analyzing data, building models, and finding trends": "Business Intelligence and Data Analytics",
            "Creating campaigns and understanding consumer behavior": "Digital Marketing",
            "Managing supply chains and global trade": "Logistic Sciences",
            "Working with financial records and corporate money": "International Accounting",
            "Leading teams and managing general business operations": "Management Science"
        }
        
    elif "Computing" in school:
        focus = st.radio("What is your primary interest in technology?",
            ["Writing code, developing software, and algorithms", 
             "Designing computer hardware and integrated systems",
             "Creating interactive media, 3D environments, and video games"], index=None)
        mapping = {
            "Writing code, developing software, and algorithms": "Computer Science",
            "Designing computer hardware and integrated systems": "Computer Engineering",
            "Creating interactive media, 3D environments, and video games": "Game Design and Media Informatics"
        }
        
    elif "Architecture" in school or "Built" in school:
        focus = st.radio("What do you want to design?",
            ["Entire buildings and urban structures", 
             "Indoor living spaces and aesthetics",
             "Visual graphics, branding, and multimedia"], index=None)
        mapping = {
            "Entire buildings and urban structures": "Architecture",
            "Indoor living spaces and aesthetics": "Interior Architecture",
            "Visual graphics, branding, and multimedia": "Design and Visual Communication"
        }
        
    elif "Technical" in school or "SATS" in school:
        focus = st.radio("Which area of engineering excites you more?",
            ["Robotics, automation, and smart systems", 
             "Optimizing manufacturing processes and production lines",
             "Designing physical machines and mechanical systems"], index=None)
        mapping = {
            "Robotics, automation, and smart systems": "Mechatronics Engineering",
            "Optimizing manufacturing processes and production lines": "Industrial Engineering",
            "Designing physical machines and mechanical systems": "Mechanical and Maintenance Engineering"
        }
        
    elif "Sustainable" in school or "SSSE" in school:
        focus = st.radio("What kind of systems do you want to build?",
            ["Green infrastructure and water resources", 
             "Renewable power systems and sustainable fuels",
             "Electrical circuits, power grids, and electronics"], index=None)
        mapping = {
            "Green infrastructure and water resources": "Civil and Environmental Engineering",
            "Renewable power systems and sustainable fuels": "Energy Engineering",
            "Electrical circuits, power grids, and electronics": "Electrical Engineering"
        }
        
    elif "Humanities" in school or "Social" in school:
        focus = st.radio("What is your professional focus?",
            ["Translating texts and linguistics across languages", 
             "Corporate communications and international public relations"], index=None)
        mapping = {
            "Translating texts and linguistics across languages": "Translation German, English, Arabic",
            "Corporate communications and international public relations": "German and English for Business and Communication (GEBC)"
        }
        
    elif "Medical" in school or "SAMS" in school:
        focus = st.radio("Which medical advancement interests you?",
            ["Designing medical equipment, prosthetics, and health tech", 
             "Developing chemical processes and new pharmaceuticals"], index=None)
        mapping = {
            "Designing medical equipment, prosthetics, and health tech": "Biomedical Engineering",
            "Developing chemical processes and new pharmaceuticals": "Pharmaceutical & Chemical Engineering"
        }
        
    elif "Nursing" in school:
        focus = "Nursing" # Auto-select
        mapping = {"Nursing": "Nursing Science"}
        st.write("Your predicted faculty offers a dedicated, specialized track.")
        
    else:
        st.error(f"⚠️ Developer Note: The AI predicted '**{school}**', which isn't mapped. Update the conditions to catch this string!")

    # 7b. Major Reveal Button
    if focus:
        if st.button("Reveal My Target Major", type="primary"):
            st.session_state.final_major = mapping[focus]
            st.rerun()

# --- 8. FINAL RESULT & FEEDBACK ---
if st.session_state.final_major:
    st.markdown(f"<h1 style='text-align: center; color: #004b87;'>{st.session_state.final_major}</h1>", unsafe_allow_html=True)
    st.balloons()
    
    st.markdown("---")
    st.subheader("Was this recommendation accurate?")
    
    col1, col2 = st.columns(2)
    
    def save_and_reset(feedback_type):
        try:
            existing_data = conn.read(usecols=[0, 1, 2], ttl=5).dropna(how="all")
            new_row = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Major_Recommended": st.session_state.final_major,
                "User_Feedback": feedback_type
            }])
            updated_data = pd.concat([existing_data, new_row], ignore_index=True)
            conn.update(data=updated_data)
        except:
            pass
            
        st.toast("✅ Feedback recorded!")
        time.sleep(1.5)
        st.session_state.prediction = None
        st.session_state.survey_submitted = False
        st.session_state.final_major = None
        st.rerun()

    if col1.button("Yes, fits me perfectly! ✅", use_container_width=True):
        save_and_reset("Correct")

    if col2.button("No, I expected something else ❌", use_container_width=True):
        save_and_reset("Incorrect")
