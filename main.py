# --- THE FINAL, ROBUST CSS FUNCTION (COPY-PASTE READY) ---
def apply_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* --- CORE APP STYLING --- */
        .stApp {
            background: linear-gradient(180deg, #0f0f23 0%, #1a1a3e 100%);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* --- ROBUST WIDGET STYLING (SIMULATED GLASSMORPHISM) --- */

        /* Text Input & Select Box Styling */
        div[data-testid="stTextInput"] input,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            /* SIMULATED GLASS EFFECT: Semi-transparent gradient background */
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%) !important;
            
            /* REMOVED backdrop-filter to ensure compatibility */
            
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 10px !important;
            color: #e2e8f0 !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
            transition: all 0.3s ease !important;
        }
        
        /* Hover & Focus Effects */
        div[data-testid="stTextInput"] input:hover,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {
            border-color: rgba(102, 126, 234, 0.6) !important;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
            transform: translateY(-2px);
        }
        
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div[aria-expanded="true"] {
            border-color: rgba(102, 126, 234, 0.8) !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.25) !important;
        }

        /* Dropdown menu for Selectbox */
        div[data-baseweb="popover"] ul {
            background: linear-gradient(180deg, #1a1a3e 0%, #0f0f23 100%) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 10px !important;
            padding: 5px !important;
        }
        div[data-baseweb="popover"] ul li:hover {
            background-color: rgba(102, 126, 234, 0.2) !important;
        }
        
        /* Alert Styling */
        div[data-testid="stAlert"] {
            border-radius: 12px !important;
            border-left-width: 4px !important;
            border-top: none !important; border-right: none !important; border-bottom: none !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        div[data-testid="stAlert"]:hover {
             transform: translateX(5px);
        }
        div[data-testid="stAlert"][data-baseweb="alert-success"] { background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%) !important; border-left-color: #10b981 !important; }
        div[data-testid="stAlert"][data-baseweb="alert-warning"] { background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%) !important; border-left-color: #f59e0b !important; }
        div[data-testid="stAlert"][data-baseweb="alert-error"] { background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%) !important; border-left-color: #ef4444 !important; }
        div[data-testid="stAlert"][data-baseweb="alert-info"] { background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%) !important; border-left-color: #3b82f6 !important; }

        /* Button Styling */
        .stButton > button {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.1) 100%) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            color: white !important;
            border-radius: 10px !important;
            transition: all 0.3s ease !important;
        }
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
            border-color: rgba(102, 126, 234, 0.5) !important;
        }
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            border: none !important;
            font-size: 1.2rem;
            padding: 1rem 3rem;
            font-weight: 600;
        }
        .stButton > button[kind="primary"]:hover {
            box-shadow: 0 10px 30px rgba(16, 185, 129, 0.4);
        }

        /* --- ALL OTHER ORIGINAL STYLES --- */
        .main .block-container { padding-top: 1rem; max-width: 1600px; }
        h1 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700 !important; font-size: 2.5rem !important; }
        h2 { color: #ffffff !important; font-weight: 600 !important; font-size: 1.8rem !important; }
        h3 { color: #e2e8f0 !important; font-weight: 500 !important; }
        .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.2rem; margin: 1.5rem 0; }
        .info-item { background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.05) 100%); padding: 1rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1); }
        div[data-testid="metric-container"] { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.18); padding: 1.2rem; border-radius: 16px; box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37); }
        div[data-testid="stTabs"] [data-baseweb="tab-list"] { border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1); }
        div[data-testid="stTabs"] [aria-selected="true"] { background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%); color: #ffffff !important; }
        .social-pills { display: flex; gap: 1rem; margin-top: 1rem; }
        .social-pill { background: rgba(255, 255, 255, 0.05); border: 2px solid rgba(255, 255, 255, 0.1); width: 50px; height: 50px; border-radius: 50%; font-size: 1.5rem; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; transition: all 0.3s ease; }
        .social-pill:hover { background: rgba(102, 126, 234, 0.2); transform: scale(1.1); }
        #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)
