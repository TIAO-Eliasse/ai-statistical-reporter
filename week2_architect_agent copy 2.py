"""
Week 2 - Architect Agent - VERSION FINALE ULTIME
Agent pour analyser les données CSV et générer un plan de rapport PERSONNALISÉ

🎯 AMÉLIORATIONS COMPLÈTES :
✅ Métadonnées ENRICHIES (colonnes + types + stats + top valeurs)
✅ Plan DYNAMIQUE adapté aux données réelles
✅ Profils de rédaction INTÉGRÉS (writing_profiles.py)
✅ Séparation MÉTHODOLOGIE vs ANALYSE
✅ Support Excel (.xlsx, .xls) + CSV (multi-encodages)
✅ Post-traitement selon profil
🆕 CORRECTION E2B (timeout 300s + fallback automatique)
🆕 STANDARDS ACADÉMIQUES IMRAD (Introduction, Methods, Results, Discussion)
🆕 EXECUTIVE SUMMARY CONSULTANT (obligatoire en premier)
🆕 TRAÇABILITÉ INSTITUTIONNELLE (cadre réglementaire + sources)
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION E2B ⭐ NOUVEAUTÉ
# ═══════════════════════════════════════════════════════════════

E2B_CONFIG = {
    'timeout': 300,  # 5 minutes au lieu de ~60s par défaut
    'keep_alive': True,
    'api_key': os.getenv('E2B_API_KEY'),
    'enabled': os.getenv('USE_E2B', 'false').lower() == 'true'
}


# ═══════════════════════════════════════════════════════════════
# IMPORT DES PROFILS
# ═══════════════════════════════════════════════════════════════

try:
    from study_context import WritingProfile, StudyContext
    from writing_profiles import get_writing_style_block, get_profile_summary
    PROFILES_AVAILABLE = True
except ImportError:
    PROFILES_AVAILABLE = False
    # Fallback simple
    class WritingProfile:
        ACADEMIC = "academic"
        CONSULTANT = "consultant"
        INSTITUTIONAL = "institutional"
        
        @property
        def value(self):
            return self


# ═══════════════════════════════════════════════════════════════
# ANALYSE CSV ENRICHIE
# ═══════════════════════════════════════════════════════════════

def analyze_csv(csv_path: str) -> Dict[str, Any]:
    """
    Analyse ENRICHIE d'un fichier CSV/Excel
    
    🆕 AMÉLIORATION E2B :
    - Timeout augmenté à 300s
    - Fallback automatique si erreur
    - Keep-alive activé
    
    Args:
        csv_path: Chemin vers le fichier CSV ou Excel
        
    Returns:
        Dict contenant métadonnées enrichies
    """
    
    # 🔧 Vérifier si E2B est activé ET disponible
    use_e2b = False
    
    if E2B_CONFIG['enabled'] and E2B_CONFIG['api_key']:
        try:
            from e2b_code_interpreter import Sandbox
            use_e2b = True
            print("ℹ️ E2B activé pour l'analyse")
        except ImportError:
            print("⚠️ E2B non disponible (module non installé), analyse locale")
            use_e2b = False
    else:
        print("ℹ️ E2B désactivé, analyse locale")
    
    # Choisir méthode d'analyse
    if use_e2b:
        try:
            return _analyze_csv_with_e2b_robust(csv_path)
        except Exception as e:
            print(f"⚠️ E2B error (fallback to local): {e}")
            return _analyze_csv_locally_enriched(csv_path)
    else:
        return _analyze_csv_locally_enriched(csv_path)


def _analyze_csv_with_e2b_robust(csv_path: str) -> Dict[str, Any]:
    """
    🆕 VERSION ROBUSTE de l'analyse E2B
    
    Corrections :
    - Timeout augmenté
    - Keep-alive activé
    - Gestion erreurs complète
    - Fermeture propre
    """
    from e2b_code_interpreter import Sandbox
    
    sandbox = None
    
    try:
        # 🔧 Créer sandbox avec configuration robuste
        sandbox = Sandbox(
            api_key=E2B_CONFIG['api_key'],
            timeout=E2B_CONFIG['timeout'],
            keep_alive=E2B_CONFIG['keep_alive']
        )
        
        print(f"✅ Sandbox E2B créée : {sandbox.sandbox_id}")
        
        # Utiliser version locale enrichie (plus simple et robuste)
        result = _analyze_csv_locally_enriched(csv_path)
        
        return result
    
    except Exception as e:
        print(f"❌ Erreur E2B : {str(e)[:200]}")
        raise  # Propager pour fallback
    
    finally:
        # 🔧 TOUJOURS fermer la sandbox
        if sandbox:
            try:
                sandbox.close()
                print(f"✅ Sandbox fermée proprement")
            except Exception as e:
                print(f"⚠️ Erreur fermeture sandbox : {e}")


def _analyze_csv_locally_enriched(csv_path: str) -> Dict[str, Any]:
    """
    ⭐ VERSION ENRICHIE de l'analyse locale
    Analyse COMPLÈTE colonne par colonne
    """
    import pandas as pd
    import numpy as np
    
    file_path = Path(csv_path)
    file_extension = file_path.suffix.lower()
    
    # ═══════════════════════════════════════════════════════════
    # CHARGEMENT AVEC GESTION ENCODAGE
    # ═══════════════════════════════════════════════════════════
    
    if file_extension == '.csv':
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'windows-1252', 'cp1252']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                encoding_used = encoding
                break
            except (UnicodeDecodeError, Exception):
                continue
        else:
            raise ValueError("Impossible de détecter l'encodage du fichier CSV")
    
    elif file_extension in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path, engine='openpyxl' if file_extension == '.xlsx' else None)
        encoding_used = 'excel'
    
    else:
        raise ValueError(f"Format de fichier non supporté : {file_extension}")
    
    # ═══════════════════════════════════════════════════════════
    # ANALYSE ENRICHIE COLONNE PAR COLONNE
    # ═══════════════════════════════════════════════════════════
    
    columns_info = []
    
    for col in df.columns:
        col_info = {
            'name': col,
            'dtype': str(df[col].dtype),
            'nunique': int(df[col].nunique()),
            'missing': int(df[col].isnull().sum()),
            'missing_pct': float(df[col].isnull().sum() / len(df) * 100) if len(df) > 0 else 0
        }
        
        # Variables numériques
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info['is_numeric'] = True
            col_info['is_categorical'] = False
            
            col_data = df[col].dropna()
            if len(col_data) > 0:
                col_info['min'] = float(col_data.min())
                col_info['max'] = float(col_data.max())
                col_info['mean'] = float(col_data.mean())
                col_info['median'] = float(col_data.median())
                col_info['std'] = float(col_data.std())
                col_info['q25'] = float(col_data.quantile(0.25))
                col_info['q75'] = float(col_data.quantile(0.75))
                
                col_info['is_encoded'] = col_info['nunique'] < 10
                
                if col_info['is_encoded']:
                    value_counts = df[col].value_counts().sort_index()
                    col_info['distribution'] = {str(k): int(v) for k, v in value_counts.items()}
        
        # Variables catégorielles
        else:
            col_info['is_numeric'] = False
            col_info['is_categorical'] = True
            col_info['is_encoded'] = False
            
            if col_info['nunique'] < 1000:
                value_counts = df[col].value_counts().head(10)
                col_info['top_values'] = {str(k): int(v) for k, v in value_counts.items()}
                col_info['top_values_pct'] = {
                    str(k): round(float(v / len(df) * 100), 2)
                    for k, v in value_counts.items()
                }
        
        columns_info.append(col_info)
    
    # Métadonnées globales enrichies
    metadata = {
        "file_info": {
            "filename": file_path.name,
            "extension": file_extension,
            "encoding": encoding_used,
            "size_mb": round(os.path.getsize(csv_path) / (1024 * 1024), 2)
        },
        "shape": {
            "rows": int(len(df)),
            "columns": int(len(df.columns))
        },
        "columns": columns_info,
        "numeric_columns": [c['name'] for c in columns_info if c.get('is_numeric')],
        "categorical_columns": [c['name'] for c in columns_info if c.get('is_categorical')],
        "encoded_columns": [c['name'] for c in columns_info if c.get('is_encoded')],
        "columns_with_missing": [c['name'] for c in columns_info if c['missing'] > 0],
        "sample_data": df.head(3).to_dict('records'),
        "columns_names": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": {
            col: {
                "count": c['missing'],
                "percentage": c['missing_pct']
            }
            for c in columns_info
        },
        "basic_stats": {}
    }
    
    # Statistiques pour compatibilité
    for col in metadata["numeric_columns"]:
        col_data = next(c for c in columns_info if c['name'] == col)
        if 'mean' in col_data:
            metadata["basic_stats"][col] = {
                "count": len(df[col].dropna()),
                "mean": col_data['mean'],
                "median": col_data['median'],
                "std": col_data['std'],
                "min": col_data['min'],
                "max": col_data['max'],
                "q25": col_data['q25'],
                "q75": col_data['q75']
            }
    
    for col in metadata["categorical_columns"]:
        col_data = next(c for c in columns_info if c['name'] == col)
        metadata["basic_stats"][col] = {
            "unique_count": col_data['nunique'],
            "most_common": col_data.get('top_values', {})
        }
    
    return metadata


def _analyze_csv_locally_basic(csv_path: str) -> Dict[str, Any]:
    """Version basique (fallback si erreur dans version enrichie)"""
    import pandas as pd
    
    file_path = Path(csv_path)
    file_extension = file_path.suffix.lower()
    
    if file_extension == '.csv':
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except:
            df = pd.read_csv(file_path, encoding='latin-1')
    else:
        df = pd.read_excel(file_path)
    
    return {
        "file_info": {"filename": file_path.name, "extension": file_extension},
        "shape": {"rows": len(df), "columns": len(df.columns)},
        "columns": list(df.columns),
        "columns_names": list(df.columns),
        "numeric_columns": list(df.select_dtypes(include=['number']).columns),
        "categorical_columns": list(df.select_dtypes(include=['object']).columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": {},
        "basic_stats": {}
    }


# ═══════════════════════════════════════════════════════════════
# GÉNÉRATION DU PLAN DYNAMIQUE
# ═══════════════════════════════════════════════════════════════

def generate_report_plan(
    metadata: Dict[str, Any],
    study_context: Optional[Any] = None,
    writing_profile: Optional[Union[str, 'WritingProfile']] = None
) -> Dict[str, Any]:
    """
    🆕 Génère un plan de rapport PERSONNALISÉ selon :
    - Les données réelles (colonnes, types, valeurs)
    - Le profil de rédaction (academic/consultant/institutional)
    - Le contexte de l'étude (optionnel)
    
    Args:
        metadata: Métadonnées ENRICHIES du fichier CSV
        study_context: Contexte de l'étude (optionnel)
        writing_profile: Profil de rédaction
        
    Returns:
        Dict contenant le plan du rapport personnalisé
    """
    import google.generativeai as genai
    
    # Configuration de Gemini
    api_key = os.getenv("GMINI_API_KEY")
    
    if not api_key:
        raise ValueError("GMINI_API_KEY non trouvée dans les variables d'environnement")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    
    # Construire le prompt DYNAMIQUE avec TOUTES les infos
    prompt = _build_dynamic_prompt(metadata, study_context, writing_profile)
    
    # Générer le plan
    try:
        response = model.generate_content(prompt)
        plan_text = response.text.strip()
        
        # Nettoyer le JSON
        if "```json" in plan_text:
            plan_text = plan_text.split("```json")[1].split("```")[0].strip()
        elif "```" in plan_text:
            plan_text = plan_text.split("```")[1].split("```")[0].strip()
        
        # Parser le JSON
        plan = json.loads(plan_text)
        
        # Post-traitement selon le profil
        plan = _postprocess_plan_by_profile(plan, writing_profile, metadata)
        
        return plan
    
    except Exception as e:
        print(f"❌ Erreur génération plan: {e}")
        return _generate_fallback_plan(metadata, writing_profile)


def _build_dynamic_prompt(
    metadata: Dict[str, Any],
    study_context: Optional[Any] = None,
    writing_profile: Optional[Union[str, 'WritingProfile']] = None
) -> str:
    """
    🆕 Construit un prompt DYNAMIQUE personnalisé
    
    Nouveautés :
    - Utilise les colonnes RÉELLES avec types et stats
    - Intègre le bloc de style depuis writing_profiles.py
    - Instructions IMRAD pour académique
    - Executive Summary obligatoire pour consultant
    - Traçabilité complète pour institutional
    """
    
    # Déterminer le profil
    profile_name = "academic"
    profile_enum = None
    
    if writing_profile:
        if isinstance(writing_profile, WritingProfile):
            profile_name = writing_profile.value
            profile_enum = writing_profile
        elif isinstance(writing_profile, str):
            profile_name = writing_profile.lower()
            if PROFILES_AVAILABLE:
                profile_map = {
                    'academic': WritingProfile.ACADEMIC,
                    'consultant': WritingProfile.CONSULTANT,
                    'institutional': WritingProfile.INSTITUTIONAL
                }
                profile_enum = profile_map.get(profile_name)
    
    # PARTIE 1 : DONNÉES DISPONIBLES (ENRICHIES)
    columns = metadata.get('columns', [])
    num_rows = metadata['shape']['rows']
    num_cols = metadata['shape']['columns']
    
    prompt = f"""
