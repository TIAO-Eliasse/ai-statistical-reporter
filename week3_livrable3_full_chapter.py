"""
SEMAINE 3 - LIVRABLE 3 (Jour 6-7)
Génération d'un chapitre complet avec toutes ses sections
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Import des fonctions des scripts précédents
from week3_writer_agent import (
    load_csv_metadata,
    generate_analysis_code,
    execute_analysis,
    write_section_text
)
from week3_graph_generator import (
    generate_visualization_code,
    create_visualizations
)

load_dotenv()


def generate_chapter(csv_path: str, chapter_info: dict, metadata: dict, output_dir: str = "output/chapters") -> dict:
    """
    Génère un chapitre complet avec toutes ses sections
    """
    print("\n" + "="*70)
    print(f"GÉNÉRATION DU CHAPITRE {chapter_info['numero']}: {chapter_info['titre']}")
    print("="*70)
    
    # Créer le dossier de sortie
    chapter_dir = Path(output_dir) / f"chapitre_{chapter_info['numero']}"
    chapter_dir.mkdir(parents=True, exist_ok=True)
    images_dir = chapter_dir / "images"
    images_dir.mkdir(exist_ok=True)
    
    # Structure du chapitre
    chapter_content = {
        "numero": chapter_info['numero'],
        "titre": chapter_info['titre'],
        "sections": []
    }
    
    # Générer chaque section
    for i, section_info in enumerate(chapter_info['sections'], 1):
        print(f"\n{'─'*70}")
        print(f"Section {chapter_info['numero']}.{i}: {section_info['titre']}")
        print(f"{'─'*70}")
        
        try:
            # 1. Générer le code d'analyse
            print("  📝 Génération du code d'analyse...")
            code = generate_analysis_code(section_info, metadata)
            
            # 2. Exécuter l'analyse
            print("  🔧 Exécution de l'analyse...")
            results = execute_analysis(csv_path, code)
            
            # 3. Générer les visualisations (utilise LLM si disponible, sinon fallback)
            print("  🎨 Génération des visualisations...")
            visualizations = generate_visualization_code(section_info, metadata)
            
            # Si aucune visualisation générée par LLM, utiliser fallback
            if not visualizations:
                print("    ⚠️ Pas de visualisations LLM, utilisation du fallback...")
                from week3_graph_generator_fallback import generate_basic_visualizations
                visualizations = generate_basic_visualizations(metadata)
            
            # Ne prendre que 2 visualisations par section pour ne pas surcharger
            visualizations = visualizations[:2]
            
            # 4. Créer les images
            print("  📊 Création des images...")
            images = create_visualizations(csv_path, visualizations, str(images_dir))
            
            # 5. Rédiger le texte
            print("  ✍️ Rédaction du texte...")
            text = write_section_text(section_info, results, metadata)
            
            # 6. Assembler la section
            section_markdown = f"### {chapter_info['numero']}.{i}. {section_info['titre']}\n\n"
            section_markdown += text + "\n\n"
            
            if images:
                section_markdown += "**Visualisations :**\n\n"
                for img in images:
                    section_markdown += f"![{img['description']}](images/{img['filename']})\n\n"
                    section_markdown += f"*Figure {chapter_info['numero']}.{i}.{images.index(img)+1} : {img['description']}*\n\n"
            
            chapter_content["sections"].append({
                "numero": f"{chapter_info['numero']}.{i}",
                "titre": section_info['titre'],
                "markdown": section_markdown,
                "images_count": len(images)
            })
            
            print(f"  ✅ Section {chapter_info['numero']}.{i} terminée ({len(images)} images)")
        
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
            # Continuer avec les autres sections
            chapter_content["sections"].append({
                "numero": f"{chapter_info['numero']}.{i}",
                "titre": section_info['titre'],
                "markdown": f"### {chapter_info['numero']}.{i}. {section_info['titre']}\n\n*[Erreur lors de la génération]*\n\n",
                "images_count": 0
            })
    
    # Assembler le chapitre complet
    print(f"\n{'─'*70}")
    print("📑 Assemblage du chapitre...")
    
    full_markdown = f"# Chapitre {chapter_info['numero']} : {chapter_info['titre']}\n\n"
    full_markdown += f"*Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*\n\n"
    full_markdown += "---\n\n"
    
    for section in chapter_content["sections"]:
        full_markdown += section["markdown"]
        full_markdown += "\n---\n\n"
    
    # Sauvegarder le chapitre
    output_file = chapter_dir / f"chapitre_{chapter_info['numero']}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_markdown)
    
    print(f"✅ Chapitre sauvegardé: {output_file}")
    
    # Statistiques
    total_images = sum(s["images_count"] for s in chapter_content["sections"])
    word_count = len(full_markdown.split())
    
    return {
        "numero": chapter_info['numero'],
        "titre": chapter_info['titre'],
        "output_file": str(output_file),
        "sections_count": len(chapter_content["sections"]),
        "images_count": total_images,
        "word_count": word_count,
        "markdown": full_markdown
    }


def main():
    """Point d'entrée - génère un chapitre complet"""
    print("="*70)
    print("SEMAINE 3 - LIVRABLE 3")
    print("Génération d'un chapitre complet")
    print("="*70)
    
    if len(sys.argv) < 2:
        print("\nUsage: python week3_livrable3_full_chapter.py <fichier.csv> [numero_chapitre]")
        print("\nExemples:")
        print("  python week3_livrable3_full_chapter.py test_data.csv 1")
        print("  python week3_livrable3_full_chapter.py test_data.csv 2")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    chapter_num = sys.argv[2] if len(sys.argv) > 2 else "1"
    
    if not os.path.exists(csv_path):
        print(f"❌ Fichier {csv_path} introuvable")
        sys.exit(1)
    
    # Charger le plan
    print("\n📋 Chargement du plan...")
    with open("report_plan.json", 'r', encoding='utf-8') as f:
        plan = json.load(f)
    
    print(f"✅ Plan: {plan['titre']}")
    
    # Trouver le chapitre demandé
    chapter = None
    for chap in plan['chapitres']:
        if chap['numero'] == str(chapter_num):
            chapter = chap
            break
    
    if not chapter:
        print(f"❌ Chapitre {chapter_num} introuvable dans le plan")
        sys.exit(1)
    
    # Charger les métadonnées
    print(f"\n📊 Analyse du dataset...")
    metadata = load_csv_metadata(csv_path)
    print(f"✅ {metadata['shape']['rows']} lignes, {metadata['shape']['columns']} colonnes")
    
    # Générer le chapitre
    result = generate_chapter(csv_path, chapter, metadata)
    
    # Afficher les statistiques
    print("\n" + "="*70)
    print("✅ LIVRABLE 3 TERMINÉ!")
    print("="*70)
    print(f"\nChapitre {result['numero']}: {result['titre']}")
    print(f"  • Fichier: {result['output_file']}")
    print(f"  • Sections: {result['sections_count']}")
    print(f"  • Images: {result['images_count']}")
    print(f"  • Mots: ~{result['word_count']}")
    print(f"  • Pages estimées: {result['word_count'] // 300}-{result['word_count'] // 250}")
    
    print(f"\n📂 Dossier du chapitre: output/chapters/chapitre_{result['numero']}/")
    print(f"📄 Fichier Markdown: {result['output_file']}")
    print(f"🖼️  Images: output/chapters/chapitre_{result['numero']}/images/")
    
    print("\n" + "="*70)
    print("🎉 SEMAINE 3 TERMINÉE!")
    print("="*70)
    print("\n👉 Prochaine étape: Semaine 4 - Intégration complète")
    print("   (Génération de tous les chapitres + assemblage en PDF)")


if __name__ == "__main__":
    main()