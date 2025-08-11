import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from db import (get_all_clients, ajouter_contrat, get_all_contrats, 
                supprimer_contrat, modifier_contrat, get_contrat_by_id)
import uuid
def apply_dashboard_css():
    """Appliquer uniquement les styles pour le titre et le bouton de déconnexion"""
    st.markdown("""
    <style>
    /* Style pour les titres - cohérent avec votre design existant */
    .title-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .dashboard-title {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        text-align: center;
    }
    
    .dashboard-subtitle {
        color: white;
        font-size: 1.2rem;
        margin: 0;
        text-align: center;
        opacity: 0.9;
    }
        div.stButton > button.secondary {
        background: #f8f9fa !important;
        color: #333 !important;
        border: 1px solid #ddd !important;
        transition: all 0.3s ease !important;
    }
    
    div.stButton > button.secondary:hover {
        background: #e9ecef !important;
        border-color: #ccc !important;
    }
    
    /* Style cohérent pour tous les boutons */
    div.stButton > button {
        font-weight: 500 !important;
        border-radius: 5px !important;
        padding: 0.5rem 1rem !important;
        margin: 0.25rem 0 !important;
    }
    /* Style pour le bouton d'actualisation - cohérent avec votre design */
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
def show():
    apply_dashboard_css()
    
    # Titre avec HTML personnalisé
    st.markdown("""
    <div class="title-container">
        <h1 class="dashboard-title"> Gestion des Contrats</h1>
    </div>
    """, unsafe_allow_html=True)
    # Tabs pour différentes actions
    tab1, tab2, tab3 = st.tabs([" Nouveau Contrat", " Liste des Contrats", " Statistiques"])
    
    with tab1:
        nouveau_contrat()
    
    with tab2:
        liste_contrats()
    
    with tab3:
        statistiques_contrats()

def nouveau_contrat():
    """Formulaire de création d'un nouveau contrat"""
    st.subheader("Créer un Nouveau Contrat")
    
    # Récupérer la liste des clients
    clients_physiques = get_all_clients("physique")
    clients_moraux = get_all_clients("moral")
    
    if not clients_physiques and not clients_moraux:
        st.warning("⚠️ Aucun client enregistré. Veuillez d'abord ajouter des clients.")
        return
    
    with st.form("form_nouveau_contrat"):
        # Sélection du client
        st.markdown("###  Informations Client")
        
        # Préparer les options de clients
        client_options = []
        client_mapping = {}
        
        if clients_physiques:
            for client in clients_physiques:
                label = f" {client['nom']} {client['prenom']} - CIN: {client['cin']}"
                client_options.append(label)
                client_mapping[label] = {'id': client['id'], 'type': 'physique', 'data': client}
        
        if clients_moraux:
            for client in clients_moraux:
                label = f" {client['raison_sociale']} - ICE: {client['ice']}"
                client_options.append(label)
                client_mapping[label] = {'id': client['id'], 'type': 'moral', 'data': client}
        
        selected_client = st.selectbox(
            "Sélectionner le client *",
            [""] + client_options,
            help="Choisissez le client pour ce contrat"
        )
        
        # Informations du contrat
        st.markdown("###  Détails du Contrat")
        
        col1, col2 = st.columns(2)
        
        with col1:
            numero_contrat = st.text_input(
                "Numéro de Contrat *",
                value=f"DOM-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}",
                help="Numéro unique du contrat"
            )
            
            type_service = st.selectbox(
                "Type de Service *",
                ["", "Domiciliation commerciale", "Domiciliation fiscale", 
                 "Domiciliation complète", "Bureau virtuel", "Autre"]
            )
            
            date_debut = st.date_input(
                "Date de Début *",
                value=datetime.now().date(),
                help="Date d'entrée en vigueur du contrat"
            )
            
            duree_mois = st.number_input(
                "Durée (en mois) *",
                min_value=1,
                max_value=120,
                value=12,
                help="Durée du contrat en mois"
            )
        
        with col2:
            montant_mensuel = st.number_input(
                "Montant Mensuel (DH) *",
                min_value=0.0,
                step=50.0,
                format="%.2f",
                help="Montant mensuel du service"
            )
            
            frais_ouverture = st.number_input(
                "Frais d'Ouverture (DH)",
                min_value=0.0,
                step=50.0,
                value=0.0,
                format="%.2f",
                help="Frais d'ouverture du dossier"
            )
            
            depot_garantie = st.number_input(
                "Dépôt de Garantie (DH)",
                min_value=0.0,
                step=50.0,
                value=0.0,
                format="%.2f",
                help="Dépôt de garantie demandé"
            )
            
            # Calcul automatique de la date de fin
            if date_debut:
                date_fin = date_debut + timedelta(days=duree_mois * 30)
                st.date_input("Date de Fin", value=date_fin, disabled=True)
        
        # Services inclus
        st.markdown("###  Services Inclus")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            courrier = st.checkbox(" Réception du courrier", value=True)
            telephone = st.checkbox(" Standard téléphonique")
            domiciliation_fiscale = st.checkbox(" Domiciliation fiscale")
        
        with col2:
            salle_reunion = st.checkbox(" Salle de réunion")
            assistance_admin = st.checkbox(" Assistance administrative")
            scan_courrier = st.checkbox(" Scan du courrier")
        
        with col3:
            transfert_courrier = st.checkbox(" Transfert du courrier")
            accueil_visiteurs = st.checkbox(" Accueil des visiteurs")
            autres_services = st.text_input("Autres services", placeholder="Spécifiez...")
        
        # Conditions particulières
        st.markdown("###  Conditions Particulières")
        conditions = st.text_area(
            "Conditions et remarques",
            height=100,
            placeholder="Conditions particulières, clauses spécifiques, etc."
        )
        
        # Statut du contrat
        statut = st.selectbox(
            "Statut *",
            ["Actif", "En attente", "Suspendu", "Résilié"],
            index=0
        )
        
        submit = st.form_submit_button("💾 Créer le Contrat", use_container_width=True)
        
        if submit:
            # Validation
            erreurs = []
            
            if not selected_client:
                erreurs.append("Veuillez sélectionner un client")
            if not numero_contrat.strip():
                erreurs.append("Le numéro de contrat est obligatoire")
            if not type_service:
                erreurs.append("Veuillez sélectionner un type de service")
            if montant_mensuel <= 0:
                erreurs.append("Le montant mensuel doit être supérieur à 0")
            
            if erreurs:
                for erreur in erreurs:
                    st.error(f"✗ {erreur}")
            else:
                # Préparer les données du contrat
                client_info = client_mapping[selected_client]
                
                # Services sélectionnés
                services_list = []
                if courrier:
                    services_list.append("Réception du courrier")
                if telephone:
                    services_list.append("Standard téléphonique")
                if domiciliation_fiscale:
                    services_list.append("Domiciliation fiscale")
                if salle_reunion:
                    services_list.append("Salle de réunion")
                if assistance_admin:
                    services_list.append("Assistance administrative")
                if scan_courrier:
                    services_list.append("Scan du courrier")
                if transfert_courrier:
                    services_list.append("Transfert du courrier")
                if accueil_visiteurs:
                    services_list.append("Accueil des visiteurs")
                if autres_services:
                    services_list.append(f"Autres: {autres_services}")
                
                contrat_data = {
                    'numero_contrat': numero_contrat.strip(),
                    'client_id': client_info['id'],
                    'client_type': client_info['type'],
                    'type_service': type_service,
                    'date_debut': str(date_debut),
                    'date_fin': str(date_fin),
                    'duree_mois': duree_mois,
                    'montant_mensuel': montant_mensuel,
                    'frais_ouverture': frais_ouverture,
                    'depot_garantie': depot_garantie,
                    'services_inclus': ', '.join(services_list),
                    'conditions': conditions.strip() if conditions else None,
                    'statut': statut,
                    'date_creation': str(datetime.now().date())
                }
                
                if ajouter_contrat(contrat_data):
                    st.success("✅ Contrat créé avec succès !")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(" Erreur lors de la création du contrat")

def modifier_contrat_interface(contrat_id):
    """Interface complète de modification d'un contrat avec tous les champs modifiables"""
    contrat = get_contrat_by_id(contrat_id)
    
    if not contrat:
        st.error("✗ Contrat non trouvé")
        return
    
    st.markdown(f"###  Modification du Contrat: {contrat['numero_contrat']}")
    
    # Récupérer la liste des clients pour permettre le changement
    clients_physiques = get_all_clients("physique")
    clients_moraux = get_all_clients("moral")
    
    with st.form(f"form_modifier_contrat_{contrat_id}"):
        st.markdown("#### 🗎 Informations Générales")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Numéro de contrat modifiable
            numero_contrat = st.text_input(
                "Numéro de Contrat",
                value=contrat.get('numero_contrat', ''),
                help="Numéro unique du contrat"
            )
            
            # Type de service modifiable
            services_options = ["Domiciliation commerciale", "Domiciliation fiscale", 
                               "Domiciliation complète", "Bureau virtuel", "Autre"]
            type_service_index = 0
            if contrat.get('type_service') in services_options:
                type_service_index = services_options.index(contrat.get('type_service'))
            
            type_service = st.selectbox(
                "Type de Service",
                services_options,
                index=type_service_index
            )
            
            # Dates modifiables
            date_debut = st.date_input(
                "Date de Début",
                value=datetime.strptime(contrat.get('date_debut', '2024-01-01'), '%Y-%m-%d').date(),
                help="Date d'entrée en vigueur du contrat"
            )
            
            duree_mois = st.number_input(
                "Durée (en mois)",
                min_value=1,
                max_value=120,
                value=int(contrat.get('duree_mois', 12)),
                help="Durée du contrat en mois"
            )
        
        with col2:
            # Montants modifiables
            montant_mensuel = st.number_input(
                "Montant Mensuel (DH)",
                min_value=0.0,
                step=50.0,
                value=float(contrat.get('montant_mensuel', 0)),
                format="%.2f"
            )
            
            frais_ouverture = st.number_input(
                "Frais d'Ouverture (DH)",
                min_value=0.0,
                step=50.0,
                value=float(contrat.get('frais_ouverture', 0)),
                format="%.2f"
            )
            
            depot_garantie = st.number_input(
                "Dépôt de Garantie (DH)",
                min_value=0.0,
                step=50.0,
                value=float(contrat.get('depot_garantie', 0)),
                format="%.2f"
            )
            
            # Calcul automatique de la date de fin
            if date_debut and duree_mois:
                date_fin = date_debut + timedelta(days=duree_mois * 30)
                st.date_input("Date de Fin (Calculée)", value=date_fin, disabled=True)
        
        # Changement de client (optionnel mais possible)
        st.markdown("#### ⚲⚲ Client Associé")
        
        # Préparer les options de clients
        client_options = []
        client_mapping = {}
        
        # Client actuel
        client_actuel = f"[ACTUEL] {contrat.get('client_nom', 'Client inconnu')}"
        client_options.append(client_actuel)
        client_mapping[client_actuel] = {
            'id': contrat.get('client_id'), 
            'type': contrat.get('client_type'),
            'current': True
        }
        
        # Autres clients physiques
        if clients_physiques:
            for client in clients_physiques:
                if client['id'] != contrat.get('client_id') or contrat.get('client_type') != 'physique':
                    label = f"⚲⚲ {client['nom']} {client['prenom']} - CIN: {client['cin']}"
                    client_options.append(label)
                    client_mapping[label] = {'id': client['id'], 'type': 'physique'}
        
        # Autres clients moraux
        if clients_moraux:
            for client in clients_moraux:
                if client['id'] != contrat.get('client_id') or contrat.get('client_type') != 'moral':
                    label = f" {client['raison_sociale']} - ICE: {client['ice']}"
                    client_options.append(label)
                    client_mapping[label] = {'id': client['id'], 'type': 'moral'}
        
        selected_client = st.selectbox(
            "Client",
            client_options,
            index=0,  # Client actuel par défaut
            help="Sélectionner un autre client ou garder le client actuel"
        )
        
        # Services inclus modifiables
        st.markdown("#### ⚙  Services Inclus")
        
        services_actuels = contrat.get('services_inclus', '').split(', ') if contrat.get('services_inclus') else []
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            courrier = st.checkbox(" Réception du courrier", 
                                 value="Réception du courrier" in services_actuels)
            telephone = st.checkbox(" Standard téléphonique",
                                  value="Standard téléphonique" in services_actuels)
            domiciliation_fiscale = st.checkbox(" Domiciliation fiscale",
                                              value="Domiciliation fiscale" in services_actuels)
        
        with col2:
            salle_reunion = st.checkbox(" Salle de réunion",
                                      value="Salle de réunion" in services_actuels)
            assistance_admin = st.checkbox(" Assistance administrative",
                                         value="Assistance administrative" in services_actuels)
            scan_courrier = st.checkbox(" Scan du courrier",
                                      value="Scan du courrier" in services_actuels)
        
        with col3:
            transfert_courrier = st.checkbox(" Transfert du courrier",
                                           value="Transfert du courrier" in services_actuels)
            accueil_visiteurs = st.checkbox(" Accueil des visiteurs",
                                          value="Accueil des visiteurs" in services_actuels)
            
            # Autres services
            autres_actuels = [s for s in services_actuels if s.startswith("Autres:")]
            autres_value = autres_actuels[0].replace("Autres:", "").strip() if autres_actuels else ""
            autres_services = st.text_input("➕ Autres services", 
                                           value=autres_value,
                                           placeholder="Spécifiez...")
        
        # Conditions particulières
        st.markdown("#### 🗎 Conditions et Statut")
        
        conditions = st.text_area(
            "Conditions Particulières",
            value=contrat.get('conditions', ''),
            height=100,
            placeholder="Conditions particulières, clauses spécifiques, etc."
        )
        
        # Statut modifiable
        statuts = ["Actif", "En attente", "Suspendu", "Résilié"]
        statut_index = 0
        if contrat.get('statut') in statuts:
            statut_index = statuts.index(contrat.get('statut'))
        
        statut = st.selectbox(
            "Statut",
            statuts,
            index=statut_index
        )
        
        # Boutons d'action
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            submit = st.form_submit_button("💾 Sauvegarder les Modifications", use_container_width=True)
        
        with col2:
            if st.form_submit_button("⟲ Réinitialiser", use_container_width=True):
                st.rerun()
        
        with col3:
            if st.form_submit_button("✗ Annuler", use_container_width=True):
                if 'editing_contract_id' in st.session_state:
                    del st.session_state['editing_contract_id']
                st.rerun()
        
        if submit:
            # Validation des données
            erreurs = []
            
            if not numero_contrat.strip():
                erreurs.append("Le numéro de contrat est obligatoire")
            if montant_mensuel <= 0:
                erreurs.append("Le montant mensuel doit être supérieur à 0")
            if duree_mois <= 0:
                erreurs.append("La durée doit être supérieure à 0")
            
            if erreurs:
                for erreur in erreurs:
                    st.error(f"✗ {erreur}")
            else:
                # Préparer les services sélectionnés
                services_list = []
                if courrier: services_list.append("Réception du courrier")
                if telephone: services_list.append("Standard téléphonique")
                if domiciliation_fiscale: services_list.append("Domiciliation fiscale")
                if salle_reunion: services_list.append("Salle de réunion")
                if assistance_admin: services_list.append("Assistance administrative")
                if scan_courrier: services_list.append("Scan du courrier")
                if transfert_courrier: services_list.append("Transfert du courrier")
                if accueil_visiteurs: services_list.append("Accueil des visiteurs")
                if autres_services: services_list.append(f"Autres: {autres_services}")
                
                # Calculer la nouvelle date de fin
                nouvelle_date_fin = date_debut + timedelta(days=duree_mois * 30)
                
                # Préparer les modifications
                client_info = client_mapping[selected_client]
                
                modifications = {
                    'numero_contrat': numero_contrat.strip(),
                    'type_service': type_service,
                    'date_debut': str(date_debut),
                    'date_fin': str(nouvelle_date_fin),
                    'duree_mois': duree_mois,
                    'montant_mensuel': montant_mensuel,
                    'frais_ouverture': frais_ouverture,
                    'depot_garantie': depot_garantie,
                    'services_inclus': ', '.join(services_list),
                    'conditions': conditions.strip() if conditions else None,
                    'statut': statut
                }
                
                # Ajouter client seulement si changé
                if not client_info.get('current', False):
                    modifications['client_id'] = client_info['id']
                    modifications['client_type'] = client_info['type']
                
                # Effectuer la modification
                success = modifier_contrat(contrat_id, modifications)
                
                if success:
                    st.success("✅ Contrat modifié avec succès!")
                    st.balloons()
                    if 'editing_contract_id' in st.session_state:
                        del st.session_state['editing_contract_id']
                    st.rerun()
                else:
                    st.error("✗ Erreur lors de la modification du contrat")


def liste_contrats():
    """Liste et gestion des contrats existants - VERSION MODIFIÉE"""
    st.subheader("Liste des Contrats")
    
    # Vérifier s'il y a un contrat en cours de modification
    if 'editing_contract_id' in st.session_state:
        modifier_contrat_interface(st.session_state['editing_contract_id'])
        return
    
    # Filtres existants (garder le code existant)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtre_statut = st.selectbox(
            "Filtrer par statut",
            ["Tous", "Actif", "En attente", "Suspendu", "Résilié"]
        )
    
    with col2:
        filtre_type = st.selectbox(
            "Filtrer par type",
            ["Tous", "Domiciliation commerciale", "Domiciliation fiscale", 
             "Domiciliation complète", "Bureau virtuel", "Autre"]
        )
    
    with col3:
        search_term = st.text_input(
            " Rechercher",
            placeholder="Numéro, client..."
        )
    
    # Récupérer les contrats (garder le code existant pour les filtres)
    contrats = get_all_contrats()
    
    if not contrats:
        st.info("Aucun contrat enregistré")
        return
    
    # Appliquer les filtres (garder le code existant)
    if filtre_statut != "Tous":
        contrats = [c for c in contrats if c.get('statut') == filtre_statut]
    
    if filtre_type != "Tous":
        contrats = [c for c in contrats if c.get('type_service') == filtre_type]
    
    if search_term:
        contrats = [c for c in contrats if 
                   search_term.lower() in c.get('numero_contrat', '').lower() or
                   search_term.lower() in str(c.get('client_nom', '')).lower()]
    
    if contrats:
        # Affichage du tableau (garder le code existant)
        df_data = []
        for contrat in contrats:
            try:
                date_fin = datetime.strptime(contrat['date_fin'], '%Y-%m-%d').date()
                jours_restants = (date_fin - datetime.now().date()).days
                statut_badge = "🟢" if jours_restants > 30 else "🟡" if jours_restants > 0 else "🔴"
            except:
                jours_restants = 0
                statut_badge = "?"
            
            df_data.append({
                'ID': contrat['id'],
                'Numéro': contrat['numero_contrat'],
                'Client': contrat.get('client_nom', 'N/A'),
                'Type': contrat['type_service'],
                'Début': contrat['date_debut'],
                'Fin': contrat['date_fin'],
                'Jours Restants': f"{statut_badge} {jours_restants}j",
                'Montant': f"{contrat['montant_mensuel']:.0f} DH/mois",
                'Statut': contrat['statut']
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Actions sur les contrats - VERSION MODIFIÉE
        st.markdown("---")
        st.markdown("### Actions")
        
        contrat_options = [f"{c['numero_contrat']} - {c.get('client_nom', 'N/A')}" for c in contrats]
        selected_contrat = st.selectbox("Sélectionner un contrat", [""] + contrat_options)
        
        if selected_contrat:
            contrat_id = next(c['id'] for c in contrats if f"{c['numero_contrat']} - {c.get('client_nom', 'N/A')}" == selected_contrat)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(" Voir Détails"):
                    voir_details_contrat(contrat_id)
            
            with col2:
                if st.button(" Modifier", use_container_width=True):
                    st.session_state['editing_contract_id'] = contrat_id
                    st.rerun()
            
            with col3:
                if st.button(" Supprimer", type="secondary"):
                    if st.session_state.get('confirm_delete') == contrat_id:
                        if supprimer_contrat(contrat_id):
                            st.success("✅ Contrat supprimé !")
                            st.rerun()
                        else:
                            st.error("✗ Erreur lors de la suppression")
                    else:
                        st.session_state.confirm_delete = contrat_id
                        st.warning("Cliquez à nouveau pour confirmer la suppression")
    else:
        st.info("Aucun contrat ne correspond aux critères de recherche")

def statistiques_contrats():
    """Affichage des statistiques des contrats"""
    st.subheader("Statistiques des Contrats")
    
    contrats = get_all_contrats()
    
    if not contrats:
        st.info("Aucune donnée disponible")
        return
    
    # Métriques générales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_contrats = len(contrats)
        st.metric("Total Contrats", total_contrats)
    
    with col2:
        contrats_actifs = len([c for c in contrats if c.get('statut') == 'Actif'])
        st.metric("Contrats Actifs", contrats_actifs)
    
    with col3:
        ca_mensuel = sum(float(c.get('montant_mensuel', 0)) for c in contrats if c.get('statut') == 'Actif')
        st.metric("CA Mensuel", f"{ca_mensuel:,.0f} DH")
    
    with col4:
        # Contrats expirant dans les 30 jours
        contrats_expirants = 0
        for contrat in contrats:
            try:
                date_fin = datetime.strptime(contrat['date_fin'], '%Y-%m-%d').date()
                if 0 <= (date_fin - datetime.now().date()).days <= 30:
                    contrats_expirants += 1
            except:
                continue
        
        st.metric("Expirent bientôt", contrats_expirants, delta=-contrats_expirants if contrats_expirants > 0 else None)
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        # Répartition par statut
        statuts = {}
        for contrat in contrats:
            statut = contrat.get('statut', 'Inconnu')
            statuts[statut] = statuts.get(statut, 0) + 1
        
        if statuts:
            import plotly.express as px
            fig = px.pie(
                values=list(statuts.values()),
                names=list(statuts.keys()),
                title="Répartition par Statut"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Répartition par type de service
        types_service = {}
        for contrat in contrats:
            type_serv = contrat.get('type_service', 'Inconnu')
            types_service[type_serv] = types_service.get(type_serv, 0) + 1
        
        if types_service:
            fig = px.bar(
                x=list(types_service.keys()),
                y=list(types_service.values()),
                title="Répartition par Type de Service"
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

def voir_details_contrat(contrat_id):
    """Afficher les détails complets d'un contrat"""
    contrat = get_contrat_by_id(contrat_id)
    
    if not contrat:
        st.error("Contrat non trouvé")
        return
    
    with st.expander(f" Détails du Contrat {contrat['numero_contrat']}", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Numéro:** {contrat['numero_contrat']}")
            st.write(f"**Client:** {contrat.get('client_nom', 'N/A')}")
            st.write(f"**Type de Service:** {contrat['type_service']}")
            st.write(f"**Statut:** {contrat['statut']}")
            st.write(f"**Date de Création:** {contrat.get('date_creation', 'N/A')}")
        
        with col2:
            st.write(f"**Période:** {contrat['date_debut']} → {contrat['date_fin']}")
            st.write(f"**Durée:** {contrat.get('duree_mois', 'N/A')} mois")
            st.write(f"**Montant Mensuel:** {contrat['montant_mensuel']} DH")
            
            if contrat.get('frais_ouverture', 0) > 0:
                st.write(f"**Frais d'Ouverture:** {contrat['frais_ouverture']} DH")
            if contrat.get('depot_garantie', 0) > 0:
                st.write(f"**Dépôt de Garantie:** {contrat['depot_garantie']} DH")
        
        if contrat.get('services_inclus'):
            st.write("**Services Inclus:**")
            services = contrat['services_inclus'].split(', ')
            for service in services:
                st.write(f"• {service}")
        
        if contrat.get('conditions'):
            st.write("**Conditions Particulières:**")
            st.write(contrat['conditions'])