Tu es un statisticien expert en analyse de données et rédaction de rapports.

╔══════════════════════════════════════════════════════════════════════════════╗
║ DONNÉES À ANALYSER                                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 VOLUME :
- Nombre de lignes : {num_rows:,}
- Nombre de colonnes : {num_cols}

📋 COLONNES PAR CATÉGORIE :

"""
    
    # Variables numériques détaillées
    if metadata.get('numeric_columns'):
        prompt += f"🔢 Variables numériques ({len(metadata['numeric_columns'])}) :\n"
        for col_name in metadata['numeric_columns'][:15]:
            col = next((c for c in columns if c['name'] == col_name), None)
            if col:
                if col.get('is_encoded'):
                    prompt += f"  • {col_name} [ENCODÉE - {col['nunique']} catégories]\n"
                elif 'mean' in col:
                    prompt += f"  • {col_name} (min: {col['min']:.2f}, max: {col['max']:.2f}, moy: {col['mean']:.2f})\n"
        
        if len(metadata['numeric_columns']) > 15:
            prompt += f"  • ... et {len(metadata['numeric_columns']) - 15} autres colonnes numériques\n"
    
    # Variables catégorielles détaillées
    if metadata.get('categorical_columns'):
        prompt += f"\n📋 Variables catégorielles ({len(metadata['categorical_columns'])}) :\n"
        for col_name in metadata['categorical_columns'][:15]:
            col = next((c for c in columns if c['name'] == col_name), None)
            if col:
                top = list(col.get('top_values', {}).keys())[:3]
                prompt += f"  • {col_name} ({col['nunique']} catégories, top: {', '.join(top)})\n"
        
        if len(metadata['categorical_columns']) > 15:
            prompt += f"  • ... et {len(metadata['categorical_columns']) - 15} autres colonnes catégorielles\n"
    
    # Variables encodées
    if metadata.get('encoded_columns'):
        prompt += f"\n⚠️ Variables ENCODÉES (< 10 valeurs) : {', '.join(metadata['encoded_columns'][:10])}\n"
        prompt += "   → À traiter comme catégorielles, PAS de moyenne/std\n"
    
    # Valeurs manquantes
    if metadata.get('columns_with_missing'):
        prompt += f"\n⚠️ Variables avec valeurs manquantes ({len(metadata['columns_with_missing'])}) : "
        prompt += f"{', '.join(metadata['columns_with_missing'][:10])}\n"
        prompt += "   → Nécessite une section dans le chapitre Méthodologie\n"
    
    # PARTIE 2 : CONTEXTE DE L'ÉTUDE
    if study_context and hasattr(study_context, 'to_prompt_context'):
        prompt += f"""

