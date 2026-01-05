"""
Week 2 - Architect Agent
Agent pour analyser les données CSV et générer un plan de rapport

VERSION AMÉLIORÉE avec :
- Support des profils de rédaction (Académique, Consultant, Institutionnel)
- Gestion encodage CSV/Excel (UTF-8, Latin-1, ISO-8859-1, Windows-1252)
- Support Excel (.xlsx, .xls)
- Adaptation du plan selon le profil
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union


# ═══════════════════════════════════════════════════════════════
# IMPORT DES PROFILS (si disponibles)
# ═══════════════════════════════════════════════════════════════

try:
    from study_context import WritingProfile
    from writing_profiles import get_profile_summary
    PROFILES_AVAILABLE = True
except ImportError:
    PROFILES_AVAILABLE = False
    # Définir des profils simples en fallback
    class WritingProfile:
        ACADEMIC = "academic"
        CONSULTANT = "consultant"
        INSTITUTIONAL = "institutional"


def analyze_csv(csv_path: str) -> Dict[str, Any]:
    """
    Analyse un fichier CSV/Excel et retourne les métadonnées
    
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
    """Analyse le CSV localement (fallback si E2B non disponible)"""
    import pandas as pd
    import numpy as np
    
    file_path = Path(csv_path)
    file_extension = file_path.suffix.lower()
    
    # Chargement avec gestion encodage
    if file_extension == '.csv':
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
                    df = pd.read_csv(file_path, encoding='windows-1252')
                    encoding_used = 'windows-1252'
    
    elif file_extension in ['.xlsx', '.xls']:
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
        "numeric_columns": list(df.select_dtypes(include=['number']).columns),
        "categorical_columns": list(df.select_dtypes(include=['object', 'category']).columns),
        "missing_values": {},
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
    """Analyse le CSV en utilisant E2B (sandbox isolé)"""
    from e2b_code_interpreter import Sandbox
    
    with open(csv_path, 'rb') as f:
        file_content = f.read()
    
    file_path = Path(csv_path)
    file_extension = file_path.suffix.lower()
    
    python_code = f"""
import pandas as pd
import numpy as np
import json

def load_data_file(filepath):
    from pathlib import Path
    
    file_path = Path(filepath)
    file_extension = file_path.suffix.lower()
    
    if file_extension == '.csv':
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'windows-1252', 'cp1252']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(filepath, encoding=encoding)
                return df, encoding
            except (UnicodeDecodeError, Exception):
                continue
        
        raise ValueError("Impossible de détecter l'encodage du fichier CSV")
    
    elif file_extension in ['.xlsx', '.xls']:
        try:
            df = pd.read_excel(filepath, engine='openpyxl' if file_extension == '.xlsx' else None)
            return df, 'excel'
        except ImportError:
            raise ImportError("openpyxl ou xlrd non installé pour lire Excel")
    
    else:
        raise ValueError(f"Format de fichier non supporté : {{file_extension}}")

df, encoding_used = load_data_file('/home/user/data{file_extension}')

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
    "numeric_columns": list(df.select_dtypes(include=['number']).columns),
    "categorical_columns": list(df.select_dtypes(include=['object', 'category']).columns),
    "missing_values": {{}},
    "basic_stats": {{}}
}}

for col in df.columns:
    missing_count = df[col].isnull().sum()
    metadata["missing_values"][col] = {{
        "count": int(missing_count),
        "percentage": round((missing_count / len(df)) * 100, 2)
    }}

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

for col in metadata["categorical_columns"]:
    try:
        value_counts = df[col].value_counts()
        metadata["basic_stats"][col] = {{
            "unique_count": int(df[col].nunique()),
            "most_common": {{str(k): int(v) for k, v in value_counts.head(10).items()}}
        }}
    except Exception as e:
        pass

print(json.dumps(metadata))
"""
    
    try:
        sandbox = Sandbox()
        sandbox.files.write(f'/home/user/data{file_extension}', file_content)
        execution = sandbox.run_code(python_code)
        
        if execution.error:
            raise Exception(f"Erreur lors de l'analyse: {execution.error}")
        
        output = execution.logs.stdout[0] if execution.logs.stdout else "{}"
        metadata = json.loads(output)
        
        sandbox.close()
        
        return metadata
    
    except Exception as e:
        print(f"E2B error, falling back to local analysis: {e}")
        return _analyze_csv_locally(csv_path)


