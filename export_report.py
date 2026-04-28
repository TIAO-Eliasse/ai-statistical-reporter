"""
Script d'export du rapport dans différents formats
L'utilisateur choisit : Word, HTML, PDF, ou tous
"""

import os
import sys
import base64
import re
from pathlib import Path
import subprocess


def embed_images_base64(md_content: str, images_dir: str) -> str:
    """Remplace les références d'images par des images base64"""
    pattern = r'!\[([^\]]*)\]\(([^\)]+)\)'
    
    images_embedded = 0
    images_failed = 0
    
    def replace_image(match):
        nonlocal images_embedded, images_failed
        
        alt_text = match.group(1)
        image_path = match.group(2)
        
        # Construire le chemin complet
        if image_path.startswith('images/'):
            filename = image_path.replace('images/', '')
            full_path = os.path.join(images_dir, filename)
        else:
            full_path = os.path.join(images_dir, image_path)
        
        # Debug
        print(f"   🔍 Recherche: {image_path} → {full_path}")
        
        if os.path.exists(full_path):
            try:
                with open(full_path, 'rb') as f:
                    image_data = f.read()
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                
                ext = os.path.splitext(full_path)[1].lower()
                mime_type = 'image/png' if ext == '.png' else 'image/jpeg'
                
                images_embedded += 1
                print(f"      ✅ Embarquée")
                
                return f'<img src="data:{mime_type};base64,{base64_data}" alt="{alt_text}" style="max-width: 100%; height: auto; display: block; margin: 20px auto;">'
            except Exception as e:
                images_failed += 1
                print(f"      ❌ Erreur: {e}")
                return f'<p style="color: red;">[Image non disponible: {image_path}]</p>'
        else:
            images_failed += 1
            print(f"      ❌ Fichier introuvable")
            return f'<p style="color: red;">[Image non trouvée: {image_path}]</p>'
    
    result = re.sub(pattern, replace_image, md_content)
    print(f"\n   📊 Résumé: {images_embedded} embarquées, {images_failed} échouées")
    return result


