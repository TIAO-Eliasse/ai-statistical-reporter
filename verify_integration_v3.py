"""Vérifie que l'intégration v2.0 est correcte"""

import re

print("="*70)
print("VÉRIFICATION INTÉGRATION v2.0")
print("="*70)

# Lire le fichier
with open('app_streamlit_workflow_v3.py', 'r', encoding='utf-8') as f:
    content = f.read()

checks = {
    "Import UserProfileManager": "from user_profile_manager import" in content,
    "Import DataIntelligence": "from data_intelligence import" in content,
    "Variable USER_PROFILE_MANAGER_AVAILABLE": "USER_PROFILE_MANAGER_AVAILABLE" in content,
    "Variable DATA_INTELLIGENCE_AVAILABLE": "DATA_INTELLIGENCE_AVAILABLE" in content,
    "Sélecteur de profil (selectbox)": 'st.selectbox(\n        "Choisissez votre profil"' in content or "Choisissez votre profil" in content,
    "Passage user_profile_manager au workflow": "user_profile_manager=profile_mgr" in content,
    "Affichage profil actif": "workflow.user_profile_manager" in content,
    "Compteur modules (11)": "/11 modules actifs" in content
}

print("\n📋 Résultats :")
all_ok = True
for check, result in checks.items():
    status = "✅" if result else "❌"
    print(f"{status} {check}")
    if not result:
        all_ok = False

print("\n" + "="*70)
if all_ok:
    print("✅ TOUTES LES MODIFICATIONS SONT PRÉSENTES !")
else:
    print("❌ CERTAINES MODIFICATIONS MANQUENT")
    print("\nConsulte le guide ci-dessus pour les ajouter.")

print("="*70)