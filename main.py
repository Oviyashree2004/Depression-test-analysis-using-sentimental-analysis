import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time
from nltk.sentiment import SentimentIntensityAnalyzer
import plotly.express as px
import sqlite3
import speech_recognition as sr

sia = SentimentIntensityAnalyzer()

conn = sqlite3.connect('user_data.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    mood_data TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS progress (
    username TEXT,
    date TEXT,
    score INTEGER,
    category TEXT
)
''')

if 'user_db' not in st.session_state:
    st.session_state.user_db = {}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = 'signup'
if 'progress_data' not in st.session_state:
    st.session_state.progress_data = pd.DataFrame(columns=['username', 'date', 'score', 'category'])
if 'mood_data' not in st.session_state:
    st.session_state.mood_data = pd.DataFrame(columns=['username', 'date', 'mood', 'comment'])
if 'username' not in st.session_state:
    st.session_state.username = None  

if 'last_action_time' not in st.session_state:
    st.session_state.last_action_time = time.time()

def is_double_click():
    current_time = time.time()
    if 'last_action_time' in st.session_state:
        if current_time - st.session_state.last_action_time < 0.5:
            return True
    st.session_state.last_action_time = current_time
    return False

def set_background_image():
    st.markdown(
        """
        <style>
        body {
            font-size: 50px; /* Base font size for the entire app */
        }
        .stApp {
            background-image: url('https://png.pngtree.com/thumb_back/fh260/background/20231027/pngtree-hexagonal-abstract-background-with-a-black-textured-surface-image_13704307.png');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        .stTitle {
            font-size: 38px; /* Increased font size for titles */
        }
        .stButton>button {
            font-size: 25px; /* Increase button font size */
        }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            font-size: 25px; /* Increase input and text area font size */
        }
        .stSelectbox>div>div>select {
            font-size: 22px; /* Increase selectbox font size */
        }
        .question-text {
            font-size: 30px; /* Increase font size for questions */
        }
        .stRadio > div > label {
            font-size: 24px; /* Increase font size for radio options */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def set_category_background_image():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url('https://getwallpapers.com/wallpaper/full/8/6/3/92629.jpg'); 
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        .transparent-container {
            background-color: rgba(255, 255, 255, 0.6);
            padding: 30px;
            border-radius: 15px;
            width: 60%;
            margin: auto;
            text-align:center;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
        }
        .category-btn {
            width: 120px;  
            background-color: rgba(0, 123, 255, 0.8);
            color: black;
            padding: 10px;
            border: none;
            border-radius: 8px;
            font-size: 24px;  /* Increase font size for buttons */
            cursor: pointer;
        }
        .sentiment-block {
            padding: 20px;
            border-radius: 8px;
            color: black;
            margin: 20px 0;
            text-align: center;
            font-size: 24px;  /* Increase font size for sentiment block */
            width: 60%;
            margin-left: auto;
            margin-right: auto;
        }
        .text-background {
            background-color: rgba(255, 255, 255, 0.8);
            padding:  20px;
            border-radius: 10px;
            font-size: 22px;  /* Increase font size for text background */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def sidebar():
    st.sidebar.title("User Authentication")
    if not st.session_state.logged_in:
        if st.sidebar.button("Login", key="login_button"):
            st.session_state.page = 'login'
        if st.sidebar.button("Sign Up", key="signup_button"):
            st.session_state.page = 'signup'
    else:
        if st.sidebar.button("Logout", key="logout_button"):
            st.session_state.logged_in = False
            st.session_state.page = 'signup'
    
    if st.sidebar.button("Admin Page", key="admin_page_button"):
        st.session_state.page = 'admin'

def signup():
    set_background_image()
    st.markdown("<h1 style='font-size: 36px;'>Sign Up</h1>", unsafe_allow_html=True)

    new_username = st.text_input("Create a Username", key='signup_username')
    new_password = st.text_input("Create a Password", type="password", key='signup_password')
    confirm_password = st.text_input("Confirm Password", type="password", key='confirm_password')

    if st.button("Sign Up", key='signup_btn'):
        if is_double_click():
            return
        if not new_username or not new_password or not confirm_password:
            st.error("Please fill out all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            # ✅ Check if username already exists
            c.execute('SELECT username FROM users WHERE username = ?', (new_username,))
            if c.fetchone():
                st.error("Username already exists. Please choose a different one.")
            else:
                c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (new_username, new_password))
                conn.commit()
                st.success("Account created successfully! You can now log in.")
                st.session_state.page = 'login'

    st.markdown("<div class='text-background' style='font-size: 20px;'>Welcome to the platform! Please sign up to get started.</div>", unsafe_allow_html=True)


def login():
    set_background_image()
    st.markdown("<h1 style='font-size: 36px;'>Login</h1>", unsafe_allow_html=True)  # Increase title font size
    st.markdown("""
        <style>
            .stTextInput label {
                font-size: 60px;  /* Adjust label font size here */
            }
            input[type="text"], input[type="password"] {
                font-size: 24px;  /* Adjust input font size here */
            }
        </style>
    """, unsafe_allow_html=True)
    
    username = st.text_input("Username", key='login_username')
    password = st.text_input("Password", type="password", key='login_password')

    if st.button("Login", key='login_btn'):
        if is_double_click():
            return
        if not username or not password:
            st.error("Please enter both username and password.")
        else:
            c.execute('SELECT password, mood_data FROM users WHERE username = ?', (username,))
            result = c.fetchone()
            if result and result[0] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.mood_data = pd.read_json(result[1]) if result[1] else pd.DataFrame()
                st.success("Login successful!")
                st.session_state.page = 'category'
            else:
                st.error("Invalid username or password.")

def show_category_options():
    set_category_background_image()
    st.markdown("<div class='transparent-container'><h2>Select Your Category</h2>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Students"):
            st.session_state.page = 'students'
    with col2:
        if st.button("Working People"):
            st.session_state.page = 'working'
    with col3:
        if st.button("Aged People"):
            st.session_state.page = 'aged'
    with col4:
        if st.button("Mood Tracker"):
            st.session_state.page = 'mood_tracker'

    st.markdown('</div>', unsafe_allow_html=True)

def save_progress(score, user_type):
    date_str = datetime.now().strftime("%Y -%m-%d")  
    new_progress = pd.DataFrame({
        'username': [st.session_state.username],
        'date': [date_str],  
        'score': [score],
        'category': [user_type]
    })

    st.session_state.progress_data = pd.concat([st.session_state.progress_data, new_progress], ignore_index=True)

    c.execute('INSERT INTO progress (username, date, score, category) VALUES (?, ?, ?, ?)',
              (st.session_state.username, date_str, score, user_type))
    conn.commit()

def analyze_sentiment(text):
    score = sia.polarity_scores(text)
    return score

def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Sorry, I could not understand the audio."
        except sr.RequestError:
            return "Could not request results from the service."

def display_questions(user_type):
    if user_type == 'students':
        st.title("Questions for Students")
        questions = get_student_questions()
    elif user_type == 'working':
        st.title("Questions for Working People")
        questions = get_working_questions()
    elif user_type == 'aged':
        st.title("Questions for Aged People")
        questions = get_aged_questions()

    answers = []
    for question in questions:
        st.markdown(f"<div class='question-text'>{question}</div>", unsafe_allow_html=True)  # Updated line
        answer = st.radio("", ["Never", "Rarely", "Sometimes", "Often", "Always"], key=question)
        answers.append(answer)

        if answer == "Never":
            st.image("https://media.tenor.com/NJsnnVyDK_4AAAAj/cute.gif", caption="You're doing great!")
        elif answer == "Rarely":
            st.image("E:\md\streamlitenv\icegif-382.gif", caption="Seems like you're doing okay.")
        elif answer == "Sometimes":
            st.image("https://media.tenor.com/hJWsOR_X40oAAAAi/take-care-of-yourself-take-it-easy.gif", caption="Take it easy!")
        elif answer == "Often":
            st.image("https://media.tenor.com/mzR2hoDgjm0AAAAj/meobeo-worried.gif", caption="You're feeling stressed.")
        elif answer == "Always":
            st.image("https://media.tenor.com/DcVGg7sEEhgAAAAj/emotion-cartoon.gif", caption="Please take care of your mental health.")

    score = calculate_score(answers)
    state, recommendation = get_depression_state(score, user_type)

    st.subheader(f"Your score: {score}")
    st.subheader(f"Depression state: {state}")
    st.subheader(f"Recommendation: {recommendation}")
    save_progress(score, user_type)

    user_text = st.text_area("Share your thoughts:")
    if st.button("Analyze Text"):
        if user_text:
            sentiment_score = analyze_sentiment(user_text)
            st.write(f"Sentiment Score: {sentiment_score}")

    if st.button("Speak your thoughts"):
        spoken_text = get_voice_input()
        st.write(f"You said: {spoken_text}")
        sentiment_score = analyze_sentiment(spoken_text)
        st.write(f"Sentiment Score: {sentiment_score}")

    st.subheader("Your Score Over Time")
    scores_df = st.session_state.progress_data[st.session_state.progress_data['username'] == st.session_state.username]
    if not scores_df.empty:
        fig = px.line(scores_df, x='date', y='score', title="Score History", labels ={'date': 'Date', 'score': 'Score'}, markers=True, color_discrete_sequence=["#1f77b4"])  # Customize color
        st.plotly_chart(fig)

    if st.button("Back to Categories"):
        st.session_state.page = 'category'

def get_student_questions():
    return [
        "1. How often do you feel stressed?",
        "2. Do you have someone to talk to?",
        "3. How often do you feel lonely?",
        "4. Do you find it difficult to focus?",
        "5. Do you feel overwhelmed by your academic workload?"
    ]

def get_working_questions():
    return [
        "1. How often do you feel stressed at work?",
        "2. Do you have difficulty balancing work and personal life?",
        "3. How often do you feel fatigued after work?",
        "4. Do you find it hard to concentrate on tasks?",
        "5. Are you satisfied with your current job?"
    ]

def get_aged_questions():
    return [
        "1. Do you often feel lonely?",
        "2. How frequently do you feel happy?",
        "3. Are you satisfied with your social life?",
        "4. How often do you feel bored?",
        "5. Do you find joy in daily activities?"
    ]

def ask_questions(questions):
    answers = []
    for question in questions:
        answer = st.radio(question, ["Never", "Rarely", "Sometimes", "Often", "Always"], key=question)
        answers.append(answer)
    return answers

def calculate_score(answers):
    scoring = {
        "Never": 0,
        "Rarely": 1,
        "Sometimes": 2,
        "Often": 3,
        "Always": 4
    }
    return sum(scoring[answer] for answer in answers)

def get_depression_state(score, user_type):
    if score <5:
        return "Normal ", "Keep maintaining a healthy lifestyle!"
    elif score <10:
        return "Mild", "Consider talking to someone about your feelings."
    elif score <15:
        return "Moderate", "It may be helpful to seek professional help."
    else:
        return "Severe", "Please reach out to a mental health professional."

def display_user_depression_state():
    st.title("User  Depression State Overview")
    c.execute('SELECT * FROM progress')
    progress = c.fetchall()
    
    if progress:
        progress_df = pd.DataFrame(progress, columns=['Username', 'Date', 'Score', 'Category'])
        depression_states = []
        
        for username in progress_df['Username'].unique():
            user_progress = progress_df[progress_df['Username'] == username]
            scores = user_progress['Score']
            if not scores.empty:  
                state = get_depression_state(scores.mean(), 'students')  
                depression_states.append({'Username': username, 'Depression State': state[0]})
        
        depression_states_df = pd.DataFrame(depression_states)
        st.dataframe(depression_states_df)
        
        depression_state_counts = depression_states_df['Depression State'].value_counts().reset_index()
        depression_state_counts.columns = ['Depression State', 'Count']
        
        fig_depression_state = px.bar(depression_state_counts, x='Depression State', y='Count', color='Depression State',
                                    title="Depression State Distribution",
                                    labels={'Count': 'Count'},
                                    color_discrete_sequence=px.colors.qualitative.Set1)
        st.plotly_chart(fig_depression_state)
    else:
        st.write("No user progress data found.")

def mood_tracker():
    st.title("Mood Tracker")
    
    mood = st.selectbox("How do you feel today?", ["Happy", "Sad", "Neutral", "Anxious", "Angry"])
    comment = st.text_area("Any comments about your mood?")
    
    if st.button("Submit Mood", key='submit_mood'):
        if is_double_click():
            return
        
        date = datetime.now().strftime("%Y-%m-%d")  
        mood_entry = {'username': st.session_state.username, 'date': date, 'mood': mood, 'comment': comment}
        
        
        st.session_state.mood_data = pd.concat([st.session_state.mood_data, pd.DataFrame([mood_entry])], ignore_index=True)

        
        c.execute('UPDATE users SET mood_data = ? WHERE username = ?', (st.session_state.mood_data.to_json(), st.session_state.username))
        conn.commit()

        st.success("Mood recorded successfully!")
    
    sentiment_result = ""
    if st.button("Analyze Comment Sentiment"):
        if comment:
            sentiment = analyze_sentiment(comment)
            sentiment_result = f"Sentiment Analysis Result: {sentiment}"
        else:
            st.error("Please enter a comment to analyze.")

    if st.button("Record Mood Comment"):
        spoken_text = get_voice_input()
        if spoken_text and "Sorry" not in spoken_text:
            st.success(f"You said: {spoken_text}")
            comment = spoken_text
            sentiment = analyze_sentiment(comment)
            sentiment_result = f"Sentiment Analysis Result: {sentiment}"

    if sentiment_result:
        st.markdown(f"<div class='sentiment-block'>{sentiment_result}</div>", unsafe_allow_html=True)

    st.write("Your Mood Entries:")
    st.dataframe(st.session_state.mood_data)

    if not st.session_state.mood_data.empty:
        st.session_state.mood_data['date'] = pd.to_datetime(st.session_state.mood_data['date'], errors='coerce')  # Convert to datetime, handle errors
        mood_counts = st.session_state.mood_data['mood'].value_counts().reset_index()
        mood_counts.columns = ['Mood', 'Count']
        
        fig_dist = px.bar(mood_counts, x='Mood', y='Count', color='Mood',
                          title="Mood Distribution",
                          labels={'Count': 'Count'},
                          color_discrete_sequence=px.colors.qualitative.Set1)
        st.plotly_chart(fig_dist)

    if not st.session_state.mood_data.empty:
        last_week_data = st.session_state.mood_data[st.session_state.mood_data['date'] >= (datetime.now() - pd.Timedelta(days=7))]
        
        if not last_week_data.empty:
            mood_trend = last_week_data.groupby('date')['mood'].value_counts().unstack().fillna(0)
            mood_trend = mood_trend.reset_index()
            
            fig_trend = px.bar(mood_trend, x='date', y=mood_trend.columns[1:], 
                               title="Mood Trend Over Time (Last 7 Days)",
                               labels={'value': 'Count', 'date': 'Date'},
                               color_discrete_sequence=px.colors.sequential.Plasma)
            st.plotly_chart(fig_trend)
        else:
            st.write("No mood entries in the last 7 days.")

    if st.button("Back to Categories"):
        st.session_state.page = 'category'
    
    
def admin_login():
    st.title("Admin Login")
    admin_username = st.text_input("Admin Username", key='admin_username')
    admin_password = st.text_input("Admin Password", type="password", key='admin_password')

    if st.button("Login", key='admin_login_btn'):
        if admin_username == "admin" and admin_password == "admin123":
            st.session_state.admin_logged_in = True
            st.success("Admin login successful!")
        else:
            st.error("Invalid admin username or password.")

def display_user_data():
    st.title("User   Data Overview")

    c.execute('SELECT * FROM users')
    users = c.fetchall()

    if users:
        user_df = pd.DataFrame(users, columns=['Username', 'Password', 'Mood Data'])
        st.dataframe(user_df)
        c.execute('SELECT * FROM progress')
        progress = c.fetchall()

        if progress:
            progress_df = pd.DataFrame(progress, columns=['Username', 'Date', 'Score', 'Category'])
            progress_df['Date'] = pd.to_datetime(progress_df['Date'])  # Convert to datetime
            st.subheader("User   Progress Data")
            st.dataframe(progress_df)
    else:
        st.write(" No user data found.")

def display_user_depression_state():
    st.title("User   Depression State Overview")
    c.execute('SELECT * FROM progress')
    progress = c.fetchall()
    
    if progress:
        progress_df = pd.DataFrame(progress, columns=['Username', 'Date', 'Score', 'Category'])
        depression_states = []
        for username in progress_df['Username'].unique():
            user_progress = progress_df[progress_df['Username'] == username]
            scores = user_progress['Score']
            state = get_depression_state(scores.mean(), 'students') 
            depression_states.append({'Username': username, 'Depression State': state[0]})
        
        
        depression_states_df = pd.DataFrame(depression_states)
        st.dataframe(depression_states_df)
        
        
        depression_state_counts = depression_states_df['Depression State'].value_counts().reset_index()
        depression_state_counts.columns = ['Depression State', 'Count']
        
        fig_depression_state = px.bar(depression_state_counts, x='Depression State', y='Count', color='Depression State',
                                    title="Depression State Distribution",
                                    labels={'Count': 'Count'},
                                    color_discrete_sequence=px.colors.qualitative.Set1)
        st.plotly_chart(fig_depression_state)
    else:
        st.write("No user progress data found.")

def admin_page():
    if st.session_state.admin_logged_in:
        display_user_data()
        display_user_depression_state()
    else:
        admin_login()

def main():
    set_background_image()
    sidebar()

    if st.session_state.page == 'signup':
        signup()
    elif st.session_state.page == 'login':
        login()
    elif st.session_state.page == 'category':
        show_category_options()
    elif st.session_state.page == 'mood_tracker':
        mood_tracker()
    elif st.session_state.page == 'students':
        if st.session_state.username:
            display_questions('students')
        else:
            st.error("Please log in first.")
    elif st.session_state.page == 'working':
        if st.session_state.username:
            display_questions('working')
        else:
            st.error("Please log in first.")
    elif st.session_state.page == 'aged':
        if st.session_state.username:
            display_questions('aged')
        else:
            st.error("Please log in first.")
    elif st.session_state.page == 'admin':
        admin_page()
if __name__ == "__main__": 
    main()