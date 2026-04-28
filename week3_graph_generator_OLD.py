"""
SEMAINE 3 - Jour 4-5: Génération de Graphiques (VERSION CORRIGÉE)
Objectif: Créer des visualisations robustes et les sauvegarder en PNG

FIX PRINCIPAL: Téléchargement correct des images PNG depuis E2B
"""

import os
import json
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox
from google.genai import Client as GminiClient
from langchain_anthropic import ChatAnthropic

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


def clean_generated_code(code: str) -> str:
    """
    Nettoie le code généré pour éviter les problèmes d'échappement
    et les caractères Unicode problématiques
    """
    # Remplacer les guillemets et apostrophes problématiques
    replacements = {
        '"': '"',      # Guillemet français ouvrant
        '"': '"',      # Guillemet français fermant
        ''': "'",      # Apostrophe courbe gauche
        ''': "'",      # Apostrophe courbe droite
        '«': '"',      # Guillemet français double ouvrant
        '»': '"',      # Guillemet français double fermant
        '…': '...',    # Points de suspension
        '–': '-',      # Tiret demi-cadratin
        '—': '-',      # Tiret cadratin
        '\u00A0': ' ', # Espace insécable
    }
    
    cleaned = code
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    
    # Normaliser les séquences d'échappement
    cleaned = cleaned.replace(r"\'", "'").replace(r'\"', '"')
    
    # Remplacer les apostrophes dans les strings matplotlib
    # plt.title('texte d'exemple') -> plt.title("texte d'exemple")
    patterns = [
        (r"plt\.title\('([^']*)'", r'plt.title("\1"'),
        (r"plt\.xlabel\('([^']*)'", r'plt.xlabel("\1"'),
        (r"plt\.ylabel\('([^']*)'", r'plt.ylabel("\1"'),
        (r"plt\.suptitle\('([^']*)'", r'plt.suptitle("\1"'),
        (r"ax\.set_title\('([^']*)'", r'ax.set_title("\1"'),
        (r"ax\.set_xlabel\('([^']*)'", r'ax.set_xlabel("\1"'),
        (r"ax\.set_ylabel\('([^']*)'", r'ax.set_ylabel("\1"'),
    ]
    
    for pattern, replacement in patterns:
        cleaned = re.sub(pattern, replacement, cleaned)
    
    return cleaned


def validate_visualization_code(code: str) -> tuple[bool, str]:
    """
    Valide que le code de visualisation contient les éléments essentiels
    Retourne (is_valid, error_message)
    """
    required_elements = [
        ('plt.figure', "Code doit créer une figure avec plt.figure()"),
        ('plt.savefig', "Code doit sauvegarder avec plt.savefig()"),
        ('plt.close', "Code doit fermer la figure avec plt.close()"),
    ]
    
    for element, error_msg in required_elements:
        if element not in code:
            return False, error_msg
    
    # Vérifier que le chemin de sauvegarde est correct
    if '/home/user/' not in code:
        return False, "Le chemin de sauvegarde doit être dans /home/user/"
    
    return True, ""


