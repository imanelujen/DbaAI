import streamlit as st
import requests
import oracledb
import time

# -----------------------------------------------------------------------------
# CONFIGURATION & THEME
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Oracle AI Platform",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look (Dark Mode + Glassmorphism + Gradients)
st.markdown("""
<style>
    /* Global Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Background & Global Colors */
    .stApp {
        background: #0e1117;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0e1117;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Button Styling (Unified) */
    div.stButton > button {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        opacity: 0.9;
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4);
    }
    
    /* Sidebar Specific Buttons (Outline style for secondary actions) */
    [data-testid="stSidebar"] div.stButton > button {
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #ddd;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
         border-color: #4facfe;
         color: #4facfe;
         background: rgba(79, 172, 254, 0.1);
    }

    /* Custom Cards (Glassmorphism) */
    .premium-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
        height: 100%; /* Uniform height */
        transition: transform 0.2s;
    }
    .premium-card:hover {
        transform: translateY(-5px);
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    
    /* Inputs & Selects to match theme */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.05);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
    }

    /* Titles with Gradients */
    .gradient-text {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    /* Login Box Centered */
    .login-container {
        max-width: 450px;
        margin: 100px auto;
        padding: 40px;
        background: rgba(20, 20, 20, 0.6);
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }

    /* Status Badges */
    .badge-critical {
        background-color: rgba(255, 75, 75, 0.15);
        color: #ff6b6b;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: 600;
        border: 1px solid rgba(255, 75, 75, 0.3);
    }
    .badge-ok {
        background-color: rgba(0, 204, 102, 0.15);
        color: #2ed573;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: 600;
        border: 1px solid rgba(0, 204, 102, 0.3);
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Navigation Radio Button Style (Override default Red) */
    div[role="radiogroup"] > label > div:first-child {
        background-color: transparent !important;
        border-color: #4facfe !important;
    }
    div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
        background-color: transparent !important; 
    }
    /* The selected dot */
    div[role="radiogroup"] > label[aria-checked="true"] > div:first-child {
        background-color: #4facfe !important;
        border-color: #4facfe !important;
    }
    /* The text label when selected */
    div[role="radiogroup"] > label[aria-checked="true"] p {
        color: #4facfe !important;
        font-weight: 800 !important;
    }
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

# -----------------------------------------------------------------------------
# LOGIN PAGE (CENTERED)
# -----------------------------------------------------------------------------
def login_page():
    st.markdown("""
        <div style='text-align: center; margin-top: 50px;'>
            <h1 style='font-size: 3.5rem; margin-bottom: 0;'>🔮 Oracle AI Platform</h1>
            <p style='color: #888; font-size: 1.2rem;'>Administration Autonome & Intelligente</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        st.subheader("Connexion Sécurisée")
        
        with st.form("login_form"):
            col_a, col_b = st.columns(2)
            host = col_a.text_input("Host", "localhost")
            port = col_b.number_input("Port", 1521)
            service = st.text_input("Service / PDB", "freepdb1")
            user = st.text_input("User", "system")
            password = st.text_input("Password", type="password")
            
            st.markdown("---")
            st.markdown("**Moteur d'Intelligence Artificielle**")
            llm_choice = st.selectbox("Sélectionnez le modèle", ["groq", "gemini"], index=0, help="Groq est recommandé pour sa vitesse.")
            
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
        st.header("🔮 Oracle AI")
        st.success(f"🟢 Connecté ")
        
        # Actions Principales
        col_ref, col_log = st.columns(2)
        if col_ref.button("🔄 Refresh"):
             with st.spinner(".."):
                try:
                    requests.post(f"{API_URL}/connect-and-refresh", json=st.session_state.db_config)
                    st.toast("Données rafraîchies !", icon="✅")
                except:
                    st.error("Erreur refresh")
        
        if col_log.button("🔓 Logout"):
            st.session_state.clear()
            st.rerun()

        st.markdown("---")
        
        page = st.radio("Navigation", [
            "Accueil", 
            "Audit Sécurité", 
            "Performance SQL", 
            "Détection Anomalies", 
            "Backup Intelligent",
            "Chatbot DBA"
        ])
        
        st.markdown("---")
        
        # Quick Chat Sidebar
        with st.expander("💬 Chat Rapide", expanded=True):
            for msg in st.session_state.sidebar_messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
            
            if q_prompt := st.chat_input("Question rapide...", key="sidebar_chat"):
                st.session_state.sidebar_messages.append({"role": "user", "content": q_prompt})
                with st.chat_message("user"):
                    st.write(q_prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("..."):
                        try:
                            resp = requests.post(f"{API_URL}/chat/", json={"query": q_prompt})
                            ans = resp.json().get("response", "Erreur")
                            st.write(ans)
                            st.session_state.sidebar_messages.append({"role": "assistant", "content": ans})
                        except Exception as e:
                            st.error("Erreur API")

    # Routing
    if page == "Accueil":
        show_home()
    elif page == "Audit Sécurité":
        show_security()
    elif page == "Performance SQL":
        show_performance()
    elif page == "Détection Anomalies":
        show_anomalies()
    elif page == "Backup Intelligent":
        show_backup()
    elif page == "Chatbot DBA":
        show_chatbot()

# -----------------------------------------------------------------------------
# PAGE COMPONENTS
# -----------------------------------------------------------------------------
def show_home():
    st.markdown("<h1 class='gradient-text'>Accueil</h1>", unsafe_allow_html=True)
    
    # 3 KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Santé Base", "98%", "+2%")
    c2.metric("Requêtes Lentes", "5", "-3")
    c3.metric("Sécurité", "Score A", "Stable")
    
    st.markdown("### Accès Rapide")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="premium-card">
            <h3>🛡️ Sécurité</h3>
            <p>Audit complet, analyse des privilèges et chiffrement.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="premium-card">
            <h3>⚡ Performance</h3>
            <p>Optimisation automatique des requêtes SQL lentes.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="premium-card">
            <h3>🧠 Assistant IA</h3>
            <p>Posez vos questions en langage naturel à votre DBA virtuel.</p>
        </div>
        """, unsafe_allow_html=True)

def show_security():
    st.markdown("<h1 class='gradient-text'>Audit de Sécurité</h1>", unsafe_allow_html=True)
    
    if st.button("🔄 Lancer un nouvel audit"):
        st.cache_data.clear()
        
    with st.spinner("Analyse de sécurité par l'IA..."):
        try:
            resp = requests.get(f"{API_URL}/security/")
            data = resp.json()
            
            score = data.get('score', 0)
            st.progress(score / 100, text=f"Score de Sécurité : {score}/100")
            

            
            st.subheader("Risques Identifiés")
            for risk in data.get('risks', []):
                sev = risk.get('severity', 'Moyenne')
                badge_class = "badge-critical" if sev in ["Critique", "Haute"] else "badge-ok"
                
                with st.expander(f"{sev} : {risk['description'][:50]}..."):
                    st.markdown(f"<span class='{badge_class}'>{sev.upper()}</span>", unsafe_allow_html=True)
                    st.write(risk['description'])
                    st.info(f"💡 Recommendation : {risk.get('recommendation', 'Non spécifiée')}")
                        
        except Exception as e:
            st.error(f"Erreur audit : {e}")

def show_performance():
    st.markdown("<h1 class='gradient-text'>Performance SQL</h1>", unsafe_allow_html=True)
    
    try:
        resp = requests.get(f"{API_URL}/performance/slow-queries")
        queries = resp.json().get('queries', [])
        
        if not queries:
            st.success("Aucune requête lente détectée !")
            return

        for i, q in enumerate(queries[:5]):
            with st.container():
                st.markdown(f"""
                <div class="premium-card">
                    <h4>Requête #{i+1}</h4>
                    <code style="display:block; white-space:pre-wrap;">{q.get('sql_text', '')}</code>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"⚡ Optimiser Requête #{i+1}", key=f"opt_{i}"):
                    with st.spinner("Le LLM analyse le plan d'exécution..."):
                        opt_res = requests.post(f"{API_URL}/performance/optimize", json={"sql": q.get('sql_text')}).json()
                        st.success("Analyse terminée")
                        st.markdown(f"**Explication**: {opt_res.get('explanation')}")
                        st.markdown("**Recommandations**:")
                        for r in opt_res.get('recommendations', []):
                            st.write(f"- {r}")
                            
    except Exception as e:
        st.error(f"Erreur API : {e}")

def show_anomalies():
    st.markdown("<h1 class='gradient-text'>Détection d'Anomalies (IA)</h1>", unsafe_allow_html=True)
    
    if st.button("🔍 Scanner les logs récents"):
        with st.spinner("Analyse des logs par batch..."):
            try:
                resp = requests.get(f"{API_URL}/anomaly/")
                results = resp.json().get('results', [])
                
                for res in results:
                    cls = res.get('classification', 'normal')
                    color = "#ff4b4b" if cls == "critique" else "#ffa421" if cls == "suspect" else "#00cc66"
                    
                    st.markdown(f"""
                    <div style="border-left: 5px solid {color}; padding-left: 15px; margin-bottom: 20px;">
                        <h4 style="color:{color}">{cls.upper()}</h4>
                        <p><b>Justification :</b> {res.get('justification')}</p>
                        <small>Log: {res.get('log')}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"Erreur : {e}")

def show_backup():
    st.markdown("<h1 class='gradient-text'>Backup Intelligent</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    rpo = c1.selectbox("RPO (Perte admissible)", ["1h", "4h", "24h"])
    rto = c2.selectbox("RTO (Temps rétablissement)", ["30min", "2h", "4h"])
    budget = c3.select_slider("Budget Stockage", ["Low", "Medium", "High"])
    
    if st.button("Générer Stratégie RMAN"):
        with st.spinner("Génération..."):
            try:
                resp = requests.post(f"{API_URL}/backup/recommend", json={"rpo": rpo, "rto": rto, "budget": budget})
                data = resp.json()
                
                st.subheader("Stratégie Recommandée")
                st.info(data.get('strategy'))
                
                st.subheader("Script RMAN Généré")
                st.code(data.get('script'), language='bash')
            except Exception as e:
                st.error(f"Erreur : {e}")

def show_chatbot():
    st.markdown("<h1 class='gradient-text'>Assistant DBA</h1>", unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Votre question Oracle..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.text("Réflexion...")
            
            try:
                resp = requests.post(f"{API_URL}/chat/", json={"query": prompt})
                ai_msg = resp.json().get("response", "Erreur réponse")
                message_placeholder.markdown(ai_msg)
                st.session_state.messages.append({"role": "assistant", "content": ai_msg})
            except Exception as e:
                message_placeholder.error(f"Erreur : {e}")

# -----------------------------------------------------------------------------
# APP ENTRY POINT
# -----------------------------------------------------------------------------
if st.session_state.connected:
    main_dashboard()
else:
    login_page()