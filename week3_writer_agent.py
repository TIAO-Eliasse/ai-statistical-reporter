"""
SEMAINE 3 - Jour 1-3: L'Agent Rédacteur
Objectif: Générer le contenu d'une section du rapport (texte + code + résultats)
"""

import os
import json
import sys
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


def load_plan(plan_file: str = "report_plan.json") -> dict:
    """Charge le plan du rapport"""
    with open(plan_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_csv_metadata(csv_path: str) -> dict:
    """Charge les métadonnées du CSV (réutilise le code de Semaine 2)"""
    print(f"📊 Chargement des métadonnées: {csv_path}")
    
    with Sandbox.create() as sandbox:
        with open(csv_path, 'rb') as f:
            sandbox.files.write("data.csv", f)
        
        analysis_code = """
import pandas as pd
import json

df = pd.read_csv('/home/user/data.csv')

metadata = {
    "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
    "columns": list(df.columns),
    "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    "numeric_columns": list(df.select_dtypes(include='number').columns),
    "categorical_columns": list(df.select_dtypes(include='object').columns),
}

print(json.dumps(metadata, indent=2))
"""
        execution = sandbox.run_code(analysis_code)
        result = format_execution_result(execution)
        return json.loads(result)


def generate_analysis_code(section_info: dict, metadata: dict) -> str:
    """
    Génère le code Python pour réaliser les analyses d'une section
    """
    print(f"\n🤖 Génération du code pour: {section_info['titre']}")
    
    prompt = f"""
Tu es un data analyst expert en Python.

CONTEXTE DU DATASET:
- Colonnes: {', '.join(metadata['columns'])}
- Colonnes numériques: {', '.join(metadata['numeric_columns'])}
- Colonnes catégorielles: {', '.join(metadata['categorical_columns'])}
- Lignes: {metadata['shape']['rows']}

SECTION À ANALYSER:
Titre: {section_info['titre']}

Analyses demandées:
{chr(10).join('- ' + a for a in section_info['analyses'])}

TÂCHE:
Génère du code Python qui:
1. Réalise TOUTES les analyses demandées
2. Calcule les statistiques pertinentes
3. Print les résultats de façon claire et structurée
4. Utilise pandas pour les calculs
5. Le DataFrame est déjà chargé dans 'df'

IMPORTANT:
- Code Python uniquement, sans markdown
- Print tous les résultats avec des titres clairs
- Gère les erreurs potentielles
- Ne génère PAS de graphiques (on le fera séparément)

Code:
"""
    
    # Essayer Gemini
    code = None
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
                code = str(gen)
        except Exception as e:
            print(f"   ⚠️ Erreur Gemini: {e}")
    
    # Fallback Anthropic
    if not code:
        try:
            llm = ChatAnthropic(
                model="claude-sonnet-4-20250514",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                temperature=0
            )
            response = llm.invoke(prompt)
            code = response.content
        except Exception as e:
            print(f"   ⚠️ Erreur Anthropic: {e}")
            return "print('Erreur: Impossible de générer le code')"
    
    # Nettoyer le code
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0].strip()
    elif "```" in code:
        code = code.split("```")[1].split("```")[0].strip()
    
    return code


def execute_analysis(csv_path: str, code: str) -> str:
    """Exécute le code d'analyse dans E2B"""
    print("🔧 Exécution du code d'analyse...")
    
    with Sandbox.create() as sandbox:
        # Upload CSV
        with open(csv_path, 'rb') as f:
            sandbox.files.write("data.csv", f)
        
        # Setup
        setup = "import pandas as pd\nimport numpy as np\ndf = pd.read_csv('/home/user/data.csv')"
        sandbox.run_code(setup)
        
        # Exécuter l'analyse
        execution = sandbox.run_code(code)
        
        if execution and getattr(execution, "error", None):
            return f"❌ Erreur: {execution.error}"
        
        result = format_execution_result(execution)
        print("✅ Analyse exécutée")
        return result


