"""
SEMAINE 3 - Jour 4-5: Génération de Graphiques (Mode Fallback)
Version de secours qui fonctionne SANS appeler les LLMs
Utilise des templates de visualisations prédéfinis
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox

load_dotenv()


def format_execution_result(execution):
    """Extrait le texte d'un objet Execution"""
    try:
        if execution is None:
            return None
        if hasattr(execution, "text") and execution.text:
            return execution.text
        
        parts = []
        if hasattr(execution, "results") and execution.results:
            for r in execution.results:
                if getattr(r, "text", None):
                    parts.append(r.text)
        if parts:
            return "\n".join(parts)
        
        if hasattr(execution, "logs") and execution.logs:
            if hasattr(execution.logs, "stdout"):
                return "\n".join(execution.logs.stdout)
        
        return repr(execution)
    except Exception:
        return str(execution)


def generate_basic_visualizations(metadata: dict) -> list:
    """
    Génère des visualisations basiques SANS LLM
    Utilise des templates prédéfinis selon les colonnes disponibles
    """
    print("\n🎨 Génération de visualisations (mode fallback - sans LLM)")
    
    visualizations = []
    
    # 1. Histogramme pour chaque colonne numérique
    for col in metadata['numeric_columns'][:2]:  # Max 2
        viz = {
            "description": f"Distribution de {col}",
            "filename": f"hist_{col}.png",
            "code": f"""
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(10, 6))
plt.hist(df['{col}'], bins=10, edgecolor='black', alpha=0.7)
plt.title('Distribution de {col}', fontsize=16, fontweight='bold')
plt.xlabel('{col}', fontsize=12)
plt.ylabel('Fréquence', fontsize=12)
plt.grid(axis='y', alpha=0.3)
plt.savefig('/home/user/hist_{col}.png', dpi=300, bbox_inches='tight')
plt.close()
"""
        }
        visualizations.append(viz)
    
    # 2. Boxplot pour les colonnes numériques
    if len(metadata['numeric_columns']) >= 2:
        cols = metadata['numeric_columns'][:2]
        viz = {
            "description": f"Comparaison {' vs '.join(cols)}",
            "filename": "boxplot_comparison.png",
            "code": f"""
import matplotlib.pyplot as plt
import seaborn as sns

fig, axes = plt.subplots(1, {len(cols)}, figsize=(12, 5))
fig.suptitle('Comparaison des distributions', fontsize=16, fontweight='bold')

for idx, col in enumerate({cols}):
    axes[idx].boxplot(df[col])
    axes[idx].set_title(col)
    axes[idx].set_ylabel('Valeur')
    axes[idx].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('/home/user/boxplot_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
"""
        }
        visualizations.append(viz)
    
    # 3. Barplot pour les colonnes catégorielles
    if metadata['categorical_columns']:
        col = metadata['categorical_columns'][0]
        viz = {
            "description": f"Répartition par {col}",
            "filename": f"bar_{col}.png",
            "code": f"""
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
counts = df['{col}'].value_counts()
counts.plot(kind='bar', color='steelblue', edgecolor='black')
plt.title('Répartition par {col}', fontsize=16, fontweight='bold')
plt.xlabel('{col}', fontsize=12)
plt.ylabel('Nombre', fontsize=12)
plt.xticks(rotation=45)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('/home/user/bar_{col}.png', dpi=300, bbox_inches='tight')
plt.close()
"""
        }
        visualizations.append(viz)
    
    # 4. Scatterplot si 2+ colonnes numériques
    if len(metadata['numeric_columns']) >= 2:
        col1, col2 = metadata['numeric_columns'][:2]
        viz = {
            "description": f"Relation entre {col1} et {col2}",
            "filename": f"scatter_{col1}_{col2}.png",
            "code": f"""
import matplotlib.pyplot as plt
import numpy as np

plt.figure(figsize=(10, 6))
plt.scatter(df['{col1}'], df['{col2}'], alpha=0.6, s=100, edgecolors='black')

# Ligne de régression
z = np.polyfit(df['{col1}'], df['{col2}'], 1)
p = np.poly1d(z)
plt.plot(df['{col1}'], p(df['{col1}']), "r--", alpha=0.8, linewidth=2, label='Tendance')

plt.title('Relation entre {col1} et {col2}', fontsize=16, fontweight='bold')
plt.xlabel('{col1}', fontsize=12)
plt.ylabel('{col2}', fontsize=12)
plt.legend()
plt.grid(alpha=0.3)
plt.savefig('/home/user/scatter_{col1}_{col2}.png', dpi=300, bbox_inches='tight')
plt.close()
"""
        }
        visualizations.append(viz)
    
    print(f"✅ {len(visualizations)} visualisation(s) générée(s) (templates)")
    return visualizations


