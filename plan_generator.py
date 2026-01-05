"""
Wrapper pour week2_architect_agent avec support du contexte
Ce module enrichit les prompts avec le contexte de l'étude
"""

from typing import Dict, Optional
import json

# Import du module original
try:
    from week2_architect_agent import analyze_csv as original_analyze_csv
    from week2_architect_agent import generate_report_plan as original_generate_report_plan
    ORIGINAL_AVAILABLE = True
except ImportError:
    ORIGINAL_AVAILABLE = False
    print("⚠️ week2_architect_agent non disponible")

try:
    from study_context import StudyContext
    STUDY_CONTEXT_AVAILABLE = True
except ImportError:
    STUDY_CONTEXT_AVAILABLE = False
    print("⚠️ study_context non disponible")


def analyze_csv(csv_path: str) -> Dict:
    """
    Analyse le CSV - passthrough vers le module original
    """
    if not ORIGINAL_AVAILABLE:
        raise ImportError("week2_architect_agent non disponible")
    
    return original_analyze_csv(csv_path)


def generate_report_plan(metadata: Dict, study_context: Optional['StudyContext'] = None) -> Dict:
    """
    Génère un plan de rapport avec support optionnel du contexte
    
    Args:
        metadata: Métadonnées du CSV (colonnes, types, stats...)
        study_context: Contexte de l'étude (optionnel)
    
    Returns:
        Plan du rapport au format dict
    """
    if not ORIGINAL_AVAILABLE:
        raise ImportError("week2_architect_agent non disponible")
    
    # Si pas de contexte, utiliser la fonction originale
    if not study_context or not STUDY_CONTEXT_AVAILABLE:
        return original_generate_report_plan(metadata)
    
    # Sinon, enrichir les métadonnées avec le contexte
    enriched_metadata = metadata.copy()
    
    # Ajouter le contexte formaté dans les métadonnées
    enriched_metadata['study_context'] = {
        'formatted_prompt': study_context.to_prompt_context(),
        'research_question': study_context.research_question,
        'hypotheses': study_context.hypotheses,
        'objectives': study_context.objectives,
        'study_type': study_context.study_type,
        'dependent_variable': study_context.dependent_variable,
        'independent_variables': study_context.independent_variables,
        'key_analyses_needed': study_context.key_analyses_needed,
        'reporting_style': study_context.reporting_style,
    }
    
    # Appeler la fonction originale avec les métadonnées enrichies
    # Note: La fonction originale devra être modifiée pour utiliser study_context
    # Pour l'instant, on essaie de passer le contexte et on fallback si ça échoue
    try:
        # Essayer de passer le contexte directement
        plan = original_generate_report_plan(enriched_metadata)
    except Exception:
        # Si erreur, utiliser la version originale
        plan = original_generate_report_plan(metadata)
    
    return plan


# Pour compatibilité avec l'import existant dans app_streamlit_professional.py
# Les imports resteront : from week2_architect_agent import analyze_csv, generate_report_plan
# Mais vous pouvez aussi faire : from plan_generator import analyze_csv, generate_report_plan