import streamlit as st
from login import login_page, clear_session, is_logged_in
from PIL import Image
import os
import sys
from db import init_db
from datetime import datetime
import time

# Configuration de la page
st.set_page_config(
    page_title="App Domiciliation",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation de la base de données au démarrage
try:
    init_db()
except Exception as e:
    st.error(f"Erreur d'initialisation de la base de données: {e}")

# =================== GESTION DE L'AUTHENTIFICATION ===================

# CORRECTION : Initialisation et vérification de session intelligente
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    # Au premier chargement, vérifier s'il y a une session sauvegardée
    from login import load_session
    saved_username, saved_page = load_session()
    
    if saved_username:  # Session valide trouvée
        st.session_state.update({
            'logged_in': True,
            'username': saved_username,
            'login_time': datetime.now(),
            'current_page': saved_page
        })

# Vérification finale : si toujours pas connecté, afficher login
if not st.session_state.get('logged_in', False):
    # Masquer sidebar et header pour la page de login
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] { display: none !important; }
        header[data-testid="stHeader"] { display: none !important; }
        .stApp > .block-container { padding-top: 0 !important; }
    </style>
    """, unsafe_allow_html=True)
    
    login_page()
    st.stop()

# =================== APRÈS AUTHENTIFICATION RÉUSSIE ===================

# Ajouter le dossier page au Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
page_dir = os.path.join(current_dir, 'page')

if page_dir not in sys.path:
    sys.path.insert(0, page_dir)

# Fonction pour importer les modules de page
def import_page_module(module_name):
    """Importe un module de page avec gestion d'erreurs détaillée"""
    try:
        module = __import__(module_name)
        return module
    except ImportError as e1:
        try:
            import importlib.util
            module_path = os.path.join(page_dir, f"{module_name}.py")
            
            if not os.path.exists(module_path):
                st.error(f"✗ Fichier non trouvé: {module_path}")
                st.info(f" Vérifiez que le fichier `page/{module_name}.py` existe")
                return None
            
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
            
        except Exception as e2:
            st.error(f"✗ Erreur d'importation pour {module_name}")
            st.error(f"Erreur 1: {e1}")
            st.error(f"Erreur 2: {e2}")
            
            with st.expander(" Informations de débogage"):
                st.write(f"**Répertoire courant:** {current_dir}")
                st.write(f"**Dossier page:** {page_dir}")
                st.write(f"**Fichier recherché:** {os.path.join(page_dir, f'{module_name}.py')}")
                st.write(f"**Dossier page existe:** {os.path.exists(page_dir)}")
                
                if os.path.exists(page_dir):
                    st.write("**Contenu du dossier page:**")
                    try:
                        files = os.listdir(page_dir)
                        for file in files:
                            st.write(f"  - {file}")
                    except Exception as e:
                        st.write(f"Erreur lecture dossier: {e}")
                else:
                    st.write("✗ Le dossier 'page' n'existe pas!")
            
            return None