def generate_visualization_code(section_info: dict, metadata: dict, max_retries: int = 2) -> list:
    """
    Génère du code Python pour créer des visualisations pertinentes
    Retourne une liste de dictionnaires {description, code}
    Avec retry en cas d'erreur
    """
    print(f"\n🎨 Génération des visualisations pour: {section_info['titre']}")
    
    prompt = f"""
Tu es un expert en visualisation de données avec Python (matplotlib, seaborn).

CONTEXTE DU DATASET:
- Colonnes: {', '.join(metadata['columns'])}
- Colonnes numériques: {', '.join(metadata['numeric_columns'])}
- Colonnes catégorielles: {', '.join(metadata['categorical_columns'])}
- Lignes: {metadata['shape']['rows']}

SECTION: {section_info['titre']}

Analyses demandées:
{chr(10).join('- ' + a for a in section_info['analyses'])}

TÂCHE:
Génère 2-3 visualisations pertinentes pour cette section.

Pour CHAQUE visualisation, retourne un objet JSON avec ce format EXACT:
{{
  "visualizations": [
    {{
      "description": "Description courte de ce que montre le graphique",
      "filename": "nom_fichier.png",
      "code": "code Python complet"
    }}
  ]
}}

RÈGLES CRITIQUES pour le code:
1. Importer matplotlib: import matplotlib.pyplot as plt
2. Importer seaborn si nécessaire: import seaborn as sns
3. Le DataFrame est déjà chargé dans 'df'
4. Créer une figure: plt.figure(figsize=(10, 6))
5. OBLIGATOIRE: Sauvegarder avec plt.savefig('/home/user/nom_fichier.png', dpi=300, bbox_inches='tight')
6. OBLIGATOIRE: Fermer la figure avec plt.close()
7. Ajouter des titres, labels et légendes clairs
8. Utiliser un style professionnel

⚠️ RÈGLES DE FORMATAGE STRICTES:
- Utiliser UNIQUEMENT des guillemets doubles " pour tous les textes
- NE JAMAIS utiliser de guillemets courbes/français (" " ' ')
- NE JAMAIS utiliser de caractères Unicode spéciaux dans les strings
- Éviter les accents dans les strings Python (utiliser 'Age' au lieu de 'Âge')
- Utiliser des noms de fichiers sans accents ni caractères spéciaux

EXEMPLE CORRECT:
{{
  "visualizations": [
    {{
      "description": "Distribution des salaires",
      "filename": "distribution_salaires.png",
      "code": "import matplotlib.pyplot as plt\\nimport seaborn as sns\\nplt.figure(figsize=(10, 6))\\nsns.histplot(df[\\"salaire\\"], kde=True)\\nplt.title(\\"Distribution des Salaires\\")\\nplt.xlabel(\\"Salaire\\")\\nplt.ylabel(\\"Frequence\\")\\nplt.savefig('/home/user/distribution_salaires.png', dpi=300, bbox_inches='tight')\\nplt.close()"
    }}
  ]
}}

IMPORTANT: Retourne UNIQUEMENT le JSON, sans markdown ni explications.
"""
    
    for attempt in range(max_retries):
        viz_json = None
        
        # Essayer Gemini en premier
        gmini_key = os.getenv("GMINI_API_KEY")
        
        if gmini_key:
            try:
                gclient = GminiClient(api_key=gmini_key)
                chat = gclient.chats.create(model="gemini-2.5-flash")
                gres = chat.send_message(prompt)
                
                gen = None
                if hasattr(gres, "candidates") and gres.candidates:
                    first = gres.candidates[0]
                    if hasattr(first, "content"):
                        gen = first.content
                        if not isinstance(gen, str) and hasattr(gen, "parts"):
                            parts = getattr(gen, "parts") or []
                            texts = [getattr(p, "text", "") for p in parts if getattr(p, "text", None)]
                            gen = "\n".join(texts).strip()
                
                if gen:
                    viz_json = str(gen)
                    print(f"   ✓ Réponse obtenue de Gemini (tentative {attempt + 1})")
            except Exception as e:
                print(f"   ⚠️ Erreur Gemini: {e}")
        
        # Fallback sur Anthropic
        if not viz_json:
            try:
                llm = ChatAnthropic(
                    model="claude-sonnet-4-20250514",
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    temperature=0.3
                )
                response = llm.invoke(prompt)
                viz_json = response.content
                print(f"   ✓ Réponse obtenue de Claude (tentative {attempt + 1})")
            except Exception as e:
                print(f"   ⚠️ Erreur Anthropic: {e}")
                if attempt == max_retries - 1:
                    return []
                continue
        
        # Nettoyer le JSON
        if "```json" in viz_json:
            viz_json = viz_json.split("```json")[1].split("```")[0].strip()
        elif "```" in viz_json:
            viz_json = viz_json.split("```")[1].split("```")[0].strip()
        
        # Corriger les échappements problématiques
        viz_json = viz_json.replace(r"\\", "\\").replace(r"\'", "'")
        
        # Parser et valider
        try:
            viz_data = json.loads(viz_json)
            visualizations = viz_data.get("visualizations", [])
            
            # Valider chaque visualisation
            valid_viz = []
            for viz in visualizations:
                # Nettoyer le code
                viz['code'] = clean_generated_code(viz['code'])
                
                # Valider
                is_valid, error_msg = validate_visualization_code(viz['code'])
                if is_valid:
                    valid_viz.append(viz)
                else:
                    print(f"   ⚠️ Visualisation invalide: {error_msg}")
            
            if valid_viz:
                print(f"✅ {len(valid_viz)} visualisation(s) générée(s) et validée(s)")
                return valid_viz
            else:
                print(f"   ⚠️ Aucune visualisation valide (tentative {attempt + 1})")
                
        except json.JSONDecodeError as e:
            print(f"   ❌ Erreur de parsing JSON (tentative {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                print("   🔄 Nouvelle tentative...")
            else:
                print(f"   Réponse brute:\n{viz_json[:500]}...")
    
    return []


def create_visualizations(csv_path: str, visualizations: list, output_dir: str = "output/images") -> list:
    """
    Exécute le code de visualisation et télécharge les images
    Retourne la liste des chemins d'images créées
    
    FIX PRINCIPAL: Téléchargement correct des bytes PNG
    """
    print(f"\n📊 Création de {len(visualizations)} visualisation(s)...")
    
    # Créer le dossier de sortie
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    created_images = []
    
    with Sandbox.create() as sandbox:
        # Upload CSV
        with open(csv_path, 'rb') as f:
            sandbox.files.write("data.csv", f)
        
        # Setup de base avec gestion d'erreurs
        setup = """
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Configuration du style
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    plt.style.use('default')

sns.set_palette("husl")

# Charger les données
df = pd.read_csv('/home/user/data.csv')
print(f"Dataset charge: {df.shape[0]} lignes, {df.shape[1]} colonnes")
"""
        try:
            exec_result = sandbox.run_code(setup)
            if exec_result and getattr(exec_result, "error", None):
                print(f"   ⚠️ Avertissement setup: {exec_result.error}")
        except Exception as e:
            print(f"   ⚠️ Erreur setup: {e}")
        
        # Créer chaque visualisation
        for i, viz in enumerate(visualizations, 1):
            try:
                desc_short = viz['description'][:60] + "..." if len(viz['description']) > 60 else viz['description']
                print(f"   {i}. {desc_short}", end=" ")
                
                # Nettoyer le code (double sécurité)
                clean_code = clean_generated_code(viz['code'])
                
                # Wrapper avec gestion d'erreurs
                wrapped_code = f"""
try:
{chr(10).join('    ' + line for line in clean_code.split(chr(10)))}
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {{e}}")
    import traceback
    traceback.print_exc()
"""
                
                # Exécuter le code
                execution = sandbox.run_code(wrapped_code)
                
                # Vérifier les erreurs
                if execution and getattr(execution, "error", None):
                    print(f"❌ Erreur: {execution.error}")
                    continue
                
                # Vérifier le succès dans les logs
                exec_output = format_execution_result(execution)
                if exec_output and "ERROR:" in exec_output:
                    print(f"❌ Erreur: {exec_output}")
                    continue
                
                # ============================================================
                # FIX CRITIQUE: Téléchargement correct des images PNG
                # ============================================================
                remote_path = f"/home/user/{viz['filename']}"
                
                try:
                    # Lire le fichier depuis la sandbox
                    file_content = sandbox.files.read(remote_path)
                    
                    # FIX: Gérer correctement tous les types de retour
                    image_bytes = None
                    
                    if isinstance(file_content, bytes):
                        # C'est déjà des bytes, parfait !
                        image_bytes = file_content
                        
                    elif isinstance(file_content, str):
                        # C'est une string, essayer plusieurs conversions
                        try:
                            # Tentative 1: Base64
                            import base64
                            image_bytes = base64.b64decode(file_content)
                        except:
                            try:
                                # Tentative 2: Latin-1 encoding (compatible avec bytes bruts)
                                image_bytes = file_content.encode('latin-1')
                            except:
                                try:
                                    # Tentative 3: UTF-8 avec ignore
                                    image_bytes = file_content.encode('utf-8', errors='ignore')
                                except:
                                    print(f"❌ Impossible de convertir string en bytes")
                                    continue
                    else:
                        # Type inconnu, essayer conversion forcée
                        try:
                            image_bytes = bytes(file_content)
                        except:
                            try:
                                image_bytes = str(file_content).encode('latin-1')
                            except:
                                print(f"❌ Type de contenu non supporté: {type(file_content)}")
                                continue
                    
                    if not image_bytes:
                        print("❌ Contenu vide")
                        continue
                    
                    # Vérifier la signature PNG (premiers 8 bytes)
                    png_signature = b'\x89PNG\r\n\x1a\n'
                    if not image_bytes.startswith(png_signature):
                        print(f"⚠️ Pas une signature PNG valide, sauvegarde quand même...")
                        # Ne pas continuer, parfois les images sont valides malgré tout
                    
                    # Sauvegarder localement
                    local_path = os.path.join(output_dir, viz['filename'])
                    with open(local_path, 'wb') as f:
                        f.write(image_bytes)
                    
                    # Vérifier la taille du fichier
                    file_size = os.path.getsize(local_path)
                    
                    if file_size > 100:  # Un PNG valide fait au moins 100 bytes
                        created_images.append({
                            "description": viz['description'],
                            "filename": viz['filename'],
                            "path": local_path
                        })
                        print(f"✅ ({file_size:,} bytes)")
                    else:
                        print(f"❌ Fichier trop petit ({file_size} bytes)")
                        os.remove(local_path)  # Supprimer le fichier corrompu
                
                except Exception as e:
                    print(f"❌ Erreur téléchargement: {e}")
                    import traceback
                    traceback.print_exc()
            
            except Exception as e:
                print(f"❌ Erreur globale: {e}")
                import traceback
                traceback.print_exc()
    
    print(f"\n✅ {len(created_images)}/{len(visualizations)} image(s) créée(s) avec succès")
    return created_images


def generate_section_with_graphs(csv_path: str, section_info: dict, metadata: dict, output_dir: str = "output") -> dict:
    """
    Génère une section complète avec texte ET graphiques
    """
    print("\n" + "="*70)
    print(f"GÉNÉRATION COMPLÈTE: {section_info['titre']}")
    print("="*70)
    
    # 1. Générer les visualisations
    visualizations = generate_visualization_code(section_info, metadata)
    
    if not visualizations:
        print("⚠️ Aucune visualisation générée, on continue avec le texte seul")
    
    # 2. Créer les images
    images = create_visualizations(csv_path, visualizations, f"{output_dir}/images")
    
    # 3. Générer le texte (importé de week3_writer_agent.py)
    try:
        from week3_writer_agent import generate_analysis_code, execute_analysis, write_section_text
        
        code = generate_analysis_code(section_info, metadata)
        results = execute_analysis(csv_path, code)
        text = write_section_text(section_info, results, metadata)
    except ImportError:
        print("⚠️ Module week3_writer_agent non trouvé, génération de texte basique")
        text = f"Analyse de la section: {section_info['titre']}\n\n"
        text += f"Analyses effectuées:\n"
        for analyse in section_info.get('analyses', []):
            text += f"- {analyse}\n"
        code = ""
        results = ""
    
    # 4. Assembler le Markdown avec les images
    markdown = f"## {section_info['titre']}\n\n"
    markdown += text + "\n\n"
    
    if images:
        markdown += "### Visualisations\n\n"
        for img in images:
            markdown += f"**{img['description']}**\n\n"
            markdown += f"![{img['description']}](images/{img['filename']})\n\n"
    
    return {
        "titre": section_info['titre'],
        "markdown": markdown,
        "images": images,
        "code": code,
        "resultats": results,
        "nb_images": len(images),
        "success": len(images) > 0
    }


def main():
    """Test de génération avec graphiques"""
    print("="*70)
    print("SEMAINE 3 - GÉNÉRATION AVEC GRAPHIQUES (VERSION CORRIGÉE)")
    print("="*70)
    
    if len(sys.argv) < 2:
        print("\n❌ Usage: python week3_graph_generator.py <fichier.csv>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    if not os.path.exists(csv_path):
        print(f"❌ Fichier {csv_path} introuvable")
        sys.exit(1)
    
    print(f"\n📂 Fichier: {csv_path}")
    
    # Charger le plan
    plan_path = "report_plan.json"
    if not os.path.exists(plan_path):
        print(f"❌ Plan {plan_path} introuvable")
        sys.exit(1)
    
    with open(plan_path, 'r', encoding='utf-8') as f:
        plan = json.load(f)
    
    print(f"✅ Plan chargé: {plan['titre']}")
    
    # Charger métadonnées
    print("\n📊 Chargement des métadonnées...")
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
    
    print(f"✅ {metadata['shape']['rows']} lignes, {metadata['shape']['columns']} colonnes")
    
    # Sélectionner une section de test
    section_viz = None
    for chapitre in plan['chapitres']:
        if "visualisation" in chapitre['titre'].lower() or "analyse" in chapitre['titre'].lower():
            section_viz = chapitre['sections'][0]
            break
    
    if not section_viz:
        # Fallback: prendre la première section du chapitre 2
        section_viz = plan['chapitres'][1]['sections'][0] if len(plan['chapitres']) > 1 else plan['chapitres'][0]['sections'][0]
    
    print(f"\n📝 Test avec: {section_viz['titre']}")
    
    # Générer la section avec graphiques
    section_content = generate_section_with_graphs(csv_path, section_viz, metadata)
    
    # Sauvegarder
    output_file = "section_with_graphs.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(section_content['markdown'])
    
    print("\n" + "="*70)
    print("✅ SECTION AVEC GRAPHIQUES GÉNÉRÉE!")
    print("="*70)
    print(f"📄 Fichier Markdown: {output_file}")
    print(f"🖼️  Images créées: {section_content['nb_images']}")
    
    if section_content['images']:
        print("\n📸 Liste des images:")
        for img in section_content['images']:
            print(f"   • {img['filename']}")
            print(f"     └─ {img['path']}")
    
    print("\n" + "="*70)
    print("👉 Ouvrez section_with_graphs.md pour voir le résultat")
    print("👉 Les images sont dans: output/images/")
    print("👉 Prochaine étape: Livrable 3 - Génération complète (J6-J7)")
    print("="*70)


if __name__ == "__main__":
    main()