def export_to_html(md_file: str, output_file: str) -> bool:
    """Exporte en HTML auto-contenu avec images embarquées"""
    try:
        print("\n📄 Export HTML...")
        
        # Lire le Markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        images_dir = os.path.join(os.path.dirname(md_file), 'images')
        
        # Embarquer les images
        md_with_images = embed_images_base64(md_content, images_dir)
        
        # Convertir Markdown en HTML (simple)
        # Remplacer les titres
        html_body = md_with_images
        html_body = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_body, flags=re.MULTILINE)
        html_body = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_body, flags=re.MULTILINE)
        html_body = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_body, flags=re.MULTILINE)
        html_body = re.sub(r'^\*\*(.+?)\*\*', r'<strong>\1</strong>', html_body, flags=re.MULTILINE)
        html_body = re.sub(r'^\*(.+?)\*', r'<em>\1</em>', html_body, flags=re.MULTILINE)
        
        # Paragraphes
        html_body = html_body.replace('\n\n', '</p><p>')
        html_body = '<p>' + html_body + '</p>'
        
        # Template HTML
        html_full = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport d'Analyse Statistique</title>
    <style>
        body {{
            font-family: 'Georgia', serif;
            line-height: 1.8;
            max-width: 900px;
            margin: 40px auto;
            padding: 30px;
            color: #333;
            background: #fff;
        }}
        h1 {{
            color: #1a1a1a;
            border-bottom: 4px solid #2c5aa0;
            padding-bottom: 15px;
            margin-top: 50px;
        }}
        h2 {{
            color: #2c5aa0;
            margin-top: 40px;
            padding-left: 10px;
            border-left: 5px solid #2c5aa0;
        }}
        h3 {{
            color: #4a7ba7;
            margin-top: 30px;
        }}
        p {{
            text-align: justify;
            margin: 15px 0;
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 30px auto;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-radius: 5px;
        }}
        strong {{ color: #2c5aa0; }}
        em {{ color: #666; font-style: italic; }}
        @media print {{
            body {{ max-width: 100%; }}
        }}
    </style>
</head>
<body>
    {html_body}
</body>
</html>"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_full)
        
        print(f"   ✅ HTML créé: {output_file}")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur HTML: {e}")
        return False


def export_to_word(md_file: str, output_file: str) -> bool:
    """Exporte en Word (.docx) avec pandoc"""
    try:
        print("\n📘 Export Word (.docx)...")
        
        # Vérifier si pandoc est installé
        result = subprocess.run(['pandoc', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        
        if result.returncode != 0:
            print("   ⚠️ Pandoc non installé")
            return False
        
        # Commande pandoc pour Word
        cmd = [
            'pandoc',
            md_file,
            '-o', output_file,
            '--reference-doc=default',  # Style par défaut
            '-V', 'geometry:margin=2.5cm'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"   ✅ Word créé: {output_file}")
            return True
        else:
            print(f"   ❌ Erreur Pandoc: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("   ⚠️ Pandoc n'est pas installé")
        print("   💡 Téléchargez: https://pandoc.org/installing.html")
        return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False


def export_to_pdf(md_file: str, output_file: str) -> bool:
    """Exporte en PDF avec pandoc"""
    try:
        print("\n📕 Export PDF...")
        
        result = subprocess.run(['pandoc', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        
        if result.returncode != 0:
            print("   ⚠️ Pandoc non installé")
            return False
        
        cmd = [
            'pandoc',
            md_file,
            '-o', output_file,
            '--pdf-engine=xelatex',
            '-V', 'geometry:margin=2.5cm',
            '-V', 'fontsize=11pt'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0:
            print(f"   ✅ PDF créé: {output_file}")
            return True
        else:
            print(f"   ❌ Erreur: {result.stderr[:200]}")
            return False
            
    except FileNotFoundError:
        print("   ⚠️ Pandoc n'est pas installé")
        return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False


def main():
    """Point d'entrée avec menu interactif"""
    print("="*70)
    print("📊 EXPORT DU RAPPORT - CHOIX DU FORMAT")
    print("="*70)
    
    # Fichier source
    md_file = "output/final_report/rapport_complet.md"
    
    if not os.path.exists(md_file):
        print(f"\n❌ Fichier {md_file} introuvable")
        print("💡 Générez d'abord le rapport avec: python week4_generate_full_report.py")
        sys.exit(1)
    
    print(f"\n📄 Fichier source: {md_file}")
    
    # Menu de choix
    print("\n" + "="*70)
    print("CHOISISSEZ LE(S) FORMAT(S) D'EXPORT :")
    print("="*70)
    print("1. HTML (auto-contenu avec images embarquées)")
    print("2. Word (.docx) - nécessite Pandoc")
    print("3. PDF - nécessite Pandoc + LaTeX")
    print("4. TOUS les formats")
    print("5. Quitter")
    print("="*70)
    
    choix = input("\nVotre choix (1-5) : ").strip()
    
    base_name = md_file.replace('.md', '')
    results = {}
    
    if choix == '1' or choix == '4':
        results['HTML'] = export_to_html(md_file, f"{base_name}.html")
    
    if choix == '2' or choix == '4':
        results['Word'] = export_to_word(md_file, f"{base_name}.docx")
    
    if choix == '3' or choix == '4':
        results['PDF'] = export_to_pdf(md_file, f"{base_name}.pdf")
    
    if choix == '5':
        print("\n👋 Au revoir!")
        sys.exit(0)
    
    if choix not in ['1', '2', '3', '4', '5']:
        print("\n❌ Choix invalide")
        sys.exit(1)
    
    # Résumé
    print("\n" + "="*70)
    print("📊 RÉSUMÉ DES EXPORTS")
    print("="*70)
    
    success_count = sum(1 for v in results.values() if v)
    
    for format_name, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {format_name}")
    
    if success_count > 0:
        print(f"\n🎉 {success_count} format(s) créé(s) avec succès!")
        print(f"\n📂 Fichiers dans: output/final_report/")
        
        if results.get('HTML'):
            print("   • rapport_complet.html (ouvrez dans votre navigateur)")
        if results.get('Word'):
            print("   • rapport_complet.docx (ouvrez dans Word)")
        if results.get('PDF'):
            print("   • rapport_complet.pdf")
    else:
        print("\n⚠️ Aucun export réussi")
        print("\n💡 Pour installer Pandoc:")
        print("   Windows: https://pandoc.org/installing.html")
        print("   Ou essayez l'export HTML qui fonctionne toujours!")
    
    print("\n" + "="*70)
    print("✅ TERMINÉ!")
    print("="*70)


if __name__ == "__main__":
    main()