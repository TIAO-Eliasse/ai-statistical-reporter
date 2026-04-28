"""
SEMAINE 4 - Génération du rapport complet
Objectif: Générer tous les chapitres et assembler en un document final
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Import des fonctions de Semaine 3
from week3_livrable3_full_chapter import generate_chapter, load_csv_metadata

load_dotenv()


def create_cover_page(plan: dict, metadata: dict) -> str:
    """Génère la page de garde du rapport"""
    cover = f"""---
title: {plan['titre']}
author: AI Statistical Reporter
date: {datetime.now().strftime('%d %B %Y')}
---

<div style="text-align: center; margin-top: 200px;">

# {plan['titre']}

---

**Rapport d'analyse statistique automatisé**

---

**Dataset analysé :**
- {metadata['shape']['rows']} observations
- {metadata['shape']['columns']} variables

---

**Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}**

**Par : AI Statistical Reporter**  
**Powered by : Claude Sonnet 4 & Gemini 2.5 Flash**

</div>

<div style="page-break-after: always;"></div>

"""
    return cover


def create_table_of_contents(plan: dict) -> str:
    """Génère la table des matières"""
    toc = "# Table des Matières\n\n"
    
    for chapitre in plan['chapitres']:
        toc += f"## {chapitre['numero']}. {chapitre['titre']}\n\n"
        
        for i, section in enumerate(chapitre['sections'], 1):
            toc += f"   {chapitre['numero']}.{i}. {section['titre']}\n\n"
    
    toc += "\n<div style=\"page-break-after: always;\"></div>\n\n"
    return toc


def create_executive_summary(plan: dict, metadata: dict, stats: dict) -> str:
    """Génère un résumé exécutif"""
    summary = f"""# Résumé Exécutif

Ce rapport présente une analyse statistique descriptive complète d'un dataset de **{metadata['shape']['rows']} observations** et **{metadata['shape']['columns']} variables**.

## Caractéristiques du dataset

**Variables numériques :** {', '.join(metadata['numeric_columns'])}

**Variables catégorielles :** {', '.join(metadata['categorical_columns'])}

## Structure du rapport

Le rapport est organisé en **{len(plan['chapitres'])} chapitres** :

