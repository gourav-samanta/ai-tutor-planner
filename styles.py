"""
Modern Gen-Z UI/UX Styling
Clean, aesthetic, smooth animations
"""

CUSTOM_CSS = """
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* Main container */
    .main {
        background: #0a0e1a;
        padding: 2rem;
    }
    
    /* Cards with subtle styling */
    .stCard, div[data-testid="stMetricValue"] {
        background: rgba(20, 25, 40, 0.8) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(100, 110, 140, 0.15);
        border-radius: 20px;
        padding: 1.5rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
    }
    
    .stCard:hover {
        transform: translateY(-2px);
        border-color: rgba(100, 110, 140, 0.25);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Buttons - Muted colors */
    .stButton > button {
        background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
        color: #e2e8f0;
        border: 1px solid rgba(100, 110, 140, 0.2);
        border-radius: 14px;
        padding: 0.75rem 2rem;
        font-weight: 500;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        background: linear-gradient(135deg, #5a6678 0%, #3d4758 100%);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        border-color: rgba(100, 110, 140, 0.3);
    }
    
    /* Primary action buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #7c8ef0 0%, #8659b0 100%);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background: rgba(20, 25, 40, 0.9) !important;
        border: 1px solid rgba(100, 110, 140, 0.2);
        border-radius: 14px;
        color: #e2e8f0;
        padding: 0.875rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(102, 126, 234, 0.5);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        background: rgba(20, 25, 40, 1) !important;
    }
    
    /* Progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Dividers */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(100, 110, 140, 0.2) 50%, transparent 100%);
        margin: 2rem 0;
    }
    
    /* Checkboxes */
    .stCheckbox {
        padding: 0.5rem;
        border-radius: 10px;
        transition: all 0.2s ease;
    }
    
    .stCheckbox:hover {
        background: rgba(100, 110, 140, 0.08);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(20, 25, 40, 0.8);
        border-radius: 14px;
        border: 1px solid rgba(100, 110, 140, 0.15);
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: rgba(100, 110, 140, 0.25);
        background: rgba(20, 25, 40, 0.95);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
        border-bottom: 1px solid rgba(100, 110, 140, 0.15);
        padding-bottom: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        background: transparent;
        color: #94a3b8;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(102, 126, 234, 0.15);
        color: #e2e8f0;
        border-bottom: 2px solid #667eea;
    }
    
    /* Sidebar - Creative design */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1419 0%, #0a0e1a 100%);
        border-right: 1px solid rgba(100, 110, 140, 0.15);
    }
    
    section[data-testid="stSidebar"] > div {
        padding-top: 2rem;
    }
    
    /* Sidebar header styling */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #e2e8f0;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border-left: 3px solid #667eea;
        margin-left: 1rem;
    }
    
    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        text-align: left;
        justify-content: flex-start;
        background: rgba(20, 25, 40, 0.6);
        margin: 0.25rem 0;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(102, 126, 234, 0.15);
        transform: translateX(4px);
    }
    
    /* Success/Error/Warning messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 14px;
        border-left: 3px solid;
        padding: 1rem 1.25rem;
        backdrop-filter: blur(10px);
    }
    
    .stSuccess {
        background: rgba(52, 211, 153, 0.08);
        border-left-color: #34d399;
    }
    
    .stError {
        background: rgba(248, 113, 113, 0.08);
        border-left-color: #f87171;
    }
    
    .stWarning {
        background: rgba(251, 191, 36, 0.08);
        border-left-color: #fbbf24;
    }
    
    .stInfo {
        background: rgba(102, 126, 234, 0.08);
        border-left-color: #667eea;
    }
    
    /* Chat messages */
    .stChatMessage {
        background: rgba(20, 25, 40, 0.8);
        border-radius: 16px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(100, 110, 140, 0.15);
        backdrop-filter: blur(10px);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Smooth fade-in animation */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .main > div {
        animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0e1a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #7c8ef0 0%, #8659b0 100%);
    }
    
    /* Form styling */
    .stForm {
        background: rgba(20, 25, 40, 0.6);
        border: 1px solid rgba(100, 110, 140, 0.15);
        border-radius: 20px;
        padding: 2rem;
    }
    
    /* Title styling */
    h1 {
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    h2, h3 {
        font-weight: 600;
        letter-spacing: -0.01em;
    }
</style>
"""

def apply_custom_css():
    """Apply custom CSS to the Streamlit app"""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
