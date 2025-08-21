from datetime import datetime, timedelta
from typing import Dict, Any

def formater_montant(montant: float) -> str:
    """
    Formate un montant en dirhams marocains
    
    Args:
        montant (float): Le montant à formater
        
    Returns:
        str: Le montant formaté (ex: "1 500,00 DH")
    """
    if montant is None:
        return "0,00 DH"
    
    try:
        # Convertir en float si ce n'est pas déjà fait
        montant = float(montant)
        
        # Formater avec séparateur de milliers et 2 décimales
        return f"{montant:,.2f} DH".replace(",", " ").replace(".", ",")
    except (ValueError, TypeError):
        return "0,00 DH"

def get_statut_contrat(date_fin: str, statut_actuel: str = "Actif") -> Dict[str, Any]:
    """
    Détermine le statut d'un contrat selon sa date de fin
    
    Args:
        date_fin (str): Date de fin du contrat au format YYYY-MM-DD
        statut_actuel (str): Statut actuel du contrat
        
    Returns:
        Dict: Informations sur le statut (statut, couleur, badge)
    """
    try:
        # Si le statut n'est pas "Actif", retourner le statut actuel
        if statut_actuel != "Actif":
            couleurs = {
                "Résilié": "red",
                "Suspendu": "orange", 
                "En attente": "blue"
            }
            badges = {
                "Résilié": "❌",
                "Suspendu": "⏸️",
                "En attente": "⏳"
            }
            
            return {
                "statut": statut_actuel,
                "couleur": couleurs.get(statut_actuel, "gray"),
                "badge": badges.get(statut_actuel, "ℹ️")
            }
        
        # Convertir la date de fin
        if isinstance(date_fin, str):
            date_fin_obj = datetime.strptime(date_fin, "%Y-%m-%d")
        else:
            date_fin_obj = date_fin
            
        date_actuelle = datetime.now()
        jours_restants = (date_fin_obj - date_actuelle).days
        
        # Déterminer le statut selon les jours restants
        if jours_restants < 0:
            return {
                "statut": "Expiré",
                "couleur": "red",
                "badge": "❌"
            }
        elif jours_restants <= 7:
            return {
                "statut": f"Expire dans {jours_restants} jour(s)",
                "couleur": "red",
                "badge": "🔴"
            }
        elif jours_restants <= 30:
            return {
                "statut": f"Expire dans {jours_restants} jour(s)",
                "couleur": "orange", 
                "badge": "🟡"
            }
        else:
            return {
                "statut": "Actif",
                "couleur": "green",
                "badge": "✅"
            }
            
    except (ValueError, TypeError) as e:
        return {
            "statut": "Erreur de date",
            "couleur": "gray",
            "badge": "⚠️"
        }

def calculer_jours_restants(date_fin: str) -> int:
    """
    Calcule le nombre de jours restants jusqu'à une date
    
    Args:
        date_fin (str): Date de fin au format YYYY-MM-DD
        
    Returns:
        int: Nombre de jours restants (négatif si expiré)
    """
    try:
        if isinstance(date_fin, str):
            date_fin_obj = datetime.strptime(date_fin, "%Y-%m-%d")
        else:
            date_fin_obj = date_fin
            
        date_actuelle = datetime.now()
        return (date_fin_obj - date_actuelle).days
        
    except (ValueError, TypeError):
        return 0

def formater_date(date_str: str, format_sortie: str = "%d/%m/%Y") -> str:
    """
    Formate une date pour l'affichage
    
    Args:
        date_str (str): Date au format YYYY-MM-DD
        format_sortie (str): Format de sortie souhaité
        
    Returns:
        str: Date formatée
    """
    try:
        if isinstance(date_str, str):
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            date_obj = date_str
            
        return date_obj.strftime(format_sortie)
        
    except (ValueError, TypeError):
        return date_str if date_str else ""

def valider_email(email: str) -> bool:
    """
    Valide un format d'email simple
    
    Args:
        email (str): Adresse email à valider
        
    Returns:
        bool: True si valide, False sinon
    """
    if not email:
        return True  # Email optionnel
        
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def valider_telephone(telephone: str) -> bool:
    """
    Valide un numéro de téléphone marocain
    
    Args:
        telephone (str): Numéro à valider
        
    Returns:
        bool: True si valide, False sinon
    """
    if not telephone:
        return False
        
    # Enlever les espaces et tirets
    tel_clean = telephone.replace(" ", "").replace("-", "").replace(".", "")
    
    # Vérifier les formats marocains courants
    import re
    patterns = [
        r'^0[5-7]\d{8}$',      # Format local: 06XXXXXXXX
        r'^\+212[5-7]\d{8}$',  # Format international: +212XXXXXXXXX
        r'^212[5-7]\d{8}$'     # Format international sans +: 212XXXXXXXXX
    ]
    
    return any(re.match(pattern, tel_clean) for pattern in patterns)

