"""
Week 2 - Architect Agent
Agent pour analyser les données CSV et générer un plan de rapport

VERSION CORRIGÉE avec gestion encodage CSV/Excel (inspirée de la V1)
- Support UTF-8, Latin-1, ISO-8859-1, Windows-1252
- Support Excel (.xlsx, .xls)
- Gestion robuste des erreurs
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


def analyze_csv(csv_path: str) -> Dict[str, Any]:
    """
    Analyse un fichier CSV/Excel et retourne les métadonnées
    
    CORRECTION : Gestion automatique de l'encodage (UTF-8, Latin-1, ISO-8859-1, etc.)
    comme dans la V1 de l'application Streamlit
    
    Args:
        csv_path: Chemin vers le fichier CSV ou Excel
        
    Returns:
        Dict contenant les métadonnées du fichier
    """
    
    # Vérifier si E2B est disponible
    try:
        from e2b_code_interpreter import Sandbox
        USE_E2B = True
    except ImportError:
        USE_E2B = False
    
    if USE_E2B:
        return _analyze_csv_with_e2b(csv_path)
    else:
        return _analyze_csv_locally(csv_path)


def _analyze_csv_locally(csv_path: str) -> Dict[str, Any]:
    """
    Analyse le CSV localement (fallback si E2B non disponible)
    Utilise EXACTEMENT la même logique que la V1 Streamlit
    """
    import pandas as pd
    import numpy as np
    
    file_path = Path(csv_path)
    file_extension = file_path.suffix.lower()
    
    # ✅ CHARGEMENT AVEC GESTION ENCODAGE (comme V1)
    if file_extension == '.csv':
        # Essayer différents encodages pour les CSV
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            encoding_used = 'utf-8'
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file_path, encoding='latin-1')
                encoding_used = 'latin-1'
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(file_path, encoding='iso-8859-1')
                    encoding_used = 'iso-8859-1'
                except UnicodeDecodeError:
                    # Dernier recours
                    df = pd.read_csv(file_path, encoding='windows-1252')
                    encoding_used = 'windows-1252'
    
    elif file_extension in ['.xlsx', '.xls']:
        # Lire le fichier Excel
        df = pd.read_excel(file_path, engine='openpyxl' if file_extension == '.xlsx' else None)
        encoding_used = 'excel'
    
    else:
        raise ValueError(f"Format de fichier non supporté : {file_extension}")
    
    # Collecter les métadonnées
    metadata = {
        "file_info": {
            "filename": file_path.name,
            "extension": file_extension,
            "encoding": encoding_used
        },
        "shape": {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1])
        },
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        
        # Variables numériques
        "numeric_columns": list(df.select_dtypes(include=['number']).columns),
        
        # Variables catégorielles
        "categorical_columns": list(df.select_dtypes(include=['object', 'category']).columns),
        
        # Valeurs manquantes
        "missing_values": {},
        
        # Statistiques de base
        "basic_stats": {}
    }
    
    # Valeurs manquantes
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        metadata["missing_values"][col] = {
            "count": int(missing_count),
            "percentage": round((missing_count / len(df)) * 100, 2)
        }
    
    # Statistiques numériques
    for col in metadata["numeric_columns"]:
        try:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                metadata["basic_stats"][col] = {
                    "count": int(len(col_data)),
                    "mean": float(col_data.mean()),
                    "median": float(col_data.median()),
                    "std": float(col_data.std()),
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "q25": float(col_data.quantile(0.25)),
                    "q75": float(col_data.quantile(0.75))
                }
        except Exception as e:
            print(f"Warning: Could not compute stats for {col}: {e}")
    
    # Statistiques catégorielles
    for col in metadata["categorical_columns"]:
        try:
            value_counts = df[col].value_counts()
            metadata["basic_stats"][col] = {
                "unique_count": int(df[col].nunique()),
                "most_common": {str(k): int(v) for k, v in value_counts.head(10).items()}
            }
        except Exception as e:
            print(f"Warning: Could not compute stats for {col}: {e}")
    
    return metadata


def _analyze_csv_with_e2b(csv_path: str) -> Dict[str, Any]:
    """
    Analyse le CSV en utilisant E2B (sandbox isolé)
    VERSION CORRIGÉE avec gestion encodage
    """
    from e2b_code_interpreter import Sandbox
    
    # Lire le fichier pour le transférer à E2B
    with open(csv_path, 'rb') as f:
        file_content = f.read()
    
    file_path = Path(csv_path)
    file_extension = file_path.suffix.lower()
    
    # ✅ CODE PYTHON AVEC GESTION ENCODAGE (comme V1)
    python_code = f"""
import pandas as pd
import numpy as np
import json

