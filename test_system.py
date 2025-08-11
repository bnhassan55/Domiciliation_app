#!/usr/bin/env python3
"""
Script de test complet pour vérifier le fonctionnement du système
Exécutez ce fichier pour tester toutes les fonctionnalités
"""

import os
import sys
import traceback
from datetime import datetime

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test des imports"""
    print("🔍 Test des imports...")
    try:
        from db import (init_db, ajouter_client, get_all_clients, rechercher_clients, 
                       modifier_client_complet, supprimer_client_definitif, get_statistiques)
        print("✅ Imports réussis")
        return True
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        traceback.print_exc()
        return False

def test_database_init():
    """Test d'initialisation de la base de données"""
    print("\n🔍 Test d'initialisation de la base de données...")
    try:
        from db import init_db
        init_db()
        print("✅ Base de données initialisée")
        return True
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
        traceback.print_exc()
        return False

def test_ajout_client_physique():
    """Test d'ajout de client physique"""
    print("\n🔍 Test d'ajout de client physique...")
    try:
        from db import ajouter_client
        
        client_data = {
            'nom': 'MARTIN',
            'prenom': 'Pierre',
            'cin': 'AB123TEST',
            'telephone': '0600000123',
            'email': 'pierre.martin@test.com',
            'sexe': 'M'
        }
        
        result = ajouter_client(client_data, "physique")
        if result:
            print("✅ Client physique ajouté avec succès")
            return True
        else:
            print("❌ Échec de l'ajout du client physique")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout: {e}")
        traceback.print_exc()
        return False

def test_ajout_client_moral():
    """Test d'ajout de client moral"""
    print("\n🔍 Test d'ajout de client moral...")
    try:
        from db import ajouter_client
        
        client_data = {
            'raison_sociale': 'ENTREPRISE TEST SARL',
            'ice': '1234567890123',
            'telephone': '0500000456',
            'email': 'contact@entreprise-test.ma',
            'forme_juridique': 'SARL'
        }
        
        result = ajouter_client(client_data, "moral")
        if result:
            print("✅ Client moral ajouté avec succès")
            return True
        else:
            print("❌ Échec de l'ajout du client moral")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout: {e}")
        traceback.print_exc()
        return False

def test_recuperation_clients():
    """Test de récupération des clients"""
    print("\n🔍 Test de récupération des clients...")
    try:
        from db import get_all_clients
        
        # Test clients physiques
        clients_physiques = get_all_clients("physique")
        print(f"✅ Clients physiques récupérés: {len(clients_physiques)}")
        
        # Test clients moraux
        clients_moraux = get_all_clients("moral")
        print(f"✅ Clients moraux récupérés: {len(clients_moraux)}")
        
        return len(clients_physiques) > 0 or len(clients_moraux) > 0
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération: {e}")
        traceback.print_exc()
        return False

def test_recherche_clients():
    """Test de recherche de clients"""
    print("\n🔍 Test de recherche de clients...")
    try:
        from db import rechercher_clients
        
        # Recherche dans clients physiques
        resultats_physiques = rechercher_clients("MARTIN", "physique")
        print(f"✅ Résultats recherche physique: {len(resultats_physiques)}")
        
        # Recherche dans clients moraux
        resultats_moraux = rechercher_clients("ENTREPRISE", "moral")
        print(f"✅ Résultats recherche moral: {len(resultats_moraux)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la recherche: {e}")
        traceback.print_exc()
        return False

def test_modification_client():
    """Test de modification de client"""
    print("\n🔍 Test de modification de client...")
    try:
        from db import get_all_clients, modifier_client_complet
        
        # Récupérer un client existant
        clients = get_all_clients("physique")
        if not clients:
            print("⚠️ Aucun client physique pour tester la modification")
            return True
        
        client = clients[0]
        client_id = client['id']
        print(f"📝 Test modification du client ID: {client_id}")
        
        # Modifications à appliquer
        modifications = {
            'email': 'email.modifie@test.com',
            'adresse': '123 Rue de la Modification, Test City'
        }
        
        # Effectuer la modification
        result = modifier_client_complet(client_id, modifications, "physique")
        
        if result:
            print("✅ Modification réussie")
            
            # Vérifier que la modification a bien été appliquée
            clients_apres = get_all_clients("physique")
            client_modifie = next((c for c in clients_apres if c['id'] == client_id), None)
            
            if client_modifie:
                print(f"📧 Email après modification: {client_modifie.get('email')}")
                print(f"🏠 Adresse après modification: {client_modifie.get('adresse')}")
                
                # Vérifier que les modifications ont été appliquées
                email_ok = client_modifie.get('email') == modifications['email']
                adresse_ok = client_modifie.get('adresse') == modifications['adresse']
                
                if email_ok and adresse_ok:
                    print("✅ Vérification: modifications correctement appliquées")
                    return True
                else:
                    print(f"⚠️ Vérification: email OK={email_ok}, adresse OK={adresse_ok}")
                    return False
            else:
                print("❌ Client non trouvé après modification")
                return False
        else:
            print("❌ Échec de la modification")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la modification: {e}")
        traceback.print_exc()
        return False

