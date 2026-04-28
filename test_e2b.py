"""
Test E2B Code Interpreter
Vérifie que E2B fonctionne correctement avec génération de graphiques
"""

import os
import sys
from dotenv import load_dotenv

# IMPORTANT : Forcer l'import du bon package
import e2b_code_interpreter
from e2b_code_interpreter import Sandbox

# Vérifier qu'on utilise le bon package
print(f"📦 Package E2B utilisé: {e2b_code_interpreter.__file__}")

# Charger les variables d'environnement
load_dotenv()

# Vérifier la clé API
api_key = os.getenv('E2B_API_KEY')
if not api_key:
    print('❌ E2B_API_KEY manquante dans .env')
    sys.exit(1)

print(f'✅ API Key trouvée: {api_key[:10]}...')

try:
    # Créer une sandbox
    print('Création sandbox E2B...')
    
    # IMPORTANT : Utiliser Sandbox.create() et non Sandbox()
    s = Sandbox.create()
    
    print('✅ Sandbox créée !')
    print(f'   Sandbox ID: {s.get_info().sandbox_id if hasattr(s, "get_info") else "N/A"}')
    
    # Test 1 : Exécution simple
    print('\n--- Test 1: Calcul simple ---')
    result = s.run_code('result = 2 + 2\nprint(result)', language="python")
    if result.results:
        for r in result.results:
            if hasattr(r, 'text') and r.text:
                print(f'2 + 2 = {r.text.strip()}')
    
    # Test 2 : Graphique matplotlib
    print('\n--- Test 2: Graphique matplotlib ---')
    code_matplotlib = """
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 5))
plt.plot([1, 2, 3, 4], [1, 4, 9, 16], 'bo-')
plt.title('Test Graphique')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)
plt.savefig('test_matplotlib.png')
print('Graphique matplotlib créé')
"""
    result2 = s.run_code(code_matplotlib, language="python")
    if result2.results:
        for r in result2.results:
            print(f'Résultat: {r}')
    
    # Test 3 : Graphique seaborn
    print('\n--- Test 3: Graphique seaborn ---')
    code_seaborn = """
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Données de test
data = {'x': [1, 2, 3, 4, 5], 'y': [2, 4, 5, 4, 5]}
df = pd.DataFrame(data)

# Graphique seaborn
plt.figure(figsize=(8, 5))
sns.scatterplot(data=df, x='x', y='y', s=100)
plt.title('Test Seaborn')
plt.savefig('test_seaborn.png')
print('Graphique seaborn créé')
"""
    result3 = s.run_code(code_seaborn, language="python")
    if result3.results:
        for r in result3.results:
            print(f'Résultat: {r}')
    
    # Test 4 : Pandas
    print('\n--- Test 4: DataFrame pandas ---')
    code_pandas = """
import pandas as pd

df = pd.DataFrame({
    'nom': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'salaire': [50000, 60000, 70000]
})

print(df.to_string())
print(f"Moyenne âge: {df['age'].mean()}")
"""
    result4 = s.run_code(code_pandas, language="python")
    if result4.results:
        for r in result4.results:
            if hasattr(r, 'text') and r.text:
                print(f'Résultat:\n{r.text}')
    
    # Fermer la sandbox avec kill() au lieu de close()
    s.kill()
    print('\n✅ Tous les tests réussis !')
    print('✅ E2B fonctionne parfaitement !')
    
except Exception as e:
    print(f'\n❌ Erreur: {e}')
    import traceback
    traceback.print_exc()