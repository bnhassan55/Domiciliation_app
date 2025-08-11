import streamlit as st
from datetime import datetime
import time

# Dictionnaire des utilisateurs (username: password)
USERS = {
    "admin": "admin123",
    "user1": "password123",
    "manager": "manager456"
}

def verify_credentials(username, password):
    """Vérification des identifiants avec le dictionnaire"""
    return username in USERS and USERS[username] == password

def login_page():
    """Interface de connexion principale"""
    
    # CSS personnalisé pour la page de login
    st.markdown("""
    <style>
        /* STYLE GARANTI POUR LE BOUTON */
        div.stButton > button:first-child {
            background: rgb(237, 225, 207) !important;
            color: #333 !important;
            border: 1px solid rgb(210, 195, 170) !important;
            border-radius: 12px !important;
            padding: 12px 24px !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }
        
        div.stButton > button:hover {
            background: rgb(225, 210, 190) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
        }
        
        div.stButton > button:active {
            transform: translateY(0) !important;
        }
        /* Masquer l'en-tête complet */
        [data-testid="stHeader"] {
            display: none !important;
        }
        
        /* Masquer l'espace réservé de l'en-tête */
        .stApp > header {
            display: none !important;
        }
        
        /* Supprimer l'espace vide laissé par l'en-tête */
        .stApp > .block-container {
            padding-top: 0rem !important;
        }
        
        /* Masquer le menu burger */
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        
        /* Masquer le footer */
        footer {
            visibility: hidden !important;
        }
        
        /* Masquer le bouton "Made with Streamlit" */
        .stApp > footer:after {
            content: "" !important;     

        /* Container principal */
        .login-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Carte de connexion */
        .login-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        /* Logo et titre */
        /* Styles pour centrer le contenu */
        .login-header {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-bottom: 30px;
        }
        
        .login-title {
            color: #333;
            font-size: 28px;
            font-weight: 700;
            margin: 15px 0 10px 0;
            text-align: center;
            width: 100%;
        }
        
        .login-subtitle {
            color: #666;
            font-size: 16px;
            margin-bottom: 30px;
            text-align: center;
            width: 100%;
        }
        
        /* Style des champs de saisie */
        .stTextInput > div > div > input {
            border-radius: 12px;
            border: 2px solid #e1e5e9;
            padding: 12px 16px;
            font-size: 16px;
            background: #f8f9fa;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            background: white;
        }
        
        
        /* Messages d'erreur et de succès */
        .login-message {
            padding: 12px;
            border-radius: 8px;
            margin: 15px 0;
            font-weight: 500;
        }
        
        .error-message {
            background: #fee;
            color: #c53030;
            border: 1px solid #fed7d7;
        }
        
        .success-message {
            background: #f0fff4;
            color: #2d7d32;
            border: 1px solid #c6f6d5;
        }
        
        /* Animation de chargement */
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Footer */
        .login-footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e1e5e9;
            color: #666;
            font-size: 14px;
        }
        
        /* Icône de l'entreprise */
        .company-icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .login-card {
                margin: 20px;
                padding: 30px 20px;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Container principal
    
    # Créer les colonnes pour centrer la carte
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        # Header avec logo et titre
        st.markdown("""
        <div class="login-header">
            <h1 class="login-title">connexion</h1>
            <p class="login-subtitle">Connectez-vous à votre espace</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Formulaire de connexion
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Nom d'utilisateur",
                placeholder="Entrez votre nom d'utilisateur",
                key="username_input"
            )
            
            password = st.text_input(
                "Mot de passe",
                type="password",
                placeholder="Entrez votre mot de passe",
                key="password_input"
            )
            
            # Espacement
            st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
            
            # Bouton de connexion
            login_button = st.form_submit_button("Se connecter")
            
            if login_button:
                if username and password:
                    # Afficher un spinner de chargement
                    with st.spinner("Vérification des identifiants..."):
                        time.sleep(0.3)  # Simulation du temps de traitement
                        
                        # Vérifier les identifiants
                        if verify_credentials(username, password):
                            # Connexion réussie
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.login_time = datetime.now()
                            
                            st.success("Connexion réussie ! Redirection en cours...")
                            time.sleep(1)
                            st.rerun()
                            
                        else:
                            st.error(" Nom d'utilisateur ou mot de passe incorrect")
                else:
                    st.warning("⚠️ Veuillez remplir tous les champs")
        
        # Section d'aide avec les comptes disponibles
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def logout():
    """Fonction de déconnexion"""
    # Nettoyer toutes les variables de session liées à l'authentification
    keys_to_remove = ['logged_in', 'username', 'login_time']
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("Déconnexion réussie !")
    st.rerun()

def is_logged_in():
    """Vérifier si l'utilisateur est connecté"""
    return st.session_state.get('logged_in', False)

def get_current_user():
    """Obtenir les informations de l'utilisateur actuel"""
    if is_logged_in():
        return {
            'username': st.session_state.get('username'),
            'login_time': st.session_state.get('login_time')
        }
    return None 