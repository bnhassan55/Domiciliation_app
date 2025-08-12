import streamlit as st
from datetime import datetime
import time
import hashlib
import os


# Dictionnaire des utilisateurs (username: password)
USERS = {
    "admin": "admin123",
    "user1": "password123",
    "manager": "manager456"
}

SESSION_FILE = ".streamlit_session.txt"
# Dans votre fichier login.py, modifiez les fonctions de session :

def save_session(username, current_page="Accueil"):
    """Sauvegarder la session dans un fichier local"""
    try:
        session_data = f"{username}|{int(time.time())}|{current_page}"
        with open(SESSION_FILE, 'w') as f:
            f.write(session_data)
    except Exception as e:
        pass  # Ignorer les erreurs de fichier

def load_session():
    """Charge la session avec gestion d'erreurs améliorée"""
    try:
        if not os.path.exists(SESSION_FILE):
            return None, "Accueil"
            
        with open(SESSION_FILE, 'r') as f:
            data = f.read().strip()
            if not data:
                return None, "Accueil"
                
            parts = data.split('|')
            if len(parts) < 2:
                return None, "Accueil"
                
            username = parts[0]
            timestamp = parts[1]
            current_page = parts[2] if len(parts) > 2 else "Accueil"
            
            # Vérification expiration (24h)
            if int(time.time()) - int(timestamp) > 86400:
                clear_session()  # Nettoie les sessions expirées
                return None, "Accueil"
                
            return username, current_page
            
    except Exception as e:
        print(f"Erreur lecture session: {e}")
        clear_session()  # Nettoie en cas d'erreur
        return None, "Accueil"

def clear_session():
    """Supprimer complètement le fichier de session"""
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        return True
    except Exception as e:
        print(f"Erreur suppression session: {e}")
        return False

def logout_user():
    """Fonction de déconnexion complète"""
    # 1. Supprimer le fichier de session
    clear_session()
    
    # 2. Réinitialiser complètement le session_state
    st.session_state.clear()
    
    # 3. Forcer le rechargement complet
    st.rerun()

def verify_credentials(username, password):
    """Vérification des identifiants avec le dictionnaire"""
    return username in USERS and USERS[username] == password



def login_page():
    """Interface de connexion principale"""
    # D'abord vérifier si déjà connecté via session_state
    if st.session_state.get('logged_in', False):
        st.rerun()
        
    # Ensuite vérifier la session fichier
    saved_username, _ = load_session()
    if saved_username:
        st.session_state.update({
            'logged_in': True,
            'username': saved_username,
            'login_time': datetime.now()
        })
        st.rerun()
    
    st.markdown("""
    <style>
        /* Gardez tout votre CSS existant ici - ne le changez pas */
        [data-testid="stHeader"] {
            display: none !important;
        }
        
        .stApp > header {
            display: none !important;
        }
        
        .stApp > .block-container {
            padding-top: 0rem !important;
        }
        
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        
        footer {
            visibility: hidden !important;
        }
        
        .stApp > footer:after {
            content: "" !important;
        }

        .login-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
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
                            save_session(username)

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
    clear_session()  # Supprime le fichier de session
    
    # Nettoyer toutes les variables de session liées à l'authentification
    keys_to_remove = ['logged_in', 'username', 'login_time']
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("Déconnexion réussie !")
    time.sleep(1)  # Donne le temps de voir le message
    st.rerun()

def is_logged_in():
    """Vérifier si l'utilisateur est connecté"""
    if not st.session_state.get('logged_in', False):
        saved_username = load_session()
        if saved_username:
            st.session_state.logged_in = True
            st.session_state.username = saved_username
            st.session_state.login_time = datetime.now()
            return True
    return st.session_state.get('logged_in', False)

def get_current_user():
    """Obtenir les informations de l'utilisateur actuel"""
    if is_logged_in():
        return {
            'username': st.session_state.get('username'),
            'login_time': st.session_state.get('login_time')
        }
    return None 