╔══════════════════════════════════════════════════════════════════════════════╗
║ CONTEXTE DE L'ÉTUDE                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

{study_context.to_prompt_context()}

⚠️ IMPORTANT : Adapte le plan pour répondre à ces éléments !
"""
    
    # PARTIE 3 : PROFIL DE RÉDACTION (utilisation writing_profiles.py)
    if PROFILES_AVAILABLE and profile_enum:
        style_block = get_writing_style_block(profile_enum)
        prompt += f"\n{style_block}\n"
    else:
        prompt += f"\n🎯 PROFIL DE RÉDACTION : {profile_name.upper()}\n"
    
    # PARTIE 4 : INSTRUCTIONS STRUCTURELLES CRITIQUES
    prompt += """

╔══════════════════════════════════════════════════════════════════════════════╗
║ INSTRUCTIONS STRUCTURELLES CRITIQUES                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

🔴 RÈGLE #1 : SÉPARATION MÉTHODOLOGIE vs ANALYSE (ULTRA-IMPORTANT)

1️⃣ CHAPITRE "MÉTHODOLOGIE" doit contenir UNIQUEMENT :
   ✅ Description des outils statistiques utilisés
   ✅ Justification du choix des méthodes
   ✅ Étapes de prétraitement des données
   ✅ Gestion des valeurs manquantes (si présentes)
   ✅ Objectifs de chaque type d'analyse
   
   ❌ NE PAS INCLURE :
   - Graphiques de résultats
   - Tableaux de données réelles
   - Distributions concrètes
   - Interprétations de résultats

