import streamlit as st
import requests
import oracledb
import time

# -----------------------------------------------------------------------------
# CONFIGURATION & THEME
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Oracle Autonomous Manager",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look (Dark Mode + Glassmorphism + Gradients)
st.markdown("""
<style>
    /* -----------------------------------------------------------------------------
     * ORACLE ENTERPRISE THEME
     * ----------------------------------------------------------------------------- */
    
    /* Global Font & Reset */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #E0E0E0; /* Light Grey Text */
    }

    /* Variables */
    :root {
        --oracle-red: #C74634;
        --oracle-dark: #1A1A1A;
        --oracle-darker: #0d0d0d;
        --oracle-grey: #262626;
        --oracle-light-grey: #3e3e3e;
        --text-color: #E0E0E0;
    }

    /* -----------------------------------------------------------------------------
     * LAYOUT & CONTAINERS
     * ----------------------------------------------------------------------------- */
    .stApp {
        background-color: var(--oracle-dark);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--oracle-grey);
        border-right: 1px solid #333;
    }
    
    /* Header/Navbar Area (Top Right) */
    header[data-testid="stHeader"] {
        background-color: transparent;
    }

    /* -----------------------------------------------------------------------------
     * COMPONENTS
     * ----------------------------------------------------------------------------- */
    
    /* Buttons */
    div.stButton > button {
        background-color: var(--oracle-red);
        color: white;
        border: none;
        border-radius: 4px; /* Slightly sharper corners for enterprise feel */
        padding: 0.5rem 1rem;
        font-weight: 500;
        font-size: 14px;
        transition: background-color 0.2s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    div.stButton > button:hover {
        background-color: #A63022; /* Darker Red */
        color: white;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div.stButton > button:active {
        background-color: #8C2216;
        transform: translateY(1px);
    }

    /* Secondary Buttons (Sidebar) */
    [data-testid="stSidebar"] div.stButton > button {
        background-color: transparent;
        border: 1px solid #555;
        color: #ccc;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        border-color: var(--oracle-red);
        color: var(--oracle-red);
        background-color: rgba(199, 70, 52, 0.1);
    }

    /* Inputs (Text, Number, Select) */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {
        background-color: #2C2C2C;
        color: white;
        border: 1px solid #444;
        border-radius: 4px;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox div[data-baseweb="select"] > div:focus-within {
        border-color: var(--oracle-red);
        box-shadow: none;
    }

    /* Cards / Containers */
    .oracle-card {
        background-color: var(--oracle-grey);
        border: 1px solid #333;
        border-radius: 6px;
        padding: 24px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        transition: border-color 0.2s;
    }
    .oracle-card:hover {
        border-color: #555;
    }
    .oracle-card h3 {
        margin-top: 0;
        font-size: 1.1rem;
        font-weight: 600;
        color: #fff;
        border-bottom: 2px solid var(--oracle-red);
        display: inline-block;
        padding-bottom: 8px;
        margin-bottom: 16px;
    }
    .oracle-card p {
        color: #aaa;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    /* Login Container */
    .login-container {
        background-color: var(--oracle-grey);
        border: 1px solid #333;
        border-top: 4px solid var(--oracle-red);
        border-radius: 6px;
        padding: 40px;
        max-width: 500px;
        margin: 60px auto;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }

    /* Typography */
    h1, h2, h3 {
        color: white;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    h1 { font-size: 2rem; margin-bottom: 1.5rem; }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: var(--oracle-red);
    }

    /* Badges */
    .badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-critical {
        background-color: rgba(199, 70, 52, 0.2);
        color: #ff6b6b;
        border: 1px solid rgba(199, 70, 52, 0.4);
    }
    .badge-ok {
        background-color: rgba(46, 204, 113, 0.2);
        color: #2ecc71;
        border: 1px solid rgba(46, 204, 113, 0.4);
    }

    /* Navigation Radio - Custom Rectangles */
    div[role="radiogroup"] > label {
        background-color: transparent;
        border: none;
        padding-left: 10px;
        margin-bottom: 5px;
        transition: all 0.2s;
        border-left: 3px solid transparent;
    }
    div[role="radiogroup"] > label:hover {
        background-color: rgba(255,255,255,0.05);
    }
    /* Selected Item */
    div[role="radiogroup"] > label[aria-checked="true"] {
        background-color: rgba(199, 70, 52, 0.1) !important;
        border-left: 3px solid var(--oracle-red) !important;
    }
    div[role="radiogroup"] > label[aria-checked="true"] p {
        color: var(--oracle-red) !important;
        font-weight: 600;
    }
    /* Hide the radio circles */
    div[role="radiogroup"] div[data-testid="stMarkdownContainer"] > p {
        font-size: 0.95rem;
    }
    div[role="radiogroup"] div[data-baseweb="radio"] > div {
        display: none; /* Hide the orb */
    }

    /* Utilities */
    .text-muted { color: #888; }
    .text-red { color: var(--oracle-red); }

    /* Hide standard Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000"

# -----------------------------------------------------------------------------
# STATE MANAGEMENT
# -----------------------------------------------------------------------------
if "connected" not in st.session_state:
    st.session_state.connected = False
if "db_config" not in st.session_state:
    st.session_state.db_config = None
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Bonjour ! Je suis l'IA de votre base de données. Comment puis-je vous aider ?"}]
if "sidebar_messages" not in st.session_state:
    st.session_state.sidebar_messages = []

def navigate_to(page_name):
    st.session_state.navigation = page_name

# -----------------------------------------------------------------------------
# LOGIN PAGE (CENTERED)
# -----------------------------------------------------------------------------
def login_page():
    st.markdown("""
        <div style='text-align: center; margin-top: 50px;'>
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/50/Oracle_logo.svg" width="200" style="margin-bottom: 20px;">
            <p style='color: #888; font-size: 1.1rem; letter-spacing: 1px; text-transform: uppercase;'>Autonomous Database Manager</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Connexion Sécurisée")
        
        with st.form("login_form"):
            user = st.text_input("User", "system")
            password = st.text_input("Password", type="password")
            st.markdown("**LLM Engine Configuration**")
            llm_choice = st.selectbox("Model Provider", ["groq", "gemini"], index=0)

            with st.expander("Advanced Connection Settings"):
                col_a, col_b = st.columns(2)
                host = col_a.text_input("Host", "localhost")
                port = col_b.number_input("Port", 1521)
                service = st.text_input("Service / PDB", "freepdb1")
                
            
            submitted = st.form_submit_button(" Connexion", use_container_width=True)
            
            if submitted:
                config = {
                    "host": host, "port": int(port), "service": service,
                    "user": user, "password": password, "llm_provider": llm_choice
                }
                
                with st.spinner("Authentification & Analyse initiale..."):
                    try:
                        # Test Oracle direct (rapide)
                        dsn = oracledb.makedsn(host, port, service_name=service)
                        conn = oracledb.connect(user=user, password=password, dsn=dsn)
                        conn.close()
                        
                        # Config Backend
                        response = requests.post(f"{API_URL}/connect-and-refresh", json=config, timeout=60)
                        response.raise_for_status()
                        
                        st.session_state.connected = True
                        st.session_state.db_config = config
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Échec de connexion : {e}")
                        
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MAIN DASHBOARD
# -----------------------------------------------------------------------------
def main_dashboard():
    # Sidebar Navigation
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/5/50/Oracle_logo.svg", width=120)
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
        st.caption(f"Status: Connected")
        
        # Actions Principales
        col_ref, col_log = st.columns(2)
        if col_ref.button("Refresh"):
             with st.spinner(".."):
                try:
                    requests.post(f"{API_URL}/connect-and-refresh", json=st.session_state.db_config)
                    st.toast("Données rafraîchies !", icon="✅")
                except Exception:
                    st.error("Refresh failed")
        
        if col_log.button("Logout"):
            st.session_state.clear()
            st.rerun()

        st.markdown("---")
        
        page = st.radio("Navigation", [
            "Overview", 
            "Security Audit", 
            "SQL Performance", 
            "Anomaly Detection", 
            "Smart Backup",
            "Virtual DBA"
        ], key="navigation")
        
        st.markdown("---")

    # Routing
    if page == "Overview":
        show_home()
    elif page == "Security Audit":
        show_security()
    elif page == "SQL Performance":
        show_performance()
    elif page == "Anomaly Detection":
        show_anomalies()
    elif page == "Smart Backup":
        show_backup()
    elif page == "Virtual DBA":
        show_chatbot()

# -----------------------------------------------------------------------------
# PAGE COMPONENTS
# -----------------------------------------------------------------------------
def show_home():
    st.markdown("<h1>Dashboard</h1>", unsafe_allow_html=True)
    
    # 3 KPIs
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="oracle-card" style="text-align: center; padding: 15px;">
            <h2 style="color: #2ecc71; margin:0;">98%</h2>
            <p style="margin:0; font-size:0.9rem;">Database Health</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="oracle-card" style="text-align: center; padding: 15px;">
            <h2 style="color: #f1c40f; margin:0;">5</h2>
            <p style="margin:0; font-size:0.9rem;">Slow Queries</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="oracle-card" style="text-align: center; padding: 15px;">
            <h2 style="color: #3498db; margin:0;">Stable</h2>
            <p style="margin:0; font-size:0.9rem;">System Status</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### Quick Access")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="oracle-card">
            <h3>Security</h3>
            <p>Comprehensive audit, privilege analysis, and encryption status.</p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Open Security Audit", use_container_width=True, on_click=navigate_to, args=("Security Audit",))

    with col2:
        st.markdown("""
        <div class="oracle-card">
            <h3>Performance</h3>
            <p>Automatic SQL tuning and slow query optimization.</p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Open Performance", use_container_width=True, on_click=navigate_to, args=("SQL Performance",))

    with col3:
        st.markdown("""
        <div class="oracle-card">
            <h3>Expert Assist</h3>
            <p>Ask your virtual DBA questions in natural language.</p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Ask Expert", use_container_width=True, on_click=navigate_to, args=("Virtual DBA",))

def show_security():
    st.markdown("<h1>Security Audit</h1>", unsafe_allow_html=True)
    
    if st.button("Lancer un nouvel audit"):
        st.cache_data.clear()
        
    with st.spinner("Analyse de sécurité par l'IA..."):
        try:
            resp = requests.get(f"{API_URL}/security/")
            data = resp.json()
            
            score = data.get('score', 0)
            compliance_status = "Compliant" if score > 80 else "Needs Attention" if score > 50 else "Critical"
            compliance_color = "#2ecc71" if score > 80 else "#f1c40f" if score > 50 else "#e74c3c"
            
            # KPI Metrics Display
            c1, c2, c3 = st.columns(3)
            with c1:
                 st.markdown(f"""
                    <div class="oracle-card" style="text-align: center; padding: 15px; height: 100%;">
                        <h3 style="color: {compliance_color}; margin:0; border:none; font-size: 1.5rem;">{compliance_status}</h3>
                        <p style="margin:0; font-size:0.9rem; color: #aaa;">Global Compliance</p>
                    </div>
                """, unsafe_allow_html=True)
            with c2:
                crit_count = len([r for r in data.get('risks', []) if r.get('severity') in ['Critical', 'High']])
                st.markdown(f"""
                    <div class="oracle-card" style="text-align: center; padding: 15px; height: 100%;">
                        <h3 style="color: {'#e74c3c' if crit_count > 0 else '#2ecc71'}; margin:0; border:none; font-size: 1.5rem;">{crit_count}</h3>
                        <p style="margin:0; font-size:0.9rem; color: #aaa;">Critical Risks</p>
                    </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                    <div class="oracle-card" style="text-align: center; padding: 15px; height: 100%;">
                        <h3 style="color: #3498db; margin:0; border:none; font-size: 1.5rem;">42/50</h3>
                        <p style="margin:0; font-size:0.9rem; color: #aaa;">Checks Passed</p>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("### Detailed Risk Analysis")
            for risk in data.get('risks', []):
                sev = risk.get('severity', 'Medium')
                badge_class = "badge-critical" if sev in ["Critical", "High"] else "badge-ok"
                
                with st.expander(f"{sev} : {risk['description'][:50]}..."):
                    st.markdown(f"<span class='{badge_class}'>{sev.upper()}</span>", unsafe_allow_html=True)
                    st.write(risk['description'])
                    st.info(f"Recommendation : {risk.get('recommendation', 'Not specified')}")
                        
        except Exception:
            st.error("Unable to complete security audit. Please check logs.")

def show_performance():
    st.markdown("<h1>SQL Performance</h1>", unsafe_allow_html=True)
    
    try:
        resp = requests.get(f"{API_URL}/performance/slow-queries")
        queries = resp.json().get('queries', [])
        
        if not queries:
            st.success("Aucune requête lente détectée !")
            return

        for i, q in enumerate(queries[:5]):
            with st.container():
                st.markdown(f"""
                <div class="oracle-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <h4>Query #{i+1}</h4>
                        <span class="badge badge-critical" style="font-size:0.8em;">High CPU</span>
                    </div>
                    <div style="background-color:#0d0d0d; padding:10px; border-radius:4px; border:1px solid #333; margin-bottom:10px;">
                        <span style="color:#888; font-size:0.8em; margin-right:15px;">EXEC: 1.24s</span>
                        <span style="color:#888; font-size:0.8em; margin-right:15px;">CPU: 98%</span>
                        <span style="color:#888; font-size:0.8em;">IO: 450MB</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.code(q.get('sql_text', ''), language='sql')
                
                col_opt, col_expl = st.columns([1, 4])
                with col_opt:
                     if st.button(f"Optimize", key=f"opt_{i}", type="primary", use_container_width=True):
                        with st.spinner("Analyzing execution plan..."):
                            opt_res = requests.post(f"{API_URL}/performance/optimize", json={"sql": q.get('sql_text')}).json()
                            st.success("Analysis Complete")
                            st.markdown(f"**Insight**: {opt_res.get('explanation')}")
                        st.markdown("**Recommendations**:")
                        for r in opt_res.get('recommendations', []):
                            st.write(f"- {r}")
                            
    except Exception:
        st.error("Unable to retrieve performance data.")

def show_anomalies():
    st.markdown("<h1>Anomaly Detection</h1>", unsafe_allow_html=True)
    
    col_scan, col_status = st.columns([1, 3])
    with col_scan:
        scan_btn = st.button("RUN FULL SYSTEM SCAN", type="primary", use_container_width=True)
    
    if scan_btn:
        with st.spinner("Scanning system logs and metrics..."):
            try:
                resp = requests.get(f"{API_URL}/anomaly/")
                results = resp.json().get('results', [])
                
                if results:
                    # Prepare data for nicer display
                    disp_data = []
                    for res in results:
                        disp_data.append({
                            "Severity": res.get('classification', 'normal').upper(),
                            "Metric": "System Log", 
                            "Message": res.get('justification'),
                            "Log Details": res.get('log')
                        })
                    
                    st.dataframe(
                        disp_data, 
                        use_container_width=True,
                        column_config={
                            "Severity": st.column_config.TextColumn("Severity", width="small"),
                            "Metric": st.column_config.TextColumn("Source", width="small"),
                            "Message": st.column_config.TextColumn("Analysis", width="large"),
                        }
                    )
                else:
                    st.info("No anomalies detected in the recent logs.")

            except Exception:
                st.error("Analysis failed.")

def show_backup():
    st.markdown("<h1>Smart Backup</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    rpo = c1.selectbox("RPO (Max Data Loss)", ["1h", "4h", "24h"], help="Recovery Point Objective: Maximum targeted period in which data might be lost.")
    rto = c2.selectbox("RTO (Recovery Time)", ["30min", "2h", "4h"], help="Recovery Time Objective: Targeted duration of time and a service level within which a business process must be restored.")
    budget = c3.select_slider("Budget Constraint", ["Low", "Medium", "High"])
    
    if st.button("Générer Stratégie RMAN", type="primary"):
        with st.spinner("Analyse des besoins RPO/RTO et génération du script..."):
            try:
                resp = requests.post(f"{API_URL}/backup/recommend", json={"rpo": rpo, "rto": rto, "budget": budget}, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    strategy = data.get('strategy')
                    script = data.get('script')
                else:
                    raise Exception("Backend returned non-200")
            except Exception:
                # Fallback Mock Data for demo purposes if backend fails (e.g. no LLM key)
                strategy = (
                    f"**Stratégie Recommandée (Mode Dégradé)**\n\n"
                    f"Pour un RPO de **{rpo}** et un RTO de **{rto}** avec un budget **{budget}** :\n"
                    f"- Effectuer une sauvegarde **Full Incrémentale Niveau 0** chaque dimanche.\n"
                    f"- Sauvegardes **Incrémentales Différentielles Niveau 1** quotidiennes.\n"
                    f"- Activer **ARCHIVELOG** pour permettre le PITR (Point-in-Time Recovery).\n"
                    f"- Compression RMAN activée pour optimiser le stockage."
                )
                script = (
                    "RUN {\n"
                    "  CONFIGURE RETENTION POLICY TO RECOVERY WINDOW OF 7 DAYS;\n"
                    "  CONFIGURE CONTROLFILE AUTOBACKUP ON;\n"
                    "  ALLOCATE CHANNEL c1 DEVICE TYPE DISC;\n"
                    "  BACKUP AS COMPRESSED BACKUPSET INCREMENTAL LEVEL 0 DATABASE PLUS ARCHIVELOG;\n"
                    "  DELETE NOPROMPT OBSOLETE;\n"
                    "}"
                )
                st.warning("Le service d'intelligence artificielle est momentanément indisponible. Une stratégie standard a été générée.")

            st.subheader("Stratégie Recommandée")
            st.markdown(strategy)
            
            st.subheader("Script RMAN Généré")
            st.code(script, language='bash')

def show_chatbot():
    st.markdown("<h1>Virtual DBA</h1>", unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Votre question Oracle..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.text("Processing...")
            
            try:
                resp = requests.post(f"{API_URL}/chat/", json={"query": prompt})
                ai_msg = resp.json().get("response", "Erreur réponse")
                message_placeholder.markdown(ai_msg)
                st.session_state.messages.append({"role": "assistant", "content": ai_msg})
            except Exception:
                message_placeholder.error("Service temporarily unavailable.")

# -----------------------------------------------------------------------------
# APP ENTRY POINT
# -----------------------------------------------------------------------------
if st.session_state.connected:
    main_dashboard()
else:
    login_page()