def generate_report_plan(
    metadata: Dict[str, Any],
    study_context: Optional[Any] = None,
    writing_profile: Optional[Union[str, 'WritingProfile']] = None
) -> Dict[str, Any]:
    """
    Génère un plan de rapport basé sur les métadonnées
    
    Args:
        metadata: Métadonnées du fichier CSV
        study_context: Contexte de l'étude (optionnel)
        writing_profile: Profil de rédaction (academic/consultant/institutional)
        
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
    
    # Construire le prompt avec le profil
    prompt = _build_plan_prompt(metadata, study_context, writing_profile)
    
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
    
    # Post-traitement selon le profil
    plan = _post_process_plan_for_profile(plan, writing_profile)
    
    return plan


def _build_plan_prompt(
    metadata: Dict[str, Any],
    study_context: Optional[Any] = None,
    writing_profile: Optional[Union[str, 'WritingProfile']] = None
) -> str:
    """Construit le prompt pour générer le plan selon le profil"""
    
    from datetime import datetime
    
    # Informations de base
    num_rows = metadata["shape"]["rows"]
    num_cols = metadata["shape"]["columns"]
    numeric_cols = metadata["numeric_columns"]
    categorical_cols = metadata["categorical_columns"]
    
    # ═══════════════════════════════════════════════════════════════
    # DÉTERMINER LE PROFIL ET SES INSTRUCTIONS
    # ═══════════════════════════════════════════════════════════════
    
    profile_name = "standard"
    profile_instructions = ""
    
    if writing_profile:
        # Convertir en string si nécessaire
        if isinstance(writing_profile, WritingProfile):
            profile_name = writing_profile.value
        elif isinstance(writing_profile, str):
            profile_name = writing_profile.lower()
        
        # Instructions spécifiques par profil
        if profile_name == "academic":
            profile_instructions = """
PROFIL ACADÉMIQUE - STRUCTURE ATTENDUE :

Le plan doit suivre les standards académiques :

1. **Introduction et Cadre Théorique**
   - Revue de littérature pertinente
   - Question de recherche claire
   - Hypothèses à tester
   - Objectifs de l'étude

2. **Méthodologie**
   - Description des données
   - Approche analytique
   - Justification des méthodes statistiques
   - Limites méthodologiques

3. **Résultats**
   - Analyse descriptive détaillée
   - Tests d'hypothèses
   - Analyses bivariées et multivariées
   - Présentation rigoureuse des résultats

4. **Discussion**
   - Interprétation des résultats
   - Comparaison avec la littérature
   - Implications théoriques
   - Limites de l'étude

5. **Conclusion**
   - Synthèse des contributions
   - Perspectives de recherche future

STYLE : Formel, rigoureux, vocabulaire scientifique précis
"""
        
        elif profile_name == "consultant":
            profile_instructions = """
PROFIL CONSULTANT - STRUCTURE ATTENDUE :

Le plan doit être orienté ACTION et BUSINESS :

1. **Executive Summary**
   - Contexte business et enjeux
   - 3-5 insights clés (bullet points)
   - Recommandations principales (top 3)
   - Impacts quantifiés

2. **Analyse Exploratoire et Diagnostic**
   - État des lieux (où en sommes-nous ?)
   - Identification des PROBLÉMATIQUES business
   - Détection des OPPORTUNITÉS
   - KPIs et métriques clés

3. **Analyse Approfondie**
   - Deep dive sur les leviers de performance
   - Segmentation et patterns business-critical
   - Corrélations et drivers identifiés
   - Benchmarks (si applicable)

4. **Modélisation et Scénarios**
   - Modèles prédictifs pour la prise de décision
   - Scénarios d'optimisation
   - Quantification des impacts (€, %, ROI)
   - Analyse de sensibilité

5. **Recommandations Stratégiques et Plan d'Action** ⭐ CRITIQUE
   - Synthèse des insights clés
   - Recommandations actionnables (Court terme / Moyen terme)
   - Priorisation (Impact vs Effort)
   - Plan de mise en œuvre détaillé
   - KPIs de suivi
   - Quick wins identifiés

STYLE : Orienté action, focus résultats, langage business, visuel
MOTS-CLÉS À UTILISER : Opportunités, Leviers, Optimisation, ROI, Impact, Recommandations, Actions prioritaires
"""
        
        elif profile_name == "institutional":
            profile_instructions = """