def create_visualizations(csv_path: str, visualizations: list, output_dir: str = "output/images") -> list:
    """
    Exécute le code de visualisation et télécharge les images
    """
    print(f"\n📊 Création de {len(visualizations)} visualisation(s)...")
    
    # Créer le dossier de sortie
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    created_images = []
    
    try:
        with Sandbox.create() as sandbox:
            # Upload CSV
            with open(csv_path, 'rb') as f:
                sandbox.files.write("data.csv", f)
            
            # Setup de base
            setup = """
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Backend sans affichage
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration du style
plt.style.use('default')

# Charger les données
df = pd.read_csv('/home/user/data.csv')
print("✓ Données chargées")
"""
            exec_result = sandbox.run_code(setup)
            print(f"   Setup: {format_execution_result(exec_result)}")
            
            # Créer chaque visualisation
            for i, viz in enumerate(visualizations, 1):
                try:
                    print(f"   {i}. {viz['description']}...", end=" ")
                    
                    # Exécuter le code de visualisation
                    execution = sandbox.run_code(viz['code'])
                    
                    if execution and getattr(execution, "error", None):
                        print(f"❌ Erreur: {execution.error}")
                        continue
                    
                    # Télécharger l'image
                    remote_path = f"/home/user/{viz['filename']}"
                    
                    try:
                        # Lire le fichier depuis la sandbox
                        file_content = sandbox.files.read(remote_path)
                        
                        # Convertir en bytes si c'est un string (changement API E2B)
                        if isinstance(file_content, str):
                            file_content = file_content.encode('latin-1')
                        
                        # Sauvegarder localement
                        local_path = os.path.join(output_dir, viz['filename'])
                        with open(local_path, 'wb') as f:
                            f.write(file_content)
                        
                        created_images.append({
                            "description": viz['description'],
                            "filename": viz['filename'],
                            "path": local_path
                        })
                        
                        print("✅")
                    
                    except Exception as e:
                        print(f"❌ Téléchargement: {e}")
                
                except Exception as e:
                    print(f"❌ Erreur: {e}")
        
        print(f"\n✅ {len(created_images)} image(s) créée(s)")
        return created_images
    
    except Exception as e:
        print(f"\n❌ Erreur E2B: {e}")
        print("💡 Vérifiez votre clé API E2B et vos crédits")
        return []


def generate_simple_text(section_info: dict, metadata: dict) -> str:
    """
    Génère un texte simple SANS LLM (template de base)
    """
    print("✍️ Génération du texte (mode fallback - template)")
    
    text = f"## {section_info['titre']}\n\n"
    
    text += "### Introduction\n\n"
    text += f"Cette section présente une analyse descriptive des données, basée sur un échantillon de **{metadata['shape']['rows']} observations** "
    text += f"et **{metadata['shape']['columns']} variables**.\n\n"
    
    text += "### Variables analysées\n\n"
    text += "Les variables numériques comprennent : " + ", ".join(f"**{c}**" for c in metadata['numeric_columns']) + ".\n\n"
    
    if metadata['categorical_columns']:
        text += "Les variables catégorielles comprennent : " + ", ".join(f"**{c}**" for c in metadata['categorical_columns']) + ".\n\n"
    
    text += "### Analyses réalisées\n\n"
    for analyse in section_info['analyses']:
        text += f"- {analyse}\n"
    
    text += "\n### Observations\n\n"
    text += "Les visualisations ci-dessous illustrent les principales caractéristiques des données.\n\n"
    
    return text