def write_section_text(section_info: dict, analysis_results: str, metadata: dict) -> str:
    """
    Génère le texte rédigé de la section basé sur les résultats d'analyse
    """
    print(f"✍️ Rédaction du texte pour: {section_info['titre']}")
    
    prompt = f"""
Tu es un rédacteur scientifique expert en statistiques.

CONTEXTE:
Tu rédiges une section d'un rapport statistique académique.

SECTION: {section_info['titre']}

ANALYSES DEMANDÉES:
{chr(10).join('- ' + a for a in section_info['analyses'])}

RÉSULTATS D'ANALYSE:
{analysis_results}

TÂCHE:
Rédige un texte académique et détaillé (500-800 mots) pour cette section qui:
1. Présente et interprète TOUS les résultats d'analyse
2. Utilise un style formel et professionnel
3. Cite les chiffres exacts des résultats
4. Explique la méthodologie utilisée
5. Tire des conclusions pertinentes
6. Utilise des paragraphes bien structurés

FORMAT:
- Markdown avec titres (##, ###)
- Paragraphes de 4-6 phrases
- Citations de chiffres entre **guillemets gras**
- Formules mathématiques si nécessaire

IMPORTANT:
- Minimum 500 mots
- Style académique (évite "je", "nous")
- Interprétation approfondie, pas juste une liste de chiffres
- Relie les résultats entre eux

Rédaction:
"""
    
    # Essayer Gemini
    text = None
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
                text = str(gen)
        except Exception as e:
            print(f"   ⚠️ Erreur Gemini: {e}")
    
    # Fallback Anthropic
    if not text:
        try:
            llm = ChatAnthropic(
                model="claude-sonnet-4-20250514",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                temperature=0.7
            )
            response = llm.invoke(prompt)
            text = response.content
        except Exception as e:
            print(f"   ⚠️ Erreur Anthropic: {e}")
            text = f"## {section_info['titre']}\n\n[Erreur lors de la génération du texte]\n\nRésultats bruts:\n{analysis_results}"
    
    print("✅ Texte rédigé")
    return text


def generate_section(csv_path: str, section_info: dict, metadata: dict, output_dir: str = "output") -> dict:
    """
    Génère une section complète du rapport
    """
    print("\n" + "="*70)
    print(f"GÉNÉRATION DE SECTION: {section_info['titre']}")
    print("="*70)
    
    # Créer le dossier de sortie
    Path(output_dir).mkdir(exist_ok=True)
    
    # 1. Générer le code d'analyse
    code = generate_analysis_code(section_info, metadata)
    
    # 2. Exécuter l'analyse
    results = execute_analysis(csv_path, code)
    
    # 3. Rédiger le texte
    text = write_section_text(section_info, results, metadata)
    
    # 4. Assembler
    section_content = {
        "titre": section_info['titre'],
        "code": code,
        "resultats": results,
        "texte": text,
        "analyses_demandees": section_info['analyses']
    }
    
    return section_content


def main():
    """Test de génération d'une section"""
    print("="*70)
    print("SEMAINE 3 - AGENT RÉDACTEUR")
    print("Test de génération d'une section")
    print("="*70)
    
    if len(sys.argv) < 2:
        print("\nUsage: python week3_writer_agent.py <fichier.csv>")
        print("\nCe script va générer la PREMIÈRE section du premier chapitre.")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    if not os.path.exists(csv_path):
        print(f"❌ Fichier {csv_path} introuvable")
        sys.exit(1)
    
    # Charger le plan
    plan = load_plan()
    print(f"✅ Plan chargé: {plan['titre']}")
    
    # Charger les métadonnées du CSV
    metadata = load_csv_metadata(csv_path)
    print(f"✅ Métadonnées chargées: {metadata['shape']['rows']} lignes, {metadata['shape']['columns']} colonnes")
    
    # Prendre la première section du premier chapitre pour le test
    premier_chapitre = plan['chapitres'][0]
    premiere_section = premier_chapitre['sections'][0]
    
    print(f"\n📝 Test avec: Chapitre {premier_chapitre['numero']} - {premiere_section['titre']}")
    
    # Générer la section
    section_content = generate_section(csv_path, premiere_section, metadata)
    
    # Sauvegarder
    output_file = "section_test.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# {section_content['titre']}\n\n")
        f.write(section_content['texte'])
        f.write(f"\n\n---\n\n**Code utilisé:**\n```python\n{section_content['code']}\n```")
        f.write(f"\n\n**Résultats bruts:**\n```\n{section_content['resultats']}\n```")
    
    print("\n" + "="*70)
    print("✅ SECTION GÉNÉRÉE!")
    print("="*70)
    print(f"Fichier créé: {output_file}")
    print(f"Nombre de mots: ~{len(section_content['texte'].split())}")
    print("\n👉 Ouvrez section_test.md pour voir le résultat")
    print("👉 Prochaine étape: Génération de graphiques (J4-J5)")


if __name__ == "__main__":
    main()