def generer_numero_contrat(prefix: str = "DOM") -> str:
    """
    Génère un numéro de contrat unique
    
    Args:
        prefix (str): Préfixe du numéro de contrat
        
    Returns:
        str: Numéro de contrat généré
    """
    from datetime import datetime
    import random
    
    # Format: PREFIX-YYYYMM-XXXX
    date_str = datetime.now().strftime("%Y%m")
    random_num = random.randint(1000, 9999)
    
    return f"{prefix}-{date_str}-{random_num}"

def generer_numero_facture(prefix: str = "FACT") -> str:
    """
    Génère un numéro de facture unique
    
    Args:
        prefix (str): Préfixe du numéro de facture
        
    Returns:
        str: Numéro de facture généré
    """
    from datetime import datetime
    import random
    
    # Format: PREFIX-YYYYMM-XXXX
    date_str = datetime.now().strftime("%Y%m")
    random_num = random.randint(1000, 9999)
    
    return f"{prefix}-{date_str}-{random_num}"

def calculer_tva(montant_ht: float, taux_tva: float = 20.0) -> Dict[str, float]:
    """
    Calcule la TVA et le montant TTC
    
    Args:
        montant_ht (float): Montant hors taxe
        taux_tva (float): Taux de TVA en pourcentage
        
    Returns:
        Dict: Montant HT, TVA, et TTC
    """
    try:
        montant_ht = float(montant_ht)
        taux_tva = float(taux_tva)
        
        montant_tva = montant_ht * (taux_tva / 100)
        montant_ttc = montant_ht + montant_tva
        
        return {
            "montant_ht": round(montant_ht, 2),
            "montant_tva": round(montant_tva, 2),
            "montant_ttc": round(montant_ttc, 2),
            "taux_tva": taux_tva
        }
        
    except (ValueError, TypeError):
        return {
            "montant_ht": 0.0,
            "montant_tva": 0.0,
            "montant_ttc": 0.0,
            "taux_tva": 0.0
        }

def valider_cin(cin: str) -> str:
    """
    Formate un numéro CIN (Carte d'Identité Nationale)
    
    Args:
        cin (str): Numéro CIN à formater
        
    Returns:
        str: CIN formaté
    """
    if not cin:
        return ""
        
    # Enlever les espaces et mettre en majuscules
    cin_clean = cin.replace(" ", "").upper()
    
    # Format attendu: 2 lettres + 6 chiffres (ex: AB123456)
    if len(cin_clean) == 8 and cin_clean[:2].isalpha() and cin_clean[2:].isdigit():
        return f"{cin_clean[:2]}{cin_clean[2:]}"
    
    return cin_clean

def valider_ice(ice: str) -> str:
    """
    Formate un numéro ICE (Identifiant Commun de l'Entreprise)
    
    Args:
        ice (str): Numéro ICE à formater
        
    Returns:
        str: ICE formaté
    """
    if not ice:
        return ""
        
    # Enlever les espaces
    ice_clean = ice.replace(" ", "")
    
    # Format attendu: 15 chiffres
    if len(ice_clean) == 15 and ice_clean.isdigit():
        # Formater avec des espaces pour la lisibilité: XXX XXX XXX XXX XXX
        return f"{ice_clean[:3]} {ice_clean[3:6]} {ice_clean[6:9]} {ice_clean[9:12]} {ice_clean[12:]}"
    
    return ice_clean

def obtenir_mois_francais(numero_mois: int) -> str:
    """
    Retourne le nom du mois en français
    
    Args:
        numero_mois (int): Numéro du mois (1-12)
        
    Returns:
        str: Nom du mois en français
    """
    mois = {
        1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
        5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
        9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
    }
    
    return mois.get(numero_mois, "Inconnu")

def calculer_duree_contrat(date_debut: str, date_fin: str) -> int:
    """
    Calcule la durée d'un contrat en mois
    
    Args:
        date_debut (str): Date de début au format YYYY-MM-DD
        date_fin (str): Date de fin au format YYYY-MM-DD
        
    Returns:
        int: Durée en mois
    """
    try:
        debut = datetime.strptime(date_debut, "%Y-%m-%d")
        fin = datetime.strptime(date_fin, "%Y-%m-%d")
        
        # Calcul approximatif en mois
        duree_jours = (fin - debut).days
        duree_mois = max(1, round(duree_jours / 30.44))  # Moyenne de jours par mois
        
        return duree_mois
        
    except (ValueError, TypeError):
        return 12  # Valeur par défaut

# Constantes utiles
TYPES_CLIENTS = {
    "physique": "Personne Physique",
    "moral": "Personne Morale"
}

STATUTS_CONTRAT = {
    "Actif": "✅ Actif",
    "En attente": "⏳ En attente",
    "Suspendu": "⏸️ Suspendu", 
    "Résilié": "❌ Résilié"
}

MODES_PAIEMENT = [
    "Espèces",
    "Chèque",
    "Virement",
    "Carte bancaire",
    "Autre"
]

SERVICES_DOMICILIATION = [
    "Standard",
    "Premium", 
    "Professionnel",
    "Bureaux virtuels",
    "Secrétariat",
    "Courrier"
]
