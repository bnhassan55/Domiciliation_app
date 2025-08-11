import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from db import (get_all_contrats, ajouter_facture, get_all_factures, 
                modifier_facture, supprimer_facture, get_facture_by_id)
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
        <h1 class="dashboard-title">Gestion de la Facturation</h1>
    </div>
    """, unsafe_allow_html=True)
    # Tabs pour différentes actions
    tab1, tab2, tab4 = st.tabs([" Nouvelle Facture", " Liste des Factures", " Tableau de Bord"])
    
    with tab1:
        nouvelle_facture()
    
    with tab2:
        liste_factures()
    
    with tab4:
        tableau_bord_facturation()

def nouvelle_facture():
    """Formulaire de création d'une nouvelle facture"""
    st.subheader("Créer une Nouvelle Facture")
    
    # Récupérer les contrats actifs
    contrats = get_all_contrats()
    contrats_actifs = [c for c in contrats if c.get('statut') == 'Actif']
    
    if not contrats_actifs:
        st.warning("⚠️ Aucun contrat actif trouvé. Impossible de créer une facture.")
        return
    
    with st.form("form_nouvelle_facture"):
        # Sélection du contrat
        st.markdown("###  Contrat à Facturer")
        
        contrat_options = [f"{c['numero_contrat']} - {c.get('client_nom', 'N/A')} ({c['montant_mensuel']:.0f} DH/mois)" 
                          for c in contrats_actifs]
        selected_contrat = st.selectbox(
            "Sélectionner le contrat *",
            [""] + contrat_options
        )
        
        if selected_contrat:
            # Récupérer les détails du contrat sélectionné
            contrat_index = contrat_options.index(selected_contrat)
            contrat = contrats_actifs[contrat_index]
            
            # Afficher les infos du contrat
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Client:** {contrat.get('client_nom', 'N/A')}")
                st.info(f"**Type:** {contrat['type_service']}")
            with col2:
                st.info(f"**Montant mensuel:** {contrat['montant_mensuel']:.0f} DH")
                st.info(f"**Services:** {contrat.get('services_inclus', 'N/A')}")
        
        # Informations de la facture
        st.markdown("###  Détails de la Facture")
        
        col1, col2 = st.columns(2)
        
        with col1:
            numero_facture = st.text_input(
                "Numéro de Facture *",
                value=f"FACT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}",
                help="Numéro unique de la facture"
            )
            
            type_facture = st.selectbox(
                "Type de Facture *",
                ["", "Mensuelle", "Trimestrielle", "Semestrielle", "Annuelle", "Frais d'ouverture", "Ponctuelle"]
            )
            
            date_facture = st.date_input(
                "Date de Facture *",
                value=datetime.now().date()
            )
            
            date_echeance = st.date_input(
                "Date d'Échéance *",
                value=datetime.now().date() + timedelta(days=30)
            )
        
        with col2:
            periode_debut = st.date_input(
                "Période - Début",
                value=datetime.now().replace(day=1).date()
            )
            
            periode_fin = st.date_input(
                "Période - Fin",
                value=(datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            )
            
            # Calcul automatique du montant basé sur le contrat
            if selected_contrat and type_facture:
                montant_base = float(contrat['montant_mensuel'])
                if type_facture == "Trimestrielle":
                    montant_calcule = montant_base * 3
                elif type_facture == "Semestrielle":
                    montant_calcule = montant_base * 6
                elif type_facture == "Annuelle":
                    montant_calcule = montant_base * 12
                elif type_facture == "Frais d'ouverture":
                    montant_calcule = float(contrat.get('frais_ouverture', 0))
                else:
                    montant_calcule = montant_base
            else:
                montant_calcule = 0.0
            
            montant_ht = st.number_input(
                "Montant HT (DH) *",
                value=montant_calcule,
                min_value=0.0,
                step=50.0,
                format="%.2f"
            )
            
            taux_tva = st.number_input(
                "Taux TVA (%)",
                value=20.0,
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                format="%.1f"
            )
        
        # Calculs automatiques
        montant_tva = montant_ht * (taux_tva / 100)
        montant_ttc = montant_ht + montant_tva
        
        # Affichage des totaux
        st.markdown("###  Totaux")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Montant HT", f"{montant_ht:,.2f} DH")
        with col2:
            st.metric("TVA", f"{montant_tva:,.2f} DH")
        with col3:
            st.metric("**Total TTC**", f"{montant_ttc:,.2f} DH")
        
        # Détails supplémentaires
        st.markdown("###  Détails Supplémentaires")
        
        description = st.text_area(
            "Description/Commentaires",
            placeholder="Description des services facturés, commentaires...",
            height=100
        )
        
        mode_reglement = st.selectbox(
            "Mode de Règlement",
            ["Virement bancaire", "Chèque", "Espèces", "Carte bancaire", "Prélèvement"]
        )
        
        submit = st.form_submit_button("💾 Créer la Facture", use_container_width=True)
        
        if submit:
            # Validation
            erreurs = []
            
            if not selected_contrat:
                erreurs.append("Veuillez sélectionner un contrat")
            if not numero_facture.strip():
                erreurs.append("Le numéro de facture est obligatoire")
            if not type_facture:
                erreurs.append("Veuillez sélectionner un type de facture")
            if montant_ht <= 0:
                erreurs.append("Le montant HT doit être supérieur à 0")
            if date_echeance < date_facture:
                erreurs.append("La date d'échéance ne peut pas être antérieure à la date de facture")
            
            if erreurs:
                for erreur in erreurs:
                    st.error(f" {erreur}")
            else:
                # Préparer les données de la facture
                facture_data = {
                    'numero_facture': numero_facture.strip(),
                    'contrat_id': contrat['id'],
                    'client_id': contrat['client_id'],
                    'type_facture': type_facture,
                    'date_facture': str(date_facture),
                    'date_echeance': str(date_echeance),
                    'periode_debut': str(periode_debut),
                    'periode_fin': str(periode_fin),
                    'montant_ht': montant_ht,
                    'taux_tva': taux_tva,
                    'montant_tva': montant_tva,
                    'montant_ttc': montant_ttc,
                    'description': description.strip() if description else None,
                    'mode_reglement': mode_reglement,
                    'statut': 'En attente',
                    'date_creation': str(datetime.now().date())
                }
                
                if ajouter_facture(facture_data):
                    st.success("✅ Facture créée avec succès !")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(" Erreur lors de la création de la facture")

def modifier_facture_interface(facture_id):
    """Interface complète de modification d'une facture avec tous les champs modifiables"""
    facture = get_facture_by_id(facture_id)
    
    if not facture:
        st.error("✗ Facture non trouvée")
        return
    
    st.markdown(f"###  Modification de la Facture: {facture['numero_facture']}")
    
    # Récupérer la liste des contrats pour permettre le changement
    contrats = get_all_contrats()
    contrats_actifs = [c for c in contrats if c.get('statut') == 'Actif']
    
    with st.form(f"form_modifier_facture_{facture_id}"):
        st.markdown("#### 🗎 Informations Générales")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Numéro de facture modifiable
            numero_facture = st.text_input(
                "Numéro de Facture",
                value=facture.get('numero_facture', ''),
                help="Numéro unique de la facture"
            )
            
            # Type de facture modifiable
            types_facture = ["Mensuelle", "Trimestrielle", "Semestrielle", "Annuelle", 
                           "Frais d'ouverture", "Ponctuelle"]
            type_index = 0
            if facture.get('type_facture') in types_facture:
                type_index = types_facture.index(facture.get('type_facture'))
            
            type_facture = st.selectbox(
                "Type de Facture",
                types_facture,
                index=type_index
            )
            
            # Dates modifiables
            date_facture = st.date_input(
                "Date de Facture",
                value=datetime.strptime(facture.get('date_facture', '2024-01-01'), '%Y-%m-%d').date()
            )
            
            date_echeance = st.date_input(
                "Date d'Échéance",
                value=datetime.strptime(facture.get('date_echeance', '2024-01-01'), '%Y-%m-%d').date()
            )
        
        with col2:
            # Période de facturation
            periode_debut = st.date_input(
                "Période - Début",
                value=datetime.strptime(facture.get('periode_debut', '2024-01-01'), '%Y-%m-%d').date() if facture.get('periode_debut') else datetime.now().replace(day=1).date()
            )
            
            periode_fin = st.date_input(
                "Période - Fin",
                value=datetime.strptime(facture.get('periode_fin', '2024-01-01'), '%Y-%m-%d').date() if facture.get('periode_fin') else datetime.now().date()
            )
            
            # Mode de règlement
            modes_reglement = ["Virement bancaire", "Chèque", "Espèces", "Carte bancaire", "Prélèvement"]
            mode_index = 0
            if facture.get('mode_reglement') in modes_reglement:
                mode_index = modes_reglement.index(facture.get('mode_reglement'))
            
            mode_reglement = st.selectbox(
                "Mode de Règlement",
                modes_reglement,
                index=mode_index
            )
        
        # Changement de contrat (optionnel)
        st.markdown("#### 🗎 Contrat Associé")
        
        # Préparer les options de contrats
        contrat_options = []
        contrat_mapping = {}
        
        # Contrat actuel
        contrat_actuel = f"[ACTUEL] {facture.get('numero_contrat', 'Contrat actuel')} - {facture.get('client_nom', 'Client')}"
        contrat_options.append(contrat_actuel)
        contrat_mapping[contrat_actuel] = {
            'id': facture.get('contrat_id'), 
            'client_id': facture.get('client_id'),
            'current': True
        }
        
        # Autres contrats actifs
        if contrats_actifs:
            for contrat in contrats_actifs:
                if contrat['id'] != facture.get('contrat_id'):
                    label = f"🗎 {contrat['numero_contrat']} - {contrat.get('client_nom', 'N/A')} ({contrat['montant_mensuel']:.0f} DH/mois)"
                    contrat_options.append(label)
                    contrat_mapping[label] = {
                        'id': contrat['id'], 
                        'client_id': contrat['client_id'],
                        'montant': contrat['montant_mensuel']
                    }
        
        selected_contrat = st.selectbox(
            "Contrat",
            contrat_options,
            index=0,  # Contrat actuel par défaut
            help="Sélectionner un autre contrat ou garder le contrat actuel"
        )
        
        # Montants modifiables
        st.markdown("####  Montants")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            montant_ht = st.number_input(
                "Montant HT (DH)",
                min_value=0.0,
                step=50.0,
                value=float(facture.get('montant_ht', 0)),
                format="%.2f"
            )
        
        with col2:
            taux_tva = st.number_input(
                "Taux TVA (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                value=float(facture.get('taux_tva', 20.0)),
                format="%.1f"
            )
        
        # Calculs automatiques
        montant_tva = montant_ht * (taux_tva / 100)
        montant_ttc = montant_ht + montant_tva
        
        with col3:
            st.metric("Montant TTC", f"{montant_ttc:,.2f} DH")
        
        # Affichage des détails de calcul
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**TVA calculée:** {montant_tva:,.2f} DH")
        with col2:
            st.success(f"**Total TTC:** {montant_ttc:,.2f} DH")
        
        # Description modifiable
        st.markdown("#### 🗎 Description")
        
        description = st.text_area(
            "Description/Commentaires",
            value=facture.get('description', ''),
            height=100,
            placeholder="Description des services facturés, commentaires..."
        )
        
        # Statut modifiable
        st.markdown("####  Statut")
        
        statuts = ["En attente", "Payée", "En retard", "Annulée"]
        statut_index = 0
        if facture.get('statut') in statuts:
            statut_index = statuts.index(facture.get('statut'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            statut = st.selectbox(
                "Statut de la Facture",
                statuts,
                index=statut_index
            )
        
        with col2:
            # Date de paiement si facture payée
            date_paiement = None
            if statut == "Payée":
                date_paiement_actuelle = facture.get('date_paiement')
                if date_paiement_actuelle:
                    try:
                        date_paiement = st.date_input(
                            "Date de Paiement",
                            value=datetime.strptime(date_paiement_actuelle, '%Y-%m-%d').date()
                        )
                    except:
                        date_paiement = st.date_input("Date de Paiement", value=datetime.now().date())
                else:
                    date_paiement = st.date_input("Date de Paiement", value=datetime.now().date())
            elif facture.get('date_paiement'):
                st.info("💡 La date de paiement sera supprimée si le statut n'est pas 'Payée'")
        
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
                if 'editing_facture_id' in st.session_state:
                    del st.session_state['editing_facture_id']
                st.rerun()
        
        if submit:
            # Validation des données
            erreurs = []
            
            if not numero_facture.strip():
                erreurs.append("Le numéro de facture est obligatoire")
            if montant_ht <= 0:
                erreurs.append("Le montant HT doit être supérieur à 0")
            if date_echeance < date_facture:
                erreurs.append("La date d'échéance ne peut pas être antérieure à la date de facture")
            
            if erreurs:
                for erreur in erreurs:
                    st.error(f"✗ {erreur}")
            else:
                # Préparer les modifications
                contrat_info = contrat_mapping[selected_contrat]
                
                modifications = {
                    'numero_facture': numero_facture.strip(),
                    'type_facture': type_facture,
                    'date_facture': str(date_facture),
                    'date_echeance': str(date_echeance),
                    'periode_debut': str(periode_debut),
                    'periode_fin': str(periode_fin),
                    'montant_ht': montant_ht,
                    'taux_tva': taux_tva,
                    'montant_tva': montant_tva,
                    'montant_ttc': montant_ttc,
                    'description': description.strip() if description else None,
                    'mode_reglement': mode_reglement,
                    'statut': statut
                }
                
                # Ajouter contrat seulement si changé
                if not contrat_info.get('current', False):
                    modifications['contrat_id'] = contrat_info['id']
                    modifications['client_id'] = contrat_info['client_id']
                
                # Gérer la date de paiement
                if statut == "Payée" and date_paiement:
                    modifications['date_paiement'] = str(date_paiement)
                elif statut != "Payée":
                    modifications['date_paiement'] = None
                
                # Effectuer la modification
                success = modifier_facture(facture_id, modifications)
                
                if success:
                    st.success("✅ Facture modifiée avec succès!")
                    st.balloons()
                    if 'editing_facture_id' in st.session_state:
                        del st.session_state['editing_facture_id']
                    st.rerun()
                else:
                    st.error("✗ Erreur lors de la modification de la facture")

def liste_factures():
    """Liste et gestion des factures existantes - VERSION MODIFIÉE"""
    st.subheader("Liste des Factures")
    
    # Vérifier s'il y a une facture en cours de modification
    if 'editing_facture_id' in st.session_state:
        modifier_facture_interface(st.session_state['editing_facture_id'])
        return
    
    # Filtres (garder le code existant)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filtre_statut = st.selectbox(
            "Statut",
            ["Tous", "En attente", "Payée", "En retard", "Annulée"]
        )
    
    with col2:
        filtre_type = st.selectbox(
            "Type",
            ["Tous", "Mensuelle", "Trimestrielle", "Semestrielle", "Annuelle", "Frais d'ouverture", "Ponctuelle"]
        )
    
    with col3:
        filtre_mois = st.selectbox(
            "Mois",
            ["Tous"] + [f"{i:02d}/{datetime.now().year}" for i in range(1, 13)]
        )
    
    with col4:
        search_term = st.text_input(
            " Rechercher",
            placeholder="Numéro, client..."
        )
    
    # Récupérer les factures
    factures = get_all_factures()
    
    if not factures:
        st.info("Aucune facture enregistrée")
        return
    
    # Mettre à jour le statut des factures (en retard)
    for facture in factures:
        try:
            date_echeance = datetime.strptime(facture['date_echeance'], '%Y-%m-%d').date()
            if facture['statut'] == 'En attente' and date_echeance < datetime.now().date():
                facture['statut'] = 'En retard'
        except:
            pass
    
    # Appliquer les filtres
    if filtre_statut != "Tous":
        factures = [f for f in factures if f.get('statut') == filtre_statut]
    
    if filtre_type != "Tous":
        factures = [f for f in factures if f.get('type_facture') == filtre_type]
    
    if filtre_mois != "Tous":
        mois_filtre = filtre_mois.split('/')[0]
        factures = [f for f in factures if f.get('date_facture', '')[:7].endswith(f'-{mois_filtre}')]
    
    if search_term:
        factures = [f for f in factures if 
                   search_term.lower() in f.get('numero_facture', '').lower() or
                   search_term.lower() in str(f.get('client_nom', '')).lower()]
    
    if factures:
        # Préparer les données pour l'affichage
        df_data = []
        for facture in factures:
            # Badge de statut
            status_badges = {
                'En attente': '🟡',
                'Payée': '🟢',
                'En retard': '🔴',
                'Annulée': '⚫'
            }
            
            statut_badge = status_badges.get(facture['statut'], '?')
            
            df_data.append({
                'ID': facture['id'],
                'Numéro': facture['numero_facture'],
                'Client': facture.get('client_nom', 'N/A'),
                'Type': facture['type_facture'],
                'Date': facture['date_facture'],
                'Échéance': facture['date_echeance'],
                'Montant TTC': f"{facture['montant_ttc']:,.2f} DH",
                'Statut': f"{statut_badge} {facture['statut']}"
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Statistiques rapides
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_factures = len(factures)
            st.metric("Total Factures", total_factures)
        
        with col2:
            factures_payees = len([f for f in factures if f['statut'] == 'Payée'])
            st.metric("Payées", factures_payees)
        
        with col3:
            factures_attente = len([f for f in factures if f['statut'] == 'En attente'])
            st.metric("En attente", factures_attente)
        
        with col4:
            factures_retard = len([f for f in factures if f['statut'] == 'En retard'])
            st.metric("En retard", factures_retard, delta=-factures_retard if factures_retard > 0 else None)
        
        # Actions sur les factures - VERSION MODIFIÉE
        st.markdown("---")
        st.markdown("### Actions")
        
        facture_options = [f"{f['numero_facture']} - {f.get('client_nom', 'N/A')} ({f['montant_ttc']:.2f} DH)" 
                          for f in factures]
        selected_facture = st.selectbox("Sélectionner une facture", [""] + facture_options)
        
        if selected_facture:
            facture_id = next(f['id'] for f in factures 
                             if f"{f['numero_facture']} - {f.get('client_nom', 'N/A')} ({f['montant_ttc']:.2f} DH)" == selected_facture)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button(" Voir Détails"):
                    voir_details_facture(facture_id)
            
            with col2:
                if st.button(" Modifier", use_container_width=True):
                    st.session_state['editing_facture_id'] = facture_id
                    st.rerun()
            
            with col3:
                if st.button(" Marquer Payée"):
                    if modifier_facture(facture_id, {'statut': 'Payée', 'date_paiement': str(datetime.now().date())}):
                        st.success("✅ Facture marquée comme payée !")
                        st.rerun()
            
            with col4:
                if st.button(" Supprimer"):
                    if st.session_state.get('confirm_delete_facture') == facture_id:
                        if supprimer_facture(facture_id):
                            st.success("✅ Facture supprimée !")
                            st.rerun()
                        else:
                            st.error("✗ Erreur lors de la suppression")
                    else:
                        st.session_state.confirm_delete_facture = facture_id
                        st.warning("Cliquez à nouveau pour confirmer la suppression")
    else:
        st.info("Aucune facture ne correspond aux critères")

        
def tableau_bord_facturation():
    """Tableau de bord de la facturation"""
    st.subheader("Tableau de Bord Facturation")
    
    # Récupérer toutes les factures
    factures = get_all_factures()
    
    if not factures:
        st.info("Aucune donnée de facturation disponible")
        return
    
    # Calculs pour le tableau de bord
    aujourd_hui = datetime.now().date()
    debut_mois = aujourd_hui.replace(day=1)
    
    # Métriques du mois en cours
    factures_mois = [f for f in factures 
                    if datetime.strptime(f.get('date_facture', '1900-01-01'), '%Y-%m-%d').date() >= debut_mois]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ca_mois = sum(f['montant_ttc'] for f in factures_mois)
        st.metric("CA du Mois", f"{ca_mois:,.0f} DH")
    
    with col2:
        factures_payees_mois = [f for f in factures_mois if f.get('statut') == 'Payée']
        ca_encaisse = sum(f['montant_ttc'] for f in factures_payees_mois)
        st.metric("Encaissé", f"{ca_encaisse:,.0f} DH")
    
    with col3:
        factures_impayees = [f for f in factures if f.get('statut') in ['En attente', 'En retard']]
        ca_impaye = sum(f['montant_ttc'] for f in factures_impayees)
        st.metric("Impayés", f"{ca_impaye:,.0f} DH", delta=-ca_impaye if ca_impaye > 0 else None)
    
    with col4:
        nb_factures_mois = len(factures_mois)
        st.metric("Factures du Mois", nb_factures_mois)
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        # Évolution du CA sur les 6 derniers mois
        st.markdown("###  Évolution CA (6 derniers mois)")
        
        ca_evolution = []
        for i in range(6):
            mois_date = (aujourd_hui.replace(day=1) - timedelta(days=i*30))
            mois_str = mois_date.strftime('%Y-%m')
            
            ca_mois = sum(f['montant_ttc'] for f in factures 
                         if f.get('date_facture', '1900-01-01').startswith(mois_str))
            
            ca_evolution.insert(0, {
                'Mois': mois_date.strftime('%m/%Y'),
                'CA': ca_mois
            })
        
        if ca_evolution:
            import plotly.express as px
            fig = px.line(ca_evolution, x='Mois', y='CA', title="Évolution du CA")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Répartition des statuts de paiement
        st.markdown("###  Statuts de Paiement")
        
        statuts = {}
        for facture in factures:
            statut = facture.get('statut', 'Inconnu')
            statuts[statut] = statuts.get(statut, 0) + 1
        
        if statuts:
            fig = px.pie(values=list(statuts.values()), names=list(statuts.keys()), 
                        title="Répartition par Statut")
            st.plotly_chart(fig, use_container_width=True)
    
    # Alertes et notifications
    st.markdown("---")
    st.markdown("### 🚨 Alertes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Factures en retard
        factures_retard = [f for f in factures if f.get('statut') == 'En retard']
        if factures_retard:
            st.error(f"⚠️ {len(factures_retard)} facture(s) en retard de paiement")
            
            for facture in factures_retard[:3]:  # Afficher les 3 premières
                try:
                    date_echeance = datetime.strptime(facture['date_echeance'], '%Y-%m-%d').date()
                    jours_retard = (aujourd_hui - date_echeance).days
                    st.write(f"• {facture['numero_facture']} - {jours_retard}j de retard")
                except:
                    st.write(f"• {facture['numero_facture']} - Retard")
        else:
            st.success("✅ Aucune facture en retard")
    
    with col2:
        # Échéances à venir (7 prochains jours)
        echeances_proches = []
        for facture in factures:
            if facture.get('statut') == 'En attente':
                try:
                    date_echeance = datetime.strptime(facture['date_echeance'], '%Y-%m-%d').date()
                    jours_restants = (date_echeance - aujourd_hui).days
                    if 0 <= jours_restants <= 7:
                        echeances_proches.append(facture)
                except:
                    continue
        
        if echeances_proches:
            st.warning(f"🗋	 {len(echeances_proches)} échéance(s) dans les 7 prochains jours")
            
            for facture in echeances_proches:
                st.write(f"• {facture['numero_facture']} - {facture['date_echeance']}")
        else:
            st.info("🗋 Aucune échéance proche")
    

def voir_details_facture(facture_id):
    """Afficher les détails complets d'une facture"""
    facture = get_facture_by_id(facture_id)
    
    if not facture:
        st.error("Facture non trouvée")
        return
    
    with st.expander(f"🗎 Détails de la Facture {facture['numero_facture']}", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Numéro:** {facture['numero_facture']}")
            st.write(f"**Client:** {facture.get('client_nom', 'N/A')}")
            st.write(f"**Type:** {facture['type_facture']}")
            st.write(f"**Date de Facture:** {facture['date_facture']}")
            st.write(f"**Date d'Échéance:** {facture['date_echeance']}")
            st.write(f"**Statut:** {facture['statut']}")
        
        with col2:
            st.write(f"**Période:** {facture.get('periode_debut', 'N/A')} → {facture.get('periode_fin', 'N/A')}")
            st.write(f"**Montant HT:** {facture['montant_ht']:,.2f} DH")
            st.write(f"**TVA ({facture['taux_tva']:.1f}%):** {facture['montant_tva']:,.2f} DH")
            st.write(f"**Montant TTC:** {facture['montant_ttc']:,.2f} DH")
            st.write(f"**Mode de Règlement:** {facture.get('mode_reglement', 'N/A')}")
        
        if facture.get('description'):
            st.write("**Description:**")
            st.write(facture['description'])
        
        if facture.get('date_paiement'):
            st.success(f"✅ Payée le {facture['date_paiement']}")



