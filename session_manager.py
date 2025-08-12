import streamlit as st
import hashlib
import time
from datetime import datetime, timedelta
import os

# Fichier pour sauvegarder les sessions
SESSION_FILE = "active_sessions.txt"

def generate_session_token(username):
    """Générer un token de session unique"""
    timestamp = str(time.time())
    return hashlib.md5(f"{username}_{timestamp}".encode()).hexdigest()

def save_session_to_file(username, token, expiry_time):
    """Sauvegarder la session dans un fichier"""
    try:
        with open(SESSION_FILE, "a", encoding="utf-8") as f:
            f.write(f"{token}|{username}|{expiry_time.isoformat()}\n")
    except Exception as e:
        st.error(f"Erreur de sauvegarde de session: {e}")

def load_active_sessions():
    """Charger les sessions actives depuis le fichier"""
    sessions = {}
    if not os.path.exists(SESSION_FILE):
        return sessions
    
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        valid_lines = []
        current_time = datetime.now()
        
        for line in lines:
            line = line.strip()
            if line:
                parts = line.split("|")
                if len(parts) == 3:
                    token, username, expiry_str = parts
                    try:
                        expiry_time = datetime.fromisoformat(expiry_str)
                        # Vérifier si la session n'a pas expiré
                        if expiry_time > current_time:
                            sessions[token] = {
                                'username': username,
                                'expiry': expiry_time
                            }
                            valid_lines.append(line)
                    except Exception:
                        continue
        
        # Réécrire le fichier avec seulement les sessions valides
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            for line in valid_lines:
                f.write(line + "\n")
                
    except Exception as e:
        st.error(f"Erreur de chargement des sessions: {e}")
    
    return sessions

def validate_session_token(token):
    """Valider un token de session"""
    sessions = load_active_sessions()
    if token in sessions:
        session_data = sessions[token]
        if session_data['expiry'] > datetime.now():
            return session_data['username']
    return None

def create_persistent_session(username):
    """Créer une session persistante"""
    # Générer un token
    token = generate_session_token(username)
    
    # Définir l'expiration (24 heures)
    expiry_time = datetime.now() + timedelta(hours=24)
    
    # Sauvegarder dans le fichier
    save_session_to_file(username, token, expiry_time)
    
    # Stocker dans la session Streamlit
    st.session_state.session_token = token
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.login_time = datetime.now()
    
    return token

def check_persistent_session():
    """Vérifier si une session persistante existe"""
    # Si déjà connecté dans la session courante, ne rien faire
    if st.session_state.get('logged_in', False):
        return True
    
    # Vérifier si un token existe dans la session
    token = st.session_state.get('session_token')
    if token:
        username = validate_session_token(token)
        if username:
            # Restaurer la session
            st.session_state.logged_in = True
            st.session_state.username = username
            return True
    
    return False

def logout_session():
    """Déconnexion et nettoyage de la session"""
    token = st.session_state.get('session_token')
    
    if token:
        # Supprimer le token du fichier
        sessions = load_active_sessions()
        if token in sessions:
            del sessions[token]
            
            # Réécrire le fichier sans ce token
            try:
                with open(SESSION_FILE, "w", encoding="utf-8") as f:
                    for t, data in sessions.items():
                        f.write(f"{t}|{data['username']}|{data['expiry'].isoformat()}\n")
            except Exception as e:
                st.error(f"Erreur lors de la suppression de session: {e}")
    
    # Nettoyer la session Streamlit
    keys_to_remove = ['logged_in', 'username', 'login_time', 'session_token', 'current_page']
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]

def cleanup_expired_sessions():
    """Nettoyer les sessions expirées (à appeler périodiquement)"""
    load_active_sessions()  # Cette fonction nettoie automatiquement les sessions expirées