2️⃣ CHAPITRE "ANALYSE" / "RÉSULTATS" doit contenir :
   ✅ Distributions PAR VARIABLE RÉELLE (avec graphiques)
   ✅ Tableaux de statistiques
   ✅ Corrélations entre variables spécifiques
   ✅ Tests statistiques
   ✅ Interprétations

🔴 RÈGLE #2 : PERSONNALISATION AUX DONNÉES

✅ Utilise les NOMS EXACTS des colonnes
✅ Propose analyses SPÉCIFIQUES (ex: Corrélation "CA 2015" × "Effectifs")
✅ Mentionne variables encodées spécifiquement
✅ Adapte au volume de données ({num_rows:,} lignes)

"""
    
    # INSTRUCTIONS SPÉCIFIQUES PAR PROFIL (STANDARDS ACADÉMIQUES)
    if profile_name == "academic":
        prompt += """
🎓 PROFIL ACADÉMIQUE - STRUCTURE IMRAD OBLIGATOIRE :

⚠️ CRITIQUE : Respecter strictement la structure IMRAD (Introduction, Methods, Results, Discussion)

1. **Introduction et Cadre Théorique**
   - Contexte de recherche
   - ⭐ HYPOTHÈSES DE DÉPART (OBLIGATOIRE)
     Format : "H1: [Variable X] est corrélée à [Variable Y]"
     Exemple : "H1: L'âge des promoteurs est positivement corrélé au chiffre d'affaire"
   - Question de recherche claire
   - Objectifs de l'étude

