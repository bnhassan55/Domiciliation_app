import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict

# Configuration de la base de données
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "domiciliation.db")

def get_db_connection():
    """Établit une connexion à la base de données"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialise la structure de la base de données"""
    conn = get_db_connection()
    
    try:
        # Table Clients Physiques
        conn.execute("""
        CREATE TABLE IF NOT EXISTS clients_physiques (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            sexe TEXT CHECK(sexe IN ('M', 'F', 'Autre')),
            cin TEXT UNIQUE NOT NULL,
            telephone TEXT NOT NULL,
            email TEXT,
            adresse TEXT,
            date_naissance TEXT,
            date_creation TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Table Clients Moraux
        conn.execute("""
        CREATE TABLE IF NOT EXISTS clients_moraux (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raison_sociale TEXT NOT NULL,
            ice TEXT UNIQUE NOT NULL,
            rc TEXT,
            forme_juridique TEXT,
            telephone TEXT NOT NULL,
            email TEXT,
            adresse TEXT,
            rep_nom TEXT,
            rep_prenom TEXT,
            rep_cin TEXT,
            rep_qualite TEXT,
            date_creation TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Table Types de Domiciliation
        conn.execute("""
        CREATE TABLE IF NOT EXISTS types_domiciliation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            libelle TEXT NOT NULL,
            description TEXT,
            tarif_base REAL NOT NULL
        )
        """)
        
        # Table Contrats
        conn.execute("""
        CREATE TABLE IF NOT EXISTS contrats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_contrat TEXT UNIQUE NOT NULL,
            client_id INTEGER NOT NULL,
            client_type TEXT CHECK(client_type IN ('physique', 'moral')) NOT NULL,
            type_service TEXT NOT NULL,
            date_debut TEXT NOT NULL,
            date_fin TEXT NOT NULL,
            duree_mois INTEGER NOT NULL DEFAULT 12,
            montant_mensuel REAL NOT NULL,
            frais_ouverture REAL DEFAULT 0,
            depot_garantie REAL DEFAULT 0,
            services_inclus TEXT,
            conditions TEXT,
            statut TEXT DEFAULT 'Actif' CHECK(statut IN ('Actif', 'En attente', 'Suspendu', 'Résilié')),
            date_creation TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Table Paiements
        conn.execute("""
        CREATE TABLE IF NOT EXISTS paiements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contrat_id INTEGER NOT NULL,
            montant REAL NOT NULL,
            date_paiement TEXT NOT NULL,
            mode_paiement TEXT DEFAULT 'Espèces',
            reference TEXT,
            date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contrat_id) REFERENCES contrats(id) ON DELETE CASCADE
        )
        """)
        
        conn.execute("""
        CREATE TABLE IF NOT EXISTS factures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_facture TEXT UNIQUE NOT NULL,
            contrat_id INTEGER,
            client_id INTEGER NOT NULL,
            type_facture TEXT DEFAULT 'Domiciliation',
            date_facture TEXT NOT NULL,
            date_echeance TEXT,
            periode_debut TEXT,
            periode_fin TEXT,
            montant_ht REAL NOT NULL,
            taux_tva REAL DEFAULT 20.0,
            montant_tva REAL,
            montant_ttc REAL NOT NULL,
            description TEXT,
            mode_reglement TEXT DEFAULT 'Virement',
            statut TEXT DEFAULT 'En attente',
            date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contrat_id) REFERENCES contrats(id),
            FOREIGN KEY (client_id) REFERENCES clients_physiques(id)
        )
        """)

        # Données de base pour types de domiciliation
        conn.executemany("""
        INSERT OR IGNORE INTO types_domiciliation (libelle, description, tarif_base)
        VALUES (?, ?, ?)
        """, [
            ('Standard', 'Domiciliation de base', 2000.0),
            ('Premium', 'Service complet avec secrétariat', 5000.0),
            ('Professionnel', 'Pour professions réglementées', 3500.0)
        ])
        
        conn.commit()
        update_db_structure()

        
    except Exception as e:
        print(f"Erreur d'initialisation DB: {e}")
        conn.rollback()
    finally:
        conn.close()

# CORRECTION 1: Fonction pour réorganiser les IDs après suppression


# CORRECTION 2: Fonction de suppression complètement corrigée
def supprimer_client_definitif(client_id: int) -> bool:
    """Supprime définitivement un client après vérifications approfondies"""
    conn = get_db_connection()
    
    try:
        # ÉTAPE 1: Identifier le type de client et vérifier son existence
        client_physique = conn.execute(
            "SELECT id FROM clients_physiques WHERE id = ?", (client_id,)
        ).fetchone()
        
        client_moral = conn.execute(
            "SELECT id FROM clients_moraux WHERE id = ?", (client_id,)
        ).fetchone()
        
        if not client_physique and not client_moral:
            print(f"Aucun client trouvé avec l'ID {client_id}")
            return False
        
        client_type = "physique" if client_physique else "moral"
        table_name = f"clients_{client_type}s"
        
        # ÉTAPE 2: Vérification APPROFONDIE des contrats
        print(f"Vérification des contrats pour client {client_id} de type {client_type}")
        
        # Compter tous les contrats (actifs, inactifs, etc.)
        contrats_count = conn.execute(
            "SELECT COUNT(*) as count FROM contrats WHERE client_id = ? AND client_type = ?",
            (client_id, client_type)
        ).fetchone()
        
        print(f"Nombre total de contrats trouvés: {contrats_count['count']}")
        
        if contrats_count['count'] > 0:
            # Lister les contrats pour débug
            contrats = conn.execute(
                "SELECT id, numero_contrat, statut FROM contrats WHERE client_id = ? AND client_type = ?",
                (client_id, client_type)
            ).fetchall()
            
            print("Contrats associés:")
            for contrat in contrats:
                print(f"  - Contrat ID: {contrat['id']}, Numéro: {contrat['numero_contrat']}, Statut: {contrat['statut']}")
            
            return False
        
        # ÉTAPE 3: Vérification des factures
        factures_count = conn.execute(
            "SELECT COUNT(*) as count FROM factures WHERE client_id = ?",
            (client_id,)
        ).fetchone()
        
        print(f"Nombre de factures trouvées: {factures_count['count']}")
        
        if factures_count['count'] > 0:
            print("Client associé à des factures, suppression impossible")
            return False
        
        # ÉTAPE 4: Suppression effective
        print(f"Suppression du client {client_id} de la table {table_name}")
        
        cursor = conn.execute(f"DELETE FROM {table_name} WHERE id = ?", (client_id,))
        rows_affected = cursor.rowcount
        
        if rows_affected == 0:
            print(f"Aucune ligne supprimée pour client {client_id}")
            return False
        
        conn.commit()
        print(f"Client {client_id} supprimé avec succès. Lignes affectées: {rows_affected}")
        
        # ÉTAPE 5: Réorganisation des IDs
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de la suppression du client {client_id}: {e}")
        import traceback
        print(f"Détails de l'erreur: {traceback.format_exc()}")
        try:
            conn.rollback()
        except:
            pass
        return False

    finally:
        try:
            conn.close()
        except:
            pass


# CORRECTION 3: Fonction de modification complètement reécrite
def modifier_client_complet(client_id: int, modifications: Dict, client_type: str) -> bool:
    """
    Modifie un client avec validation complète et gestion d'erreurs AMÉLIORÉE
    
    Args:
        client_id: ID du client à modifier
        modifications: Dictionnaire des modifications à apporter
        client_type: Type de client ('physique' ou 'moral')
    
    Returns:
        bool: True si la modification réussit, False sinon
    """
    conn = None
    
    try:
        conn = get_db_connection()
        
        # Déterminer la table correcte
        table = "clients_physiques" if client_type == "physique" else "clients_moraux"
        
        print(f"🔍 DEBUG: Modification du client ID={client_id}, Type={client_type}, Table={table}")
        print(f"🔍 DEBUG: Modifications reçues: {modifications}")
        
        # ÉTAPE 1: Vérifier l'existence du client
        cursor = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (client_id,))
        client_existant = cursor.fetchone()
        
        if not client_existant:
            print(f"❌ Client {client_id} non trouvé dans {table}")
            return False
        
        print(f"✅ Client trouvé: {dict(client_existant)}")
        
        # ÉTAPE 2: Vérifier si des modifications sont nécessaires
        if not modifications:
            print("⚠️ Aucune modification fournie")
            return True
        
        # ÉTAPE 3: Valider les champs modifiables selon le type
        champs_modifiables = {
            'physique': ['nom', 'prenom', 'sexe', 'cin', 'telephone', 'email', 'adresse', 'date_naissance'],
            'moral': ['raison_sociale', 'ice', 'rc', 'forme_juridique', 'telephone', 'email', 'adresse',
                     'rep_nom', 'rep_prenom', 'rep_cin', 'rep_qualite']
        }
        
        champs_autorises = champs_modifiables.get(client_type, [])
        if not champs_autorises:
            print(f"❌ Type de client invalide: {client_type}")
            return False
        
        # ÉTAPE 4: Préparer les modifications avec validation des contraintes
        modifications_validees = {}
        valeurs_actuelles = dict(client_existant)
        
        for champ, nouvelle_valeur in modifications.items():
            if champ not in champs_autorises:
                print(f"⚠️ Champ non autorisé ignoré: {champ}")
                continue
            
            # Obtenir la valeur actuelle
            valeur_actuelle = valeurs_actuelles.get(champ)
            
            # Normalisation des valeurs vides
            if nouvelle_valeur in ['', 'None', None]:
                nouvelle_valeur = None if champ in ['sexe', 'email', 'adresse', 'date_naissance', 'rc', 'forme_juridique', 'rep_nom', 'rep_prenom', 'rep_cin', 'rep_qualite'] else ''
            
            # Validation spécifique par champ
            if nouvelle_valeur and champ == 'email':
                from utils import valider_email
                if not valider_email(nouvelle_valeur):
                    print(f"❌ Format email invalide pour {champ}: {nouvelle_valeur}")
                    continue
            
            elif nouvelle_valeur and champ in ['cin', 'rep_cin']:
                from utils import valider_cin
                if not valider_cin(nouvelle_valeur):
                    print(f"❌ Format CIN invalide pour {champ}: {nouvelle_valeur}")
                    continue
            
            elif nouvelle_valeur and champ == 'ice':
                from utils import valider_ice
                if not valider_ice(nouvelle_valeur):
                    print(f"❌ Format ICE invalide pour {champ}: {nouvelle_valeur}")
                    continue
            
            # Ajouter à la liste des modifications si différent
            if str(valeur_actuelle) != str(nouvelle_valeur):
                modifications_validees[champ] = nouvelle_valeur
                print(f"📝 Modification détectée - {champ}: '{valeur_actuelle}' → '{nouvelle_valeur}'")
            else:
                print(f"➡️ Pas de changement pour {champ}: '{valeur_actuelle}'")
        
        # ÉTAPE 5: Vérifier s'il y a des modifications à effectuer
        if not modifications_validees:
            print("ℹ️ Aucune modification réelle détectée")
            return True
        
        # ÉTAPE 6: Vérifier les contraintes d'unicité avant la modification
        contraintes_uniques = {
            'physique': {'cin': 'CIN'},
            'moral': {'ice': 'ICE'}
        }
        
        if client_type in contraintes_uniques:
            for champ_unique, nom_affichage in contraintes_uniques[client_type].items():
                if champ_unique in modifications_validees:
                    nouvelle_valeur_unique = modifications_validees[champ_unique]
                    
                    # Vérifier si cette valeur n'existe pas déjà pour un autre client
                    cursor_check = conn.execute(
                        f"SELECT id FROM {table} WHERE {champ_unique} = ? AND id != ?",
                        (nouvelle_valeur_unique, client_id)
                    )
                    if cursor_check.fetchone():
                        print(f"❌ Contrainte d'unicité violée - {nom_affichage} déjà existant: {nouvelle_valeur_unique}")
                        return False
        
        # ÉTAPE 7: Construire et exécuter la requête de mise à jour
        set_clauses = []
        valeurs = []
        
        for champ, valeur in modifications_validees.items():
            set_clauses.append(f"{champ} = ?")
            valeurs.append(valeur)
        
        valeurs.append(client_id)  # Pour la clause WHERE
        
        requete = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE id = ?"
        
        print(f"🔧 Requête SQL: {requete}")
        print(f"🔧 Valeurs: {valeurs}")
        
        # ÉTAPE 8: Exécuter la mise à jour avec gestion des erreurs
        cursor_update = conn.execute(requete, valeurs)
        lignes_modifiees = cursor_update.rowcount
        
        print(f"📊 Lignes affectées par UPDATE: {lignes_modifiees}")
        
        if lignes_modifiees == 0:
            print("❌ Aucune ligne modifiée - Peut-être que l'ID n'existe pas")
            return False
        
        # ÉTAPE 9: Valider les changements
        conn.commit()
        print("✅ Modifications commitées en base de données")
        
        # ÉTAPE 10: Vérification finale des modifications appliquées
        cursor_verif = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (client_id,))
        client_apres = cursor_verif.fetchone()
        
        if client_apres:
            print(f"✅ Client après modification: {dict(client_apres)}")
            
            # Vérifier chaque modification pour s'assurer qu'elle a été appliquée
            verification_reussie = True
            for champ, valeur_attendue in modifications_validees.items():
                valeur_db = client_apres[champ] if hasattr(client_apres, champ) else dict(client_apres).get(champ)
                
                # Normaliser pour la comparaison (gérer les None)
                valeur_db_norm = str(valeur_db) if valeur_db is not None else ''
                valeur_attendue_norm = str(valeur_attendue) if valeur_attendue is not None else ''
                
                if valeur_db_norm == valeur_attendue_norm:
                    print(f"✅ Vérification OK - {champ}: '{valeur_db}'")
                else:
                    print(f"❌ Vérification FAILED - {champ}: attendu='{valeur_attendue}', trouvé='{valeur_db}'")
                    verification_reussie = False
            
            if not verification_reussie:
                print("⚠️ Certaines vérifications ont échoué mais la modification a été commitée")
        
        success = lignes_modifiees > 0
        print(f"🎯 Résultat final: {'SUCCESS' if success else 'FAILED'}")
        
        return success
        
    except sqlite3.IntegrityError as e:
        print(f"❌ Erreur d'intégrité lors de la modification: {e}")
        if "UNIQUE constraint failed" in str(e):
            if "cin" in str(e).lower():
                print("❌ Cette CIN existe déjà pour un autre client")
            elif "ice" in str(e).lower():
                print("❌ Cet ICE existe déjà pour une autre entreprise")
        if conn:
            conn.rollback()
        return False
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification du client {client_id}: {e}")
        import traceback
        print(f"📋 Traceback complet: {traceback.format_exc()}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()
            print("🔒 Connexion fermée")


def modifier_client_avec_historique(client_id: int, modifications: Dict, client_type: str, utilisateur: str = "Système") -> bool:
    """
    Version avancée de modification avec historique des changements
    
    Args:
        client_id: ID du client à modifier
        modifications: Dictionnaire des modifications à apporter
        client_type: Type de client ('physique' ou 'moral')
        utilisateur: Nom de l'utilisateur qui effectue la modification
    
    Returns:
        bool: True si la modification réussit, False sinon
    """
    conn = None
    
    try:
        conn = get_db_connection()
        
        # Créer la table d'historique si elle n'existe pas
        conn.execute("""
        CREATE TABLE IF NOT EXISTS historique_modifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            client_type TEXT NOT NULL,
            champ_modifie TEXT NOT NULL,
            ancienne_valeur TEXT,
            nouvelle_valeur TEXT,
            utilisateur TEXT DEFAULT 'Système',
            date_modification TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        table = "clients_physiques" if client_type == "physique" else "clients_moraux"
        
        # Récupérer l'état actuel du client
        cursor = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (client_id,))
        client_avant = cursor.fetchone()
        
        if not client_avant:
            return False
        
        client_avant_dict = dict(client_avant)
        
        # Effectuer la modification principale
        success = modifier_client_complet(client_id, modifications, client_type)
        
        if success:
            # Enregistrer l'historique des changements
            for champ, nouvelle_valeur in modifications.items():
                ancienne_valeur = client_avant_dict.get(champ)
                
                if str(ancienne_valeur) != str(nouvelle_valeur):
                    conn.execute("""
                    INSERT INTO historique_modifications 
                    (client_id, client_type, champ_modifie, ancienne_valeur, nouvelle_valeur, utilisateur)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        client_id, 
                        client_type, 
                        champ, 
                        str(ancienne_valeur) if ancienne_valeur else None,
                        str(nouvelle_valeur) if nouvelle_valeur else None,
                        utilisateur
                    ))
            
            conn.commit()
            print(f"✅ Historique des modifications enregistré pour le client {client_id}")
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification avec historique: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def get_historique_client(client_id: int, client_type: str) -> List[Dict]:
    """Récupère l'historique des modifications d'un client"""
    conn = get_db_connection()
    try:
        cursor = conn.execute("""
        SELECT * FROM historique_modifications 
        WHERE client_id = ? AND client_type = ?
        ORDER BY date_modification DESC
        """, (client_id, client_type))
        
        return [dict(row) for row in cursor.fetchall()]
        
    except Exception as e:
        print(f"Erreur récupération historique: {e}")
        return []
    finally:
        conn.close()


def valider_donnees_client(client_data: Dict, client_type: str) -> tuple[bool, List[str]]:
    """
    Valide les données d'un client selon son type
    
    Args:
        client_data: Dictionnaire des données du client
        client_type: Type de client ('physique' ou 'moral')
    
    Returns:
        tuple: (validation_reussie, liste_des_erreurs)
    """
    erreurs = []
    
    if client_type == "physique":
        # Validation client physique
        if not client_data.get('nom', '').strip():
            erreurs.append("Le nom est obligatoire")
        elif len(client_data.get('nom', '').strip()) < 2:
            erreurs.append("Le nom doit contenir au moins 2 caractères")
            
        if not client_data.get('prenom', '').strip():
            erreurs.append("Le prénom est obligatoire")
        elif len(client_data.get('prenom', '').strip()) < 2:
            erreurs.append("Le prénom doit contenir au moins 2 caractères")
            
        if not client_data.get('cin', '').strip():
            erreurs.append("La CIN est obligatoire")
        else:
            from utils import valider_cin
            if not valider_cin(client_data.get('cin', '').strip()):
                erreurs.append("Format CIN invalide")
                
        if not client_data.get('telephone', '').strip():
            erreurs.append("Le téléphone est obligatoire")
        elif len(client_data.get('telephone', '').strip()) < 10:
            erreurs.append("Le numéro de téléphone doit contenir au moins 10 chiffres")
            
        email = client_data.get('email', '').strip()
        if email:
            from utils import valider_email
            if not valider_email(email):
                erreurs.append("Format email invalide")
                
    else:  # client moral
        if not client_data.get('raison_sociale', '').strip():
            erreurs.append("La raison sociale est obligatoire")
        elif len(client_data.get('raison_sociale', '').strip()) < 3:
            erreurs.append("La raison sociale doit contenir au moins 3 caractères")
            
        if not client_data.get('ice', '').strip():
            erreurs.append("L'ICE est obligatoire")
        else:
            from utils import valider_ice
            if not valider_ice(client_data.get('ice', '').strip()):
                erreurs.append("Format ICE invalide")
                
        if not client_data.get('telephone', '').strip():
            erreurs.append("Le téléphone est obligatoire")
        elif len(client_data.get('telephone', '').strip()) < 10:
            erreurs.append("Le numéro de téléphone doit contenir au moins 10 chiffres")
            
        email = client_data.get('email', '').strip()
        if email:
            from utils import valider_email
            if not valider_email(email):
                erreurs.append("Format email invalide")
                
        rep_cin = client_data.get('rep_cin', '').strip()
        if rep_cin:
            from utils import valider_cin
            if not valider_cin(rep_cin):
                erreurs.append("Format CIN du représentant invalide")
    
    return len(erreurs) == 0, erreurs


# Fonction auxiliaire pour diagnostiquer les problèmes
def diagnostiquer_modification_client(client_id: int, client_type: str):
    """Fonction de diagnostic pour identifier les problèmes"""
    conn = None
    try:
        conn = get_db_connection()
        table = "clients_physiques" if client_type == "physique" else "clients_moraux"
        
        print(f"🔍 DIAGNOSTIC pour client ID={client_id}, type={client_type}")
        
        # Vérifier l'existence
        cursor = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (client_id,))
        client = cursor.fetchone()
        
        if client:
            print(f"✅ Client trouvé dans {table}")
            print(f"📋 Données actuelles: {dict(client)}")
            
            # Vérifier les colonnes de la table
            cursor_cols = conn.execute(f"PRAGMA table_info({table})")
            colonnes = cursor_cols.fetchall()
            print(f"📝 Colonnes disponibles dans {table}:")
            for col in colonnes:
                print(f"   - {col[1]} ({col[2]})")
                
        else:
            print(f"❌ Client non trouvé dans {table}")
            
            # Vérifier s'il existe dans l'autre table
            autre_table = "clients_moraux" if client_type == "physique" else "clients_physiques"
            cursor_autre = conn.execute(f"SELECT * FROM {autre_table} WHERE id = ?", (client_id,))
            client_autre = cursor_autre.fetchone()
            
            if client_autre:
                print(f"⚠️ ATTENTION: Client trouvé dans {autre_table} au lieu de {table}")
                print(f"   Vérifiez le paramètre client_type!")
            
    except Exception as e:
        print(f"❌ Erreur lors du diagnostic: {e}")
    finally:
        if conn:
            conn.close()

# CORRECTION 4: Maintenir les anciennes fonctions pour compatibilité
def supprimer_client(client_id: int) -> bool:
    """Version de compatibilité - utilise la nouvelle fonction"""
    return supprimer_client_definitif(client_id)

def supprimer_client_fixed(client_id: int) -> bool:
    """Version de compatibilité - utilise la nouvelle fonction"""
    return supprimer_client_definitif(client_id)

def modifier_client(client_id: int, client_data: Dict, client_type: str) -> bool:
    """Version de compatibilité - utilise la nouvelle fonction"""
    return modifier_client_complet(client_id, client_data, client_type)

def modifier_client_fixed(client_id: int, client_data: dict, client_type: str) -> bool:
    """Version de compatibilité - utilise la nouvelle fonction"""
    return modifier_client_complet(client_id, client_data, client_type)

# Fonctions CRUD Clients (inchangées mais améliorées)
def ajouter_client(client_data: Dict, client_type: str) -> bool:
    """Ajoute un nouveau client"""
    conn = get_db_connection()
    try:
        table = "clients_physiques" if client_type == "physique" else "clients_moraux"
        
        # Validation des champs requis
        if client_type == "physique":
            required_fields = ['nom', 'prenom', 'cin', 'telephone']
        else:
            required_fields = ['raison_sociale', 'ice', 'telephone']
        
        for field in required_fields:
            if not client_data.get(field):
                return False
        
        columns = ", ".join(client_data.keys())
        placeholders = ", ".join(["?"] * len(client_data))
        
        conn.execute(
            f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
            tuple(client_data.values())
        )
        conn.commit()
        
        return True
         
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Erreur ajout client: {e}")
        return False
    finally:
        conn.close()

def rechercher_clients(search_term: str = "", client_type: Optional[str] = None) -> List[Dict]:
    """Recherche des clients"""
    conn = get_db_connection()
    try:
        if client_type == "physique":
            query = """
            SELECT *
            FROM clients_physiques
            WHERE nom LIKE ? OR prenom LIKE ? OR cin LIKE ? OR telephone LIKE ?
            ORDER BY id
            """
            params = [f"%{search_term}%"] * 4
            
        elif client_type == "moral":
            query = """
            SELECT *
            FROM clients_moraux
            WHERE raison_sociale LIKE ? OR ice LIKE ? OR telephone LIKE ?
            ORDER BY id
            """
            params = [f"%{search_term}%"] * 3
            
        else:
            # Recherche dans les deux tables
            query_physique = """
            SELECT *, 'physique' as type_client
            FROM clients_physiques
            WHERE nom LIKE ? OR prenom LIKE ? OR cin LIKE ? OR telephone LIKE ?
            """
            query_moral = """
            SELECT *, 'moral' as type_client
            FROM clients_moraux
            WHERE raison_sociale LIKE ? OR ice LIKE ? OR telephone LIKE ?
            """
            
            params = [f"%{search_term}%"] * 4
            
            cursor_physique = conn.execute(query_physique, params)
            cursor_moral = conn.execute(query_moral, params[:3])
            
            results = [dict(row) for row in cursor_physique.fetchall()]
            results.extend([dict(row) for row in cursor_moral.fetchall()])
            
            return sorted(results, key=lambda x: x.get('id', 0))
        
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
        
    except Exception as e:
        print(f"Erreur recherche clients: {e}")
        return []
    finally:
        conn.close()

def get_all_clients(client_type: str) -> List[Dict]:
    """Récupère tous les clients d'un type donné"""
    conn = get_db_connection()
    try:
        if client_type == "physique":
            query = """
            SELECT id, nom, prenom, cin, telephone, email, sexe, 
                   date_naissance, adresse, date_creation
            FROM clients_physiques
            ORDER BY id
            """
        else:  # moral
            query = """
            SELECT id, raison_sociale, ice, rc, forme_juridique, 
                   telephone, email, adresse, date_creation,
                   rep_nom, rep_prenom, rep_cin, rep_qualite
            FROM clients_moraux
            ORDER BY id
            """
        
        cursor = conn.execute(query)
        return [dict(row) for row in cursor.fetchall()]
        
    except Exception as e:
        print(f"Erreur récupération clients {client_type}: {e}")
        return []
    finally:
        conn.close()

# Fonctions Contrats (inchangées)
def ajouter_contrat(contrat_data: Dict) -> bool:
    """Ajoute un nouveau contrat"""
    conn = get_db_connection()
    try:
        # Validation des champs requis
        required_fields = ['numero_contrat', 'client_id', 'client_type', 'type_service', 
                          'date_debut', 'date_fin', 'montant_mensuel']
        
        for field in required_fields:
            if not contrat_data.get(field):
                print(f"Champ requis manquant: {field}")
                return False
        
        # Insérer le contrat
        conn.execute("""
        INSERT INTO contrats (
            numero_contrat, client_id, client_type, type_service,
            date_debut, date_fin, duree_mois, montant_mensuel,
            frais_ouverture, depot_garantie, services_inclus,
            conditions, statut, date_creation
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contrat_data['numero_contrat'],
            contrat_data['client_id'],
            contrat_data['client_type'],
            contrat_data['type_service'],
            contrat_data['date_debut'],
            contrat_data['date_fin'],
            contrat_data.get('duree_mois', 12),
            contrat_data['montant_mensuel'],
            contrat_data.get('frais_ouverture', 0),
            contrat_data.get('depot_garantie', 0),
            contrat_data.get('services_inclus', ''),
            contrat_data.get('conditions', ''),
            contrat_data.get('statut', 'Actif'),
            contrat_data.get('date_creation', datetime.now().strftime('%Y-%m-%d'))
        ))
        
        conn.commit()
        return True
        
    except sqlite3.IntegrityError as e:
        print(f"Erreur d'intégrité lors de l'ajout du contrat: {e}")
        return False
    except Exception as e:
        print(f"Erreur ajout contrat: {e}")
        return False
    finally:
        conn.close()

def get_all_contrats() -> List[Dict]:
    """Récupère tous les contrats avec les informations des clients"""
    conn = get_db_connection()
    try:
        query = """
        SELECT 
            c.*,
            CASE 
                WHEN c.client_type = 'physique' THEN cp.nom || ' ' || cp.prenom
                ELSE cm.raison_sociale
            END as client_nom,
            CASE 
                WHEN c.client_type = 'physique' THEN cp.cin
                ELSE cm.ice
            END as client_identifiant,
            CASE 
                WHEN c.client_type = 'physique' THEN cp.telephone
                ELSE cm.telephone
            END as client_telephone
        FROM contrats c
        LEFT JOIN clients_physiques cp ON c.client_id = cp.id AND c.client_type = 'physique'
        LEFT JOIN clients_moraux cm ON c.client_id = cm.id AND c.client_type = 'moral'
        ORDER BY c.date_creation DESC
        """
        
        cursor = conn.execute(query)
        return [dict(row) for row in cursor.fetchall()]
        
    except Exception as e:
        print(f"Erreur récupération contrats: {e}")
        return []
    finally:
        conn.close()

def get_contrat_by_id(contrat_id: int) -> Optional[Dict]:
    """Récupère un contrat par son ID avec les informations du client"""
    conn = get_db_connection()
    try:
        query = """
        SELECT 
            c.*,
            CASE 
                WHEN c.client_type = 'physique' THEN cp.nom || ' ' || cp.prenom
                ELSE cm.raison_sociale
            END as client_nom,
            CASE 
                WHEN c.client_type = 'physique' THEN cp.cin
                ELSE cm.ice
            END as client_identifiant,
            CASE 
                WHEN c.client_type = 'physique' THEN cp.telephone
                ELSE cm.telephone
            END as client_telephone,
            CASE 
                WHEN c.client_type = 'physique' THEN cp.email
                ELSE cm.email
            END as client_email,
            CASE 
                WHEN c.client_type = 'physique' THEN cp.adresse
                ELSE cm.adresse
            END as client_adresse
        FROM contrats c
        LEFT JOIN clients_physiques cp ON c.client_id = cp.id AND c.client_type = 'physique'
        LEFT JOIN clients_moraux cm ON c.client_id = cm.id AND c.client_type = 'moral'
        WHERE c.id = ?
        """
        
        cursor = conn.execute(query, (contrat_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
        
    except Exception as e:
        print(f"Erreur récupération contrat par ID: {e}")
        return None
    finally:
        conn.close()

def modifier_contrat(contrat_id: int, modifications: dict) -> bool:
    """
    Modifie un contrat existant avec validation complète et gestion d'erreurs améliorée
    
    Args:
        contrat_id: ID du contrat à modifier
        modifications: Dictionnaire des modifications à apporter
    
    Returns:
        bool: True si la modification réussit, False sinon
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print(f"🔍 DEBUG: Modification du contrat ID={contrat_id}")
        print(f"🔍 DEBUG: Modifications reçues: {modifications}")
        
        # ÉTAPE 1: Vérifier l'existence du contrat
        cursor.execute("SELECT * FROM contrats WHERE id = ?", (contrat_id,))
        contrat_existant = cursor.fetchone()
        
        if not contrat_existant:
            print(f"❌ Contrat {contrat_id} non trouvé")
            return False
        
        print(f"✅ Contrat trouvé: {dict(contrat_existant)}")
        
        # ÉTAPE 2: Vérifier si des modifications sont nécessaires
        if not modifications:
            print("⚠️ Aucune modification fournie")
            return True
        
        # ÉTAPE 3: Validation des champs modifiables
        champs_autorises = [
            'numero_contrat', 'client_id', 'client_type', 'type_service',
            'date_debut', 'date_fin', 'duree_mois', 'montant_mensuel',
            'frais_ouverture', 'depot_garantie', 'services_inclus',
            'conditions', 'statut'
        ]
        
        # ÉTAPE 4: Filtrer et préparer les modifications valides
        modifications_validees = {}
        valeurs_actuelles = dict(contrat_existant)
        
        for champ, nouvelle_valeur in modifications.items():
            if champ not in champs_autorises:
                print(f"⚠️ Champ non autorisé ignoré: {champ}")
                continue
            
            # Obtenir la valeur actuelle
            valeur_actuelle = valeurs_actuelles.get(champ)
            
            # Normaliser les valeurs vides
            if nouvelle_valeur == '' or nouvelle_valeur == 'None':
                nouvelle_valeur = None
            
            # Convertir les types numériques si nécessaire
            if champ in ['client_id', 'duree_mois'] and nouvelle_valeur is not None:
                try:
                    nouvelle_valeur = int(nouvelle_valeur)
                except (ValueError, TypeError):
                    print(f"❌ Erreur de conversion pour {champ}: {nouvelle_valeur}")
                    continue
            
            elif champ in ['montant_mensuel', 'frais_ouverture', 'depot_garantie'] and nouvelle_valeur is not None:
                try:
                    nouvelle_valeur = float(nouvelle_valeur)
                except (ValueError, TypeError):
                    print(f"❌ Erreur de conversion pour {champ}: {nouvelle_valeur}")
                    continue
            
            # Vérifier si la valeur a réellement changé
            if valeur_actuelle != nouvelle_valeur:
                modifications_validees[champ] = nouvelle_valeur
                print(f"📝 Modification détectée - {champ}: '{valeur_actuelle}' → '{nouvelle_valeur}'")
            else:
                print(f"➡️ Pas de changement pour {champ}: '{valeur_actuelle}'")
        
        # ÉTAPE 5: Vérifier s'il y a des modifications à effectuer
        if not modifications_validees:
            print("ℹ️ Aucune modification réelle détectée")
            return True
        
        # ÉTAPE 6: Validations métier spécifiques
        if 'numero_contrat' in modifications_validees:
            # Vérifier l'unicité du numéro de contrat
            cursor.execute(
                "SELECT id FROM contrats WHERE numero_contrat = ? AND id != ?",
                (modifications_validees['numero_contrat'], contrat_id)
            )
            if cursor.fetchone():
                print(f"❌ Numéro de contrat déjà existant: {modifications_validees['numero_contrat']}")
                return False
        
        if 'montant_mensuel' in modifications_validees and modifications_validees['montant_mensuel'] <= 0:
            print("❌ Le montant mensuel doit être supérieur à 0")
            return False
        
        if 'duree_mois' in modifications_validees and modifications_validees['duree_mois'] <= 0:
            print("❌ La durée doit être supérieure à 0")
            return False
        
        # ÉTAPE 7: Construire et exécuter la requête de mise à jour
        set_clauses = []
        valeurs = []
        
        for champ, valeur in modifications_validees.items():
            set_clauses.append(f"{champ} = ?")
            valeurs.append(valeur)
        
        valeurs.append(contrat_id)  # Pour la clause WHERE
        
        requete = f"UPDATE contrats SET {', '.join(set_clauses)} WHERE id = ?"
        
        print(f"🔧 Requête SQL: {requete}")
        print(f"🔧 Valeurs: {valeurs}")
        
        cursor.execute(requete, valeurs)
        lignes_modifiees = cursor.rowcount
        
        print(f"📊 Lignes affectées par UPDATE: {lignes_modifiees}")
        
        if lignes_modifiees == 0:
            print("❌ Aucune ligne modifiée")
            return False
        
        # ÉTAPE 8: Valider les changements
        conn.commit()
        
        # ÉTAPE 9: Vérification finale
        cursor.execute("SELECT * FROM contrats WHERE id = ?", (contrat_id,))
        contrat_apres = cursor.fetchone()
        
        if contrat_apres:
            print(f"✅ Contrat après modification: {dict(contrat_apres)}")
            
            # Vérifier chaque modification
            for champ, valeur_attendue in modifications_validees.items():
                valeur_db = contrat_apres[champ] if hasattr(contrat_apres, champ) else dict(contrat_apres).get(champ)
                if valeur_db == valeur_attendue:
                    print(f"✅ Vérification OK - {champ}: {valeur_db}")
                else:
                    print(f"❌ Vérification FAILED - {champ}: attendu={valeur_attendue}, trouvé={valeur_db}")
        
        success = lignes_modifiees > 0
        print(f"🎯 Résultat final: {'SUCCESS' if success else 'FAILED'}")
        
        return success
        
    except sqlite3.IntegrityError as e:
        print(f"❌ Erreur d'intégrité lors de la modification: {e}")
        if conn:
            conn.rollback()
        return False
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification du contrat {contrat_id}: {e}")
        import traceback
        print(f"📋 Traceback complet: {traceback.format_exc()}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()
            print("🔒 Connexion fermée")

def diagnostiquer_modification_contrat(contrat_id: int):
    """Fonction de diagnostic pour identifier les problèmes de modification de contrat"""
    conn = None
    try:
        conn = get_db_connection()
        
        print(f"🔍 DIAGNOSTIC pour contrat ID={contrat_id}")
        
        # Vérifier l'existence
        cursor = conn.execute("SELECT * FROM contrats WHERE id = ?", (contrat_id,))
        contrat = cursor.fetchone()
        
        if contrat:
            print(f"✅ Contrat trouvé")
            print(f"📋 Données actuelles: {dict(contrat)}")
            
            # Vérifier les colonnes de la table
            cursor_cols = conn.execute("PRAGMA table_info(contrats)")
            colonnes = cursor_cols.fetchall()
            print(f"📝 Colonnes disponibles dans contrats:")
            for col in colonnes:
                print(f"   - {col[1]} ({col[2]})")
                
        else:
            print(f"❌ Contrat non trouvé")
            
    except Exception as e:
        print(f"❌ Erreur lors du diagnostic: {e}")
    finally:
        if conn:
            conn.close()


def supprimer_contrat(contrat_id: int) -> bool:
    """Supprime un contrat"""
    conn = get_db_connection()
    try:
        # Vérifier s'il y a des paiements associés
        paiements = conn.execute(
            "SELECT COUNT(*) as count FROM paiements WHERE contrat_id = ?",
            (contrat_id,)
        ).fetchone()
        
        if paiements and paiements['count'] > 0:
            # Si il y a des paiements, on ne supprime pas mais on marque comme résilié
            conn.execute(
                "UPDATE contrats SET statut = 'Résilié' WHERE id = ?",
                (contrat_id,)
            )
        else:
            # Pas de paiements, on peut supprimer
            conn.execute("DELETE FROM contrats WHERE id = ?", (contrat_id,))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Erreur suppression contrat: {e}")
        return False
    finally:
        conn.close()

def rechercher_contrats(search_term: str = "") -> List[Dict]:
    """Recherche des contrats par terme"""
    conn = get_db_connection()
    try:
        query = """
        SELECT 
            c.*,
            CASE 
                WHEN c.client_type = 'physique' THEN cp.nom || ' ' || cp.prenom
                ELSE cm.raison_sociale
            END as client_nom
        FROM contrats c
        LEFT JOIN clients_physiques cp ON c.client_id = cp.id AND c.client_type = 'physique'
        LEFT JOIN clients_moraux cm ON c.client_id = cm.id AND c.client_type = 'moral'
        WHERE c.numero_contrat LIKE ? 
           OR c.type_service LIKE ?
           OR (c.client_type = 'physique' AND (cp.nom LIKE ? OR cp.prenom LIKE ? OR cp.cin LIKE ?))
           OR (c.client_type = 'moral' AND (cm.raison_sociale LIKE ? OR cm.ice LIKE ?))
        ORDER BY c.date_creation DESC
        """
        
        search_pattern = f"%{search_term}%"
        params = [search_pattern] * 7
        
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
        
    except Exception as e:
        print(f"Erreur recherche contrats: {e}")
        return []
    finally:
        conn.close()

def get_contrats_par_statut(statut: str) -> List[Dict]:
    """Récupère les contrats par statut"""
    conn = get_db_connection()
    try:
        query = """
        SELECT 
            c.*,
            CASE 
                WHEN c.client_type = 'physique' THEN cp.nom || ' ' || cp.prenom
                ELSE cm.raison_sociale
            END as client_nom
        FROM contrats c
        LEFT JOIN clients_physiques cp ON c.client_id = cp.id AND c.client_type = 'physique'
        LEFT JOIN clients_moraux cm ON c.client_id = cm.id AND c.client_type = 'moral'
        WHERE c.statut = ?
        ORDER BY c.date_creation DESC
        """
        
        cursor = conn.execute(query, (statut,))
        return [dict(row) for row in cursor.fetchall()]
        
    except Exception as e:
        print(f"Erreur récupération contrats par statut: {e}")
        return []
    finally:
        conn.close()

def get_contrats_expirants(jours: int = 30) -> List[Dict]:
    """Récupère les contrats qui expirent dans X jours"""
    conn = get_db_connection()
    try:
        query = """
        SELECT 
            c.*,
            CASE 
                WHEN c.client_type = 'physique' THEN cp.nom || ' ' || cp.prenom
                ELSE cm.raison_sociale
            END as client_nom,
            julianday(c.date_fin) - julianday('now') as jours_restants
        FROM contrats c
        LEFT JOIN clients_physiques cp ON c.client_id = cp.id AND c.client_type = 'physique'
        LEFT JOIN clients_moraux cm ON c.client_id = cm.id AND c.client_type = 'moral'
        WHERE c.statut = 'Actif' 
          AND julianday(c.date_fin) - julianday('now') BETWEEN 0 AND ?
        ORDER BY c.date_fin ASC
        """
        
        cursor = conn.execute(query, (jours,))
        return [dict(row) for row in cursor.fetchall()]
        
    except Exception as e:
        print(f"Erreur récupération contrats expirants: {e}")
        return []
    finally:
        conn.close()

def get_statistiques_contrats() -> Dict:
    """Récupère les statistiques des contrats"""
    conn = get_db_connection()
    try:
        # Statistiques générales
        stats_generales = conn.execute("""
        SELECT 
            COUNT(*) as total_contrats,
            COUNT(CASE WHEN statut = 'Actif' THEN 1 END) as contrats_actifs,
            COUNT(CASE WHEN statut = 'En attente' THEN 1 END) as contrats_attente,
            COUNT(CASE WHEN statut = 'Suspendu' THEN 1 END) as contrats_suspendus,
            COUNT(CASE WHEN statut = 'Résilié' THEN 1 END) as contrats_resilies,
            COALESCE(SUM(CASE WHEN statut = 'Actif' THEN montant_mensuel END), 0) as ca_mensuel_actif,
            COALESCE(SUM(montant_mensuel + COALESCE(frais_ouverture, 0)), 0) as ca_total_potentiel
        FROM contrats
        """).fetchone()
        
        # Contrats expirants
        contrats_expirants = conn.execute("""
        SELECT COUNT(*) as count
        FROM contrats 
        WHERE statut = 'Actif' 
          AND julianday(date_fin) - julianday('now') BETWEEN 0 AND 30
        """).fetchone()
        
        # Répartition par type de service
        repartition_services = conn.execute("""
        SELECT type_service, COUNT(*) as count
        FROM contrats
        WHERE statut = 'Actif'
        GROUP BY type_service
        ORDER BY count DESC
        """).fetchall()
        
        return {
            'total_contrats': stats_generales['total_contrats'],
            'contrats_actifs': stats_generales['contrats_actifs'],
            'contrats_attente': stats_generales['contrats_attente'],
            'contrats_suspendus': stats_generales['contrats_suspendus'],
            'contrats_resilies': stats_generales['contrats_resilies'],
            'ca_mensuel_actif': stats_generales['ca_mensuel_actif'],
            'ca_total_potentiel': stats_generales['ca_total_potentiel'],
            'contrats_expirants': contrats_expirants['count'],
            'repartition_services': [dict(row) for row in repartition_services]
        }
        
    except Exception as e:
        print(f"Erreur récupération statistiques contrats: {e}")
        return {}
    finally:
        conn.close()

def ajouter_paiement(paiement_data: Dict) -> bool:
    """Ajoute un paiement et met à jour le contrat"""
    conn = get_db_connection()
    try:
        # Ajouter le paiement
        conn.execute("""
        INSERT INTO paiements (contrat_id, montant, date_paiement, mode_paiement, reference)
        VALUES (?, ?, ?, ?, ?)
        """, (
            paiement_data['contrat_id'],
            paiement_data['montant'],
            paiement_data['date_paiement'],
            paiement_data.get('mode_paiement', 'Espèces'),
            paiement_data.get('reference', '')
        ))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Erreur ajout paiement: {e}")
        return False
    finally:
        conn.close()

def get_statistiques() -> Dict:
    """Récupère les statistiques générales - VERSION CORRIGÉE"""
    conn = get_db_connection()
    try:
        # Statistiques clients
        clients_physiques = conn.execute("SELECT COUNT(*) as count FROM clients_physiques").fetchone()['count']
        clients_moraux = conn.execute("SELECT COUNT(*) as count FROM clients_moraux").fetchone()['count']
        
        # Statistiques contrats - CORRIGÉE POUR NOUVELLE STRUCTURE
        stats_contrats = conn.execute("""
        SELECT 
            COUNT(*) as total_contrats,
            COUNT(CASE WHEN statut = 'Actif' THEN 1 END) as contrats_actifs,
            COUNT(CASE WHEN statut = 'Résilié' THEN 1 END) as contrats_resilies,
            COUNT(CASE WHEN date(date_fin) < date('now') AND statut = 'Actif' THEN 1 END) as contrats_expires,
            COALESCE(SUM(CASE WHEN statut = 'Actif' THEN montant_mensuel * duree_mois END), 0) as ca_total_potentiel,
            COALESCE(SUM(CASE WHEN statut = 'Actif' THEN montant_mensuel END), 0) as ca_mensuel_actif
        FROM contrats
        """).fetchone()
        
        # Calculer le montant encaissé depuis la table paiements
        montant_encaisse = conn.execute("""
        SELECT COALESCE(SUM(montant), 0) as total_encaisse
        FROM paiements
        """).fetchone()['total_encaisse']
        
        # Contrats expirant dans les 30 prochains jours
        contrats_bientot_expires = conn.execute("""
        SELECT COUNT(*) as count
        FROM contrats 
        WHERE statut = 'Actif' 
          AND julianday(date_fin) - julianday('now') BETWEEN 0 AND 30
        """).fetchone()['count']
        
        return {
            'clients_physiques': clients_physiques,
            'clients_moraux': clients_moraux,
            'total_clients': clients_physiques + clients_moraux,
            'total_contrats': stats_contrats['total_contrats'],
            'contrats_actifs': stats_contrats['contrats_actifs'],
            'contrats_resilies': stats_contrats['contrats_resilies'],
            'contrats_expires': stats_contrats['contrats_expires'],
            'contrats_bientot_expires': contrats_bientot_expires,
            'ca_total': stats_contrats['ca_total_potentiel'],
            'ca_mensuel_actif': stats_contrats['ca_mensuel_actif'],
            'montant_encaisse': montant_encaisse
        }
        
    except Exception as e:
        print(f"Erreur récupération statistiques: {e}")
        return {
            'clients_physiques': 0,
            'clients_moraux': 0,
            'total_clients': 0,
            'total_contrats': 0,
            'contrats_actifs': 0,
            'contrats_resilies': 0,
            'contrats_expires': 0,
            'contrats_bientot_expires': 0,
            'ca_total': 0,
            'ca_mensuel_actif': 0,
            'montant_encaisse': 0
        }
    finally:
        conn.close()

def ajouter_facture(facture_data):
    """Ajouter une nouvelle facture"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO factures (
                numero_facture, contrat_id, client_id, type_facture,
                date_facture, date_echeance, periode_debut, periode_fin,
                montant_ht, taux_tva, montant_tva, montant_ttc,
                description, mode_reglement, statut, date_creation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            facture_data['numero_facture'],
            facture_data['contrat_id'],
            facture_data['client_id'],
            facture_data['type_facture'],
            facture_data['date_facture'],
            facture_data['date_echeance'],
            facture_data.get('periode_debut'),
            facture_data.get('periode_fin'),
            facture_data['montant_ht'],
            facture_data['taux_tva'],
            facture_data['montant_tva'],
            facture_data['montant_ttc'],
            facture_data.get('description'),
            facture_data['mode_reglement'],
            facture_data['statut'],
            facture_data['date_creation']
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur lors de l'ajout de la facture: {e}")
        return False

def get_all_factures():
    """Récupérer toutes les factures avec les noms des clients"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT f.*, 
                   COALESCE(cp.nom || ' ' || cp.prenom, cm.raison_sociale) as client_nom
            FROM factures f
            LEFT JOIN clients_physiques cp ON f.client_id = cp.id
            LEFT JOIN clients_moraux cm ON f.client_id = cm.id
            ORDER BY f.date_facture DESC
        """)
        
        factures = []
        for row in cursor.fetchall():
            factures.append(dict(row))
        
        conn.close()
        return factures
    except Exception as e:
        print(f"Erreur lors de la récupération des factures: {e}")
        return []

def get_facture_by_id(facture_id):
    """Récupérer une facture par son ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT f.*, 
                   COALESCE(cp.nom || ' ' || cp.prenom, cm.raison_sociale) as client_nom
            FROM factures f
            LEFT JOIN clients_physiques cp ON f.client_id = cp.id
            LEFT JOIN clients_moraux cm ON f.client_id = cm.id
            WHERE f.id = ?
        """, (facture_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    except Exception as e:
        print(f"Erreur lors de la récupération de la facture: {e}")
        return None

def modifier_facture(facture_id: int, modifications: dict) -> bool:
    """
    Modifie une facture existante avec validation complète et gestion d'erreurs améliorée
    
    Args:
        facture_id: ID de la facture à modifier
        modifications: Dictionnaire des modifications à apporter
    
    Returns:
        bool: True si la modification réussit, False sinon
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print(f"🔍 DEBUG: Modification de la facture ID={facture_id}")
        print(f"🔍 DEBUG: Modifications reçues: {modifications}")
        
        # ÉTAPE 1: Vérifier l'existence de la facture
        cursor.execute("SELECT * FROM factures WHERE id = ?", (facture_id,))
        facture_existante = cursor.fetchone()
        
        if not facture_existante:
            print(f"❌ Facture {facture_id} non trouvée")
            return False
        
        print(f"✅ Facture trouvée: {dict(facture_existante)}")
        
        # ÉTAPE 2: Vérifier si des modifications sont nécessaires
        if not modifications:
            print("⚠️ Aucune modification fournie")
            return True
        
        # ÉTAPE 3: Validation des champs modifiables
        champs_autorises = [
            'numero_facture', 'contrat_id', 'client_id', 'type_facture',
            'date_facture', 'date_echeance', 'periode_debut', 'periode_fin',
            'montant_ht', 'taux_tva', 'montant_tva', 'montant_ttc',
            'description', 'mode_reglement', 'statut', 'date_paiement'
        ]
        
        # ÉTAPE 4: Filtrer et préparer les modifications valides
        modifications_validees = {}
        valeurs_actuelles = dict(facture_existante)
        
        for champ, nouvelle_valeur in modifications.items():
            if champ not in champs_autorises:
                print(f"⚠️ Champ non autorisé ignoré: {champ}")
                continue
            
            # Obtenir la valeur actuelle
            valeur_actuelle = valeurs_actuelles.get(champ)
            
            # Normaliser les valeurs vides
            if nouvelle_valeur == '' or nouvelle_valeur == 'None':
                nouvelle_valeur = None
            
            # Convertir les types numériques si nécessaire
            if champ in ['contrat_id', 'client_id'] and nouvelle_valeur is not None:
                try:
                    nouvelle_valeur = int(nouvelle_valeur)
                except (ValueError, TypeError):
                    print(f"❌ Erreur de conversion pour {champ}: {nouvelle_valeur}")
                    continue
            
            elif champ in ['montant_ht', 'taux_tva', 'montant_tva', 'montant_ttc'] and nouvelle_valeur is not None:
                try:
                    nouvelle_valeur = float(nouvelle_valeur)
                except (ValueError, TypeError):
                    print(f"❌ Erreur de conversion pour {champ}: {nouvelle_valeur}")
                    continue
            
            # Vérifier si la valeur a réellement changé
            if valeur_actuelle != nouvelle_valeur:
                modifications_validees[champ] = nouvelle_valeur
                print(f"📝 Modification détectée - {champ}: '{valeur_actuelle}' → '{nouvelle_valeur}'")
            else:
                print(f"➡️ Pas de changement pour {champ}: '{valeur_actuelle}'")
        
        # ÉTAPE 5: Vérifier s'il y a des modifications à effectuer
        if not modifications_validees:
            print("ℹ️ Aucune modification réelle détectée")
            return True
        
        # ÉTAPE 6: Validations métier spécifiques
        if 'numero_facture' in modifications_validees:
            # Vérifier l'unicité du numéro de facture
            cursor.execute(
                "SELECT id FROM factures WHERE numero_facture = ? AND id != ?",
                (modifications_validees['numero_facture'], facture_id)
            )
            if cursor.fetchone():
                print(f"❌ Numéro de facture déjà existant: {modifications_validees['numero_facture']}")
                return False
        
        if 'montant_ht' in modifications_validees and modifications_validees['montant_ht'] <= 0:
            print("❌ Le montant HT doit être supérieur à 0")
            return False
        
        if 'montant_ttc' in modifications_validees and modifications_validees['montant_ttc'] <= 0:
            print("❌ Le montant TTC doit être supérieur à 0")
            return False
        
        # Vérifier la cohérence des dates
        if 'date_facture' in modifications_validees and 'date_echeance' in modifications_validees:
            try:
                date_fact = datetime.strptime(str(modifications_validees['date_facture']), '%Y-%m-%d').date()
                date_ech = datetime.strptime(str(modifications_validees['date_echeance']), '%Y-%m-%d').date()
                if date_ech < date_fact:
                    print("❌ La date d'échéance ne peut pas être antérieure à la date de facture")
                    return False
            except ValueError:
                print("❌ Format de date invalide")
                return False
        
        # ÉTAPE 7: Construire et exécuter la requête de mise à jour
        set_clauses = []
        valeurs = []
        
        for champ, valeur in modifications_validees.items():
            set_clauses.append(f"{champ} = ?")
            valeurs.append(valeur)
        
        valeurs.append(facture_id)  # Pour la clause WHERE
        
        requete = f"UPDATE factures SET {', '.join(set_clauses)} WHERE id = ?"
        
        print(f"🔧 Requête SQL: {requete}")
        print(f"🔧 Valeurs: {valeurs}")
        
        cursor.execute(requete, valeurs)
        lignes_modifiees = cursor.rowcount
        
        print(f"📊 Lignes affectées par UPDATE: {lignes_modifiees}")
        
        if lignes_modifiees == 0:
            print("❌ Aucune ligne modifiée")
            return False
        
        # ÉTAPE 8: Valider les changements
        conn.commit()
        
        # ÉTAPE 9: Vérification finale
        cursor.execute("SELECT * FROM factures WHERE id = ?", (facture_id,))
        facture_apres = cursor.fetchone()
        
        if facture_apres:
            print(f"✅ Facture après modification: {dict(facture_apres)}")
            
            # Vérifier chaque modification
            for champ, valeur_attendue in modifications_validees.items():
                valeur_db = facture_apres[champ] if hasattr(facture_apres, champ) else dict(facture_apres).get(champ)
                if valeur_db == valeur_attendue:
                    print(f"✅ Vérification OK - {champ}: {valeur_db}")
                else:
                    print(f"❌ Vérification FAILED - {champ}: attendu={valeur_attendue}, trouvé={valeur_db}")
        
        success = lignes_modifiees > 0
        print(f"🎯 Résultat final: {'SUCCESS' if success else 'FAILED'}")
        
        return success
        
    except sqlite3.IntegrityError as e:
        print(f"❌ Erreur d'intégrité lors de la modification: {e}")
        if conn:
            conn.rollback()
        return False
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification de la facture {facture_id}: {e}")
        import traceback
        print(f"📋 Traceback complet: {traceback.format_exc()}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()
            print("🔒 Connexion fermée")

def diagnostiquer_modification_facture(facture_id: int):
    """Fonction de diagnostic pour identifier les problèmes de modification de facture"""
    conn = None
    try:
        conn = get_db_connection()
        
        print(f"🔍 DIAGNOSTIC pour facture ID={facture_id}")
        
        # Vérifier l'existence
        cursor = conn.execute("SELECT * FROM factures WHERE id = ?", (facture_id,))
        facture = cursor.fetchone()
        
        if facture:
            print(f"✅ Facture trouvée")
            print(f"📋 Données actuelles: {dict(facture)}")
            
            # Vérifier les colonnes de la table
            cursor_cols = conn.execute("PRAGMA table_info(factures)")
            colonnes = cursor_cols.fetchall()
            print(f"📝 Colonnes disponibles dans factures:")
            for col in colonnes:
                print(f"   - {col[1]} ({col[2]})")
                
        else:
            print(f"❌ Facture non trouvée")
            
    except Exception as e:
        print(f"❌ Erreur lors du diagnostic: {e}")
    finally:
        if conn:
            conn.close()

def supprimer_facture(facture_id):
    """Supprimer une facture"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM factures WHERE id = ?", (facture_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur lors de la suppression de la facture: {e}")
        return False

def update_db_structure():
    """Met à jour la structure de la base de données pour correspondre aux besoins"""
    conn = get_db_connection()
    
    try:
        # Ajouter les colonnes manquantes pour clients_physiques si elles n'existent pas
        try:
            conn.execute("ALTER TABLE clients_physiques ADD COLUMN sexe TEXT CHECK(sexe IN ('M', 'F', 'Autre'))")
        except sqlite3.OperationalError:
            pass  # Colonne existe déjà
        
        # Mettre à jour la table clients_moraux pour correspondre aux nouveaux champs
        try:
            conn.execute("ALTER TABLE clients_moraux ADD COLUMN rc TEXT")
        except sqlite3.OperationalError:
            pass
        
        try:
            conn.execute("ALTER TABLE clients_moraux ADD COLUMN forme_juridique TEXT")
        except sqlite3.OperationalError:
            pass
        
        try:
            conn.execute("ALTER TABLE clients_moraux ADD COLUMN rep_nom TEXT")
        except sqlite3.OperationalError:
            pass
        
        try:
            conn.execute("ALTER TABLE clients_moraux ADD COLUMN rep_prenom TEXT")
        except sqlite3.OperationalError:
            pass
        
        try:
            conn.execute("ALTER TABLE clients_moraux ADD COLUMN rep_cin TEXT")
        except sqlite3.OperationalError:
            pass
        
        try:
            conn.execute("ALTER TABLE clients_moraux ADD COLUMN rep_qualite TEXT")
        except sqlite3.OperationalError:
            pass
        
        conn.commit()
        
    except Exception as e:
        print(f"Erreur mise à jour structure DB: {e}")
        conn.rollback()
    finally:
        conn.close()

# CORRECTION 5: Fonction utilitaire pour déboguer la base de données
def debug_database():
    """Fonction de débogage pour vérifier l'état de la base de données"""
    conn = get_db_connection()
    try:
        print("=== DEBUG DATABASE ===")
        
        # Vérifier les clients physiques
        physiques = conn.execute("SELECT COUNT(*) as count, MAX(id) as max_id FROM clients_physiques").fetchone()
        print(f"Clients physiques: {physiques['count']} clients, ID max: {physiques['max_id']}")
        
        # Vérifier les clients moraux
        moraux = conn.execute("SELECT COUNT(*) as count, MAX(id) as max_id FROM clients_moraux").fetchone()
        print(f"Clients moraux: {moraux['count']} clients, ID max: {moraux['max_id']}")
        
        # Vérifier les contrats
        contrats = conn.execute("SELECT COUNT(*) as count FROM contrats").fetchone()
        print(f"Contrats: {contrats['count']}")
        
        # Vérifier les contrats orphelins
        contrats_orphelins = conn.execute("""
        SELECT c.id, c.client_id, c.client_type 
        FROM contrats c
        LEFT JOIN clients_physiques cp ON c.client_id = cp.id AND c.client_type = 'physique'
        LEFT JOIN clients_moraux cm ON c.client_id = cm.id AND c.client_type = 'moral'
        WHERE cp.id IS NULL AND cm.id IS NULL
        """).fetchall()
        
        if contrats_orphelins:
            print(f"ATTENTION: {len(contrats_orphelins)} contrats orphelins trouvés:")
            for contrat in contrats_orphelins:
                print(f"  - Contrat ID: {contrat['id']}, Client ID: {contrat['client_id']}, Type: {contrat['client_type']}")
        else:
            print("Aucun contrat orphelin trouvé")
        
        print("=== FIN DEBUG ===")
        
    except Exception as e:
        print(f"Erreur lors du débogage: {e}")
    finally:
        conn.close()

# CORRECTION 6: Fonction de nettoyage des données orphelines
def nettoyer_donnees_orphelines():
    """Nettoie les données orphelines dans la base de données"""
    conn = get_db_connection()
    try:
        print("Nettoyage des données orphelines...")
        
        # Supprimer les contrats orphelins
        cursor = conn.execute("""
        DELETE FROM contrats 
        WHERE id IN (
            SELECT c.id 
            FROM contrats c
            LEFT JOIN clients_physiques cp ON c.client_id = cp.id AND c.client_type = 'physique'
            LEFT JOIN clients_moraux cm ON c.client_id = cm.id AND c.client_type = 'moral'
            WHERE cp.id IS NULL AND cm.id IS NULL
        )
        """)
        
        contrats_supprimes = cursor.rowcount
        print(f"Contrats orphelins supprimés: {contrats_supprimes}")
        
        # Supprimer les paiements orphelins
        cursor = conn.execute("""
        DELETE FROM paiements 
        WHERE contrat_id NOT IN (SELECT id FROM contrats)
        """)
        
        paiements_supprimes = cursor.rowcount
        print(f"Paiements orphelins supprimés: {paiements_supprimes}")
        
        # Supprimer les factures orphelines
        cursor = conn.execute("""
        DELETE FROM factures 
        WHERE client_id NOT IN (
            SELECT id FROM clients_physiques 
            UNION 
            SELECT id FROM clients_moraux
        )
        """)
        
        factures_supprimees = cursor.rowcount
        print(f"Factures orphelines supprimées: {factures_supprimees}")
        
        conn.commit()
        print("Nettoyage terminé avec succès")
        return True
        
    except Exception as e:
        print(f"Erreur lors du nettoyage: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Base de données initialisée avec succès!")
    debug_database()
    nettoyer_donnees_orphelines()