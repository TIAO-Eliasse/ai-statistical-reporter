"""
Script de test des quotas Gemini Flash
Teste chaque modèle Flash pour voir lequel a les meilleurs quotas
"""

import google.generativeai as genai
import time

# Votre clé API
genai.configure(api_key="AIzaSyAarLfOqEc1y9a8Su_sjzz3Ryvmz9yil78")

# Liste des modèles Flash disponibles
flash_models = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-2.0-flash",
    "gemini-2.0-flash-exp",
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash-lite",
]

print("=" * 70)
print("TEST DES QUOTAS GEMINI FLASH")
print("=" * 70)

results = {}

for model_name in flash_models:
    try:
        print(f"\n🧪 Test: {model_name}")
        
        model = genai.GenerativeModel(model_name)
        
        # Test simple
        start = time.time()
        response = model.generate_content("Réponds juste 'OK'")
        duration = time.time() - start
        
        # Essayer d'obtenir les infos de quota
        try:
            # Certains modèles retournent des infos de quota
            quota_info = "Info quota non disponible"
            if hasattr(response, '_result'):
                quota_info = str(response._result)
        except:
            quota_info = "N/A"
        
        results[model_name] = {
            'status': '✅ Fonctionne',
            'response': response.text[:50],
            'duration': f'{duration:.2f}s',
            'quota': quota_info
        }
        
        print(f"  ✅ Fonctionne")
        print(f"  ⏱️  Temps: {duration:.2f}s")
        print(f"  📝 Réponse: {response.text[:50]}")
        
    except Exception as e:
        error_msg = str(e)
        results[model_name] = {
            'status': '❌ Erreur',
            'error': error_msg[:100]
        }
        
        print(f"  ❌ Erreur: {error_msg[:100]}")
        
        # Détecter les erreurs de quota
        if "quota" in error_msg.lower() or "429" in error_msg:
            print(f"  ⚠️  QUOTA DÉPASSÉ pour {model_name}")

print("\n" + "=" * 70)
print("RÉSUMÉ DES RÉSULTATS")
print("=" * 70)

working_models = [m for m, r in results.items() if r['status'] == '✅ Fonctionne']
failed_models = [m for m, r in results.items() if r['status'] == '❌ Erreur']

print(f"\n✅ Modèles fonctionnels: {len(working_models)}")
for m in working_models:
    print(f"  - {m} ({results[m]['duration']})")

print(f"\n❌ Modèles en erreur: {len(failed_models)}")
for m in failed_models:
    print(f"  - {m}")

print("\n" + "=" * 70)
print("RECOMMANDATIONS")
print("=" * 70)

if working_models:
    print(f"\n🎯 Meilleur choix pour CODE/WRITING/ANALYSIS:")
    print(f"   {working_models[0]}")
    print(f"\n💡 Configuration .env recommandée:")
    print(f"   GEMINI_MODEL_CODE={working_models[0]}")
    print(f"   GEMINI_MODEL_WRITING={working_models[0]}")
    print(f"   GEMINI_MODEL_ANALYSIS={working_models[0]}")
    print(f"   GEMINI_MODEL_PLAN={working_models[0]}")
    print(f"   GEMINI_MODEL={working_models[0]}")
else:
    print("\n⚠️  Aucun modèle Flash disponible actuellement")
    print("   Vérifiez vos quotas sur: https://ai.dev/usage?tab=rate-limit")

print("\n" + "=" * 70)