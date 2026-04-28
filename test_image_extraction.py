"""
Test d'extraction d'images depuis E2B
Vérifie que les images sont bien lues et converties en base64
"""

from e2b_code_interpreter import Sandbox
import base64
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

print("=" * 70)
print("TEST D'EXTRACTION D'IMAGES E2B")
print("=" * 70)

# Vérifier que la clé API est chargée
api_key = os.getenv('E2B_API_KEY')
if api_key:
    print(f"\n✅ Clé API E2B chargée: {api_key[:10]}...")
else:
    print("\n❌ Clé API E2B non trouvée dans .env")
    exit(1)

# Créer une sandbox
print("\n1. Création de la sandbox...")
sandbox = Sandbox.create()
print(f"   ✅ Sandbox créée: {sandbox.sandbox_id}")

# Code qui génère un graphique simple
test_code = """
import matplotlib.pyplot as plt
import numpy as np

# Créer un graphique simple
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]

plt.figure(figsize=(8, 5))
plt.plot(x, y, marker='o')
plt.title('Test Graphique')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)

# Sauvegarder
plt.savefig('test_graph.png', dpi=100, bbox_inches='tight')
print("Graphique sauvegardé dans test_graph.png")
"""

print("\n2. Génération du graphique...")
result = sandbox.run_code(test_code, language="python")

if result.error:
    print(f"   ❌ Erreur: {result.error}")
    sandbox.kill()
    exit(1)

print("   ✅ Graphique généré")

# Vérifier la sortie
if result.results:
    for r in result.results:
        if hasattr(r, 'text') and r.text:
            print(f"   📝 Output: {r.text}")

# Tester la lecture du fichier
print("\n3. Lecture du fichier depuis E2B...")

read_code = """
import os
import base64

# Vérifier que le fichier existe
if os.path.exists('test_graph.png'):
    print("✅ Fichier trouvé")
    
    # Lire le fichier
    with open('test_graph.png', 'rb') as f:
        img_data = f.read()
        print(f"📊 Taille: {len(img_data)} bytes")
        
        # Convertir en base64
        img_b64 = base64.b64encode(img_data).decode('utf-8')
        print(f"📝 Base64 length: {len(img_b64)} chars")
        
        # Afficher les premiers caractères
        print(f"🔤 Début: {img_b64[:50]}...")
        
        # Retourner le base64 complet
        print("BASE64_START")
        print(img_b64)
        print("BASE64_END")
else:
    print("❌ Fichier non trouvé")
"""

read_result = sandbox.run_code(read_code, language="python")

if read_result.error:
    print(f"   ❌ Erreur lecture: {read_result.error}")
    sandbox.kill()
    exit(1)

# Extraire le base64
img_b64 = None
if read_result.results:
    output = ""
    for r in read_result.results:
        if hasattr(r, 'text') and r.text:
            output += r.text
    
    print(f"   📄 Output reçu: {len(output)} chars")
    
    # Extraire le base64 entre les marqueurs
    if "BASE64_START" in output and "BASE64_END" in output:
        start = output.find("BASE64_START") + len("BASE64_START")
        end = output.find("BASE64_END")
        img_b64 = output[start:end].strip()
        
        print(f"   ✅ Base64 extrait: {len(img_b64)} chars")
        print(f"   🔤 Début: {img_b64[:50]}...")
    else:
        print("   ❌ Marqueurs BASE64 non trouvés")

# Sauvegarder l'image localement pour tester
if img_b64:
    print("\n4. Sauvegarde locale...")
    
    try:
        # Décoder et sauvegarder
        img_data = base64.b64decode(img_b64)
        
        # Sauvegarder dans outputs
        output_path = "/mnt/user-data/outputs/test_extracted.png"
        with open(output_path, 'wb') as f:
            f.write(img_data)
        
        print(f"   ✅ Image sauvegardée: {output_path}")
        print(f"   📊 Taille: {len(img_data)} bytes")
        
        # Créer un fichier Markdown de test avec base64 inline
        md_path = "/mnt/user-data/outputs/test_image_inline.md"
        with open(md_path, 'w') as f:
            f.write("# Test d'affichage d'image\n\n")
            f.write("## Méthode 1 : Fichier séparé\n\n")
            f.write("![Test Graph](test_extracted.png)\n\n")
            f.write("## Méthode 2 : Base64 inline\n\n")
            f.write(f"![Test Graph](data:image/png;base64,{img_b64})\n\n")
            f.write("---\n\n")
            f.write("Si vous voyez les graphiques ci-dessus, l'extraction fonctionne ! 🎉\n")
        
        print(f"   ✅ Markdown de test créé: {md_path}")
        
    except Exception as e:
        print(f"   ❌ Erreur sauvegarde: {e}")

# Nettoyer
print("\n5. Nettoyage...")
sandbox.kill()
print("   ✅ Sandbox fermée")

print("\n" + "=" * 70)
print("RÉSUMÉ")
print("=" * 70)

if img_b64:
    print("\n✅ SUCCÈS ! L'extraction d'images fonctionne.")
    print(f"\n📄 Fichiers créés :")
    print(f"   - /mnt/user-data/outputs/test_extracted.png")
    print(f"   - /mnt/user-data/outputs/test_image_inline.md")
    print(f"\n🧪 Pour tester l'affichage :")
    print(f"   1. Ouvrir test_image_inline.md dans Streamlit")
    print(f"   2. Vérifier que les deux graphiques s'affichent")
else:
    print("\n❌ ÉCHEC ! L'extraction d'images ne fonctionne pas.")
    print("\n🔍 Vérifiez :")
    print("   - La version de e2b-code-interpreter")
    print("   - Les logs ci-dessus pour identifier l'erreur")

print("\n" + "=" * 70)