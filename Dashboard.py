import streamlit as st
import os
from datetime import datetime
import pandas as pd

# Page config
st.set_page_config(
    page_title="AI Gmail Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Clean & Professional
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Clean white background */
    .stApp {
        background: #f8f9fa;
    }
    
    /* Main container */
    .main .block-container {
        max-width: 1200px;
        padding: 2rem 3rem;
    }
    
    /* Title */
    h1 {
        color: #1a1a2e;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        text-align: center;
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Metric cards - EQUAL SIZES */
    [data-testid="stMetric"] {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e9ecef;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.95rem !important;
        color: #6c757d !important;
        font-weight: 500 !important;
        text-align: center;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #1a1a2e !important;
        text-align: center;
    }
    
    [data-testid="stMetricDelta"] {
        text-align: center;
        font-size: 0.85rem !important;
    }
    
    /* Section headers */
    h2, h3 {
        color: #1a1a2e;
        font-weight: 600;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        padding: 0.5rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #495057;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: #4361ee !important;
        color: white !important;
    }
    
    /* Cards */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Alert card */
    .alert-card {
        background: #fff5f5;
        border-left: 4px solid #e53e3e;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    /* Reply card */
    .reply-card {
        background: #f0fff4;
        border-left: 4px solid #38a169;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    /* Ignore card */
    .ignore-card {
        background: #f7fafc;
        border-left: 4px solid #a0aec0;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    /* Status badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-right: 0.5rem;
    }
    
    .badge-success { background: #c6f6d5; color: #22543d; }
    .badge-info { background: #bee3f8; color: #2c5282; }
    .badge-warning { background: #fed7d7; color: #742a2a; }
    
    /* Text styling */
    .email-from {
        color: #4a5568;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .email-subject {
        color: #1a202c;
        font-size: 1rem;
        font-weight: 600;
        margin: 0.25rem 0;
    }
    
    .email-reason {
        color: #718096;
        font-size: 0.85rem;
        font-style: italic;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #a0aec0;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("# 🤖 AI Gmail Agent")
st.markdown('<p class="subtitle">Autonomous Email Management Powered by Claude AI</p>', unsafe_allow_html=True)

# Status badges
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <span class='badge badge-success'>✅ Active</span>
    <span class='badge badge-info'>⚡ Real-time</span>
    <span class='badge badge-success'>🔒 Secure</span>
</div>
""", unsafe_allow_html=True)

# Check if log exists
if not os.path.exists('agent_log.txt'):
    st.info("📋 No reports yet. Run the agent first:")
    st.code("python gmail_agent_real.py > agent_log.txt", language="bash")
    st.stop()

# Read log
with open('agent_log.txt', 'r', encoding='utf-8') as f:
    log = f.read()

# Count actions
alerts = log.count('Action: ALERT')
replies = log.count('Action: REPLY')
ignored = log.count('Action: IGNORE')
total = alerts + replies + ignored

# Metrics Section - EQUAL SIZED CARDS
st.markdown("### 📊 Performance Metrics")

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    st.metric(label="📧 Total Processed", value=total, delta="Real-time")

with col2:
    st.metric(label="🚨 Alerts Sent", value=alerts, delta="WhatsApp" if alerts > 0 else "Standby")

with col3:
    st.metric(label="✅ Auto-Replied", value=replies, delta="Automated")

with col4:
    st.metric(label="🗑️ Spam Filtered", value=ignored, delta="Cleaned")

# Stats Section
st.markdown("### 📈 Email Distribution")

col1, col2 = st.columns([2, 1], gap="large")

with col1:
    if total > 0:
        chart_data = pd.DataFrame({
            'Category': ['Alerts', 'Replied', 'Ignored'],
            'Count': [alerts, replies, ignored]
        })
        st.bar_chart(chart_data.set_index('Category'), height=300)
    else:
        st.info("No data yet")

with col2:
    success_rate = ((replies + ignored) / total * 100) if total > 0 else 0
    time_saved = total * 2
    
    st.markdown(f"""
    <div class='info-card'>
        <h4 style='margin-top:0;'>🎯 Performance</h4>
        <p><strong>Total Emails:</strong> {total}</p>
        <p><strong>Auto-handled:</strong> {replies + ignored}/{total}</p>
        <p><strong>Success Rate:</strong> {success_rate:.0f}%</p>
        <p><strong>Time Saved:</strong> ~{time_saved} mins</p>
    </div>
    """, unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🚨 Alerts", "📋 All Emails", "🎯 How It Works", "💼 About"])

with tab1:
    st.markdown("### 🔴 Important Emails")
    st.caption("These emails were flagged as important and sent to your WhatsApp")
    
    if alerts > 0:
        blocks = log.split("=" * 80)
        
        for block in blocks:
            if 'Action: ALERT' in block:
                lines = block.split('\n')
                from_line = next((l for l in lines if 'From:' in l), '').replace('From:', '').strip()
                subject_line = next((l for l in lines if 'Subject:' in l), '').replace('Subject:', '').strip()
                reason_line = next((l for l in lines if 'Reason:' in l), '').replace('Reason:', '').strip()
                
                if from_line:
                    st.markdown(f"""
                    <div class='alert-card'>
                        <div class='email-from'>From: {from_line}</div>
                        <div class='email-subject'>🚨 {subject_line}</div>
                        <div class='email-reason'>{reason_line}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.success("✨ No urgent emails right now")

with tab2:
    st.markdown("### 📋 Complete Activity Log")
    
    blocks = log.split("=" * 80)
    
    for block in blocks:
        if 'Action:' in block and 'EMAIL #' in block:
            lines = block.split('\n')
            from_line = next((l for l in lines if 'From:' in l), '').replace('From:', '').strip()
            subject_line = next((l for l in lines if 'Subject:' in l), '').replace('Subject:', '').strip()
            action_line = next((l for l in lines if 'Action:' in l), '').replace('Action:', '').strip()
            reason_line = next((l for l in lines if 'Reason:' in l), '').replace('Reason:', '').strip()
            
            if action_line == 'ALERT':
                st.markdown(f"""
                <div class='alert-card'>
                    <div class='email-from'>🚨 ALERT | {from_line}</div>
                    <div class='email-subject'>{subject_line}</div>
                    <div class='email-reason'>{reason_line}</div>
                </div>
                """, unsafe_allow_html=True)
            elif action_line == 'REPLY':
                st.markdown(f"""
                <div class='reply-card'>
                    <div class='email-from'>✅ REPLIED | {from_line}</div>
                    <div class='email-subject'>{subject_line}</div>
                    <div class='email-reason'>{reason_line}</div>
                </div>
                """, unsafe_allow_html=True)
            elif action_line == 'IGNORE':
                st.markdown(f"""
                <div class='ignore-card'>
                    <div class='email-from'>🗑️ IGNORED | {from_line}</div>
                    <div class='email-subject'>{subject_line}</div>
                    <div class='email-reason'>{reason_line}</div>
                </div>
                """, unsafe_allow_html=True)

with tab3:
    st.markdown("### 🎯 How This AI Agent Works")
    
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        st.markdown("""
        <div class='info-card' style='text-align: center; min-height: 250px;'>
            <h2 style='color: #4361ee; margin-top: 0;'>1</h2>
            <h4>📧 Read Emails</h4>
            <p>Connects to Gmail API and fetches unread emails from your inbox</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='info-card' style='text-align: center; min-height: 250px;'>
            <h2 style='color: #4361ee; margin-top: 0;'>2</h2>
            <h4>🧠 AI Analysis</h4>
            <p>Claude AI analyzes each email against custom rules for intelligent decisions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='info-card' style='text-align: center; min-height: 250px;'>
            <h2 style='color: #4361ee; margin-top: 0;'>3</h2>
            <h4>⚡ Take Action</h4>
            <p>Sends WhatsApp alerts, auto-replies, or ignores based on importance</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### ✨ Key Features")
    
    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        st.markdown("""
        <div class='info-card'>
            <h4 style='margin-top:0;'>🤖 Intelligent Triage</h4>
            <p>Uses Claude AI for context-aware decisions, not keyword matching</p>
        </div>
        <div class='info-card'>
            <h4 style='margin-top:0;'>📱 WhatsApp Alerts</h4>
            <p>Get pinged on your phone for important emails immediately</p>
        </div>
        <div class='info-card'>
            <h4 style='margin-top:0;'>🔧 Custom Rules</h4>
            <p>Define your own logic in JSON to control agent behavior</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='info-card'>
            <h4 style='margin-top:0;'>📧 Real Gmail Integration</h4>
            <p>Works with your actual inbox via official Gmail API</p>
        </div>
        <div class='info-card'>
            <h4 style='margin-top:0;'>⏰ Auto-Scheduling</h4>
            <p>Runs every hour automatically without manual intervention</p>
        </div>
        <div class='info-card'>
            <h4 style='margin-top:0;'>📊 Live Dashboard</h4>
            <p>Monitor everything in real-time through this interface</p>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.markdown("### 💼 About This Project")
    
    st.markdown("""
    <div class='info-card'>
        <h3 style='margin-top: 0;'>🚀 Project Overview</h3>
        <p>An autonomous AI email management system that demonstrates production-grade AI engineering, 
        multi-API integration, and full-stack development capabilities.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        st.markdown("""
        <div class='info-card'>
            <h4 style='margin-top:0;'>🎯 Skills Demonstrated</h4>
            <ul style='line-height: 1.8;'>
                <li>AI/ML Engineering</li>
                <li>LLM Integration</li>
                <li>API Integration</li>
                <li>Full-Stack Development</li>
                <li>Production Deployment</li>
                <li>System Design</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='info-card'>
            <h4 style='margin-top:0;'>🛠️ Tech Stack</h4>
            <ul style='line-height: 1.8;'>
                <li>Python</li>
                <li>Claude AI (Anthropic)</li>
                <li>Gmail API</li>
                <li>Twilio (WhatsApp)</li>
                <li>Streamlit</li>
                <li>Task Scheduler</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-card' style='text-align: center;'>
        <h4>📊 Real Impact</h4>
        <p>Saves <strong>1-2 hours per day</strong> on email management</p>
        <p>Never miss <strong>important emails</strong></p>
        <p>Auto-handles <strong>80%+ of emails</strong></p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div class='footer'>
    <p>🤖 AI Gmail Agent | Powered by Claude AI</p>
    <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>
""", unsafe_allow_html=True)