"""
    
    for chap in plan['chapitres']:
        summary += f"- **Chapitre {chap['numero']}** : {chap['titre']}\n"
    
    summary += f"\n## Statistiques du rapport\n\n"
    summary += f"- **Nombre total de pages** : ~{stats['total_pages']}\n"
    summary += f"- **Nombre total de mots** : {stats['total_words']}\n"
    summary += f"- **Nombre total d'images** : {stats['total_images']}\n"
    summary += f"- **Chapitres générés** : {stats['chapters_generated']}/{len(plan['chapitres'])}\n"
    
    summary += "\n<div style=\"page-break-after: always;\"></div>\n\n"
    return summary


def generate_full_report(csv_path: str, output_dir: str = "output/final_report") -> dict:
    """
    Génère le rapport complet avec tous les chapitres
    """
    print("="*70)
    print("SEMAINE 4 - GÉNÉRATION DU RAPPORT COMPLET")
    print("="*70)
    
    # Créer le dossier de sortie
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Charger le plan
    print("\n📋 Chargement du plan...")
    with open("report_plan.json", 'r', encoding='utf-8') as f:
        plan = json.load(f)
    print(f"✅ Plan: {plan['titre']}")
    print(f"   Chapitres à générer: {len(plan['chapitres'])}")
    
    # Charger les métadonnées
    print("\n📊 Analyse du dataset...")
    metadata = load_csv_metadata(csv_path)
    print(f"✅ {metadata['shape']['rows']} lignes, {metadata['shape']['columns']} colonnes")
    
    # Statistiques globales
    stats = {
        "total_words": 0,
        "total_images": 0,
        "total_pages": 0,
        "chapters_generated": 0,
        "chapters_details": []
    }
    
    # Liste pour assembler le document final
    all_markdown = []
    
    # Générer chaque chapitre
    print("\n" + "="*70)
    print("GÉNÉRATION DES CHAPITRES")
    print("="*70)
    
    for i, chapitre in enumerate(plan['chapitres'], 1):
        print(f"\n{'█'*70}")
        print(f"CHAPITRE {chapitre['numero']}/{len(plan['chapitres'])}: {chapitre['titre']}")
        print(f"{'█'*70}")
        
        try:
            # Générer le chapitre
            result = generate_chapter(csv_path, chapitre, metadata, f"{output_dir}/temp")
            
            # Mettre à jour les statistiques
            stats['total_words'] += result['word_count']
            stats['total_images'] += result['images_count']
            stats['chapters_generated'] += 1
            
            stats['chapters_details'].append({
                "numero": result['numero'],
                "titre": result['titre'],
                "sections": result['sections_count'],
                "images": result['images_count'],
                "words": result['word_count']
            })
            
            # Charger le markdown généré
            with open(result['output_file'], 'r', encoding='utf-8') as f:
                chapter_md = f.read()
            
            all_markdown.append(chapter_md)
            
            print(f"\n✅ Chapitre {chapitre['numero']} terminé")
            print(f"   └─ Mots: {result['word_count']}, Images: {result['images_count']}")
            
        except Exception as e:
            print(f"\n❌ Erreur lors de la génération du chapitre {chapitre['numero']}: {e}")
            # Ajouter un placeholder
            all_markdown.append(f"\n# Chapitre {chapitre['numero']} : {chapitre['titre']}\n\n*[Erreur lors de la génération]*\n\n")
    
    # Calculer les pages estimées
    stats['total_pages'] = stats['total_words'] // 300
    
    print("\n" + "="*70)
    print("ASSEMBLAGE DU RAPPORT FINAL")
    print("="*70)
    
    # Assembler le document final
    final_markdown = []
    
    # 1. Page de garde
    print("📄 Génération de la page de garde...")
    final_markdown.append(create_cover_page(plan, metadata))
    
    # 2. Résumé exécutif
    print("📊 Génération du résumé exécutif...")
    final_markdown.append(create_executive_summary(plan, metadata, stats))
    
    # 3. Table des matières
    print("📋 Génération de la table des matières...")
    final_markdown.append(create_table_of_contents(plan))
    
    # 4. Tous les chapitres
    print("📚 Assemblage des chapitres...")
    final_markdown.extend(all_markdown)
    
    # 5. Sauvegarder le document final
    final_file = Path(output_dir) / "rapport_complet.md"
    print(f"\n💾 Sauvegarde du rapport final...")
    
    with open(final_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(final_markdown))
    
    print(f"✅ Rapport sauvegardé: {final_file}")
    
    # Copier toutes les images dans un dossier central
    print("\n🖼️  Copie des images...")
    images_dir = Path(output_dir) / "images"
    images_dir.mkdir(exist_ok=True)
    
    import shutil
    temp_chapters_dir = Path(output_dir) / "temp"
    if temp_chapters_dir.exists():
        for chapter_dir in temp_chapters_dir.iterdir():
            if chapter_dir.is_dir():
                chapter_images = chapter_dir / "images"
                if chapter_images.exists():
                    for img_file in chapter_images.iterdir():
                        if img_file.is_file():
                            shutil.copy2(img_file, images_dir / img_file.name)
    
    print(f"✅ {stats['total_images']} images copiées dans {images_dir}")
    
    return {
        "output_file": str(final_file),
        "stats": stats,
        "success": True
    }


def create_pdf(markdown_file: str, output_pdf: str):
    """
    Convertit le Markdown en PDF (nécessite pandoc ou weasyprint)
    """
    print("\n" + "="*70)
    print("CONVERSION EN PDF")
    print("="*70)
    
    # Vérifier si pandoc est installé
    import subprocess
    
    try:
        # Test pandoc
        result = subprocess.run(['pandoc', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        
        if result.returncode == 0:
            print("✅ Pandoc détecté")
            print("\n📄 Conversion Markdown → PDF avec Pandoc...")
            
            # Commande pandoc
            cmd = [
                'pandoc',
                markdown_file,
                '-o', output_pdf,
                '--pdf-engine=xelatex',
                '-V', 'geometry:margin=2.5cm',
                '-V', 'fontsize=11pt',
                '--toc',
                '--toc-depth=2'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ PDF créé: {output_pdf}")
                return True
            else:
                print(f"❌ Erreur Pandoc: {result.stderr}")
                
    except FileNotFoundError:
        print("⚠️ Pandoc n'est pas installé")
        print("\n💡 Pour installer Pandoc:")
        print("   Windows: https://pandoc.org/installing.html")
        print("   Ou: choco install pandoc")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n💡 Alternatives:")
    print("   1. Installez Pandoc pour conversion automatique")
    print("   2. Utilisez un outil en ligne: https://www.markdowntopdf.com/")
    print("   3. Ouvrez le .md dans VSCode et exportez en PDF")
    
    return False


def main():
    """Point d'entrée"""
    print("="*70)
    print("🚀 AI STATISTICAL REPORTER - SEMAINE 4")
    print("Génération automatique du rapport complet")
    print("="*70)
    
    if len(sys.argv) < 2:
        print("\n❌ Usage: python week4_generate_full_report.py <fichier.csv>")
        print("\nExemple:")
        print("  python week4_generate_full_report.py test_data.csv")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    if not os.path.exists(csv_path):
        print(f"❌ Fichier {csv_path} introuvable")
        sys.exit(1)
    
    # Générer le rapport complet
    try:
        result = generate_full_report(csv_path)
        
        # Afficher les résultats
        print("\n" + "="*70)
        print("🎉 RAPPORT COMPLET GÉNÉRÉ!")
        print("="*70)
        
        print(f"\n📄 Fichier Markdown: {result['output_file']}")
        print(f"\n📊 Statistiques finales:")
        print(f"   • Chapitres générés: {result['stats']['chapters_generated']}")
        print(f"   • Mots totaux: {result['stats']['total_words']:,}")
        print(f"   • Images totales: {result['stats']['total_images']}")
        print(f"   • Pages estimées: ~{result['stats']['total_pages']}")
        
        print(f"\n📋 Détail par chapitre:")
        for chap in result['stats']['chapters_details']:
            print(f"   Chapitre {chap['numero']}: {chap['titre']}")
            print(f"      └─ {chap['sections']} sections, {chap['words']} mots, {chap['images']} images")
        
        # Tentative de conversion PDF
        markdown_file = result['output_file']
        pdf_file = markdown_file.replace('.md', '.pdf')
        
        print("\n" + "="*70)
        print("Tentative de conversion en PDF...")
        print("="*70)
        
        pdf_created = create_pdf(markdown_file, pdf_file)
        
        if pdf_created:
            print(f"\n✅ PDF créé: {pdf_file}")
        
        print("\n" + "="*70)
        print("✅ SEMAINE 4 TERMINÉE!")
        print("="*70)
        print("\n🎊 FÉLICITATIONS! Vous avez terminé le projet AI Statistical Reporter!")
        print(f"\n📂 Tous les fichiers sont dans: output/final_report/")
        print(f"   • Rapport Markdown: {result['output_file']}")
        print(f"   • Images: output/final_report/images/")
        if pdf_created:
            print(f"   • Rapport PDF: {pdf_file}")
        
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()