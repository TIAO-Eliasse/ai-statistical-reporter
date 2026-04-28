import textwrap
from e2b_session_manager import execute_python_code

# Simulation du problème : code avec 4 espaces de marge (comme le fait l'IA)
raw_code_from_ai = """
    import pandas as pd
    import matplotlib.pyplot as plt
    print("Test Réussi : Tableaux capturés")
    plt.plot([1, 2, 3], [10, 20, 30])
    plt.title("Test Graphique")
    plt.show()
"""

# SOLUTION : Le nettoyage par dedent
cleaned_code = textwrap.dedent(raw_code_from_ai).strip()

print("--- Tentative d'exécution avec nettoyage ---")
result = execute_python_code("test_user", cleaned_code)

if result['success']:
    print(f"✅ SUCCÈS !")
    print(f"Sortie texte : {result['output']}")
    print(f"Nombre de graphiques : {len(result['charts'])}")
else:
    print(f"❌ ÉCHEC : {result['error']}")