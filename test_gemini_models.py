"""
Script de test des modèles Gemini disponibles
Permet de voir quels modèles sont accessibles avec votre clé API
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configurer Gemini avec votre clé
api_key = os.getenv('GMINI_API_KEY')

if not api_key:
    print("❌ ERREUR: GMINI_API_KEY non trouvée dans .env")
    print("\nVérifiez que votre fichier .env contient:")
    print("GMINI_API_KEY=votre_cle_ici")
    exit(1)

print(f"✅ Clé API trouvée: {api_key[:20]}...")

genai.configure(api_key=api_key)

print('\n' + '='*60)
print('MODÈLES GEMINI DISPONIBLES AVEC VOTRE CLÉ')
print('='*60)

try:
    models = genai.list_models()
    
    print('\n📋 Modèles disponibles pour generateContent:\n')
    
    available_models = []
    
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            # Extraire le nom sans le préfixe "models/"
            model_name = m.name.replace('models/', '')
            available_models.append(model_name)
            print(f'   ✅ {model_name}')
    
    print('\n' + '='*60)
    print('CONFIGURATION RECOMMANDÉE POUR .env')
    print('='*60)
    
    if available_models:
        # Recommander le meilleur modèle
        if 'gemini-1.5-flash' in available_models:
            recommended = 'gemini-1.5-flash'
            reason = 'Rapide, quotas élevés (1,500 req/jour)'
        elif 'gemini-pro' in available_models:
            recommended = 'gemini-pro'
            reason = 'Stable, bonne qualité'
        elif 'gemini-1.5-pro' in available_models:
            recommended = 'gemini-1.5-pro'
            reason = 'Meilleure qualité'
        else:
            recommended = available_models[0]
            reason = 'Premier modèle disponible'
        
        print(f'\n✅ RECOMMANDATION: {recommended}')
        print(f'   Raison: {reason}')
        print('\nAjoutez dans votre .env:')
        print(f'   GEMINI_MODEL={recommended}')
        print(f'   USE_CLAUDE=false')
    
    else:
        print('\n⚠️  Aucun modèle disponible pour generateContent')
        print('   Vérifiez votre clé API')
    
    print('\n' + '='*60)

except Exception as e:
    print(f'\n❌ ERREUR lors de la récupération des modèles:')
    print(f'   {e}')
    print('\nPossibles causes:')
    print('   1. Clé API invalide')
    print('   2. Problème de connexion Internet')
    print('   3. Quota API dépassé')