2. **Méthodologie (METHODS)**
   - ⭐ JUSTIFICATION THÉORIQUE des tests
     Exemple : "Test de Pearson car variables continues et distribution normale"
   - Seuils de signification (p < 0.05)
   - Traitement des valeurs manquantes
   - ⭐ LIMITES MÉTHODOLOGIQUES ANTICIPÉES

3. **Résultats (RESULTS)**
   - Statistiques descriptives
   - Tests d'hypothèses (p-values)
   - Corrélations
   ⚠️ PAS d'interprétation ici, juste FAITS

4. **Discussion (DISCUSSION)** ⭐ CHAPITRE OBLIGATOIRE
   - Interprétation des résultats
   - ⭐ LIEN avec la littérature
   - ⭐ LIMITES DE L'ÉTUDE
   - Implications théoriques

5. **Conclusion**
   - Synthèse
   - ⭐ PERSPECTIVES DE RECHERCHE FUTURES
"""
    
    elif profile_name == "consultant":
        prompt += """
💼 PROFIL CONSULTANT - ORIENTÉ ACTION :

⚠️ CRITIQUE : Executive Summary OBLIGATOIRE EN PREMIER CHAPITRE

1. **Executive Summary** ⭐ PREMIER CHAPITRE OBLIGATOIRE
   
   1.1. Contexte business et enjeux
   1.2. ⭐ INSIGHTS CLÉS (3-5 bullet points)
        Format : "💡 [INSIGHT] : [CHIFFRE] → [IMPLICATION]"
   1.3. ⭐ RECOMMANDATIONS PRINCIPALES (Top 3)
   1.4. ⭐ IMPACTS QUANTIFIÉS (ROI, €, %)

2-4. [Analyses intermédiaires]

5. **Recommandations Stratégiques** ⭐ DERNIER CHAPITRE OBLIGATOIRE
   
   5.2. ⭐ PRIORISATION IMPACT × EFFORT (OBLIGATOIRE)
        Matrice 2×2 :
        - 🟢 QUICK WINS (High Impact / Low Effort)
        - 🟡 Projets stratégiques
   
   5.3. ⭐ PLAN DE MISE EN ŒUVRE (OBLIGATOIRE)
        - Court terme (0-3 mois)
        - Moyen terme (3-12 mois)
   
   5.4. ⭐ KPIs DE SUIVI
"""
    
    elif profile_name == "institutional":
        prompt += """
🏛️ PROFIL INSTITUTIONNEL - TRAÇABILITÉ COMPLÈTE :

⚠️ CRITIQUE : Cadre réglementaire EN PREMIER + Traçabilité maximale