PROFIL INSTITUTIONNEL - STRUCTURE ATTENDUE :

Le plan doit garantir TRANSPARENCE et TRAÇABILITÉ :

1. **Contexte et Cadre Réglementaire**
   - Mission et mandat
   - Obligations légales et réglementaires
   - Standards et normes applicables
   - Objectifs institutionnels

2. **Méthodologie et Processus**
   - Collecte des données (traçabilité complète)
   - Validation et contrôle qualité
   - Méthodes d'analyse (justification)
   - Conformité aux standards

3. **Analyse et Résultats**
   - Analyse descriptive exhaustive
   - Indicateurs de suivi
   - Résultats détaillés et documentés
   - Tableaux de bord réglementaires

4. **Conclusions et Conformité**
   - Synthèse des résultats
   - Respect des obligations
   - Recommandations (si applicable)
   - Suivi et accountability

5. **Annexes et Documentation**
   - Méthodologie détaillée
   - Sources de données
   - Glossaire
   - Références réglementaires

STYLE : Formel, neutre, factuel, traçable, documenté
"""
    
    # Contexte d'étude si disponible
    context_section = ""
    if study_context and hasattr(study_context, 'to_prompt_context'):
        context_section = f"""
CONTEXTE DE L'ÉTUDE:
{study_context.to_prompt_context()}
"""
    
    # ═══════════════════════════════════════════════════════════════
    # CONSTRUIRE LE PROMPT COMPLET
    # ═══════════════════════════════════════════════════════════════
    
    prompt = f"""
Tu es un expert en analyse statistique et rédaction de rapports.

PROFIL DE RÉDACTION : {profile_name.upper()}

{profile_instructions}

DONNÉES À ANALYSER:
- Nombre de lignes: {num_rows:,}
- Nombre de colonnes: {num_cols}
- Variables numériques ({len(numeric_cols)}): {', '.join(numeric_cols[:10])}{"..." if len(numeric_cols) > 10 else ""}
- Variables catégorielles ({len(categorical_cols)}): {', '.join(categorical_cols[:10])}{"..." if len(categorical_cols) > 10 else ""}

{context_section}

TÂCHE:
Génère un plan de rapport statistique détaillé ADAPTÉ AU PROFIL {profile_name.upper()}.

FORMAT DE SORTIE (JSON):
{{
  "titre": "Titre du rapport (adapté au profil)",
  "date": "{datetime.now().strftime('%Y-%m-%d')}",
  "auteur": "AI Statistical Reporter",
  "profil": "{profile_name}",
  "chapitres": [
    {{
      "numero": "1",
      "titre": "Titre du chapitre 1",
      "sections": [
        {{
          "titre": "Titre de la section",
          "analyses": [
            "Analyse concrète 1",
            "Analyse concrète 2",
            "Analyse concrète 3"
          ]
        }}
      ]
    }}
  ]
}}

RÈGLES CRITIQUES:
1. RESPECTE STRICTEMENT la structure du profil {profile_name.upper()}
2. Pour CONSULTANT : INCLURE OBLIGATOIREMENT un chapitre "Recommandations Stratégiques" en dernier
3. Adapte le vocabulaire au profil (académique = scientifique, consultant = business, institutionnel = formel)
4. Crée 4-6 chapitres pertinents selon le profil
5. Chaque chapitre a 2-4 sections
6. Chaque section a 3-5 analyses concrètes et adaptées aux données
7. Retourne UNIQUEMENT le JSON, sans texte additionnel

