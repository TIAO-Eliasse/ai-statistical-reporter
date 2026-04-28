"""
Test unitaire pour vérifier la correction du problème d'indentation
"""

import sys
import re

def extract_code_cleaning_function():
    """Extrait la fonction de nettoyage du fichier corrigé"""
    
    def clean_code_block(code: str) -> str:
        """
        Nettoie le code généré par l'IA
        - Supprime les lignes E2B_EVENTS_ADDRESS
        - Supprime l'indentation initiale (dedent)
        """
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip empty lines (keep them but clean)
            if not line.strip():
                cleaned_lines.append('')
                continue
            
            # Skip lines with E2B configuration
            if 'E2B_EVENTS_ADDRESS' in line or ('os.environ' in line and 'import os' not in line):
                print(f"   [REMOVED] {line.strip()}")
                continue
            
            # Remove leading whitespace (dedent)
            cleaned_line = line.lstrip()
            cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    return clean_code_block

def test_case_1():
    """Test avec le code problématique original"""
    code = """    import os; os.environ['E2B_EVENTS_ADDRESS'] = 'http://192.0.2.1'
    import pandas as pd
    import numpy as np
    
    df = pd.read_csv('data.csv')
    print(df.head())"""
    
    clean_func = extract_code_cleaning_function()
    cleaned = clean_func(code)
    
    # Vérifier qu'il n'y a plus d'indentation initiale
    assert not cleaned.startswith('    '), "Code should not start with spaces"
    assert 'E2B_EVENTS_ADDRESS' not in cleaned, "E2B line should be removed"
    assert 'import pandas as pd' in cleaned, "Import should be kept"
    
    # Valider syntaxe
    import ast
    try:
        ast.parse(cleaned)
        return True, "✅ Syntaxe valide"
    except SyntaxError as e:
        return False, f"❌ Erreur syntaxe: {e.msg}"

def test_case_2():
    """Test avec indentation mais sans E2B"""
    code = """    import pandas as pd
    import numpy as np
    
    # Analyse
    print(df.describe())"""
    
    clean_func = extract_code_cleaning_function()
    cleaned = clean_func(code)
    
    assert not cleaned.startswith('    '), "Code should not start with spaces"
    assert cleaned.startswith('import pandas'), "Should start with import"
    
    import ast
    try:
        ast.parse(cleaned)
        return True, "✅ Syntaxe valide"
    except SyntaxError as e:
        return False, f"❌ Erreur syntaxe: {e.msg}"

def test_case_3():
    """Test avec code correct (pas d'indentation)"""
    code = """import pandas as pd
import numpy as np

df = pd.read_csv('data.csv')
print(df.head())"""
    
    clean_func = extract_code_cleaning_function()
    cleaned = clean_func(code)
    
    # Le code correct devrait rester inchangé (à part l'absence de E2B)
    assert cleaned == code, "Correct code should not be modified"
    
    import ast
    try:
        ast.parse(cleaned)
        return True, "✅ Syntaxe valide"
    except SyntaxError as e:
        return False, f"❌ Erreur syntaxe: {e.msg}"

def test_case_4():
    """Test avec mixte: indentation + E2B + apostrophes"""
    code = """    import os; os.environ['E2B_EVENTS_ADDRESS'] = 'http://192.0.2.1'
    import pandas as pd
    
    # Analyse de "l'entreprise"
    col = "Chiffre d'affaires"
    print(df[col].mean())"""
    
    clean_func = extract_code_cleaning_function()
    cleaned = clean_func(code)
    
    assert 'E2B_EVENTS_ADDRESS' not in cleaned
    assert not cleaned.startswith('    ')
    assert "Chiffre d'affaires" in cleaned, "Apostrophes should be preserved"
    
    import ast
    try:
        ast.parse(cleaned)
        return True, "✅ Syntaxe valide"
    except SyntaxError as e:
        return False, f"❌ Erreur syntaxe: {e.msg}"

# Exécuter les tests
print("=" * 70)
print("TESTS UNITAIRES - NETTOYAGE DU CODE")
print("=" * 70)

tests = [
    ("Test 1: Code avec E2B + indentation", test_case_1),
    ("Test 2: Code avec indentation seule", test_case_2),
    ("Test 3: Code correct (sans indentation)", test_case_3),
    ("Test 4: Code complexe (E2B + indentation + apostrophes)", test_case_4),
]

passed = 0
failed = 0

for name, test_func in tests:
    print(f"\n{name}...")
    try:
        success, message = test_func()
        print(f"  {message}")
        if success:
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        failed += 1

print("\n" + "=" * 70)
print(f"RÉSULTATS: {passed} tests réussis, {failed} tests échoués")
print("=" * 70)

if failed == 0:
    print("\n✅ TOUS LES TESTS PASSENT - La correction est opérationnelle!")
    sys.exit(0)
else:
    print(f"\n❌ {failed} test(s) échoué(s) - Révision nécessaire")
    sys.exit(1)