# ═══════════════════════════════════════════════════════════
# ✅ FONCTION DE CHARGEMENT AVEC GESTION ENCODAGE (V1)
# ═══════════════════════════════════════════════════════════

def load_data_file(filepath):
    \"\"\"
    Charge un fichier CSV ou Excel avec gestion automatique de l'encodage
    Inspiré de la V1 de l'application Streamlit
    \"\"\"
    import os
    from pathlib import Path
    
    file_path = Path(filepath)
    file_extension = file_path.suffix.lower()
    
    if file_extension == '.csv':
        # Essayer différents encodages pour les CSV
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'windows-1252', 'cp1252']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(filepath, encoding=encoding)
                return df, encoding
            except (UnicodeDecodeError, Exception):
                continue
        
        # Si tous échouent
        raise ValueError("Impossible de détecter l'encodage du fichier CSV")
    
    elif file_extension in ['.xlsx', '.xls']:
        # Lire le fichier Excel
        try:
            df = pd.read_excel(filepath, engine='openpyxl' if file_extension == '.xlsx' else None)
            return df, 'excel'
        except ImportError:
            raise ImportError("openpyxl ou xlrd non installé pour lire Excel")
    
    else:
        raise ValueError(f"Format de fichier non supporté : {{file_extension}}")

# Charger le fichier
df, encoding_used = load_data_file('/home/user/data{file_extension}')

# ═══════════════════════════════════════════════════════════
# COLLECTER LES MÉTADONNÉES
# ═══════════════════════════════════════════════════════════

metadata = {{
    "file_info": {{
        "filename": "{file_path.name}",
        "extension": "{file_extension}",
        "encoding": encoding_used
    }},
    "shape": {{
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1])
    }},
    "columns": list(df.columns),
    "dtypes": {{col: str(dtype) for col, dtype in df.dtypes.items()}},
    
    # Variables numériques
    "numeric_columns": list(df.select_dtypes(include=['number']).columns),
    
    # Variables catégorielles  
    "categorical_columns": list(df.select_dtypes(include=['object', 'category']).columns),
    
    # Valeurs manquantes
    "missing_values": {{}},
    
    # Statistiques de base
    "basic_stats": {{}}
}}

# Valeurs manquantes
for col in df.columns:
    missing_count = df[col].isnull().sum()
    metadata["missing_values"][col] = {{
        "count": int(missing_count),
        "percentage": round((missing_count / len(df)) * 100, 2)
    }}

# Statistiques numériques
for col in metadata["numeric_columns"]:
    try:
        col_data = df[col].dropna()
        if len(col_data) > 0:
            metadata["basic_stats"][col] = {{
                "count": int(len(col_data)),
                "mean": float(col_data.mean()),
                "median": float(col_data.median()),
                "std": float(col_data.std()),
                "min": float(col_data.min()),
                "max": float(col_data.max()),
                "q25": float(col_data.quantile(0.25)),
                "q75": float(col_data.quantile(0.75))
            }}
    except Exception as e:
        pass

# Statistiques catégorielles
for col in metadata["categorical_columns"]:
    try:
        value_counts = df[col].value_counts()
        metadata["basic_stats"][col] = {{
            "unique_count": int(df[col].nunique()),
            "most_common": {{str(k): int(v) for k, v in value_counts.head(10).items()}}
        }}
    except Exception as e:
        pass

# Retourner le résultat en JSON
print(json.dumps(metadata))
"""
    
    # Créer le sandbox E2B
    try:
        sandbox = Sandbox()
        
        # Uploader le fichier
        sandbox.files.write(f'/home/user/data{file_extension}', file_content)
        
        # Exécuter le code
        execution = sandbox.run_code(python_code)
        
        # Récupérer le résultat
        if execution.error:
            raise Exception(f"Erreur lors de l'analyse: {execution.error}")
        
        # Parser le JSON de sortie
        output = execution.logs.stdout[0] if execution.logs.stdout else "{}"
        metadata = json.loads(output)
        
        # Fermer le sandbox
        sandbox.close()
        
        return metadata
    
    except Exception as e:
        # En cas d'erreur E2B, fallback vers analyse locale
        print(f"E2B error, falling back to local analysis: {e}")
        return _analyze_csv_locally(csv_path)


def generate_report_plan(
    metadata: Dict[str, Any],
    study_context: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Génère un plan de rapport basé sur les métadonnées
    
    Args:
        metadata: Métadonnées du fichier CSV
        study_context: Contexte de l'étude (optionnel)
        
    Returns:
        Dict contenant le plan du rapport
    """
    import google.generativeai as genai
    from datetime import datetime
    
    # Configuration de Gemini
    api_key = os.getenv("GMINI_API_KEY")
    
    if not api_key:
        raise ValueError("GMINI_API_KEY non trouvée dans les variables d'environnement")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    # Construire le prompt
    prompt = _build_plan_prompt(metadata, study_context)
    
    # Générer le plan
    response = model.generate_content(prompt)
    
    # Parser la réponse
    plan_text = response.text.strip()
    
    # Nettoyer le JSON
    if "```json" in plan_text:
        plan_text = plan_text.split("```json")[1].split("```")[0].strip()
    elif "```" in plan_text:
        plan_text = plan_text.split("```")[1].split("```")[0].strip()
    
    # Parser le JSON
    plan = json.loads(plan_text)
    
    return plan


