"""
Configuration du logging structuré
Facilite le debug en production
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(log_level=logging.INFO):
    """
    Configure le logging pour l'application
    
    Crée 3 fichiers de logs :
    - app.log : Tous les logs
    - errors.log : Seulement les erreurs
    - api_calls.log : Appels API pour tracking coûts
    """
    
    # Créer le dossier logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Format des logs
    log_format = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Logger principal
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Handler 1 : Console (pour dev)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)
    
    # Handler 2 : Fichier app.log (tous les logs)
    file_handler = logging.FileHandler(
        log_dir / 'app.log',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    
    # Handler 3 : Fichier errors.log (erreurs uniquement)
    error_handler = logging.FileHandler(
        log_dir / 'errors.log',
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)
    logger.addHandler(error_handler)
    
    # Handler 4 : API calls (pour tracking coûts)
    api_handler = logging.FileHandler(
        log_dir / 'api_calls.log',
        encoding='utf-8'
    )
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    
    api_logger = logging.getLogger('api')
    api_logger.addHandler(api_handler)
    api_logger.setLevel(logging.INFO)
    
    return logger


def log_api_call(provider: str, model: str, tokens: int = None, cost: float = None):
    """
    Log un appel API pour tracking des coûts
    
    Usage:
        log_api_call('gemini', 'gemini-2.5-flash', tokens=1500, cost=0.002)
    """
    logger = logging.getLogger('api')
    
    message = f"API_CALL | Provider={provider} | Model={model}"
    
    if tokens:
        message += f" | Tokens={tokens}"
    if cost:
        message += f" | Cost=${cost:.4f}"
    
    logger.info(message)


def log_user_action(action: str, details: dict = None):
    """
    Log une action utilisateur pour analytics
    
    Usage:
        log_user_action('plan_generated', {'csv_rows': 1000, 'csv_cols': 15})
    """
    logger = logging.getLogger('user_actions')
    
    message = f"USER_ACTION | {action}"
    
    if details:
        message += f" | {details}"
    
    logger.info(message)


# ============================================
# INTÉGRATION DANS L'APP
# ============================================

# En haut de app_streamlit_professional.py :
"""
from logging_config import setup_logging, log_api_call, log_user_action

# Au début du script (avant tout autre code)
logger = setup_logging()
logger.info("Application started")
"""

# Dans generate_report_plan() :
"""
def generate_report_plan(metadata):
    logger.info(f"Generating plan for CSV with {metadata['rows']} rows")
    
    try:
        # Appel à l'API
        plan = ... 
        
        log_api_call('gemini', 'gemini-2.5-flash', tokens=1200, cost=0.0012)
        log_user_action('plan_generated', {'success': True})
        
        return plan
    
    except Exception as e:
        logger.error(f"Plan generation failed: {str(e)}", exc_info=True)
        log_user_action('plan_generation_failed', {'error': str(e)})
        raise
"""

# Dans text_to_json_with_ai() :
"""
def text_to_json_with_ai(text):
    logger.info("Parsing text to JSON with AI")
    
    try:
        result = ...
        log_api_call('gemini', 'gemini-2.5-flash', tokens=800)
        return result
    except Exception as e:
        logger.error(f"Parsing failed: {str(e)}")
        raise
"""


# ============================================
# ANALYSE DES LOGS
# ============================================

def analyze_logs():
    """Script pour analyser les logs et extraire des métriques"""
    
    import re
    from collections import Counter
    
    # Lire api_calls.log
    with open('logs/api_calls.log', 'r') as f:
        lines = f.readlines()
    
    # Extraire les coûts
    costs = []
    for line in lines:
        match = re.search(r'Cost=\$([0-9.]+)', line)
        if match:
            costs.append(float(match.group(1)))
    
    # Calculer stats
    total_cost = sum(costs)
    avg_cost = total_cost / len(costs) if costs else 0
    
    print(f"Total API calls: {len(costs)}")
    print(f"Total cost: ${total_cost:.2f}")
    print(f"Average cost per call: ${avg_cost:.4f}")
    
    # Lire errors.log
    with open('logs/errors.log', 'r') as f:
        error_lines = f.readlines()
    
    # Compter types d'erreurs
    error_types = Counter()
    for line in error_lines:
        if 'Error' in line:
            # Extraire le type d'erreur
            match = re.search(r'(\w+Error)', line)
            if match:
                error_types[match.group(1)] += 1
    
    print("\nError types:")
    for error_type, count in error_types.most_common():
        print(f"  {error_type}: {count}")


if __name__ == "__main__":
    # Test du logging
    logger = setup_logging()
    
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")
    
    log_api_call('gemini', 'gemini-2.5-flash', tokens=1000, cost=0.001)
    log_user_action('test_action', {'key': 'value'})
    
    print("\nLogs created successfully in logs/ directory")
    print("Check: logs/app.log, logs/errors.log, logs/api_calls.log")