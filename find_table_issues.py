"""
Script pour identifier automatiquement les endroits à corriger
Trouve tous les usages de tableaux pandas mal formatés
"""

import os
import re
from pathlib import Path


def find_table_issues(file_path):
    """
    Trouve les problèmes de formatage de tableaux dans un fichier Python
    
    Returns:
        Liste de dictionnaires avec ligne, code, et suggestion
    """
    issues = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    patterns = {
        'df.describe()': {
            'pattern': r'\.describe\(\)',
            'problem': 'Tableau de statistiques non formaté',
            'fix': 'Utiliser formatter.dataframe_to_html(df.describe().T)'
        },
        'df.groupby': {
            'pattern': r'\.groupby\([^)]+\)',
            'problem': 'Agrégation non formatée',
            'fix': 'Utiliser formatter.dataframe_to_html(grouped_df, include_index=True)'
        },
        'df.corr()': {
            'pattern': r'\.corr\(\)',
            'problem': 'Matrice de corrélation non formatée',
            'fix': 'Utiliser formatter.dataframe_to_html(corr_df, include_index=True, precision=3)'
        },
        'pd.crosstab': {
            'pattern': r'pd\.crosstab\(',
            'problem': 'Tableau croisé non formaté',
            'fix': 'Utiliser format_crosstab(df, var1, var2)'
        },
        'str(df': {
            'pattern': r'str\(df[^)]*\)',
            'problem': 'Conversion DataFrame en string brut',
            'fix': 'Ne JAMAIS utiliser str(df). Toujours formater avec TableFormatter'
        },
        'print(df': {
            'pattern': r'print\(df[^)]*\)',
            'problem': 'Print DataFrame (debug)',
            'fix': 'OK pour debug, mais retirer en production'
        }
    }
    
    for line_num, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        for issue_name, config in patterns.items():
            if re.search(config['pattern'], line_stripped):
                issues.append({
                    'line': line_num,
                    'code': line_stripped,
                    'problem': config['problem'],
                    'fix': config['fix'],
                    'severity': 'HIGH' if 'str(df' in line_stripped else 'MEDIUM'
                })
    
    return issues


def scan_project(project_dir):
    """Scan tous les fichiers Python du projet"""
    
    project_path = Path(project_dir)
    
    # Fichiers à scanner
    python_files = [
        'chapter_workflow.py',
        'week2_architect_agent.py',
        'app_streamlit_workflow_FINAL.py',
        'app_streamlit_professional.py','app_streamlit_workflow.py','complete_workflow_steps.py',
        'integrate_workflow.py',
        # Ajoutez d'autres si nécessaire
    ]
    
    results = {}
    
    for filename in python_files:
        file_path = project_path / filename
        
        if file_path.exists():
            issues = find_table_issues(file_path)
            if issues:
                results[filename] = issues
        else:
            print(f"⚠️  Fichier non trouvé : {filename}")
    
    return results


def print_report(results):
    """Affiche un rapport détaillé"""
    
    print("\n" + "="*80)
    print("🔍 RAPPORT DE SCAN - PROBLÈMES DE FORMATAGE DÉTECTÉS")
    print("="*80 + "\n")
    
    if not results:
        print("✅ Aucun problème détecté ! Votre code est déjà propre.")
        return
    
    total_issues = sum(len(issues) for issues in results.values())
    high_severity = sum(1 for issues in results.values() for i in issues if i['severity'] == 'HIGH')
    
    print(f"📊 RÉSUMÉ :")
    print(f"   - {len(results)} fichier(s) avec problèmes")
    print(f"   - {total_issues} problème(s) total")
    print(f"   - {high_severity} critique(s) (haute priorité)")
    print()
    
    for filename, issues in results.items():
        print(f"\n📄 Fichier : {filename}")
        print("-" * 80)
        
        for i, issue in enumerate(issues, 1):
            severity_icon = "🔴" if issue['severity'] == 'HIGH' else "🟡"
            
            print(f"\n{severity_icon} Problème #{i} - Ligne {issue['line']}")
            print(f"   Code : {issue['code'][:70]}...")
            print(f"   ❌ Problème : {issue['problem']}")
            print(f"   ✅ Solution : {issue['fix']}")
    
    print("\n" + "="*80)
    print("📋 PROCHAINES ACTIONS :")
    print("="*80)
    print()
    print("1. Notez les fichiers et numéros de lignes ci-dessus")
    print("2. Ouvrez chaque fichier")
    print("3. Appliquez les corrections suggérées")
    print("4. Testez avec : python test_table_formatter.py")
    print()


def generate_fix_template(results, output_file='corrections_to_apply.md'):
    """Génère un fichier Markdown avec toutes les corrections à faire"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 📋 CORRECTIONS À APPLIQUER\n\n")
        f.write("Ce fichier liste toutes les corrections à faire étape par étape.\n\n")
        
        for filename, issues in results.items():
            f.write(f"## 📄 {filename}\n\n")
            
            for i, issue in enumerate(issues, 1):
                f.write(f"### ❌ Problème #{i} - Ligne {issue['line']}\n\n")
                f.write(f"**Code actuel :**\n```python\n{issue['code']}\n```\n\n")
                f.write(f"**Problème :** {issue['problem']}\n\n")
                f.write(f"**Solution :**\n```python\n# {issue['fix']}\n```\n\n")
                f.write("---\n\n")
    
    print(f"✅ Fichier de corrections généré : {output_file}")


if __name__ == "__main__":
    import sys
    
    # Chemin du projet
    if len(sys.argv) > 1:
        project_dir = sys.argv[1]
    else:
        # Utiliser le répertoire courant
        project_dir = os.getcwd()
    
    print(f"🔍 Scan du projet : {project_dir}\n")
    
    # Scanner
    results = scan_project(project_dir)
    
    # Afficher le rapport
    print_report(results)
    
    # Générer le template de corrections
    if results:
        generate_fix_template(results)
        print(f"\n💡 TIP : Consultez 'corrections_to_apply.md' pour un guide détaillé\n")