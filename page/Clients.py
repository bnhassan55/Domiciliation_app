import streamlit as st
from db import (ajouter_client, rechercher_clients, supprimer_client_definitif, 
                modifier_client_complet, get_all_clients)
from utils import valider_cin, valider_ice, valider_email
import pandas as pd
from datetime import datetime, date, timedelta
import time
import hashlib
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io

# Configuration de la page avec style personnalisé
def apply_custom_css():
    """Appliquer des styles CSS personnalisés"""
    st.markdown("""
    <style>
    /* Style général */
    .main {
        padding-top: 1rem;
    }
    
    /* Style pour les titres */
    .title-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .title-text {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        text-align: center;
    }
    
    /* Style pour les cartes statistiques */
    .stats-card {
        background: rgb(237, 225, 207);
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .stats-number {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
        margin: 0;
    }
    
    .stats-label {
        color: #666;
        margin: 0;
        font-size: 0.9rem;
    }
    
    /* Style pour les formulaires */
    .form-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-bottom: 2rem;
    }
    
    /* Style pour les boutons */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Style pour les alertes */
    .alert-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .alert-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        color: #721c24;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Style pour la modification */
    .edit-form {
        background: #f0f7ff;
        border: 2px solid #667eea;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

       /* Style pour les onglets */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgb(237, 225, 207);
        border-radius: 5px 5px 0 0;
        padding: 1rem 2rem;
        font-weight: bold;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

def safe_get_clients(type_client):
    """Récupérer les clients de manière sécurisée avec tri par ID croissant"""
    try:
        clients = get_all_clients(type_client)
        if clients is None:
            return []
        if not isinstance(clients, list):
            return []
        
        # Trier par ID croissant
        clients_sorted = sorted(clients, key=lambda x: x.get('id', 0) if isinstance(x, dict) else 0)
        return clients_sorted
        
    except Exception as e:
        st.error(f"Erreur lors de la récupération des clients {type_client}: {str(e)}")
        return []

def get_client_by_id_safe(client_id, client_type):
    """Récupérer un client par ID de manière sécurisée"""
    try:
        clients = safe_get_clients(client_type)
        for client in clients:
            if isinstance(client, dict) and client.get('id') == client_id:
                return client
        return None
    except Exception as e:
        st.error(f"Erreur lors de la récupération du client: {str(e)}")
        return None

def show_stats():
    """Afficher les statistiques des clients"""
    try:
        clients_physiques = safe_get_clients("physique")
        clients_moraux = safe_get_clients("moral")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nb_physiques = len(clients_physiques) if clients_physiques else 0
            st.markdown(f"""
            <div class="stats-card">
                <p class="stats-number">{nb_physiques}</p>
                <p class="stats-label"> Clients Physiques</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            nb_moraux = len(clients_moraux) if clients_moraux else 0
            st.markdown(f"""
            <div class="stats-card">
                <p class="stats-number">{nb_moraux}</p>
                <p class="stats-label"> Clients Moraux</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total = nb_physiques + nb_moraux
            st.markdown(f"""
            <div class="stats-card">
                <p class="stats-number">{total}</p>
                <p class="stats-label"> Total Clients</p>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Erreur lors du chargement des statistiques: {str(e)}")

def modifier_client_physique_interface(client_id):
    """Interface complète de modification d'un client physique - INSPIRÉE DE LA GESTION CONTRATS"""
    # Récupérer les données du client
    client = get_client_by_id_safe(client_id, "physique")
    
    if not client:
        st.error("✗ Client non trouvé")
        return
    
    st.markdown(f"###  Modification du Client: {client['nom']} {client['prenom']}")
    
    # Afficher les informations actuelles
    with st.expander("🗎 Informations Actuelles", expanded=False):
        st.write(f"**ID:** {client.get('id')}")
        st.write(f"**Nom complet:** {client.get('nom', '')} {client.get('prenom', '')}")
        st.write(f"**CIN:** {client.get('cin', '')}")
        st.write(f"**Téléphone:** {client.get('telephone', '')}")
        st.write(f"**Email:** {client.get('email', 'Non défini')}")
        st.write(f"**Sexe:** {client.get('sexe', 'Non défini')}")
        st.write(f"**Date naissance:** {client.get('date_naissance', 'Non définie')}")
        st.write(f"**Adresse:** {client.get('adresse', 'Non définie')}")
    
    # Formulaire de modification avec toutes les informations modifiables
    with st.form(f"form_modifier_client_{client_id}"):
        st.markdown("#### 🗎 Nouvelles Informations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("** Informations Personnelles**")
            nom = st.text_input(
                "Nom *",
                value=str(client.get('nom', '')),
                max_chars=50,
                help="Nom de famille du client"
            )
            
            prenom = st.text_input(
                "Prénom *",
                value=str(client.get('prenom', '')),
                max_chars=50,
                help="Prénom du client"
            )
            
            cin = st.text_input(
                "CIN *",
                value=str(client.get('cin', '')),
                max_chars=20,
                help="Carte d'identité nationale"
            )
            
            # Gestion du sexe avec valeur actuelle
            sexe_options = ["", "M", "F", "Autre"]
            current_sexe = str(client.get('sexe', ''))
            sexe_index = 0
            if current_sexe in sexe_options:
                sexe_index = sexe_options.index(current_sexe)
            
            sexe = st.selectbox(
                "Sexe",
                sexe_options,
                index=sexe_index,
                help="Sexe du client"
            )
        
        with col2:
            st.markdown("**✆ Contact et Adresse**")
            telephone = st.text_input(
                "Téléphone *",
                value=str(client.get('telephone', '')),
                max_chars=20,
                help="Numéro de téléphone"
            )
            
            email = st.text_input(
                "Email",
                value=str(client.get('email', '') if client.get('email') else ''),
                max_chars=100,
                help="Adresse email (optionnel)"
            )
            
            # Gestion de la date de naissance avec valeur actuelle
            date_naissance_value = None
            date_str = client.get('date_naissance', '')
            if date_str:
                try:
                    if isinstance(date_str, str):
                        # Essayer plusieurs formats
                        for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
                            try:
                                date_naissance_value = datetime.strptime(date_str, fmt).date()
                                break
                            except ValueError:
                                continue
                    elif hasattr(date_str, 'date'):
                        date_naissance_value = date_str.date()
                except Exception:
                    pass
            
            current_year = datetime.now().year
            date_naissance = st.date_input(
                "Date de Naissance",
                value=date_naissance_value,
                min_value=date(1900, 1, 1),
                max_value=date(current_year, 12, 31),
                help="Date de naissance du client"
            )
            
            adresse = st.text_area(
                "Adresse",
                value=str(client.get('adresse', '') if client.get('adresse') else ''),
                max_chars=200,
                height=100,
                help="Adresse complète"
            )
        
        # Boutons d'action
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            submit = st.form_submit_button("💾 Sauvegarder les Modifications", use_container_width=True)
        
        with col2:
            if st.form_submit_button("⟲ Réinitialiser", use_container_width=True):
                st.rerun()
        
        with col3:
            if st.form_submit_button("✗ Annuler", use_container_width=True):
                if 'editing_client_id' in st.session_state:
                    del st.session_state['editing_client_id']
                if 'editing_client_type' in st.session_state:
                    del st.session_state['editing_client_type']
                st.rerun()
        
        if submit:
            # Validation des données
            erreurs = []
            
            if not nom.strip():
                erreurs.append("Le nom est obligatoire")
            elif len(nom.strip()) < 2:
                erreurs.append("Le nom doit contenir au moins 2 caractères")
                
            if not prenom.strip():
                erreurs.append("Le prénom est obligatoire")
            elif len(prenom.strip()) < 2:
                erreurs.append("Le prénom doit contenir au moins 2 caractères")
                
            if not cin.strip():
                erreurs.append("La CIN est obligatoire")
            elif not valider_cin(cin.strip()):
                erreurs.append("Format CIN invalide")
                
            if not telephone.strip():
                erreurs.append("Le téléphone est obligatoire")
            elif len(telephone.strip()) < 10:
                erreurs.append("Le numéro de téléphone doit contenir au moins 10 chiffres")
                
            if email and email.strip() and not valider_email(email.strip()):
                erreurs.append("Format email invalide")
            
            if erreurs:
                for erreur in erreurs:
                    st.error(f"✗ {erreur}")
            else:
                # Préparer les modifications avec normalisation
                modifications = {
                    'nom': nom.strip().title(),
                    'prenom': prenom.strip().title(),
                    'cin': cin.strip().upper(),
                    'telephone': telephone.strip(),
                    'sexe': sexe if sexe else '',
                    'email': email.strip().lower() if email.strip() else '',
                    'adresse': adresse.strip() if adresse.strip() else '',
                    'date_naissance': str(date_naissance) if date_naissance else ''
                }
                
                # Effectuer la modification
                with st.spinner("💾 Sauvegarde en cours..."):
                    success = modifier_client_complet(client_id, modifications, "physique")
                    
                    if success:
                        st.success("✅ Client modifié avec succès!")
                        
                        # Nettoyer l'état et rediriger
                        if 'editing_client_id' in st.session_state:
                            del st.session_state['editing_client_id']
                        if 'editing_client_type' in st.session_state:
                            del st.session_state['editing_client_type']
                        
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error("✗ Erreur lors de la modification du client")

def modifier_client_moral_interface(client_id):
    """Interface complète de modification d'un client moral - INSPIRÉE DE LA GESTION CONTRATS"""
    # Récupérer les données du client
    client = get_client_by_id_safe(client_id, "moral")
    
    if not client:
        st.error("✗ Client non trouvé")
        return
    
    st.markdown(f"###  Modification de l'Entreprise: {client['raison_sociale']}")
    
    # Afficher les informations actuelles
    with st.expander("🗎 Informations Actuelles", expanded=False):
        st.write(f"**ID:** {client.get('id')}")
        st.write(f"**Raison sociale:** {client.get('raison_sociale', '')}")
        st.write(f"**ICE:** {client.get('ice', '')}")
        st.write(f"**RC:** {client.get('rc', 'Non défini')}")
        st.write(f"**Forme juridique:** {client.get('forme_juridique', 'Non définie')}")
        st.write(f"**Téléphone:** {client.get('telephone', '')}")
        st.write(f"**Email:** {client.get('email', 'Non défini')}")
        st.write(f"**Adresse:** {client.get('adresse', 'Non définie')}")
        
        # Représentant légal
        if any([client.get('rep_nom'), client.get('rep_prenom'), client.get('rep_cin')]):
            st.write("**Représentant légal:**")
            st.write(f"  - Nom: {client.get('rep_nom', 'Non défini')}")
            st.write(f"  - Prénom: {client.get('rep_prenom', 'Non défini')}")
            st.write(f"  - CIN: {client.get('rep_cin', 'Non défini')}")
            st.write(f"  - Qualité: {client.get('rep_qualite', 'Non définie')}")
    
    # Formulaire de modification avec toutes les informations modifiables
    with st.form(f"form_modifier_client_moral_{client_id}"):
        st.markdown("#### 🗎 Nouvelles Informations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("** Informations Entreprise**")
            raison_sociale = st.text_input(
                "Raison Sociale *",
                value=str(client.get('raison_sociale', '')),
                max_chars=100,
                help="Nom officiel de l'entreprise"
            )
            
            ice = st.text_input(
                "ICE *",
                value=str(client.get('ice', '')),
                max_chars=20,
                help="Identifiant Commun de l'Entreprise"
            )
            
            rc = st.text_input(
                "Registre Commerce",
                value=str(client.get('rc', '') if client.get('rc') else ''),
                max_chars=50,
                help="Numéro au registre de commerce"
            )
            
            # Gestion de la forme juridique avec valeur actuelle
            forme_options = ["", "SARL", "SA", "SARL-AU", "SNC", "SCS", "GIE", "Association", "Coopérative", "Autre"]
            current_forme = str(client.get('forme_juridique', ''))
            forme_index = 0
            if current_forme in forme_options:
                forme_index = forme_options.index(current_forme)
            
            forme_juridique = st.selectbox(
                "Forme Juridique",
                forme_options,
                index=forme_index,
                help="Statut juridique de l'entreprise"
            )
        
        with col2:
            st.markdown("**✆ Contact**")
            telephone = st.text_input(
                "Téléphone *",
                value=str(client.get('telephone', '')),
                max_chars=20,
                help="Numéro de téléphone principal"
            )
            
            email = st.text_input(
                "Email",
                value=str(client.get('email', '') if client.get('email') else ''),
                max_chars=100,
                help="Adresse email professionnelle"
            )
            
            adresse = st.text_area(
                "Adresse",
                value=str(client.get('adresse', '') if client.get('adresse') else ''),
                max_chars=200,
                height=100,
                help="Adresse du siège social"
            )
        
        # Représentant légal modifiable
        st.markdown("#### 👤 Représentant Légal")
        col3, col4 = st.columns(2)
        
        with col3:
            rep_nom = st.text_input(
                "Nom du Représentant",
                value=str(client.get('rep_nom', '') if client.get('rep_nom') else ''),
                max_chars=50,
                help="Nom du représentant légal"
            )
            
            rep_prenom = st.text_input(
                "Prénom du Représentant",
                value=str(client.get('rep_prenom', '') if client.get('rep_prenom') else ''),
                max_chars=50,
                help="Prénom du représentant légal"
            )
        
        with col4:
            rep_cin = st.text_input(
                "CIN du Représentant",
                value=str(client.get('rep_cin', '') if client.get('rep_cin') else ''),
                max_chars=20,
                help="CIN du représentant légal"
            )
            
            rep_qualite = st.text_input(
                "Qualité (Gérant, PDG...)",
                value=str(client.get('rep_qualite', '') if client.get('rep_qualite') else ''),
                max_chars=50,
                help="Fonction du représentant"
            )
        
        # Boutons d'action
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            submit = st.form_submit_button("💾 Sauvegarder les Modifications", use_container_width=True)
        
        with col2:
            if st.form_submit_button("⟲ Réinitialiser", use_container_width=True):
                st.rerun()
        
        with col3:
            if st.form_submit_button("✗ Annuler", use_container_width=True):
                if 'editing_client_id' in st.session_state:
                    del st.session_state['editing_client_id']
                if 'editing_client_type' in st.session_state:
                    del st.session_state['editing_client_type']
                st.rerun()
        
        if submit:
            # Validation des données
            erreurs = []
            
            if not raison_sociale.strip():
                erreurs.append("La raison sociale est obligatoire")
            elif len(raison_sociale.strip()) < 3:
                erreurs.append("La raison sociale doit contenir au moins 3 caractères")
                
            if not ice.strip():
                erreurs.append("L'ICE est obligatoire")
            elif not valider_ice(ice.strip()):
                erreurs.append("Format ICE invalide")
                
            if not telephone.strip():
                erreurs.append("Le téléphone est obligatoire")
            elif len(telephone.strip()) < 10:
                erreurs.append("Le numéro de téléphone doit contenir au moins 10 chiffres")
                
            if email and email.strip() and not valider_email(email.strip()):
                erreurs.append("Format email invalide")
                
            if rep_cin and rep_cin.strip() and not valider_cin(rep_cin.strip()):
                erreurs.append("Format CIN du représentant invalide")
            
            if erreurs:
                for erreur in erreurs:
                    st.error(f"✗ {erreur}")
            else:
                # Préparer les modifications avec normalisation
                modifications = {
                    'raison_sociale': raison_sociale.strip().title(),
                    'ice': ice.strip().upper(),
                    'telephone': telephone.strip(),
                    'rc': rc.strip() if rc.strip() else '',
                    'forme_juridique': forme_juridique if forme_juridique else '',
                    'email': email.strip().lower() if email.strip() else '',
                    'adresse': adresse.strip() if adresse.strip() else '',
                    'rep_nom': rep_nom.strip().title() if rep_nom.strip() else '',
                    'rep_prenom': rep_prenom.strip().title() if rep_prenom.strip() else '',
                    'rep_cin': rep_cin.strip().upper() if rep_cin.strip() else '',
                    'rep_qualite': rep_qualite.strip().title() if rep_qualite.strip() else ''
                }
                
                # Effectuer la modification
                with st.spinner("💾 Sauvegarde en cours..."):
                    success = modifier_client_complet(client_id, modifications, "moral")
                    
                    if success:
                        st.success("✅ Entreprise modifiée avec succès!")

                        
                        # Nettoyer l'état et rediriger
                        if 'editing_client_id' in st.session_state:
                            del st.session_state['editing_client_id']
                        if 'editing_client_type' in st.session_state:
                            del st.session_state['editing_client_type']
                        
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error("✗ Erreur lors de la modification de l'entreprise")

def show_client_details_enhanced(client_data, type_client):
    """Affichage des détails du client avec plus d'informations"""
    
    st.markdown(f"### 🗎 Profil Complet - Client ID: {client_data['id']}")
    
    if type_client == "physique":
        # Informations principales
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ⚲⚲ Informations Personnelles")
            st.info(f"""
            **Nom complet:** {client_data.get('nom', 'N/A')} {client_data.get('prenom', 'N/A')}  
            **CIN:** `{client_data.get('cin', 'Non défini')}`  
            **Sexe:** {client_data.get('sexe', 'Non spécifié')}  
            **Date de naissance:** {client_data.get('date_naissance', 'Non spécifiée')}
            """)


        
        with col2:
            st.markdown("#### ✆ Informations de Contact")
            telephone = client_data.get('telephone', 'Non défini')
            email = client_data.get('email', 'Non défini')
            adresse = client_data.get('adresse', 'Non spécifiée')
            
            st.info(f"""
            **Téléphone:** `{telephone}`  
            **Email:** {email}  
            **Adresse:** {adresse}
            """)
        
        # Calculer l'âge si date de naissance disponible
       
    
    else:  # Client moral
        # Informations principales
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("####  Informations Entreprise")
            st.info(f"""
            **Raison sociale:** {client_data.get('raison_sociale', 'N/A')}  
            **ICE:** `{client_data.get('ice', 'Non défini')}`  
            **RC:** `{client_data.get('rc', 'Non défini')}`  
            **Forme juridique:** {client_data.get('forme_juridique', 'Non spécifiée')}
            """)
        
        with col2:
            st.markdown("#### ✆ Informations de Contact")
            telephone = client_data.get('telephone', 'Non défini')
            email = client_data.get('email', 'Non défini')
            adresse = client_data.get('adresse', 'Non spécifiée')
            
            st.info(f"""
            **Téléphone:** `{telephone}`  
            **Email:** {email}  
            **Adresse:** {adresse}
            """)
        
        # Représentant légal si disponible
        if any([client_data.get('rep_nom'), client_data.get('rep_prenom'), client_data.get('rep_cin')]):
            st.markdown("#### 👤 Représentant Légal")
            st.success(f"""
            **Nom:** {client_data.get('rep_nom', 'Non spécifié')}  
            **Prénom:** {client_data.get('rep_prenom', 'Non spécifié')}  
            **CIN:** `{client_data.get('rep_cin', 'Non spécifié')}`  
            **Qualité:** {client_data.get('rep_qualite', 'Non spécifiée')}
            """)
    
    # Informations système
    st.markdown("#### ⏱ Informations Système")
    date_creation = client_data.get('date_creation', 'Non définie')
    st.warning(f"**Date de création:** {date_creation}")
    
    # Statistiques et éléments associés
    st.markdown("---")
    st.markdown("####  Éléments Associés")
    
    try:
        from db import get_db_connection
        conn = get_db_connection()
        
        # Compter les contrats
        contrats = conn.execute(
            "SELECT COUNT(*) as count FROM contrats WHERE client_id = ? AND client_type = ?",
            (client_data['id'], type_client)
        ).fetchone()
        
        # Compter les factures  
        factures = conn.execute(
            "SELECT COUNT(*) as count FROM factures WHERE client_id = ?",
            (client_data['id'],)
        ).fetchone()
        
        conn.close()
        
        col1, col2 = st.columns(2)
        
        with col1:
            nb_contrats = contrats['count'] if contrats else 0
            st.metric("🗎 Contrats", nb_contrats)
        
        with col2:
            nb_factures = factures['count'] if factures else 0
            st.metric("🧾 Factures", nb_factures)
        
        total_elements = nb_contrats + nb_factures
        if total_elements > 0:
            st.warning(f"⚠️ Ce client a {total_elements} élément(s) associé(s)")
        else:
            st.success("✅ Aucun élément associé")
            
    except Exception as e:
        st.error(f"✗ Erreur lors du chargement des éléments associés: {str(e)}")
    
    # Bouton de retour
    st.markdown("---")
    if st.button(" Retour à la liste", use_container_width=True, key="back_from_details"):
        if 'editing_client_id' in st.session_state:
            del st.session_state['editing_client_id']
        if 'editing_client_type' in st.session_state:
            del st.session_state['editing_client_type']
        st.rerun()

def show_delete_confirmation_enhanced(client_data, type_client):
    """Confirmation de suppression sécurisée"""
    
    st.markdown(f"###  Confirmation de Suppression - ID: {client_data['id']}")
    
    # Informations du client à supprimer
    if type_client == "physique":
        st.error(f"""
        ** Client à supprimer:**
        - **Nom complet:** {client_data.get('nom')} {client_data.get('prenom')}
        - **CIN:** {client_data.get('cin')}
        - **Téléphone:** {client_data.get('telephone')}
        - **Email:** {client_data.get('email', 'Non défini')}
        """)
    else:
        st.error(f"""
        ** Entreprise à supprimer:**
        - **Raison sociale:** {client_data.get('raison_sociale')}
        - **ICE:** {client_data.get('ice')}
        - **Téléphone:** {client_data.get('telephone')}
        - **Email:** {client_data.get('email', 'Non défini')}
        """)
    
    # Vérifications de sécurité
    st.warning("⚠️ **ATTENTION: Cette action est irréversible !**")
    
    try:
        from db import get_db_connection
        conn = get_db_connection()
        
        # Vérifier les éléments associés
        contrats = conn.execute(
            "SELECT COUNT(*) as count FROM contrats WHERE client_id = ? AND client_type = ?",
            (client_data['id'], type_client)
        ).fetchone()
        
        factures = conn.execute(
            "SELECT COUNT(*) as count FROM factures WHERE client_id = ?",
            (client_data['id'],)
        ).fetchone()
        
        conn.close()
        
        nb_contrats = contrats['count'] if contrats else 0
        nb_factures = factures['count'] if factures else 0
        
        if nb_contrats > 0 or nb_factures > 0:
            st.error(f"""
            **⊘ Suppression impossible !**
            
            Ce client est associé à :
            - **{nb_contrats}** contrat(s)
            - **{nb_factures}** facture(s)
            
            Vous devez d'abord supprimer/transférer ces éléments.
            """)
            
            if st.button("🔙 Revenir", use_container_width=True):
                if 'editing_client_id' in st.session_state:
                    del st.session_state['editing_client_id']
                if 'editing_client_type' in st.session_state:
                    del st.session_state['editing_client_type']
                st.rerun()
            return
        else:
            st.success("✅ Aucun élément associé trouvé. La suppression est possible.")
        
    except Exception as e:
        st.warning(f"⚠️ Impossible de vérifier les éléments associés: {str(e)}")
    
    # Interface de confirmation sécurisée
    # st.markdown("### 🔐 Confirmation Sécurisée")
    
    confirmation_text = "SUPPRIMER"
    user_confirmation = st.text_input(
        f"Tapez **{confirmation_text}** pour confirmer:",
        placeholder=confirmation_text,
        help="Cette vérification évite les suppressions accidentelles"
    )
    
    confirmation_valide = user_confirmation.upper() == confirmation_text
    
    if confirmation_valide:
        st.success("✅ Confirmation validée")
    elif user_confirmation:
        st.error("✗ Texte de confirmation incorrect")
    
    # Boutons d'action finaux
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ CONFIRMER LA SUPPRESSION", 
                    use_container_width=True,
                    type="primary",
                    disabled=not confirmation_valide):
            
            if confirmation_valide:
                with st.spinner(" Suppression en cours..."):
                    success = supprimer_client_definitif(client_data['id'])
                    
                    if success:
                        st.success("✅ Client supprimé avec succès !")
                    
                        
                        # Nettoyer l'état
                        if 'editing_client_id' in st.session_state:
                            del st.session_state['editing_client_id']
                        if 'editing_client_type' in st.session_state:
                            del st.session_state['editing_client_type']
                        
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("✗ Erreur lors de la suppression")
    
    with col2:
        if st.button(" Annuler", use_container_width=True):
            if 'editing_client_id' in st.session_state:
                del st.session_state['editing_client_id']
            if 'editing_client_type' in st.session_state:
                del st.session_state['editing_client_type']
            st.rerun()

def gestion_clients_physiques():
    """Gestion des clients physiques avec interface améliorée"""
    st.markdown("###  Gestion des Clients Physiques")
    
    # Vérifier s'il y a une modification en cours
    if st.session_state.get('editing_client_id') and st.session_state.get('editing_client_type') == 'physique':
        client_id = st.session_state['editing_client_id']
        action = st.session_state.get('editing_action', 'edit')
        
        if action == 'edit':
            modifier_client_physique_interface(client_id)
            return
        elif action == 'delete':
            client_data = get_client_by_id_safe(client_id, "physique")
            if client_data:
                show_delete_confirmation_enhanced(client_data, "physique")
                return
        elif action == 'view':
            client_data = get_client_by_id_safe(client_id, "physique")
            if client_data:
                show_client_details_enhanced(client_data, "physique")
                return
    
    # Formulaire d'ajout (reste identique)
    with st.expander("➕ Ajouter un Nouveau Client Physique", expanded=False):
        with st.form("form_client_physique", clear_on_submit=True):
            st.markdown("#### 🗎 Informations Personnelles")
            col1, col2 = st.columns(2)
            
            with col1:
                nom = st.text_input("Nom *", max_chars=50, help="Nom de famille du client")
                prenom = st.text_input("Prénom *", max_chars=50, help="Prénom du client")
                cin = st.text_input("CIN *", max_chars=20, help="Carte d'identité nationale")
                sexe = st.selectbox("Sexe", ["", "M", "F", "Autre"], help="Sexe du client")
            
            with col2:
                telephone = st.text_input("Téléphone *", max_chars=20, help="Numéro de téléphone")
                email = st.text_input("Email", max_chars=100, help="Adresse email (optionnel)")
                
                current_year = datetime.now().year
                date_naissance = st.date_input(
                    "Date de Naissance", 
                    value=None, 
                    min_value=date(1900, 1, 1),
                    max_value=date(current_year, 12, 31),
                    help="Date de naissance du client"
                )
                
                adresse = st.text_area("Adresse", max_chars=200, help="Adresse complète")
            
            submitted = st.form_submit_button("💾 Enregistrer le Client", use_container_width=True)
            
            if submitted:
                handle_client_physique_submission(nom, prenom, cin, telephone, sexe, email, date_naissance, adresse)
    
    # Liste et actions des clients
    st.markdown("---")
    st.markdown("### 🗎 Liste des Clients Physiques")
    
    # Barre de recherche
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input(
            " Rechercher un client", 
            placeholder="ID, nom, prénom, CIN ou téléphone...",
            key="search_physique"
        )
    with col2:
        refresh_btn = st.button("⟲ Actualiser", use_container_width=True, key="refresh_physique")
    
    # Récupérer et afficher les clients
    try:
        if search_term and search_term.strip():
            if search_term.strip().isdigit():
                # Recherche par ID
                client_id = int(search_term.strip())
                client = get_client_by_id_safe(client_id, "physique")
                clients = [client] if client else []
            else:
                # Recherche textuelle
                clients = rechercher_clients(search_term.strip(), "physique")
        else:
            clients = safe_get_clients("physique")
        
        if not clients:
            st.info("ℹ️ Aucun client trouvé")
            return
        
        # Afficher le tableau
        df = pd.DataFrame(clients)
        
        if not df.empty:
            # Réorganiser les colonnes
            columns_order = ['id', 'nom', 'prenom', 'cin', 'telephone', 'email', 'sexe']
            existing_columns = [col for col in columns_order if col in df.columns]
            df_display = df[existing_columns].fillna('')
            
            st.dataframe(
                df_display, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "id": st.column_config.NumberColumn("ID", width="small"),
                    "nom": st.column_config.TextColumn("Nom", width="medium"),
                    "prenom": st.column_config.TextColumn("Prénom", width="medium"),
                    "cin": st.column_config.TextColumn("CIN", width="medium"),
                    "telephone": st.column_config.TextColumn("Téléphone", width="medium"),
                    "email": st.column_config.TextColumn("Email", width="large"),
                    "sexe": st.column_config.TextColumn("Sexe", width="small")
                }
            )
            
            # Actions sur les clients
            show_client_actions_enhanced(clients, "physique")
        
    except Exception as e:
        st.error(f"✗ Erreur lors du chargement: {str(e)}")

def gestion_clients_moraux():
    """Gestion des clients moraux avec interface améliorée"""
    st.markdown("###  Gestion des Clients Moraux")
    
    # Vérifier s'il y a une modification en cours
    if st.session_state.get('editing_client_id') and st.session_state.get('editing_client_type') == 'moral':
        client_id = st.session_state['editing_client_id']
        action = st.session_state.get('editing_action', 'edit')
        
        if action == 'edit':
            modifier_client_moral_interface(client_id)
            return
        elif action == 'delete':
            client_data = get_client_by_id_safe(client_id, "moral")
            if client_data:
                show_delete_confirmation_enhanced(client_data, "moral")
                return
        elif action == 'view':
            client_data = get_client_by_id_safe(client_id, "moral")
            if client_data:
                show_client_details_enhanced(client_data, "moral")
                return
    
    # Formulaire d'ajout (reste identique)
    with st.expander("➕ Ajouter une Nouvelle Entreprise", expanded=False):
        with st.form("form_client_moral", clear_on_submit=True):
            st.markdown("#### 🗎 Informations de l'Entreprise")
            col1, col2 = st.columns(2)
            
            with col1:
                raison_sociale = st.text_input("Raison Sociale *", max_chars=100)
                ice = st.text_input("ICE *", max_chars=20)
                rc = st.text_input("Registre Commerce", max_chars=50)
                forme_juridique = st.selectbox("Forme Juridique", [
                    "", "SARL", "SA", "SARL-AU", "SNC", "SCS", "GIE", "Association", "Coopérative", "Autre"
                ])
            
            with col2:
                telephone = st.text_input("Téléphone *", max_chars=20)
                email = st.text_input("Email", max_chars=100)
                adresse = st.text_area("Adresse", max_chars=200)
            
            # Représentant légal
            st.markdown("#### ⚲⚲ Représentant Légal")
            col3, col4 = st.columns(2)
            
            with col3:
                rep_nom = st.text_input("Nom du Représentant", max_chars=50)
                rep_prenom = st.text_input("Prénom du Représentant", max_chars=50)
            
            with col4:
                rep_cin = st.text_input("CIN du Représentant", max_chars=20)
                rep_qualite = st.text_input("Qualité (Gérant, PDG...)", max_chars=50)
            
            submitted = st.form_submit_button("💾 Enregistrer l'Entreprise", use_container_width=True)
            
            if submitted:
                handle_client_moral_submission(raison_sociale, ice, rc, forme_juridique, telephone, 
                                              email, None, adresse, rep_nom, rep_prenom, rep_cin, rep_qualite)
    
    # Liste et actions des clients
    st.markdown("---")
    st.markdown("### 🗎 Liste des Entreprises")
    
    # Barre de recherche
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input(
            " Rechercher une entreprise", 
            placeholder="ID, raison sociale, ICE...",
            key="search_moral"
        )
    with col2:
        refresh_btn = st.button("⟲ Actualiser", use_container_width=True, key="refresh_moral")
    
    # Récupérer et afficher les clients
    try:
        if search_term and search_term.strip():
            if search_term.strip().isdigit():
                # Recherche par ID
                client_id = int(search_term.strip())
                client = get_client_by_id_safe(client_id, "moral")
                clients = [client] if client else []
            else:
                # Recherche textuelle
                clients = rechercher_clients(search_term.strip(), "moral")
        else:
            clients = safe_get_clients("moral")
        
        if not clients:
            st.info("ℹ️ Aucune entreprise trouvée")
            return
        
        # Afficher le tableau
        df = pd.DataFrame(clients)
        
        if not df.empty:
            # Réorganiser les colonnes
            columns_order = ['id', 'raison_sociale', 'ice', 'rc', 'telephone', 'email', 'forme_juridique']
            existing_columns = [col for col in columns_order if col in df.columns]
            df_display = df[existing_columns].fillna('')
            
            st.dataframe(
                df_display, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "id": st.column_config.NumberColumn("ID", width="small"),
                    "raison_sociale": st.column_config.TextColumn("Raison Sociale", width="large"),
                    "ice": st.column_config.TextColumn("ICE", width="medium"),
                    "rc": st.column_config.TextColumn("RC", width="medium"),
                    "telephone": st.column_config.TextColumn("Téléphone", width="medium"),
                    "email": st.column_config.TextColumn("Email", width="large"),
                    "forme_juridique": st.column_config.TextColumn("Forme Juridique", width="medium")
                }
            )
            
            # Actions sur les clients
            show_client_actions_enhanced(clients, "moral")
        
    except Exception as e:
        st.error(f"✗ Erreur lors du chargement: {str(e)}")

def show_client_actions_enhanced(clients, type_client):
    """Interface d'actions améliorée inspirée de la gestion des contrats"""
    if not clients:
        return
        
    st.markdown("### ⚙ Actions sur les Clients")
    
    # Sélection du client
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        # Créer les options de sélection
        if type_client == "physique":
            client_options = [" Sélectionner un client..."]
            for c in clients:
                if isinstance(c, dict):
                    nom = c.get('nom', 'N/A')
                    prenom = c.get('prenom', 'N/A')
                    cin = c.get('cin', 'N/A')
                    client_id = c.get('id', 'N/A')
                    client_options.append(f"⚲⚲ ID:{client_id} | {nom} {prenom} | CIN:{cin}")
        else:
            client_options = [" Sélectionner un client..."]
            for c in clients:
                if isinstance(c, dict):
                    raison = c.get('raison_sociale', 'N/A')
                    if len(raison) > 30:
                        raison = raison[:30] + "..."
                    ice = c.get('ice', 'N/A')
                    client_id = c.get('id', 'N/A')
                    client_options.append(f"⚲⚲ ID:{client_id} | {raison} | ICE:{ice}")
        
        selected_index = st.selectbox(
            "Choisir un client", 
            range(len(client_options)),
            format_func=lambda x: client_options[x],
            key=f"select_client_{type_client}"
        )
    
    # Boutons d'action
    if selected_index > 0:
        # Extraire l'ID du client sélectionné
        selected_text = client_options[selected_index]
        client_id = int(selected_text.split(" | ")[0].replace("⚲⚲ ID:", "").replace("⚲⚲ ID:", ""))
        
        with col2:
            if st.button(" Modifier", key=f"edit_{type_client}_{client_id}", use_container_width=True):
                st.session_state['editing_client_id'] = client_id
                st.session_state['editing_client_type'] = type_client
                st.session_state['editing_action'] = 'edit'
                st.rerun()
        
        with col3:
            if st.button(" Détails", key=f"view_{type_client}_{client_id}", use_container_width=True):
                st.session_state['editing_client_id'] = client_id
                st.session_state['editing_client_type'] = type_client
                st.session_state['editing_action'] = 'view'
                st.rerun()
        
        with col4:
            if st.button(" Supprimer", key=f"delete_{type_client}_{client_id}", use_container_width=True):
                st.session_state['editing_client_id'] = client_id
                st.session_state['editing_client_type'] = type_client
                st.session_state['editing_action'] = 'delete'
                st.rerun()

def handle_client_physique_submission(nom, prenom, cin, telephone, sexe, email, date_naissance, adresse):
    """Gérer la soumission du formulaire client physique"""
    try:
        # Validation
        erreurs = []
        
        if not nom or not nom.strip():
            erreurs.append("⚠️ Le nom est obligatoire")
        elif len(nom.strip()) < 2:
            erreurs.append("⚠️ Le nom doit contenir au moins 2 caractères")
            
        if not prenom or not prenom.strip():
            erreurs.append("⚠️ Le prénom est obligatoire")
        elif len(prenom.strip()) < 2:
            erreurs.append("⚠️ Le prénom doit contenir au moins 2 caractères")
            
        if not cin or not cin.strip():
            erreurs.append("⚠️ La CIN est obligatoire")
        elif not valider_cin(cin.strip()):
            erreurs.append("⚠️ Format CIN invalide")
            
        if not telephone or not telephone.strip():
            erreurs.append("⚠️ Le téléphone est obligatoire")
        elif len(telephone.strip()) < 10:
            erreurs.append("⚠️ Le numéro de téléphone doit contenir au moins 10 chiffres")
            
        if email and email.strip() and not valider_email(email.strip()):
            erreurs.append("⚠️ Format email invalide")
        
        if erreurs:
            for erreur in erreurs:
                st.error(erreur)
            return
        
        # Préparer les données
        client_data = {
            'nom': nom.strip().title(),
            'prenom': prenom.strip().title(),
            'cin': cin.strip().upper(),
            'telephone': telephone.strip(),
            'sexe': sexe if sexe else '',
            'email': email.strip().lower() if email and email.strip() else '',
            'adresse': adresse.strip() if adresse and adresse.strip() else '',
            'date_naissance': str(date_naissance) if date_naissance else ''
        }
        
        # Supprimer les valeurs vides
        client_data = {k: v for k, v in client_data.items() if v != ''}
        
        # Ajouter le client
        with st.spinner("Enregistrement en cours..."):
            if ajouter_client(client_data, "physique"):
                st.success("✅ Client ajouté avec succès !")
                time.sleep(1)
                st.rerun()
            else:
                st.error("✗ Erreur lors de l'ajout. La CIN est peut-être déjà utilisée.")
                
    except Exception as e:
        st.error(f"✗ Erreur lors de l'ajout: {str(e)}")

def handle_client_moral_submission(raison_sociale, ice, rc, forme_juridique, telephone, email, 
                                  date_creation_entreprise, adresse, rep_nom, rep_prenom, rep_cin, rep_qualite):
    """Gérer la soumission du formulaire client moral"""
    try:
        # Validation
        erreurs = []
        
        if not raison_sociale or not raison_sociale.strip():
            erreurs.append("⚠️ La raison sociale est obligatoire")
        elif len(raison_sociale.strip()) < 3:
            erreurs.append("⚠️ La raison sociale doit contenir au moins 3 caractères")
            
        if not ice or not ice.strip():
            erreurs.append("⚠️ L'ICE est obligatoire")
        elif not valider_ice(ice.strip()):
            erreurs.append("⚠️ Format ICE invalide")
            
        if not telephone or not telephone.strip():
            erreurs.append("⚠️ Le téléphone est obligatoire")
        elif len(telephone.strip()) < 10:
            erreurs.append("⚠️ Le numéro de téléphone doit contenir au moins 10 chiffres")
            
        if email and email.strip() and not valider_email(email.strip()):
            erreurs.append("⚠️ Format email invalide")
            
        if rep_cin and rep_cin.strip() and not valider_cin(rep_cin.strip()):
            erreurs.append("⚠️ Format CIN du représentant invalide")
        
        if erreurs:
            for erreur in erreurs:
                st.error(erreur)
            return
        
        # Préparer les données
        client_data = {
            'raison_sociale': raison_sociale.strip().title(),
            'ice': ice.strip().upper(),
            'telephone': telephone.strip(),
            'rc': rc.strip() if rc and rc.strip() else '',
            'forme_juridique': forme_juridique if forme_juridique else '',
            'email': email.strip().lower() if email and email.strip() else '',
            'adresse': adresse.strip() if adresse and adresse.strip() else '',
            'rep_nom': rep_nom.strip().title() if rep_nom and rep_nom.strip() else '',
            'rep_prenom': rep_prenom.strip().title() if rep_prenom and rep_prenom.strip() else '',
            'rep_cin': rep_cin.strip().upper() if rep_cin and rep_cin.strip() else '',
            'rep_qualite': rep_qualite.strip().title() if rep_qualite and rep_qualite.strip() else ''
        }
        
        # Supprimer les valeurs vides
        client_data = {k: v for k, v in client_data.items() if v != ''}
        
        # Ajouter le client
        with st.spinner("Enregistrement en cours..."):
            if ajouter_client(client_data, "moral"):
                st.success("✅ Entreprise ajoutée avec succès !")
                time.sleep(1)
                st.rerun()
            else:
                st.error("✗ Erreur lors de l'ajout. L'ICE est peut-être déjà utilisé.")
                
    except Exception as e:
        st.error(f"✗ Erreur inattendue: {str(e)}")

def generate_pdf_report(clients, type_client, title="Liste des Clients"):
    """Générer un rapport PDF des clients"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,
            textColor=colors.HexColor('#667eea')
        )
        
        # Contenu du PDF
        story = []
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))
        
        # Informations générales
        info_style = styles['Normal']
        story.append(Paragraph(f"Date de génération: {datetime.now().strftime('%d/%m/%Y %H:%M')}", info_style))
        story.append(Paragraph(f"Nombre total de clients: {len(clients)}", info_style))
        story.append(Paragraph(f"Type de clients: {type_client.title()}", info_style))
        story.append(Spacer(1, 20))
        
        if not clients:
            story.append(Paragraph("Aucun client à afficher.", info_style))
        else:
            # Préparer les données du tableau
            if type_client == "physique":
                headers = ['ID', 'Nom', 'Prénom', 'CIN', 'Téléphone', 'Email']
                data = [headers]
                for client in clients:
                    row = [
                        str(client.get('id', '')),
                        client.get('nom', ''),
                        client.get('prenom', ''),
                        client.get('cin', ''),
                        client.get('telephone', ''),
                        client.get('email', '')[:25] + '...' if client.get('email') and len(client.get('email', '')) > 25 else client.get('email', '')
                    ]
                    data.append(row)
            else:
                headers = ['ID', 'Raison Sociale', 'ICE', 'RC', 'Téléphone', 'Email']
                data = [headers]
                for client in clients:
                    row = [
                        str(client.get('id', '')),
                        client.get('raison_sociale', '')[:30] + '...' if client.get('raison_sociale') and len(client.get('raison_sociale', '')) > 30 else client.get('raison_sociale', ''),
                        client.get('ice', ''),
                        client.get('rc', ''),
                        client.get('telephone', ''),
                        client.get('email', '')[:25] + '...' if client.get('email') and len(client.get('email', '')) > 25 else client.get('email', '')
                    ]
                    data.append(row)
            
            # Créer le tableau
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(table)
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        st.error(f"Erreur lors de la génération du PDF: {str(e)}")
        return None

def export_clients_pdf():
    """Fonction pour exporter les données clients en PDF"""
    st.markdown("### 🗎 Export PDF des Données")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗎 Exporter Clients Physiques", use_container_width=True):
            try:
                clients = safe_get_clients("physique")
                if clients:
                    pdf_buffer = generate_pdf_report(clients, "physique", "Liste des Clients Physiques")
                    if pdf_buffer:
                        st.download_button(
                            label="⭳ Télécharger PDF",
                            data=pdf_buffer.getvalue(),
                            file_name=f"clients_physiques_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf"
                        )
                        st.success("✅ PDF généré avec succès !")
                else:
                    st.info("ℹ️ Aucun client physique à exporter")
            except Exception as e:
                st.error(f"✗ Erreur lors de l'export PDF: {str(e)}")
    
    with col2:
        if st.button("🗎 Exporter Clients Moraux", use_container_width=True):
            try:
                clients = safe_get_clients("moral")
                if clients:
                    pdf_buffer = generate_pdf_report(clients, "moral", "Liste des Clients Moraux")
                    if pdf_buffer:
                        st.download_button(
                            label="⭳ Télécharger PDF",
                            data=pdf_buffer.getvalue(),
                            file_name=f"clients_moraux_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf"
                        )
                        st.success("✅ PDF généré avec succès !")
                else:
                    st.info("ℹ️ Aucun client moral à exporter")
            except Exception as e:
                st.error(f"✗ Erreur lors de l'export PDF: {str(e)}")
    
    with col3:
        if st.button("🗎 Exporter Rapport Complet", use_container_width=True):
            try:
                clients_physiques = safe_get_clients("physique")
                clients_moraux = safe_get_clients("moral")
                
                if clients_physiques or clients_moraux:
                    # Créer un rapport combiné
                    buffer = io.BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
                    
                    styles = getSampleStyleSheet()
                    title_style = ParagraphStyle(
                        'CustomTitle',
                        parent=styles['Heading1'],
                        fontSize=20,
                        spaceAfter=30,
                        alignment=1,
                        textColor=colors.HexColor('#667eea')
                    )
                    
                    story = []
                    story.append(Paragraph("Rapport Complet des Clients", title_style))
                    story.append(Spacer(1, 12))
                    
                    # Statistiques générales
                    story.append(Paragraph(f"Date de génération: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
                    story.append(Paragraph(f"Clients physiques: {len(clients_physiques) if clients_physiques else 0}", styles['Normal']))
                    story.append(Paragraph(f"Clients moraux: {len(clients_moraux) if clients_moraux else 0}", styles['Normal']))
                    story.append(Paragraph(f"Total: {(len(clients_physiques) if clients_physiques else 0) + (len(clients_moraux) if clients_moraux else 0)}", styles['Normal']))
                    story.append(Spacer(1, 20))
                    
                    doc.build(story)
                    buffer.seek(0)
                    
                    st.download_button(
                        label="⭳ Télécharger Rapport PDF",
                        data=buffer.getvalue(),
                        file_name=f"rapport_clients_complet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                    st.success("✅ Rapport PDF généré avec succès !")
                else:
                    st.info("ℹ️ Aucune donnée à exporter")
            except Exception as e:
                st.error(f"✗ Erreur lors de l'export du rapport: {str(e)}")

def show():
    """Fonction principale d'affichage - VERSION FINALE CORRIGÉE"""
    apply_custom_css()
    
    # Titre principal avec style
    st.markdown("""
    <div class="title-container">
        <h1 class="title-text"> Gestion des Clients</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Menu de navigation
    menu_option = st.selectbox(
        "🗎 Choisir une section",
        [ "⚲⚲ Gestion Clients","🗎 Export PDF"],
        index=0,
        help="Sélectionnez la section que vous souhaitez utiliser"
    )
    
    # Affichage selon la sélection
    if menu_option =="🗎 Export PDF":
        export_clients_pdf()
    elif menu_option ==  "⚲⚲ Gestion Clients":
        show_stats()
        
        # Tabs pour séparer physiques et moraux
        tab1, tab2 = st.tabs([" Personnes Physiques", " Personnes Morales"])
        
        with tab1:
            gestion_clients_physiques()
        
        with tab2:
            gestion_clients_moraux()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.8em;'>"
        "© 2025 App Domiciliation - Tous droits réservés"
        "</div>", 
        unsafe_allow_html=True
    )

# Point d'entrée principal
if __name__ == "__main__":
    show()