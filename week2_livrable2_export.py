"""
SEMAINE 2 - LIVRABLE 2 (Jour 6-7)
Export du plan en Markdown pour visualisation
"""

import os
import json
from datetime import datetime


def load_plan(plan_file: str = "report_plan.json") -> dict:
    """Charge le plan JSON"""
    if not os.path.exists(plan_file):
        raise FileNotFoundError(f"Fichier {plan_file} introuvable")
    
    with open(plan_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def plan_to_markdown(plan: dict) -> str:
    """
    Convertit le plan JSON en Markdown formaté
    """
    md = []
    
    # En-tête
    md.append(f"# {plan['titre']}\n")
    md.append(f"*Plan généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*\n")
    md.append("---\n")
    
    # Table des matières
    md.append("## Table des matières\n")
    for chapitre in plan['chapitres']:
        md.append(f"{chapitre['numero']}. [{chapitre['titre']}](#chapitre-{chapitre['numero']})")
        for i, section in enumerate(chapitre['sections'], 1):
            md.append(f"   {chapitre['numero']}.{i}. {section['titre']}")
    md.append("\n---\n")
    
    # Contenu détaillé
    for chapitre in plan['chapitres']:
        md.append(f"\n## Chapitre {chapitre['numero']} : {chapitre['titre']} {{#chapitre-{chapitre['numero']}}}\n")
        
        for i, section in enumerate(chapitre['sections'], 1):
            md.append(f"\n### {chapitre['numero']}.{i}. {section['titre']}\n")
            
            if section['analyses']:
                md.append("**Analyses prévues :**\n")
                for analyse in section['analyses']:
                    md.append(f"- {analyse}")
                md.append("")  # Ligne vide
    
    # Pied de page
    md.append("\n---\n")
    md.append("*Fin du plan*\n")
    
    return "\n".join(md)


def plan_to_html(plan: dict) -> str:
    """
    Convertit le plan JSON en HTML basique
    """
    html = []
    
    html.append("<!DOCTYPE html>")
    html.append("<html lang='fr'>")
    html.append("<head>")
    html.append("    <meta charset='UTF-8'>")
    html.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html.append(f"    <title>{plan['titre']}</title>")
    html.append("    <style>")
    html.append("        body { font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; line-height: 1.6; }")
    html.append("        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }")
    html.append("        h2 { color: #34495e; margin-top: 30px; border-left: 4px solid #3498db; padding-left: 15px; }")
    html.append("        h3 { color: #7f8c8d; margin-left: 20px; }")
    html.append("        ul { margin-left: 40px; }")
    html.append("        li { margin: 5px 0; }")
    html.append("        .toc { background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }")
    html.append("        .timestamp { color: #95a5a6; font-style: italic; }")
    html.append("    </style>")
    html.append("</head>")
    html.append("<body>")
    
    # En-tête
    html.append(f"    <h1>{plan['titre']}</h1>")
    html.append(f"    <p class='timestamp'>Plan généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>")
    
    # Table des matières
    html.append("    <div class='toc'>")
    html.append("        <h2>Table des matières</h2>")
    html.append("        <ul>")
    for chapitre in plan['chapitres']:
        html.append(f"            <li><a href='#chap{chapitre['numero']}'>{chapitre['numero']}. {chapitre['titre']}</a>")
        html.append("                <ul>")
        for i, section in enumerate(chapitre['sections'], 1):
            html.append(f"                    <li>{chapitre['numero']}.{i}. {section['titre']}</li>")
        html.append("                </ul>")
        html.append("            </li>")
    html.append("        </ul>")
    html.append("    </div>")
    
    # Contenu
    for chapitre in plan['chapitres']:
        html.append(f"    <h2 id='chap{chapitre['numero']}'>Chapitre {chapitre['numero']} : {chapitre['titre']}</h2>")
        
        for i, section in enumerate(chapitre['sections'], 1):
            html.append(f"    <h3>{chapitre['numero']}.{i}. {section['titre']}</h3>")
            
            if section['analyses']:
                html.append("    <p><strong>Analyses prévues :</strong></p>")
                html.append("    <ul>")
                for analyse in section['analyses']:
                    html.append(f"        <li>{analyse}</li>")
                html.append("    </ul>")
    
    html.append("</body>")
    html.append("</html>")
    
    return "\n".join(html)


def generate_statistics(plan: dict) -> dict:
    """Génère des statistiques sur le plan"""
    stats = {
        "nb_chapitres": len(plan['chapitres']),
        "nb_sections": 0,
        "nb_analyses": 0,
        "detail_par_chapitre": []
    }
    
    for chapitre in plan['chapitres']:
        nb_sections_chap = len(chapitre['sections'])
        nb_analyses_chap = sum(len(section['analyses']) for section in chapitre['sections'])
        
        stats["nb_sections"] += nb_sections_chap
        stats["nb_analyses"] += nb_analyses_chap
        
        stats["detail_par_chapitre"].append({
            "titre": chapitre['titre'],
            "sections": nb_sections_chap,
            "analyses": nb_analyses_chap
        })
    
    return stats


def export_all(plan_file: str = "report_plan.json"):
    """Exporte le plan dans tous les formats"""
    print("="*70)
    print("EXPORT DU PLAN - LIVRABLE 2")
    print("="*70)
    
    # Charger le plan
    print(f"\n📂 Chargement de {plan_file}...")
    plan = load_plan(plan_file)
    print("✅ Plan chargé")
    
    # Statistiques
    print("\n📊 Statistiques du plan:")
    stats = generate_statistics(plan)
    print(f"   • Nombre de chapitres: {stats['nb_chapitres']}")
    print(f"   • Nombre de sections: {stats['nb_sections']}")
    print(f"   • Nombre d'analyses: {stats['nb_analyses']}")
    print(f"   • Estimation de pages: {stats['nb_analyses'] * 2}-{stats['nb_analyses'] * 3} pages")
    
    print("\n   Détail par chapitre:")
    for detail in stats['detail_par_chapitre']:
        print(f"   - {detail['titre']}: {detail['sections']} sections, {detail['analyses']} analyses")
    
    # Export Markdown
    print("\n📝 Export en Markdown...")
    md_content = plan_to_markdown(plan)
    md_file = "report_plan.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"✅ Fichier créé: {md_file}")
    
    # Export HTML
    print("\n🌐 Export en HTML...")
    html_content = plan_to_html(plan)
    html_file = "report_plan.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ Fichier créé: {html_file}")
    print(f"   👉 Ouvrez {html_file} dans votre navigateur pour visualiser")
    
    # Export statistiques JSON
    print("\n📈 Export des statistiques...")
    stats_file = "plan_statistics.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, indent=2, ensure_ascii=False, fp=f)
    print(f"✅ Fichier créé: {stats_file}")
    
    print("\n" + "="*70)
    print("✅ LIVRABLE 2 TERMINÉ!")
    print("="*70)
    print("\nFichiers générés:")
    print(f"   • {plan_file} (JSON)")
    print(f"   • {md_file} (Markdown)")
    print(f"   • {html_file} (HTML - visualisation)")
    print(f"   • {stats_file} (Statistiques)")
    print("\n👉 Prochaine étape: Semaine 3 - Génération du rapport complet")


def main():
    """Point d'entrée"""
    try:
        export_all()
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        print("💡 Générez d'abord un plan avec: python week2_architect_agent.py test_data.csv")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()