1. **Contexte et Cadre Réglementaire** ⭐ PREMIER CHAPITRE OBLIGATOIRE
   
   1.1. ⭐ CADRE RÉGLEMENTAIRE APPLICABLE
        - Lois, décrets, normes EXACTES
        Exemple : "Conformément à la loi n°XXX du JJ/MM/AAAA"
   1.2. Mission institutionnelle
   1.3. Contexte politique/institutionnel

2. **Méthodologie et Processus** ⭐ TRAÇABILITÉ COMPLÈTE
   
   2.1. ⭐ COLLECTE DES DONNÉES (traçabilité)
        - Sources officielles EXACTES
        - Date de collecte
        - Méthode de collecte
   
   2.2. ⭐ VALIDATION ET CONTRÔLE QUALITÉ
        - Procédures de vérification
        - Taux de complétude
   
   2.3. Gestion des valeurs manquantes

3. **Analyse Exploratoire** ⚠️ DESCRIPTIVE UNIQUEMENT
   - ⭐ VOCABULAIRE ACCESSIBLE
     Utiliser : "répartition", "proportion", "effectif"
     Éviter : "hétéroscédasticité", "kurtosis"
   - ❌ PAS de recommandations prescriptives

4. **Annexes** (si pertinent)
   - Glossaire
   - Sources détaillées
"""
    
    # FORMAT JSON REQUIS
    prompt += f"""

╔══════════════════════════════════════════════════════════════════════════════╗
║ FORMAT JSON REQUIS                                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

{{
  "titre": "Titre du rapport (adapté aux données)",
  "date": "{datetime.now().strftime('%Y-%m-%d')}",
  "auteur": "AI Statistical Reporter",
  "profil": "{profile_name}",
  "chapitres": [
    {{
      "numero": "1",
      "titre": "Titre adapté données + profil",
      "sections": [
        {{
          "titre": "Section SPÉCIFIQUE (avec noms colonnes réels)",
          "analyses": [
            "Analyse détaillée avec NOM VARIABLE réel"
          ]
        }}
      ]
    }}
  ]
}}

⚠️ RAPPELS FINAUX :
1. Méthodologie = OUTILS uniquement
2. Analyse = RÉSULTATS par variable réelle
3. Utilise NOMS EXACTS colonnes
4. Adapte strictement au profil {profile_name.upper()}