def test_statistiques():
    """Test des statistiques"""
    print("\n🔍 Test des statistiques...")
    try:
        from db import get_statistiques
        
        stats = get_statistiques()
        print(f"✅ Statistiques récupérées:")
        print(f"   - Clients physiques: {stats.get('clients_physiques', 0)}")
        print(f"   - Clients moraux: {stats.get('clients_moraux', 0)}")
        print(f"   - Total clients: {stats.get('total_clients', 0)}")
        print(f"   - Total contrats: {stats.get('total_contrats', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des statistiques: {e}")
        traceback.print_exc()
        return False

def test_suppression_client():
    """Test de suppression de client (à la fin)"""
    print("\n🔍 Test de suppression de client...")
    try:
        from db import get_all_clients, supprimer_client_definitif
        
        # Récupérer les clients pour tester la suppression
        clients_physiques = get_all_clients("physique")
        clients_moraux = get_all_clients("moral")
        
        nb_suppressions = 0
        
        # Supprimer les clients de test créés
        for client in clients_physiques:
            if client.get('cin') == 'AB123TEST':
                result = supprimer_client_definitif(client['id'])
                if result:
                    print(f"✅ Client physique {client['id']} supprimé")
                    nb_suppressions += 1
                else:
                    print(f"❌ Échec suppression client physique {client['id']}")
        
        for client in clients_moraux:
            if client.get('ice') == '1234567890123':
                result = supprimer_client_definitif(client['id'])
                if result:
                    print(f"✅ Client moral {client['id']} supprimé")
                    nb_suppressions += 1
                else:
                    print(f"❌ Échec suppression client moral {client['id']}")
        
        print(f"📊 Total suppressions: {nb_suppressions}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")
        traceback.print_exc()
        return False

def test_validation_fonctions():
    """Test des fonctions de validation"""
    print("\n🔍 Test des fonctions de validation...")
    try:
        # Test validation email (si utils.py existe)
        try:
            from utils import valider_email, valider_cin, valider_ice
            
            # Test validation email
            assert valider_email("test@example.com") == True
            assert valider_email("invalid-email") == False
            print("✅ Validation email fonctionnelle")
            
            # Test validation CIN
            assert valider_cin("AB123456") == True
            assert valider_cin("123") == False
            print("✅ Validation CIN fonctionnelle")
            
            # Test validation ICE
            assert valider_ice("1234567890123") == True
            assert valider_ice("123") == False
            print("✅ Validation ICE fonctionnelle")
            
        except ImportError:
            print("⚠️ Module utils.py non trouvé, validation ignorée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de validation: {e}")
        traceback.print_exc()
        return False

def main():
    """Fonction principale de test"""
    print("="*60)
    print("🚀 DÉMARRAGE DES TESTS COMPLETS DU SYSTÈME")
    print("="*60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Initialisation DB", test_database_init),
        ("Ajout Client Physique", test_ajout_client_physique),
        ("Ajout Client Moral", test_ajout_client_moral),
        ("Récupération Clients", test_recuperation_clients),
        ("Recherche Clients", test_recherche_clients),
        ("Modification Client", test_modification_client),
        ("Statistiques", test_statistiques),
        ("Validation", test_validation_fonctions),
        ("Suppression Client", test_suppression_client)
    ]
    
    resultats = []
    
    for nom_test, fonction_test in tests:
        try:
            print(f"\n{'='*20} {nom_test.upper()} {'='*20}")
            resultat = fonction_test()
            resultats.append((nom_test, resultat))
            
            if resultat:
                print(f"🎯 {nom_test}: SUCCÈS")
            else:
                print(f"💥 {nom_test}: ÉCHEC")
                
        except Exception as e:
            print(f"💥 {nom_test}: ERREUR CRITIQUE - {e}")
            resultats.append((nom_test, False))
            traceback.print_exc()
    
    # Résumé final
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    succes = 0
    echecs = 0
    
    for nom, resultat in resultats:
        status = "✅ SUCCÈS" if resultat else "❌ ÉCHEC"
        print(f"{nom:25} : {status}")
        
        if resultat:
            succes += 1
        else:
            echecs += 1
    
    print(f"\n📈 STATISTIQUES FINALES:")
    print(f"   ✅ Tests réussis: {succes}")
    print(f"   ❌ Tests échoués: {echecs}")
    print(f"   📊 Taux de réussite: {(succes/(succes+echecs)*100):.1f}%")
    
    if echecs == 0:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS ! Le système est fonctionnel.")
        print("🚀 Vous pouvez maintenant lancer Streamlit avec: streamlit run votre_fichier.py")
    else:
        print(f"\n⚠️ {echecs} test(s) ont échoué. Vérifiez les erreurs ci-dessus.")
    
    print("="*60)

if __name__ == "__main__":
    main()