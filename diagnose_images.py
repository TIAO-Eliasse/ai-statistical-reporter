"""
Script de diagnostic pour vérifier l'intégrité des images PNG
"""

import os
from pathlib import Path

def check_png_signature(filepath):
    """Vérifie la signature PNG d'un fichier"""
    try:
        with open(filepath, 'rb') as f:
            # Lire les 8 premiers bytes
            header = f.read(8)
            
            # Signature PNG correcte
            png_sig = b'\x89PNG\r\n\x1a\n'
            
            # Afficher les bytes lus
            print(f"\n📄 {os.path.basename(filepath)}")
            print(f"   Taille: {os.path.getsize(filepath):,} bytes")
            print(f"   Premiers 8 bytes: {header.hex()}")
            print(f"   Attendu (PNG):    {png_sig.hex()}")
            
            if header == png_sig:
                print(f"   ✅ Signature PNG VALIDE")
                return True
            else:
                print(f"   ⚠️ Signature différente")
                
                # Essayer d'ouvrir avec PIL quand même
                try:
                    from PIL import Image
                    img = Image.open(filepath)
                    print(f"   ✅ PIL peut ouvrir l'image: {img.size[0]}x{img.size[1]} pixels, format={img.format}")
                    return True
                except Exception as e:
                    print(f"   ❌ PIL ne peut pas ouvrir: {e}")
                    return False
                    
    except Exception as e:
        print(f"   ❌ Erreur lecture: {e}")
        return False


def main():
    print("=" * 70)
    print("DIAGNOSTIC DES IMAGES PNG")
    print("=" * 70)
    
    # Installer PIL si nécessaire
    try:
        from PIL import Image
    except ImportError:
        print("\n📦 Installation de Pillow...")
        os.system("pip install Pillow --quiet")
    
    # Chercher toutes les images
    image_paths = []
    search_dirs = [
        "output/final_report/temp",
        "output/chapters", 
        "output/images",
        "output/final_report/images"
    ]
    
    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            for root, dirs, files in os.walk(search_dir):
                for file in files:
                    if file.endswith('.png'):
                        image_paths.append(os.path.join(root, file))
    
    if not image_paths:
        print("\n❌ Aucune image PNG trouvée!")
        print("\n💡 Cherché dans:")
        for d in search_dirs:
            print(f"   • {d}")
        return
    
    print(f"\n📊 {len(image_paths)} image(s) trouvée(s)")
    
    # Vérifier chaque image
    valid_count = 0
    invalid_count = 0
    
    for img_path in image_paths:
        if check_png_signature(img_path):
            valid_count += 1
        else:
            invalid_count += 1
    
    # Résumé
    print("\n" + "=" * 70)
    print("RÉSUMÉ:")
    print(f"  ✅ Images valides (ou lisibles par PIL): {valid_count}")
    print(f"  ❌ Images corrompues: {invalid_count}")
    print("=" * 70)
    
    if invalid_count > 0:
        print("\n⚠️ RECOMMANDATIONS:")
        print("1. Essayez d'ouvrir les images dans Windows Explorer")
        print("2. Si elles s'ouvrent, ignorez l'avertissement de signature")
        print("3. Sinon, le problème vient du téléchargement E2B")
    
    # Test d'ouverture Windows
    if image_paths:
        print(f"\n💡 Pour tester manuellement, ouvrez:")
        print(f"   {os.path.dirname(image_paths[0])}")


if __name__ == "__main__":
    main()