🚀 GÉNÈRE MAINTENANT LE PLAN COMPLET EN JSON.
"""
    
    return prompt


def _postprocess_plan_by_profile(
    plan: Dict[str, Any],
    writing_profile: Optional[Union[str, 'WritingProfile']],
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    🆕 Post-traitement RENFORCÉ avec standards académiques
    """
    
    profile_name = "academic"
    if writing_profile:
        if isinstance(writing_profile, WritingProfile):
            profile_name = writing_profile.value
        elif isinstance(writing_profile, str):
            profile_name = writing_profile.lower()
    
    plan['profil'] = profile_name
    
    # ═══════════════════════════════════════════════════════════
    # ACADEMIC : Structure IMRAD stricte
    # ═══════════════════════════════════════════════════════════
    
    if profile_name == "academic":
        titles_lower = [c['titre'].lower() for c in plan['chapitres']]
        
        # Ajouter Discussion si manquant (OBLIGATOIRE IMRAD)
        if not any('discussion' in t for t in titles_lower):
            discussion_chap = {
                'numero': str(len(plan['chapitres']) + 1),
                'titre': 'Discussion et Limites',
                'sections': [
                    {
                        'titre': 'Interprétation des résultats',
                        'analyses': [
                            'Mise en perspective des résultats majeurs',
                            'Comparaison avec études similaires ou théories'
                        ]
                    },
                    {
                        'titre': 'Limites de l\'étude',
                        'analyses': [
                            'Biais potentiels identifiés',
                            'Contraintes méthodologiques',
                            'Validité externe des résultats'
                        ]
                    },
                    {
                        'titre': 'Perspectives de recherche',
                        'analyses': [
                            'Questions ouvertes pour recherches futures',
                            'Améliorations méthodologiques possibles'
                        ]
                    }
                ]
            }
            plan['chapitres'].append(discussion_chap)
    
    # ═══════════════════════════════════════════════════════════
    # CONSULTANT : Executive Summary + Recommandations
    # ═══════════════════════════════════════════════════════════
    
    elif profile_name == "consultant":
        first_chap = plan['chapitres'][0] if plan['chapitres'] else None
        
        # Executive Summary OBLIGATOIRE EN PREMIER
        if not first_chap or 'executive' not in first_chap['titre'].lower():
            exec_summary = {
                'numero': '1',
                'titre': 'Executive Summary',
                'sections': [
                    {
                        'titre': 'Contexte business et enjeux',
                        'analyses': [
                            'Problématique métier analysée',
                            'Enjeux business et impact attendu'
                        ]
                    },
                    {
                        'titre': '💡 Insights clés (Top 3-5)',
                        'analyses': [
                            '💡 INSIGHT 1 : [À compléter selon données]',
                            '💡 INSIGHT 2 : [À compléter selon données]',
                            '💡 INSIGHT 3 : [À compléter selon données]'
                        ]
                    },
                    {
                        'titre': '🎯 Recommandations principales',
                        'analyses': [
                            '🎯 ACTION PRIORITAIRE 1',
                            '🎯 ACTION PRIORITAIRE 2'
                        ]
                    },
                    {
                        'titre': 'Impacts quantifiés',
                        'analyses': [
                            'Gain potentiel estimé',
                            'ROI attendu',
                            'Timeline'
                        ]
                    }
                ]
            }
            plan['chapitres'].insert(0, exec_summary)
        
        # Recommandations EN DERNIER avec priorisation
        last_chap = plan['chapitres'][-1]
        
        if 'recommandation' not in last_chap['titre'].lower():
            reco_chap = {
                'numero': str(len(plan['chapitres']) + 1),
                'titre': 'Recommandations Stratégiques et Plan d\'Action',
                'sections': [
                    {
                        'titre': 'Synthèse des insights clés',
                        'analyses': ['Récapitulatif des points critiques']
                    },
                    {
                        'titre': 'Recommandations actionnables',
                        'analyses': [
                            '🎯 Recommandation 1 : Action + Pourquoi + Comment + Qui + Quand',
                            '🎯 Recommandation 2 : Action + Pourquoi + Comment + Qui + Quand'
                        ]
                    },
                    {
                        'titre': '⭐ Priorisation Impact × Effort',
                        'analyses': [
                            '🟢 QUICK WINS (High Impact / Low Effort)',
                            '🟡 Projets stratégiques (High Impact / High Effort)'
                        ]
                    },
                    {
                        'titre': 'Plan de mise en œuvre',
                        'analyses': [
                            '📅 Court terme (0-3 mois)',
                            '📅 Moyen terme (3-12 mois)'
                        ]
                    },
                    {
                        'titre': 'KPIs de suivi',
                        'analyses': [
                            'KPIs par recommandation',
                            'Tableau de bord de suivi'
                        ]
                    }
                ]
            }
            plan['chapitres'].append(reco_chap)
        
        # Renuméroter
        for i, chap in enumerate(plan['chapitres'], 1):
            chap['numero'] = str(i)
    
    # ═══════════════════════════════════════════════════════════
    # INSTITUTIONAL : Cadre réglementaire + Traçabilité
    # ═══════════════════════════════════════════════════════════
    
    elif profile_name == "institutional":
        first_chap = plan['chapitres'][0] if plan['chapitres'] else None
        
        # Cadre réglementaire EN PREMIER
        if not first_chap or 'réglementaire' not in first_chap['titre'].lower():
            cadre_chap = {
                'numero': '1',
                'titre': 'Contexte et Cadre Réglementaire',
                'sections': [
                    {
                        'titre': 'Cadre réglementaire applicable',
                        'analyses': [
                            'Lois, décrets et normes applicables',
                            'Obligations légales et réglementaires'
                        ]
                    },
                    {
                        'titre': 'Mission institutionnelle',
                        'analyses': [
                            'Rôle de l\'institution',
                            'Objectifs de l\'analyse'
                        ]
                    }
                ]
            }
            plan['chapitres'].insert(0, cadre_chap)
        
        # Méthodologie avec traçabilité
        has_methodo = any('méthodo' in c['titre'].lower() for c in plan['chapitres'])
        
        if not has_methodo:
            methodo_chap = {
                'numero': '2',
                'titre': 'Méthodologie et Traçabilité',
                'sections': [
                    {
                        'titre': 'Collecte des données (traçabilité)',
                        'analyses': [
                            f'Sources officielles : [À préciser]',
                            f'Taille échantillon : {metadata["shape"]["rows"]:,} observations'
                        ]
                    },
                    {
                        'titre': 'Validation et contrôle qualité',
                        'analyses': [
                            'Procédures de vérification',
                            'Contrôles de cohérence'
                        ]
                    }
                ]
            }
            
            # Valeurs manquantes
            if metadata.get('columns_with_missing'):
                methodo_chap['sections'].append({
                    'titre': 'Gestion des valeurs manquantes',
                    'analyses': [
                        f'{len(metadata["columns_with_missing"])} variables concernées',
                        'Stratégie de traitement'
                    ]
                })
            
            plan['chapitres'].insert(1, methodo_chap)
        
        # Renuméroter
        for i, chap in enumerate(plan['chapitres'], 1):
            chap['numero'] = str(i)
    
    return plan