# Styles CSS pour l'interface
st.markdown("""
<style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    [data-testid="stSidebar"] > div:first-child {
        background-color: rgb(237, 225, 207) !important;
    }
    
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    .main .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp > footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}

    .sidebar-content {
        padding: 1rem;
        background-color: transparent !important;
    }
    
    .logo-container {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
        background-color: transparent !important;
    }
    
    .company-title {
        text-align: center;
        font-size: 1.8rem;
        font-weight: normal;
        color: #2c3e50;
        margin: 1rem 0;
        padding: 0.5rem;
        background: transparent !important;
        text-transform: uppercase;
    }
    
    .menu-item {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 8px;
        background:linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        color: #333;
        font-weight: 500;
        transition: all 0.3s ease;
        cursor: pointer;
        border-left: 4px solid transparent;
    }
    
    .menu-item:hover {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        transform: translateX(4px);
        border-left: 4px solid #667eea;
    }
    
    .menu-item.active {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    .menu-icon {
        margin-right: 12px;
        width: 20px;
        text-align: center;
        font-size: 1.1rem;
    }
    
    .stButton > button {
        width: 100%;
        padding: 12px 16px;
        margin: 4px 0;
        border: none;
        border-radius: 8px;
        background:linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        color: #333;
        font-weight: 500;
        text-align: left;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        transform: translateX(2px);
    }
    
    .user-section {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
        background-color: transparent !important;
    }
    
    .logout-btn {
        background-color: rgba(255, 255, 255, 0.7) !important;
        color: #e74c3c;
        border: 1px solid #e74c3c;
        border-radius: 6px;
        padding: 10px;
        margin-top: 1rem;
        width: 100%;
        transition: all 0.3s;
    }
    
    .logout-btn:hover {
        background-color: #e74c3c !important;
        color: white !important;
    }
    
    .page-title {
        color: #333;
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }

    button[data-testid="collapsedControl"] {
        display: none !important;
    }

    section[data-testid="stSidebar"] button[kind="header"],
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de la page courante
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Accueil"

# Sidebar avec navigation
with st.sidebar:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    
    # Gestion du logo
    logo_path = os.path.join("static", "logo.jpg")
    if os.path.exists(logo_path):
        try:
            image = Image.open(logo_path)
            st.image(image, width=200)
        except Exception as e:
            st.write("🏢 **App Domiciliation**")
    else:
        st.write("🏢 **App Domiciliation**")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Menu de navigation
    st.markdown('<div class="company-title"><i>Navigation</i></div>', unsafe_allow_html=True)

    # Options de menu
    menu_options = [
        (" Accueil", "Accueil"),
        (" Clients", "Clients"),
        (" Contrats", "Contrats"),
        (" Facturation", "Facturation"),
        (" Reporting", "Reporting")
    ]
    
    # Création des boutons de navigation
    for display_name, page_name in menu_options:
        col1, col2 = st.columns([1, 20])
        with col2:
            if st.button(display_name, key=f"nav_{page_name}", use_container_width=True):
                st.session_state.current_page = page_name
                # Sauvegarder la page courante
                if st.session_state.get('logged_in'):
                    from login import save_session
                    save_session(st.session_state.username, page_name)
                st.rerun()
    
    # Espacement
    st.markdown("---")
    
    # Informations utilisateur
    st.markdown('<div class="user-section">', unsafe_allow_html=True)
    st.markdown("### <i class='fas fa-user-circle'></i> Utilisateur", unsafe_allow_html=True)
    st.success(f"✅ {st.session_state.get('username', 'Utilisateur')} connecté")
    
    # Bouton de déconnexion
    st.markdown("<br>" * 5, unsafe_allow_html=True)
    if st.button(" Déconnexion", key="logout_btn", use_container_width=True):
        from login import logout_user
        with st.spinner("Déconnexion en cours..."):
            logout_user()

# Container principal
main_container = st.container()

with main_container:
    try:
        page_name = st.session_state.current_page
        
        # Routage vers les différentes pages
        if page_name == "Accueil":
            module = import_page_module("Accueil")
            if module and hasattr(module, 'show'):
                module.show()
            else:
                st.error("✗ Module Accueil non trouvé ou fonction show() manquante")
                st.info("💡 Créez le fichier `page/Accueil.py` avec une fonction `show()`")
                
        elif page_name == "Clients":
            module = import_page_module("Clients")
            if module and hasattr(module, 'show'):
                module.show()
            else:
                st.error("✗ Module Clients non trouvé ou fonction show() manquante")
                st.info("💡 Créez le fichier `page/Clients.py` avec une fonction `show()`")
                
        elif page_name == "Contrats":
            module = import_page_module("Contrats")
            if module and hasattr(module, 'show'):
                module.show()
            else:
                st.error("✗ Module Contrats non trouvé ou fonction show() manquante")
                st.info("💡 Créez le fichier `page/Contrats.py` avec une fonction `show()`")
                
        elif page_name == "Facturation":
            module = import_page_module("Facturation")
            if module and hasattr(module, 'show'):
                module.show()
            else:
                st.error("✗ Module Facturation non trouvé ou fonction show() manquante")
                st.info("💡 Créez le fichier `page/Facturation.py` avec une fonction `show()`")
                
        elif page_name == "Reporting":
            module = import_page_module("Reporting")
            if module and hasattr(module, 'show'):
                module.show()
            else:
                st.error("✗ Module Reporting non trouvé ou fonction show() manquante")
                st.info("💡 Créez le fichier `page/Reporting.py` avec une fonction `show()`")
        
    except Exception as e:
        st.error(f"✗ Erreur lors du chargement de la page {page_name}: {e}")
        
        with st.expander(" Détails de l'erreur"):
            import traceback
            st.code(traceback.format_exc())
        
        st.info("💡 Vérifiez que tous les fichiers de pages existent dans le dossier 'page/'")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.8em;'>"
    "© 2025 App Domiciliation - Tous droits réservés"
    "</div>", 
    unsafe_allow_html=True
)