def generate_section_with_graphs_fallback(csv_path: str, section_info: dict, metadata: dict, output_dir: str = "output") -> dict:
    """
    Version fallback complète (sans LLM)
    """
    print("\n" + "="*70)
    print(f"GÉNÉRATION COMPLÈTE (MODE FALLBACK): {section_info['titre']}")
    print("="*70)
    
    # 1. Générer les visualisations (templates)
    visualizations = generate_basic_visualizations(metadata)
    
    # 2. Créer les images
    images = create_visualizations(csv_path, visualizations, f"{output_dir}/images")
    
    # 3. Générer le texte simple
    text = generate_simple_text(section_info, metadata)
    
    # 4. Assembler le Markdown
    markdown = text + "\n"
    
    if images:
        markdown += "### Visualisations\n\n"
        for img in images:
            markdown += f"**{img['description']}**\n\n"
            markdown += f"![{img['description']}](images/{img['filename']})\n\n"
    
    return {
        "titre": section_info['titre'],
        "markdown": markdown,
        "images": images
    }


def main():
    """Point d'entrée"""
    print("="*70)
    print("SEMAINE 3 - GÉNÉRATION AVEC GRAPHIQUES (MODE FALLBACK)")
    print("Version sans LLM - fonctionne sans quota Gemini/Anthropic")
    print("="*70)
    
    if len(sys.argv) < 2:
        print("\nUsage: python week3_graph_generator_fallback.py <fichier.csv>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    if not os.path.exists(csv_path):
        print(f"❌ Fichier {csv_path} introuvable")
        sys.exit(1)
    
    # Charger métadonnées
    print("📊 Chargement des métadonnées...")
    with Sandbox.create() as sandbox:
        with open(csv_path, 'rb') as f:
            sandbox.files.write("data.csv", f)
        
        code = """
import pandas as pd
import json
df = pd.read_csv('/home/user/data.csv')
metadata = {
    "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
    "columns": list(df.columns),
    "numeric_columns": list(df.select_dtypes(include='number').columns),
    "categorical_columns": list(df.select_dtypes(include='object').columns),
}
print(json.dumps(metadata))
"""
        execution = sandbox.run_code(code)
        metadata = json.loads(format_execution_result(execution))
    
    print(f"✅ Dataset: {metadata['shape']['rows']} lignes, {metadata['shape']['columns']} colonnes")
    
    # Créer une section fictive pour le test
    section_test = {
        "titre": "Visualisations des données",
        "analyses": [
            "Analyse de la distribution des variables",
            "Comparaison entre les différentes variables",
            "Identification des tendances"
        ]
    }
    
    # Générer la section
    section_content = generate_section_with_graphs_fallback(csv_path, section_test, metadata)
    
    # Sauvegarder
    output_file = "section_with_graphs_fallback.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(section_content['markdown'])
    
    print("\n" + "="*70)
    print("✅ SECTION AVEC GRAPHIQUES GÉNÉRÉE (MODE FALLBACK)!")
    print("="*70)
    print(f"Fichier Markdown: {output_file}")
    print(f"Images créées: {len(section_content['images'])}")
    for img in section_content['images']:
        print(f"   • {img['path']}")
    
    print("\n📌 Note: Cette version utilise des templates prédéfinis.")
    print("   Demain, avec vos quotas Gemini réinitialisés, vous pourrez")
    print("   utiliser la version avec LLM pour des graphiques personnalisés.")


if __name__ == "__main__":
    main()