Génère maintenant le plan en JSON:
"""
    
    return prompt


def _post_process_plan_for_profile(
    plan: Dict[str, Any],
    writing_profile: Optional[Union[str, 'WritingProfile']] = None
) -> Dict[str, Any]:
    """
    Post-traite le plan pour s'assurer qu'il respecte le profil
    Ajoute des éléments manquants si nécessaire
    """
    
    if not writing_profile:
        return plan
    
    # Convertir en string
    if isinstance(writing_profile, WritingProfile):
        profile_name = writing_profile.value
    elif isinstance(writing_profile, str):
        profile_name = writing_profile.lower()
    else:
        return plan
    
    # ═══════════════════════════════════════════════════════════════
    # POST-TRAITEMENT CONSULTANT
    # ═══════════════════════════════════════════════════════════════
    
    if profile_name == "consultant":
        # Vérifier si un chapitre "Recommandations" existe
        has_recommendations = False
        has_executive_summary = False
        
        chapitres = plan.get('chapitres', [])
        
        for chap in chapitres:
            titre_lower = chap.get('titre', '').lower()
            if 'recommandation' in titre_lower or 'action' in titre_lower:
                has_recommendations = True
            if 'executive' in titre_lower or 'synthèse' in titre_lower and chap.get('numero') == "1":
                has_executive_summary = True
        
        # Ajouter Executive Summary si manquant
        if not has_executive_summary:
            executive_summary = {
                'numero': '0',
                'titre': 'Executive Summary',
                'sections': [
                    {
                        'titre': 'Contexte et enjeux business',
                        'analyses': [
                            'Contexte de l\'analyse',
                            'Problématiques identifiées',
                            'Objectifs business'
                        ]
                    },
                    {
                        'titre': 'Insights clés',
                        'analyses': [
                            'Top 3-5 découvertes majeures',
                            'Opportunités détectées',
                            'Risques identifiés'
                        ]
                    },
                    {
                        'titre': 'Recommandations principales',
                        'analyses': [
                            'Actions prioritaires (top 3)',
                            'Impacts attendus',
                            'Quick wins'
                        ]
                    }
                ]
            }
            plan['chapitres'].insert(0, executive_summary)
            
            # Renuméroter les chapitres
            for i, chap in enumerate(plan['chapitres'], 1):
                chap['numero'] = str(i)
        
        # Ajouter chapitre Recommandations si manquant
        if not has_recommendations:
            recommendations_chapter = {
                'numero': str(len(plan['chapitres']) + 1),
                'titre': 'Recommandations Stratégiques et Plan d\'Action',
                'sections': [
                    {
                        'titre': 'Synthèse des insights business-critical',
                        'analyses': [
                            'Récapitulatif des découvertes majeures',
                            'Hiérarchisation par impact business',
                            'Opportunités vs Risques'
                        ]
                    },
                    {
                        'titre': 'Recommandations actionnables',
                        'analyses': [
                            'Actions court terme (0-3 mois) - Quick wins',
                            'Initiatives moyen terme (3-12 mois)',
                            'Stratégies long terme (12+ mois)',
                            'Quantification des impacts (€, %, ROI)'
                        ]
                    },
                    {
                        'titre': 'Plan de mise en œuvre',
                        'analyses': [
                            'Roadmap et timeline',
                            'Ressources nécessaires',
                            'KPIs de suivi',
                            'Priorisation (Impact vs Effort)',
                            'Risques et mitigation'
                        ]
                    }
                ]
            }
            plan['chapitres'].append(recommendations_chapter)
    
    # Ajouter le profil au plan
    plan['profil'] = profile_name
    
    return plan


# ═══════════════════════════════════════════════════════════════
# POINT D'ENTRÉE POUR TESTS
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python week2_architect_agent.py <csv_file_path> [profile]")
        print("Profiles: academic, consultant, institutional")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    profile = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("[SEARCH] Analyse du fichier en cours...")
    metadata = analyze_csv(csv_path)
    
    print(f"\n[OK] Analyse terminée!")
    print(f"   - Fichier: {metadata['file_info']['filename']}")
    print(f"   - Encodage: {metadata['file_info']['encoding']}")
    print(f"   - Lignes: {metadata['shape']['rows']:,}")
    print(f"   - Colonnes: {metadata['shape']['columns']}")
    
    print(f"\n📝 Génération du plan (profil: {profile or 'standard'})...")
    plan = generate_report_plan(metadata, writing_profile=profile)
    
    print(f"\n[OK] Plan généré!")
    print(f"   - Titre: {plan['titre']}")
    print(f"   - Profil: {plan.get('profil', 'N/A')}")
    print(f"   - Chapitres: {len(plan['chapitres'])}")
    
    # Afficher les titres des chapitres
    for i, chap in enumerate(plan['chapitres'], 1):
        print(f"      {i}. {chap['titre']}")
    
    # Sauvegarder le plan
    output_file = f"report_plan_{profile or 'standard'}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SAVE] Plan sauvegardé dans {output_file}")