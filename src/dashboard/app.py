import streamlit as st

st.set_page_config(
    page_title="Nifty 100 Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📈 Nifty 100 Analytics Dashboard")

st.sidebar.title("Navigation")

pages = {
    "🏠 Home": "pages/01_home.py",
    "🏢 Company Profile": "pages/02_profile.py",
    "🔍 Screener": "pages/03_screener.py",
    "👥 Peer Analysis": "pages/04_peers.py",
    "📈 Trends": "pages/05_trends.py",
    "🏭 Sectors": "pages/06_sectors.py",
    "💰 Capital Allocation": "pages/07_capital.py",
    "📄 Reports": "pages/08_reports.py",
}

choice = st.sidebar.radio(
    "Select Screen",
    list(pages.keys())
)

st.info(
    f"Selected: {choice}\n\n"
    "Use the Pages menu (left sidebar) to open the corresponding screen."
)

st.markdown("---")

st.markdown("""
### Dashboard Modules

- Home
- Company Profile
- Screener
- Peer Analysis
- Trends
- Sector Analytics
- Capital Allocation
- Reports
""")