def _build_plan_prompt(metadata: Dict[str, Any], study_context: Optional[Any] = None) -> str:
    """Construit le prompt pour générer le plan"""
    
    from datetime import datetime
    
    # Informations de base
    num_rows = metadata["shape"]["rows"]
    num_cols = metadata["shape"]["columns"]
    columns = metadata["columns"]
    numeric_cols = metadata["numeric_columns"]
    categorical_cols = metadata["categorical_columns"]
    
    # Contexte d'étude si disponible
    context_section = ""
    if study_context and hasattr(study_context, 'to_prompt_context'):
        context_section = f"""
CONTEXTE DE L'ÉTUDE:
{study_context.to_prompt_context()}
"""
    
    prompt = f"""
Tu es un expert en analyse statistique et rédaction de rapports scientifiques.

DONNÉES À ANALYSER:
- Nombre de lignes: {num_rows:,}
- Nombre de colonnes: {num_cols}
- Variables numériques ({len(numeric_cols)}): {', '.join(numeric_cols[:10])}{"..." if len(numeric_cols) > 10 else ""}
- Variables catégorielles ({len(categorical_cols)}): {', '.join(categorical_cols[:10])}{"..." if len(categorical_cols) > 10 else ""}

{context_section}

TÂCHE:
Génère un plan de rapport statistique détaillé et structuré.

FORMAT DE SORTIE (JSON):
{{
  "titre": "Titre du rapport",
  "date": "{datetime.now().strftime('%Y-%m-%d')}",
  "auteur": "AI Statistical Reporter",
  "chapitres": [
    {{
      "numero": "1",
      "titre": "Introduction et Contexte",
      "sections": [
        {{
          "titre": "Présentation de l'étude",
          "analyses": [
            "Description de l'objectif",
            "Présentation des données"
          ]
        }}
      ]
    }},
    {{
      "numero": "2",
      "titre": "Analyse Descriptive",
      "sections": [
        {{
          "titre": "Statistiques univariées",
          "analyses": [
            "Distribution des variables numériques",
            "Fréquences des variables catégorielles",
            "Détection des valeurs aberrantes"
          ]
        }}
      ]
    }},
    {{
      "numero": "3",
      "titre": "Analyse Bivariée",
      "sections": [
        {{
          "titre": "Corrélations",
          "analyses": [
            "Matrice de corrélation",
            "Tests de significativité"
          ]
        }}
      ]
    }},
    {{
      "numero": "4",
      "titre": "Conclusion et Recommandations",
      "sections": [
        {{
          "titre": "Synthèse des résultats",
          "analyses": [
            "Principaux findings",
            "Recommandations"
          ]
        }}
      ]
    }}
  ]
}}

RÈGLES:
1. Crée 4-6 chapitres pertinents
2. Chaque chapitre a 2-4 sections
3. Chaque section a 3-5 analyses concrètes
4. Adapte le plan aux données disponibles
5. Si un contexte d'étude est fourni, adapte le plan en conséquence
6. Retourne UNIQUEMENT le JSON, sans texte additionnel

Génère maintenant le plan en JSON:
"""
    
    return prompt


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE POUR TESTS
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python week2_architect_agent.py <csv_file_path>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    print("🔍 Analyse du fichier en cours...")
    metadata = analyze_csv(csv_path)
    
    print(f"\n✅ Analyse terminée!")
    print(f"   - Fichier: {metadata['file_info']['filename']}")
    print(f"   - Encodage: {metadata['file_info']['encoding']}")
    print(f"   - Lignes: {metadata['shape']['rows']:,}")
    print(f"   - Colonnes: {metadata['shape']['columns']}")
    
    print("\n📝 Génération du plan...")
    plan = generate_report_plan(metadata)
    
    print(f"\n✅ Plan généré!")
    print(f"   - Titre: {plan['titre']}")
    print(f"   - Chapitres: {len(plan['chapitres'])}")
    
    # Sauvegarder le plan
    output_file = "report_plan.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Plan sauvegardé dans {output_file}")