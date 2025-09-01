import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from db import (
    get_all_clients, get_all_contrats, get_all_factures, 
    get_statistiques, get_contrat_by_id, get_facture_by_id
)
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import io
import base64
import os

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
        <h1 class="dashboard-title">Reporting et Statistiqu</h1>
    </div>
    """, unsafe_allow_html=True)
    # Période de rapport
    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input(
            "Date de début",
            value=datetime.now().replace(day=1).date()
        )
    with col2:
        date_fin = st.date_input(
            "Date de fin",
            value=datetime.now().date()
        )
    
    # Tabs pour différents types de rapports
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        " Vue d'ensemble", 
        " Clients", 
        " Contrats", 
        " Financier",
        " Exports PDF"
    ])
    
    with tab1:
        vue_ensemble(date_debut, date_fin)
    
    with tab2:
        rapport_clients(date_debut, date_fin)
    
    with tab3:
        rapport_contrats(date_debut, date_fin)
    
    with tab4:
        rapport_financier(date_debut, date_fin)
    
    with tab5:
        exports_pdf()

def vue_ensemble(date_debut, date_fin):
    """Vue d'ensemble générale corrigée"""
    st.subheader("Vue d'Ensemble")
    
    # Récupérer les statistiques depuis la DB
    stats = get_statistiques()
    
    # Récupérer les données pour calculs spécifiques à la période
    contrats = get_all_contrats()
    factures = get_all_factures()
    
    # KPIs principaux
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Clients", stats.get('total_clients', 0))
        st.caption(f"Physiques: {stats.get('clients_physiques', 0)} | Moraux: {stats.get('clients_moraux', 0)}")
    
    with col2:
        st.metric("Contrats Actifs", stats.get('contrats_actifs', 0))
        st.caption(f"Total contrats: {stats.get('total_contrats', 0)}")
    
    with col3:
        # CA de la période sélectionnée
        ca_periode = 0
        if factures:
            for facture in factures:
                try:
                    date_facture = datetime.strptime(facture.get('date_facture', '1900-01-01'), '%Y-%m-%d').date()
                    if date_debut <= date_facture <= date_fin and facture.get('statut') == 'Payée':
                        ca_periode += facture.get('montant_ttc', 0)
                except:
                    continue
        
        st.metric("CA Période", f"{ca_periode:,.0f} DH")
        st.caption(f"CA Total: {stats.get('montant_encaisse', 0):,.0f} DH")
    
    with col4:
        # Taux de paiement sur la période
        taux_paiement = 0
        if factures:
            factures_periode = []
            for f in factures:
                try:
                    date_facture = datetime.strptime(f.get('date_facture', '1900-01-01'), '%Y-%m-%d').date()
                    if date_debut <= date_facture <= date_fin:
                        factures_periode.append(f)
                except:
                    continue
            
            if factures_periode:
                payees = len([f for f in factures_periode if f.get('statut') == 'Payée'])
                taux_paiement = (payees / len(factures_periode)) * 100
        
        st.metric("Taux de Paiement", f"{taux_paiement:.1f}%")
    
    # Alertes
    st.markdown("###  Alertes")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        contrats_expirants = stats.get('contrats_bientot_expires', 0)
        if contrats_expirants > 0:
            st.error(f"⚠️ {contrats_expirants} contrats expirent bientôt")
        else:
            st.success("✅ Aucun contrat n'expire prochainement")
    
    with col2:
        contrats_expires = stats.get('contrats_expires', 0)
        if contrats_expires > 0:
            st.warning(f" {contrats_expires} contrats expirés")
        else:
            st.success("✅ Aucun contrat expiré")
    
    with col3:
        ca_mensuel_actif = stats.get('ca_mensuel_actif', 0)
        st.info(f" CA mensuel récurrent: {ca_mensuel_actif:,.0f} DH")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        # Évolution du CA mensuel
        if factures:
            ca_mensuel = {}
            for facture in factures:
                if facture.get('statut') == 'Payée':
                    try:
                        date_facture = datetime.strptime(facture.get('date_facture', '1900-01-01'), '%Y-%m-%d')
                        mois = date_facture.strftime('%Y-%m')
                        if date_debut <= date_facture.date() <= date_fin:
                            ca_mensuel[mois] = ca_mensuel.get(mois, 0) + facture.get('montant_ttc', 0)
                    except:
                        continue
            
            if ca_mensuel:
                df_ca = pd.DataFrame(list(ca_mensuel.items()), columns=['Mois', 'CA'])
                fig = px.line(df_ca, x='Mois', y='CA', title='Évolution du CA Mensuel')
                fig.update_layout(xaxis_title="Mois", yaxis_title="CA (DH)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune donnée de CA pour la période sélectionnée")
        else:
            st.info("Aucune facture enregistrée")
    
    with col2:
        # Répartition des clients
        clients_physiques = stats.get('clients_physiques', 0)
        clients_moraux = stats.get('clients_moraux', 0)
        
        if clients_physiques > 0 or clients_moraux > 0:
            fig = px.pie(
                values=[clients_physiques, clients_moraux],
                names=['Personnes Physiques', 'Personnes Morales'],
                title='Répartition des Clients'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucun client enregistré")

def rapport_clients(date_debut, date_fin):
    """Rapport détaillé sur les clients - CORRIGÉ"""
    st.subheader("Rapport Clients")
    
    # Récupérer les clients physiques et moraux séparément
    clients_physiques = get_all_clients("physique")
    clients_moraux = get_all_clients("moral")
    
    # Combiner tous les clients avec leur type
    tous_clients = []
    
    # Ajouter les clients physiques
    if clients_physiques:
        for client in clients_physiques:
            client_data = dict(client)
            client_data['type'] = 'physique'
            client_data['nom_complet'] = f"{client.get('nom', '')} {client.get('prenom', '')}"
            client_data['identifiant'] = client.get('cin', '')
            tous_clients.append(client_data)
    
    # Ajouter les clients moraux
    if clients_moraux:
        for client in clients_moraux:
            client_data = dict(client)
            client_data['type'] = 'moral'
            client_data['nom_complet'] = client.get('raison_sociale', '')
            client_data['identifiant'] = client.get('ice', '')
            tous_clients.append(client_data)
    
    if not tous_clients:
        st.info("Aucun client enregistré")
        return
    
    # Filtrer par date de création
    clients_periode = []
    for client in tous_clients:
        try:
            date_creation_str = client.get('date_creation', '1900-01-01')
            # Gérer différents formats de date
            if ' ' in date_creation_str:
                date_creation_str = date_creation_str.split(' ')[0]
            date_creation = datetime.strptime(date_creation_str, '%Y-%m-%d').date()
            if date_debut <= date_creation <= date_fin:
                clients_periode.append(client)
        except:
            continue
    
    # Statistiques clients
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Clients", len(tous_clients))
    
    with col2:
        clients_physiques_count = len([c for c in tous_clients if c.get('type') == 'physique'])
        st.metric("Clients Physiques", clients_physiques_count)
    
    with col3:
        clients_moraux_count = len([c for c in tous_clients if c.get('type') == 'moral'])
        st.metric("Clients Moraux", clients_moraux_count)
    
    with col4:
        st.metric("Nouveaux (Période)", len(clients_periode))
    
    # Graphique d'évolution
    if clients_periode:
        # Évolution par mois
        evolution_mois = {}
        for client in clients_periode:
            try:
                date_creation_str = client.get('date_creation', '1900-01-01')
                if ' ' in date_creation_str:
                    date_creation_str = date_creation_str.split(' ')[0]
                date_creation = datetime.strptime(date_creation_str, '%Y-%m-%d')
                mois = date_creation.strftime('%Y-%m')
                evolution_mois[mois] = evolution_mois.get(mois, 0) + 1
            except:
                continue
        
        if evolution_mois:
            df_evolution = pd.DataFrame(list(evolution_mois.items()), columns=['Mois', 'Nouveaux'])
            df_evolution = df_evolution.sort_values('Mois')
            df_evolution['Cumul'] = df_evolution['Nouveaux'].cumsum()
            
            # Graphique avec double axe
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Bar(x=df_evolution['Mois'], y=df_evolution['Nouveaux'], name="Nouveaux clients"),
                secondary_y=False,
            )
            
            fig.add_trace(
                go.Scatter(x=df_evolution['Mois'], y=df_evolution['Cumul'], name="Cumul", mode='lines+markers'),
                secondary_y=True,
            )
            
            fig.update_layout(title_text="Évolution des Clients")
            fig.update_xaxes(title_text="Mois")
            fig.update_yaxes(title_text="Nouveaux clients", secondary_y=False)
            fig.update_yaxes(title_text="Total cumulé", secondary_y=True)
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Tableau détaillé des nouveaux clients
    if clients_periode:
        st.markdown("### Nouveaux Clients de la Période")
        
        # Préparer les données pour l'affichage
        tableau_clients = []
        for client in clients_periode:
            tableau_clients.append({
                'Type': 'Physique' if client['type'] == 'physique' else 'Moral',
                'Nom': client['nom_complet'],
                'Identifiant': client['identifiant'],
                'Téléphone': client.get('telephone', ''),
                'Email': client.get('email', ''),
                'Date Création': client.get('date_creation', '').split(' ')[0] if client.get('date_creation') else ''
            })
        
        df_clients = pd.DataFrame(tableau_clients)
        st.dataframe(df_clients, use_container_width=True, hide_index=True)
        
        # Export CSV
        csv = df_clients.to_csv(index=False)
        st.download_button(
            label="⭳ Télécharger la liste en CSV",
            data=csv,
            file_name=f"nouveaux_clients_{date_debut}_{date_fin}.csv",
            mime="text/csv"
        )
    
    # Répartition géographique ou par type
    col1, col2 = st.columns(2)
    
    with col1:
        # Répartition par type
        types_count = {
            'Personnes Physiques': len([c for c in tous_clients if c.get('type') == 'physique']),
            'Personnes Morales': len([c for c in tous_clients if c.get('type') == 'moral'])
        }
        
        if sum(types_count.values()) > 0:
            fig = px.pie(values=list(types_count.values()), names=list(types_count.keys()), 
                        title="Répartition par Type")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top 10 villes (si données d'adresse disponibles)
        villes = {}
        for client in tous_clients:
            adresse = client.get('adresse', '')
            if adresse:
                # Extraction simple de la ville (dernière partie après virgule)
                ville = adresse.split(',')[-1].strip() if ',' in adresse else adresse.strip()
                if ville:
                    villes[ville] = villes.get(ville, 0) + 1
        
        if villes:
            # Prendre les 10 premières villes
            top_villes = dict(sorted(villes.items(), key=lambda x: x[1], reverse=True)[:10])
            if top_villes:
                fig = px.bar(x=list(top_villes.keys()), y=list(top_villes.values()), 
                           title="Top 10 Villes")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données d'adresse insuffisantes pour l'analyse géographique")

def rapport_contrats(date_debut, date_fin):
    """Rapport détaillé sur les contrats - CORRIGÉ"""
    st.subheader("Rapport Contrats")
    
    contrats = get_all_contrats()
    
    if not contrats:
        st.info("Aucun contrat enregistré")
        return
    
    # Calculer les statistiques
    contrats_actifs = [c for c in contrats if c.get('statut') == 'Actif']
    contrats_expires = [c for c in contrats if c.get('statut') == 'Résilié']
    
    # Contrats créés dans la période
    contrats_periode = []
    for contrat in contrats:
        try:
            date_creation_str = contrat.get('date_creation', '1900-01-01')
            if ' ' in date_creation_str:
                date_creation_str = date_creation_str.split(' ')[0]
            date_creation = datetime.strptime(date_creation_str, '%Y-%m-%d').date()
            if date_debut <= date_creation <= date_fin:
                contrats_periode.append(contrat)
        except:
            continue
    
    # Contrats expirant bientôt
    contrats_expirants = []
    date_limite = datetime.now().date() + timedelta(days=60)
    
    for contrat in contrats_actifs:
        try:
            date_fin_contrat = datetime.strptime(contrat['date_fin'], '%Y-%m-%d').date()
            jours_restants = (date_fin_contrat - datetime.now().date()).days
            if 0 <= jours_restants <= 60:
                contrat_data = dict(contrat)
                contrat_data['jours_restants'] = jours_restants
                contrats_expirants.append(contrat_data)
        except:
            continue
    
    # Statistiques contrats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Contrats", len(contrats))
    
    with col2:
        st.metric("Contrats Actifs", len(contrats_actifs))
    
    with col3:
        st.metric("Nouveaux (Période)", len(contrats_periode))
    
    with col4:
        ca_mensuel = sum(float(c.get('montant_mensuel', 0)) for c in contrats_actifs)
        st.metric("CA Mensuel Récurrent", f"{ca_mensuel:,.0f} DH")
    
    # Alertes
    if contrats_expirants:
        st.warning(f"⚠️ {len(contrats_expirants)} contrats expirent dans les 60 prochains jours")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        # Répartition par statut
        statuts = {}
        for contrat in contrats:
            statut = contrat.get('statut', 'Inconnu')
            statuts[statut] = statuts.get(statut, 0) + 1
        
        if statuts:
            fig = px.pie(values=list(statuts.values()), names=list(statuts.keys()), 
                        title="Répartition par Statut")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Répartition par type de service
        types_service = {}
        for contrat in contrats:
            type_serv = contrat.get('type_service', 'Inconnu')
            types_service[type_serv] = types_service.get(type_serv, 0) + 1
        
        if types_service:
            fig = px.bar(x=list(types_service.keys()), y=list(types_service.values()), 
                        title="Répartition par Type de Service")
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    # Contrats expirant prochainement
    if contrats_expirants:
        st.markdown("### ⚠️ Contrats Expirant Prochainement (60 jours)")
        
        tableau_expirants = []
        for contrat in sorted(contrats_expirants, key=lambda x: x['jours_restants']):
            tableau_expirants.append({
                'Numéro': contrat['numero_contrat'],
                'Client': contrat.get('client_nom', 'N/A'),
                'Date Fin': contrat['date_fin'],
                'Jours Restants': contrat['jours_restants'],
                'Montant Mensuel': f"{contrat['montant_mensuel']:,.0f} DH",
                'Statut': contrat['statut']
            })
        
        df_expirants = pd.DataFrame(tableau_expirants)
        
        # Colorer selon l'urgence
        def color_urgence(val):
            try:
                if isinstance(val, str):
                    val = int(val)
                if val <= 7:
                    return 'background-color: #ffebee'  # Rouge clair
                elif val <= 30:
                    return 'background-color: #fff3e0'  # Orange clair
                else:
                    return 'background-color: #f3e5f5'  # Violet clair
            except (ValueError, TypeError):
                return ''

# CHANGEMENT PRINCIPAL: applymap au lieu d'apply
        styled_df = df_expirants.style.applymap(color_urgence, subset=['Jours Restants'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    else:
        st.success("✅ Aucun contrat n'expire dans les 60 prochains jours")
    
    # Évolution mensuelle des nouveaux contrats
    if contrats_periode:
        st.markdown("### Évolution des Nouveaux Contrats")
        
        evolution_contrats = {}
        for contrat in contrats_periode:
            try:
                date_creation_str = contrat.get('date_creation', '1900-01-01')
                if ' ' in date_creation_str:
                    date_creation_str = date_creation_str.split(' ')[0]
                date_creation = datetime.strptime(date_creation_str, '%Y-%m-%d')
                mois = date_creation.strftime('%Y-%m')
                evolution_contrats[mois] = evolution_contrats.get(mois, 0) + 1
            except:
                continue
        
        if evolution_contrats:
            df_evolution = pd.DataFrame(list(evolution_contrats.items()), columns=['Mois', 'Nouveaux Contrats'])
            df_evolution = df_evolution.sort_values('Mois')
            
            fig = px.bar(df_evolution, x='Mois', y='Nouveaux Contrats', 
                        title="Évolution Mensuelle des Nouveaux Contrats")
            st.plotly_chart(fig, use_container_width=True)

def rapport_financier(date_debut, date_fin):
    """Rapport financier détaillé - CORRIGÉ"""
    st.subheader("Rapport Financier")
    
    factures = get_all_factures()
    
    if not factures:
        st.info("Aucune facture enregistrée")
        return
    
    # Filtrer les factures par période
    factures_periode = []
    for facture in factures:
        try:
            date_facture = datetime.strptime(facture.get('date_facture', '1900-01-01'), '%Y-%m-%d').date()
            if date_debut <= date_facture <= date_fin:
                factures_periode.append(facture)
        except:
            continue
    
    # Calculs financiers
    ca_total = sum(f.get('montant_ttc', 0) for f in factures_periode)
    ca_paye = sum(f.get('montant_ttc', 0) for f in factures_periode if f.get('statut') == 'Payée')
    ca_attente = sum(f.get('montant_ttc', 0) for f in factures_periode if f.get('statut') in ['En attente', 'En retard'])
    ca_ht_total = sum(f.get('montant_ht', 0) for f in factures_periode)
    tva_total = sum(f.get('montant_tva', 0) for f in factures_periode)
    
    # Métriques financières
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("CA Total Période", f"{ca_total:,.0f} DH")
        st.caption(f"HT: {ca_ht_total:,.0f} DH")
    
    with col2:
        st.metric("CA Encaissé", f"{ca_paye:,.0f} DH")
        taux_encaissement = (ca_paye / ca_total * 100) if ca_total > 0 else 0
        st.caption(f"Taux: {taux_encaissement:.1f}%")
    
    with col3:
        st.metric("En Attente", f"{ca_attente:,.0f} DH")
        st.caption(f"TVA totale: {tva_total:,.0f} DH")
    
    with col4:
        nb_factures = len(factures_periode)
        panier_moyen = ca_total / nb_factures if nb_factures > 0 else 0
        st.metric("Panier Moyen", f"{panier_moyen:,.0f} DH")
        st.caption(f"Nb factures: {nb_factures}")
    
    # Graphiques financiers
    col1, col2 = st.columns(2)
    
    with col1:
        # Évolution mensuelle du CA
        if factures_periode:
            ca_mensuel = {}
            for facture in factures_periode:
                try:
                    date_facture = datetime.strptime(facture.get('date_facture', '1900-01-01'), '%Y-%m-%d')
                    mois = date_facture.strftime('%Y-%m')
                    ca_mensuel[mois] = ca_mensuel.get(mois, 0) + facture.get('montant_ttc', 0)
                except:
                    continue
            
            if ca_mensuel:
                df_ca = pd.DataFrame(list(ca_mensuel.items()), columns=['Mois', 'CA'])
                df_ca = df_ca.sort_values('Mois')
                fig = px.bar(df_ca, x='Mois', y='CA', title="CA Mensuel (TTC)")
                fig.update_layout(yaxis_title="CA (DH)")
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Répartition par statut de paiement
        statuts_paiement = {}
        for facture in factures_periode:
            statut = facture.get('statut', 'Inconnu')
            montant = facture.get('montant_ttc', 0)
            statuts_paiement[statut] = statuts_paiement.get(statut, 0) + montant
        
        if statuts_paiement:
            fig = px.pie(
                values=list(statuts_paiement.values()), 
                names=list(statuts_paiement.keys()), 
                title="Répartition par Statut de Paiement"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Analyse des retards de paiement
    factures_retard = []
    for facture in factures_periode:
        if facture.get('statut') in ['En attente', 'En retard']:
            try:
                date_echeance = datetime.strptime(facture.get('date_echeance', facture.get('date_facture', '1900-01-01')), '%Y-%m-%d').date()
                jours_retard = (datetime.now().date() - date_echeance).days
                if jours_retard > 0:
                    facture_data = dict(facture)
                    facture_data['jours_retard'] = jours_retard
                    factures_retard.append(facture_data)
            except:
                continue
    
    if factures_retard:
        st.markdown("###  Factures en Retard de Paiement")
        
        tableau_retards = []
        for facture in sorted(factures_retard, key=lambda x: x['jours_retard'], reverse=True):
            tableau_retards.append({
                'Numéro': facture['numero_facture'],
                'Client': facture.get('client_nom', 'N/A'),
                'Date Facture': facture['date_facture'],
                'Date Échéance': facture.get('date_echeance', 'N/A'),
                'Montant TTC': f"{facture['montant_ttc']:,.0f} DH",
                'Jours de Retard': facture['jours_retard'],
                'Statut': facture['statut']
            })
        
        df_retards = pd.DataFrame(tableau_retards)
        st.dataframe(df_retards, use_container_width=True, hide_index=True)
        
        # Total des impayés
        total_impayes = sum(f['montant_ttc'] for f in factures_retard)
        st.error(f" Total des impayés en retard: {total_impayes:,.0f} DH")
    
    # Tableau détaillé des factures de la période
    if factures_periode:
        st.markdown("###  Détail des Factures de la Période")
        
        # Options de filtrage
        col1, col2 = st.columns(2)
        with col1:
            statuts_disponibles = ['Tous'] + list(set(f.get('statut', '') for f in factures_periode))
            statut_filtre = st.selectbox("Filtrer par statut", statuts_disponibles)
        
        with col2:
            montant_min = st.number_input("Montant minimum (DH)", min_value=0, value=0)
        
        # Appliquer les filtres
        factures_filtrees = factures_periode
        if statut_filtre != 'Tous':
            factures_filtrees = [f for f in factures_filtrees if f.get('statut') == statut_filtre]
        if montant_min > 0:
            factures_filtrees = [f for f in factures_filtrees if f.get('montant_ttc', 0) >= montant_min]
        
        # Tableau des factures
        if factures_filtrees:
            tableau_factures = []
            for facture in factures_filtrees:
                tableau_factures.append({
                    'Numéro': facture['numero_facture'],
                    'Client': facture.get('client_nom', 'N/A'),
                    'Date': facture['date_facture'],
                    'Montant HT': f"{facture.get('montant_ht', 0):,.2f} DH",
                    'TVA': f"{facture.get('montant_tva', 0):,.2f} DH",
                    'Montant TTC': f"{facture.get('montant_ttc', 0):,.2f} DH",
                    'Statut': facture['statut'],
                    'Mode': facture.get('mode_reglement', 'N/A')
                })
            
            df_factures = pd.DataFrame(tableau_factures)
            st.dataframe(df_factures, use_container_width=True, hide_index=True)
            
            # Résumé des factures filtrées
            total_filtre = sum(f.get('montant_ttc', 0) for f in factures_filtrees)
            st.info(f" {len(factures_filtrees)} factures - Total: {total_filtre:,.0f} DH")
    
        else:
            st.info("Aucune facture ne correspond aux critères de filtrage")

def exports_pdf():
    """Section pour les exports PDF"""
    st.subheader(" Exports PDF")
    
    st.markdown("""
    Cette section vous permet de générer et télécharger des documents PDF 
    pour vos factures et contrats.
    """)
    
    tab1, tab2 = st.tabs([" Factures PDF", " Contrats PDF"])
    
    with tab1:
        export_factures_pdf()
    
    with tab2:
        export_contrats_pdf()

def export_factures_pdf():
    """Export des factures en PDF"""
    st.markdown("###  Export Factures PDF")
    
    factures = get_all_factures()
    
    if not factures:
        st.info("Aucune facture disponible")
        return
    
    # Sélection de la facture
    options_factures = [f"{f['numero_facture']} - {f.get('client_nom', 'N/A')} - {f['montant_ttc']:,.0f} DH" 
                       for f in factures]
    
    facture_selectionnee = st.selectbox(
        "Sélectionner une facture",
        options=range(len(factures)),
        format_func=lambda x: options_factures[x]
    )
    
    if st.button(" Générer PDF Facture", type="primary"):
        facture = factures[facture_selectionnee]
        pdf_buffer = generer_pdf_facture(facture)
        
        if pdf_buffer:
            st.success("✅ PDF généré avec succès!")
            
            # Bouton de téléchargement
            st.download_button(
                label="⭳ Télécharger la facture PDF",
                data=pdf_buffer.getvalue(),
                file_name=f"facture_{facture['numero_facture']}.pdf",
                mime="application/pdf"
            )
            
            # Aperçu (optionnel)
            st.markdown("###  Aperçu")
            pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
            pdf_display = f'<embed src="data:application/pdf;base64,{pdf_base64}" width="100%" height="600" type="application/pdf">'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.error(" Erreur lors de la génération du PDF")

def export_contrats_pdf():
    """Export des contrats en PDF"""
    st.markdown("###  Export Contrats PDF")
    
    contrats = get_all_contrats()
    
    if not contrats:
        st.info("Aucun contrat disponible")
        return
    
    # Sélection du contrat
    options_contrats = [f"{c['numero_contrat']} - {c.get('client_nom', 'N/A')} - {c['type_service']}" 
                       for c in contrats]
    
    contrat_selectionne = st.selectbox(
        "Sélectionner un contrat",
        options=range(len(contrats)),
        format_func=lambda x: options_contrats[x]
    )
    
    if st.button(" Générer PDF Contrat", type="primary"):
        contrat = contrats[contrat_selectionne]
        
        # Récupérer les détails complets du contrat
        contrat_details = get_contrat_by_id(contrat['id'])
        
        if contrat_details:
            pdf_buffer = generer_pdf_contrat(contrat_details)
            
            if pdf_buffer:
                st.success("✅ PDF généré avec succès!")
                
                # Bouton de téléchargement
                st.download_button(
                    label="⭳ Télécharger le contrat PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=f"contrat_{contrat['numero_contrat']}.pdf",
                    mime="application/pdf"
                )
                
                # Aperçu (optionnel)
                st.markdown("###  Aperçu")
                pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
                pdf_display = f'<embed src="data:application/pdf;base64,{pdf_base64}" width="100%" height="600" type="application/pdf">'
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.error(" Erreur lors de la génération du PDF")
        else:
            st.error(" Impossible de récupérer les détails du contrat")

def generer_pdf_facture(facture):
    """Génère un PDF pour une facture"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=2*cm, leftMargin=2*cm,
                              topMargin=2*cm, bottomMargin=2*cm)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12
        )
        
        normal_style = styles['Normal']
        
        # Contenu du PDF
        story = []
        
        # Ajouter le logo si disponible
        logo_path = os.path.join("static", "logo.jpg")
        if os.path.exists(logo_path):
            try:
                # Créer une table pour logo + informations société
                logo_img = ReportLabImage(logo_path, width=3*cm, height=3*cm)
                
                # Informations de l'entreprise
                company_info = Paragraph(
                    "<b>SOCIÉTÉ DE DOMICILIATION</b><br/>"
                    "Adresse de votre société<br/>"
                    "Ville, Code Postal<br/>"
                    "Téléphone: +212 XXX XXX XXX<br/>"
                    "Email: contact@domiciliation.ma",
                    normal_style
                )
                
                # Table avec logo et infos
                header_data = [[logo_img, company_info]]
                header_table = Table(header_data, colWidths=[4*cm, 10*cm])
                header_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                story.append(header_table)
                story.append(Spacer(1, 20))
                
            except Exception as e:
                # Si erreur avec l'image, utiliser texte simple
                story.append(Paragraph("SOCIÉTÉ DE DOMICILIATION", header_style))
                story.append(Paragraph("Adresse de votre société<br/>Ville, Code Postal<br/>Téléphone: +212 XXX XXX XXX", normal_style))
                story.append(Spacer(1, 20))
        else:
            # Pas de logo, utiliser texte simple
            story.append(Paragraph("SOCIÉTÉ DE DOMICILIATION", header_style))
            story.append(Paragraph("Adresse de votre société<br/>Ville, Code Postal<br/>Téléphone: +212 XXX XXX XXX", normal_style))
            story.append(Spacer(1, 20))
        
        # Titre
        story.append(Paragraph("FACTURE", title_style))
        story.append(Spacer(1, 20))
        
        # Informations de la facture
        info_facture = [
            ['Numéro de facture:', facture['numero_facture']],
            ['Date de facture:', facture['date_facture']],
            ['Date d\'échéance:', facture.get('date_echeance', 'N/A')],
            ['Statut:', facture['statut']]
        ]
        
        table_info = Table(info_facture, colWidths=[4*cm, 6*cm])
        table_info.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(table_info)
        story.append(Spacer(1, 20))
        
        # Informations client
        story.append(Paragraph("FACTURÉ À:", header_style))
        story.append(Paragraph(f"{facture.get('client_nom', 'N/A')}", normal_style))
        story.append(Spacer(1, 20))
        
        # Détails de la facture
        story.append(Paragraph("DÉTAILS:", header_style))
        
        details_data = [
            ['Description', 'Période', 'Montant HT', 'TVA', 'Montant TTC'],
            [
                facture.get('description', facture.get('type_facture', 'Service de domiciliation')),
                f"{facture.get('periode_debut', '')} - {facture.get('periode_fin', '')}",
                f"{facture.get('montant_ht', 0):,.2f} DH",
                f"{facture.get('montant_tva', 0):,.2f} DH",
                f"{facture.get('montant_ttc', 0):,.2f} DH"
            ]
        ]
        
        table_details = Table(details_data, colWidths=[4*cm, 4*cm, 2.5*cm, 2*cm, 3*cm])
        table_details.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTSIZE', (0, 1), (1, 1), 9),  # Police légèrement plus petite pour les données
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        story.append(table_details)
        story.append(Spacer(1, 30))
        
        # Total
        total_data = [
            ['Sous-total HT:', f"{facture.get('montant_ht', 0):,.2f} DH"],
            [f'TVA ({facture.get("taux_tva", 20)}%):', f"{facture.get('montant_tva', 0):,.2f} DH"],
            ['TOTAL TTC:', f"{facture.get('montant_ttc', 0):,.2f} DH"]
        ]
        
        table_total = Table(total_data, colWidths=[8*cm, 4*cm])
        table_total.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ]))
        
        story.append(table_total)
        story.append(Spacer(1, 30))
        
        # Mode de règlement
        story.append(Paragraph(f"Mode de règlement: {facture.get('mode_reglement', 'Virement')}", normal_style))
        
        # Pied de page
        story.append(Spacer(1, 50))
        story.append(Paragraph("Merci pour votre confiance!", normal_style))
        
        # Construire le PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        st.error(f"Erreur lors de la génération du PDF: {e}")
        return None
    
##################################################
##################################################
##################################################

def format_periode(debut, fin):
    """Formate la période sur plusieurs lignes"""
    try:
        if debut and fin:
            debut_dt = datetime.strptime(debut, '%Y-%m-%d')
            fin_dt = datetime.strptime(fin, '%Y-%m-%d')
            return f"Du {debut_dt.strftime('%d/%m/%Y')}\nAu {fin_dt.strftime('%d/%m/%Y')}"
        return "N/A"
    except:
        return f"{debut} -\n{fin}" if debut and fin else "N/A"
def format_periode_multiline(debut, fin):
    """Formate la période sur plusieurs lignes"""
    try:
        if debut and fin:
            debut_dt = datetime.strptime(debut, '%Y-%m-%d')
            fin_dt = datetime.strptime(fin, '%Y-%m-%d')
            return f"Du {debut_dt.strftime('%d/%m/%Y')}<br/>Au {fin_dt.strftime('%d/%m/%Y')}"
        return "N/A"
    except:
        return f"Du {debut}<br/>Au {fin}" if debut and fin else "N/A"
    
##################################################
##################################################
##################################################
# Puis utilisez-la dans details_data :
def generer_pdf_contrat(contrat):
    """Génère un PDF pour un contrat"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                              rightMargin=2*cm, leftMargin=2*cm,
                              topMargin=2*cm, bottomMargin=2*cm)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=12
        )
        
        normal_style = styles['Normal']
        
        # Contenu du PDF
        story = []
        
        # Ajouter le logo si disponible
        logo_path = os.path.join("static", "logo.jpg")
        if os.path.exists(logo_path):
            try:
                # Créer une table pour logo + informations société
                logo_img = ReportLabImage(logo_path, width=3*cm, height=3*cm)
                
                # Informations de l'entreprise
                company_info = Paragraph(
                    "<b>SOCIÉTÉ DE DOMICILIATION</b><br/>"
                    "Adresse de votre société<br/>"
                    "Ville, Code Postal<br/>"
                    "Téléphone: +212 XXX XXX XXX<br/>"
                    "Email: contact@domiciliation.ma<br/>"
                    "RC: XXXXXXXXX - IF: XXXXXXXXX",
                    normal_style
                )
                
                # Table avec logo et infos
                header_data = [[logo_img, company_info]]
                header_table = Table(header_data, colWidths=[4*cm, 10*cm])
                header_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                story.append(header_table)
                story.append(Spacer(1, 20))
                
            except Exception as e:
                # Si erreur avec l'image, utiliser texte simple
                story.append(Paragraph("SOCIÉTÉ DE DOMICILIATION", header_style))
                story.append(Paragraph("Adresse de votre société<br/>Ville, Code Postal<br/>Téléphone: +212 XXX XXX XXX", normal_style))
                story.append(Spacer(1, 20))
        else:
            # Pas de logo, utiliser texte simple
            story.append(Paragraph("SOCIÉTÉ DE DOMICILIATION", header_style))
            story.append(Paragraph("Adresse de votre société<br/>Ville, Code Postal<br/>Téléphone: +212 XXX XXX XXX", normal_style))
            story.append(Spacer(1, 20))
        
        # Titre
        story.append(Paragraph("CONTRAT DE DOMICILIATION", title_style))
        story.append(Spacer(1, 20))
        
        # Informations du contrat
        story.append(Paragraph("INFORMATIONS DU CONTRAT", header_style))
        
        info_contrat = [
            ['Numéro de contrat:', contrat['numero_contrat']],
            ['Type de service:', contrat['type_service']],
            ['Date de début:', contrat['date_debut']],
            ['Date de fin:', contrat['date_fin']],
            ['Durée:', f"{contrat.get('duree_mois', 12)} mois"],
            ['Statut:', contrat['statut']]
        ]
        
        table_info = Table(info_contrat, colWidths=[5*cm, 7*cm])
        table_info.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(table_info)
        story.append(Spacer(1, 20))
        
        # Informations client
        story.append(Paragraph("INFORMATIONS CLIENT", header_style))
        
        client_info = [
            ['Nom/Raison sociale:', contrat.get('client_nom', 'N/A')],
            ['Identifiant:', contrat.get('client_identifiant', 'N/A')],
            ['Téléphone:', contrat.get('client_telephone', 'N/A')],
            ['Email:', contrat.get('client_email', 'N/A')],
            ['Adresse:', contrat.get('client_adresse', 'N/A')[:50] + '...' if len(contrat.get('client_adresse', '')) > 50 else contrat.get('client_adresse', 'N/A')]
        ]
        
        table_client = Table(client_info, colWidths=[5*cm, 7*cm])
        table_client.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(table_client)
        story.append(Spacer(1, 20))
        
        # Conditions financières
        story.append(Paragraph("CONDITIONS FINANCIÈRES", header_style))
        
        financier_info = [
            ['Montant mensuel:', f"{contrat.get('montant_mensuel', 0):,.2f} DH"],
            ['Frais d\'ouverture:', f"{contrat.get('frais_ouverture', 0):,.2f} DH"],
            ['Dépôt de garantie:', f"{contrat.get('depot_garantie', 0):,.2f} DH"],
            ['Total sur la durée:', f"{float(contrat.get('montant_mensuel', 0)) * int(contrat.get('duree_mois', 12)):,.2f} DH"]
        ]
        
        table_financier = Table(financier_info, colWidths=[5*cm, 7*cm])
        table_financier.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ]))
        
        story.append(table_financier)
        story.append(Spacer(1, 20))
        
        # Services inclus
        if contrat.get('services_inclus'):
            story.append(Paragraph("SERVICES INCLUS", header_style))
            story.append(Paragraph(contrat['services_inclus'], normal_style))
            story.append(Spacer(1, 15))
        
        # Conditions particulières
        if contrat.get('conditions'):
            story.append(Paragraph("CONDITIONS PARTICULIÈRES", header_style))
            story.append(Paragraph(contrat['conditions'], normal_style))
            story.append(Spacer(1, 15))
        
        # Conditions générales (ajout standard)
        story.append(Paragraph("CONDITIONS GÉNÉRALES", header_style))
        conditions_generales = """
        1. Le présent contrat prend effet à la date de signature et se renouvelle automatiquement sauf résiliation.
        2. Le client s'engage à régler les factures dans les délais convenus.
        3. La société de domiciliation s'engage à fournir les services convenus avec professionnalisme.
        4. Toute modification du contrat doit faire l'objet d'un avenant écrit et signé par les deux parties.
        5. En cas de litige, les tribunaux de [Ville] seront seuls compétents.
        """
        story.append(Paragraph(conditions_generales, normal_style))
        story.append(Spacer(1, 20))
        
        # Signatures
        story.append(Paragraph("SIGNATURES", header_style))
        
        signatures_data = [
            ['Le Client', 'La Société'],
            ['', ''],
            ['Date et signature:', 'Date et signature:'],
            ['', '']
        ]
        
        table_signatures = Table(signatures_data, colWidths=[6*cm, 6*cm], rowHeights=[0.8*cm, 2*cm, 0.8*cm, 1*cm])
        table_signatures.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(table_signatures)
        
        # Pied de page
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Contrat généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", 
                             ParagraphStyle('Footer', parent=normal_style, fontSize=8, alignment=1)))
        
        # Construire le PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        st.error(f"Erreur lors de la génération du PDF: {e}")
        return None