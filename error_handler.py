"""
Gestion centralisée des erreurs pour AI Statistical Reporter
Compatible avec et sans Streamlit
"""

import logging
from functools import wraps
from typing import Callable, Any
import traceback

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Import conditionnel de Streamlit
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


class AppError(Exception):
    """Erreur de base de l'application"""
    def __init__(self, message: str, user_message: str = None):
        self.message = message
        self.user_message = user_message or message
        super().__init__(self.message)


class APIError(AppError):
    """Erreur liée aux appels API"""
    pass


class DataError(AppError):
    """Erreur liée aux données"""
    pass


class ParsingError(AppError):
    """Erreur de parsing"""
    pass


def _display_error(error_msg: str, traceback_info: str = None):
    """Affiche une erreur (Streamlit si disponible, sinon print)"""
    if STREAMLIT_AVAILABLE:
        st.error(error_msg)
        if traceback_info:
            st.code(traceback_info)
    else:
        print(f"ERROR: {error_msg}")
        if traceback_info:
            print(traceback_info)


def handle_errors(show_traceback: bool = False):
    """
    Décorateur pour gérer les erreurs de manière centralisée
    
    Usage:
        @handle_errors(show_traceback=True)
        def my_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            
            except APIError as e:
                logger.error(f"API Error in {func.__name__}: {e.message}")
                error_msg = f"""
**Erreur API**

{e.user_message}

**Solutions possibles :**
- Vérifiez votre clé API dans le fichier .env
- Vérifiez votre quota API (Gemini : 20 req/jour gratuit)
- Essayez de régénérer le plan dans quelques minutes

**Besoin d'aide ?** Consultez la documentation ou contactez le support.
                """
                _display_error(error_msg, traceback.format_exc() if show_traceback else None)
                return None
            
            except DataError as e:
                logger.error(f"Data Error in {func.__name__}: {e.message}")
                error_msg = f"""
**Erreur de données**

{e.user_message}

**Vérifications :**
- Le fichier CSV est-il bien formaté ?
- Y a-t-il des caractères spéciaux dans les noms de colonnes ?
- Le fichier contient-il au moins 2 lignes ?
                """
                _display_error(error_msg, traceback.format_exc() if show_traceback else None)
                return None
            
            except ParsingError as e:
                logger.error(f"Parsing Error in {func.__name__}: {e.message}")
                error_msg = f"""
**Erreur de traitement**

{e.user_message}

L'IA n'a pas pu traiter correctement votre demande.

**Essayez :**
- Simplifier le texte du plan
- Régénérer le plan
- Contacter le support si le problème persiste
                """
                _display_error(error_msg, traceback.format_exc() if show_traceback else None)
                return None
            
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                logger.error(traceback.format_exc())
                error_msg = f"""
**Erreur inattendue**

Une erreur imprévue s'est produite : `{type(e).__name__}`

L'équipe technique a été notifiée automatiquement.

**En attendant :**
- Rechargez la page (F5)
- Réessayez dans quelques minutes
- Contactez le support si le problème persiste
                """
                _display_error(error_msg, traceback.format_exc() if show_traceback else None)
                return None
        
        return wrapper
    return decorator


def validate_api_keys():
    """Valide que les clés API sont configurées"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    gmini_key = os.getenv("GMINI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not gmini_key and not anthropic_key:
        raise APIError(
            "No API keys configured",
            "Aucune clé API n'est configurée. Veuillez ajouter GMINI_API_KEY ou ANTHROPIC_API_KEY dans votre fichier .env"
        )
    
    if gmini_key and len(gmini_key) < 10:
        raise APIError(
            "Invalid GMINI_API_KEY",
            "La clé API Gemini semble invalide (trop courte)"
        )
    
    if anthropic_key and len(anthropic_key) < 10:
        raise APIError(
            "Invalid ANTHROPIC_API_KEY",
            "La clé API Anthropic semble invalide (trop courte)"
        )
    
    return True


def validate_csv_file(df):
    """Valide qu'un DataFrame est exploitable"""
    import pandas as pd
    
    if df is None:
        raise DataError("DataFrame is None", "Le fichier n'a pas pu être chargé")
    
    if len(df) == 0:
        raise DataError("Empty DataFrame", "Le fichier CSV est vide (0 lignes)")
    
    if len(df.columns) == 0:
        raise DataError("No columns", "Le fichier CSV n'a aucune colonne")
    
    if len(df) < 2:
        raise DataError(
            "Too few rows",
            f"Le fichier ne contient que {len(df)} ligne(s). Il faut au moins 2 lignes pour une analyse statistique."
        )
    
    # Vérifier qu'il y a au moins une colonne numérique
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) == 0:
        raise DataError(
            "No numeric columns",
            "Le fichier ne contient aucune colonne numérique. Une analyse statistique nécessite au moins une variable quantitative."
        )
    
    return True


def safe_execute(func: Callable, error_prefix: str = "Opération") -> Any:
    """
    Execute une fonction avec gestion d'erreur simplifiée
    
    Usage:
        result = safe_execute(lambda: generate_plan(csv), "Génération du plan")
    """
    try:
        return func()
    except Exception as e:
        logger.error(f"{error_prefix} failed: {str(e)}")
        error_msg = f"**Erreur : {error_prefix}**\n\n{str(e)}"
        _display_error(error_msg)
        return None