"""
Test ultra-minimal - Isole le problème exact
"""

print("Test 1 : Import du module...")
try:
    from table_formatter import TableFormatter
    print("✅ Import réussi")
except Exception as e:
    print(f"❌ Erreur import : {e}")
    exit(1)

print("\nTest 2 : Création du formatter...")
try:
    formatter = TableFormatter(style='professional')
    print("✅ Formatter créé")
except Exception as e:
    print(f"❌ Erreur création : {e}")
    exit(1)

print("\nTest 3 : Création d'un DataFrame simple...")
try:
    import pandas as pd
    df = pd.DataFrame({
        'Nom': ['Alice', 'Bob'],
        'Age': [25, 30]
    })
    print("✅ DataFrame créé")
except Exception as e:
    print(f"❌ Erreur DataFrame : {e}")
    exit(1)

print("\nTest 4 : Conversion HTML (CRITIQUE)...")
try:
    html = formatter.dataframe_to_html(df, title="Test")
    print("✅ HTML généré")
    print(f"   Taille : {len(html)} caractères")
    print(f"   Début : {html[:100]}...")
except Exception as e:
    print(f"❌ ERREUR HTML : {e}")
    print(f"   Type d'erreur : {type(e).__name__}")
    
    # Debug détaillé
    import traceback
    print("\n📋 Traceback complet :")
    traceback.print_exc()
    exit(1)

print("\nTest 5 : Conversion Markdown...")
try:
    md = formatter.dataframe_to_markdown(df)
    print("✅ Markdown généré")
except Exception as e:
    print(f"❌ Erreur Markdown : {e}")

print("\n🎉 TOUS LES TESTS PASSÉS !")