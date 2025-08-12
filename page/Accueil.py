import streamlit as st
from db import get_statistiques, get_all_contrats, get_contrats_expirants
from utils import formater_montant, get_statut_contrat
from datetime import datetime, timedelta


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
    
    /* Styles pour les icônes professionnelles */
    .metric-icon {
        display: inline-block;
        width: 20px;
        text-align: center;
        margin-right: 8px;
        font-weight: bold;
        color: #667eea;
    }
    
    .status-icon {
        display: inline-block;
        width: 16px;
        text-align: center;
        margin-right: 6px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)


def show():
    apply_dashboard_css()
    
    # Titre avec HTML personnalisé
    st.markdown("""
    <div class="title-container">
        <h1 class="dashboard-title">Tableau de Bord salah</h1>
    </div>
    """, unsafe_allow_html=True)
    
    stats = get_statistiques()
    
    if not stats or stats.get('total_clients', 0) == 0:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); 
                    border: 1px solid #3b82f6; border-radius: 10px; 
                    padding: 2rem; margin: 2rem 0; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
            <h3>▶ Bienvenue dans votre espace de gestion !</h3>
            <p>Commencez par ajouter vos premiers clients et contrats pour voir vos statistiques apparaître.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Pour commencer :")
        st.markdown("1. ◦ Ajoutez des clients dans la section **Clients**")
        st.markdown("2. ◦ Créez des contrats dans la section **Contrats**")
        st.markdown("3. ◦ Enregistrez les paiements")
        return
    
    # === MÉTRIQUES PRINCIPALES ===
    st.markdown("### ▪ Vue d'ensemble")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="◦ Total Clients", 
            value=stats.get('total_clients', 0),
            help="Nombre total de clients (physiques + moraux)"
        )
        
    with col2:
        st.metric(
            label="□ Contrats Actifs", 
            value=stats.get('contrats_actifs', 0),
            help="Contrats en cours et valides"
        )
        
    with col3:
        ca_mensuel = stats.get('ca_mensuel_actif', 0)
        st.metric(
            label=" CA Mensuel (MAD)", 
            value=formater_montant(ca_mensuel),
            help="Chiffre d'affaires mensuel des contrats actifs"
        )
        
    with col4:
        montant_encaisse = stats.get('montant_encaisse', 0)
        st.metric(
            label="✓ Encaissé", 
            value=formater_montant(montant_encaisse),
            help="Total des paiements reçus"
        )
    
    # === DÉTAILS PAR TYPE ===
    st.markdown("---")
    st.markdown("### ▪ Répartition des clients")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="◉ Clients Physiques", 
            value=stats.get('clients_physiques', 0)
        )
        
    with col2:
        st.metric(
            label="■ Clients Moraux", 
            value=stats.get('clients_moraux', 0)
        )
        
    with col3:
        ca_potentiel = stats.get('ca_total', 0)
        st.metric(
            label="◆ CA Potentiel", 
            value=formater_montant(ca_potentiel),
            help="Chiffre d'affaires potentiel total des contrats actifs"
        )
    
    # === ALERTES ET NOTIFICATIONS ===
    st.markdown("---")
    st.markdown("### ▪ Alertes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        contrats_expires = stats.get('contrats_expires', 0)
        if contrats_expires > 0:
            st.error(f"✗ **{contrats_expires}** contrat(s) expiré(s)")
        else:
            st.success("✓ Aucun contrat expiré")
    
    with col2:
        contrats_bientot_expires = stats.get('contrats_bientot_expires', 0)
        if contrats_bientot_expires > 0:
            st.warning(f"⚠ **{contrats_bientot_expires}** contrat(s) expirent bientôt")
        else:
            st.success("✓ Aucun contrat à renouveler prochainement")
    
    # === CONTRATS EXPIRANTS ===
    if contrats_bientot_expires > 0:
        st.markdown("### ⏱ Contrats à renouveler")
        
        contrats_expirants = get_contrats_expirants(30)
        
        for contrat in contrats_expirants[:5]:  # Afficher les 5 premiers
            col1, col2, col3 = st.columns([3, 2, 2])
            
            with col1:
                st.write(f"**{contrat['numero_contrat']}**")
                st.write(f"Client: {contrat['client_nom']}")
                
            with col2:
                st.write(f"Expire le: **{contrat['date_fin']}**")
                jours_restants = int(contrat.get('jours_restants', 0))
                if jours_restants <= 7:
                    st.error(f"🔴 {jours_restants} jour(s)")
                elif jours_restants <= 30:
                    st.warning(f"🟡 {jours_restants} jour(s)")
                
            with col3:
                montant = contrat.get('montant_mensuel', 0)
                st.write(f"**{formater_montant(montant)}/mois**")
    
    # === CONTRATS RÉCENTS ===
    st.markdown("---")
    st.markdown("### ▪ Contrats Récents")
    
    contrats = get_all_contrats()[:8]  # Les 8 derniers
    
    if contrats:
        for i, contrat in enumerate(contrats):
            with st.expander(f"□ {contrat['numero_contrat']} - {contrat['client_nom']}", expanded=(i < 3)):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Client:** {contrat['client_nom']}")
                    st.write(f"**Type:** {contrat['type_service']}")
                    
                with col2:
                    st.write(f"**Début:** {contrat['date_debut']}")
                    st.write(f"**Fin:** {contrat['date_fin']}")
                    
                with col3:
                    montant_mensuel = contrat.get('montant_mensuel', 0)
                    duree_mois = contrat.get('duree_mois', 1)
                    montant_total = montant_mensuel * duree_mois
                    
                    st.write(f"**Mensuel:** {formater_montant(montant_mensuel)}")
                    st.write(f"**Total:** {formater_montant(montant_total)}")
                
                # Statut avec couleur
                statut_info = get_statut_contrat(contrat['date_fin'], contrat['statut'])
                if statut_info['couleur'] == 'green':
                    st.success(f"✓ {statut_info['statut']}")
                elif statut_info['couleur'] == 'orange':
                    st.warning(f"⚠ {statut_info['statut']}")
                elif statut_info['couleur'] == 'red':
                    st.error(f"✗ {statut_info['statut']}")
                else:
                    st.info(f"◦ {statut_info['statut']}")
    else:
        st.info("Aucun contrat enregistré")
    
    # === RÉSUMÉ FINANCIER ===
    st.markdown("---")
    st.markdown("### ▪ Résumé Financier")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label=" Total Encaissé (MAD)",
            value=formater_montant(stats.get('montant_encaisse', 0))
        )
        
    with col2:
        ca_mensuel = stats.get('ca_mensuel_actif', 0)
        ca_annuel = ca_mensuel * 12
        st.metric(
            label="▣ CA Annuel Prévisionnel",
            value=formater_montant(ca_annuel)
        )
        
    with col3:
        # Taux d'encaissement (approximatif)
        ca_potentiel = stats.get('ca_total', 0)
        if ca_potentiel > 0:
            taux = (stats.get('montant_encaisse', 0) / ca_potentiel) * 100
            st.metric(
                label="▲ Taux d'Encaissement",
                value=f"{taux:.1f}%"
            )
        else:
            st.metric(
                label="▲ Taux d'Encaissement",
                value="0%"
            )
    
    # Bouton de rafraîchissement
    st.markdown("---")
    if st.button("⟲ Actualiser les données"):
        st.rerun()

if __name__ == "__main__":
    show()