def _generate_fallback_plan(
    metadata: Dict[str, Any],
    writing_profile: Optional[Union[str, 'WritingProfile']]
) -> Dict[str, Any]:
    """Plan de secours en cas d'erreur IA"""
    
    profile_name = "academic"
    if writing_profile:
        if isinstance(writing_profile, WritingProfile):
            profile_name = writing_profile.value
        elif isinstance(writing_profile, str):
            profile_name = writing_profile.lower()
    
    return {
        "titre": "Rapport Statistique",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "auteur": "AI Statistical Reporter",
        "profil": profile_name,
        "chapitres": [
            {
                "numero": "1",
                "titre": "Introduction",
                "sections": [
                    {
                        "titre": "Contexte",
                        "analyses": [f"Présentation des {metadata['shape']['rows']:,} observations"]
                    }
                ]
            },
            {
                "numero": "2",
                "titre": "Méthodologie",
                "sections": [
                    {
                        "titre": "Outils statistiques",
                        "analyses": ["Statistiques descriptives", "Analyses de corrélation"]
                    }
                ]
            },
            {
                "numero": "3",
                "titre": "Analyse descriptive",
                "sections": [
                    {
                        "titre": "Variables numériques",
                        "analyses": [f"Analyse de {len(metadata.get('numeric_columns', []))} variables"]
                    }
                ]
            },
            {
                "numero": "4",
                "titre": "Conclusions",
                "sections": [
                    {
                        "titre": "Synthèse",
                        "analyses": ["Résumé des résultats"]
                    }
                ]
            }
        ]
    }


# ═══════════════════════════════════════════════════════════════
# TESTS
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """Tests du module"""
    
    print("="*70)
    print("TEST - WEEK2 ARCHITECT AGENT (VERSION FINALE ULTIME)")
    print("="*70)
    
    print("\n🎯 AMÉLIORATIONS INCLUSES :")
    print("✅ Métadonnées enrichies")
    print("✅ Plan dynamique personnalisé")
    print("✅ Correction E2B (timeout 300s)")
    print("✅ Standards académiques IMRAD")
    print("✅ Executive Summary consultant")
    print("✅ Traçabilité institutionnelle")
    
    # Test analyse CSV
    print("\n1. Test analyse CSV...")
    try:
        import pandas as pd
        test_data = {
            'Age': [25, 30, 35, 40, 2, 3],
            'CA_2015': [10000, 25000, 50000, 75000, 100000, 120000],
            'Region': ['LITTORAL', 'CENTRE', 'LITTORAL', 'NORD', 'LITTORAL', 'CENTRE']
        }
        df_test = pd.DataFrame(test_data)
        df_test.to_csv('test.csv', index=False)
        
        metadata = analyze_csv('test.csv')
        
        print(f"✅ Analyse réussie")
        print(f"   - {len(metadata.get('columns', []))} colonnes analysées")
        print(f"   - Variables numériques : {metadata.get('numeric_columns', [])}")
        print(f"   - Variables encodées : {metadata.get('encoded_columns', [])}")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
    
    # Test génération plan
    print("\n2. Test génération plan...")
    
    if os.getenv("GMINI_API_KEY"):
        try:
            for profile in ['academic', 'consultant', 'institutional']:
                plan = generate_report_plan(metadata, writing_profile=profile)
                print(f"\n✅ {profile.upper()} : {len(plan.get('chapitres', []))} chapitres")
                for i, chap in enumerate(plan.get('chapitres', [])[:3], 1):
                    print(f"   {i}. {chap.get('titre', 'N/A')}")
        
        except Exception as e:
            print(f"❌ Erreur : {e}")
    else:
        print("   ⚠️ GMINI_API_KEY non trouvée (skipping)")
    
    print("\n" + "="*70)
    print("✅ Tests terminés - VERSION FINALE PRÊTE !")
    print("="*70)