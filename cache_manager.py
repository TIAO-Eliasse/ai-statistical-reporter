"""
Système de cache pour AI Statistical Reporter
Économise les appels API et améliore les performances
"""

import streamlit as st
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional
import pickle


class CacheManager:
    """Gestion du cache pour les opérations coûteuses"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, data: Any) -> str:
        """Génère une clé de cache unique"""
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def get(self, key: str, max_age_hours: int = 24) -> Optional[Any]:
        """Récupère une valeur du cache si elle existe et n'est pas expirée"""
        cache_file = self.cache_dir / f"{key}.pkl"
        
        if not cache_file.exists():
            return None
        
        # Vérifier l'âge du cache
        file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        if datetime.now() - file_time > timedelta(hours=max_age_hours):
            # Cache expiré
            cache_file.unlink()
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return None
    
    def set(self, key: str, value: Any):
        """Sauvegarde une valeur dans le cache"""
        cache_file = self.cache_dir / f"{key}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(value, f)
        except Exception as e:
            print(f"Erreur sauvegarde cache: {e}")
    
    def clear(self):
        """Vide le cache"""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
    
    def get_size(self) -> int:
        """Retourne la taille du cache en Mo"""
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.pkl"))
        return total_size // (1024 * 1024)


# Instance globale
cache = CacheManager()


def cached_plan_generation(csv_path: str, force_refresh: bool = False):
    """
    Génère un plan avec cache intelligent
    
    Args:
        csv_path: Chemin vers le CSV
        force_refresh: Force la régénération même si cache existe
    """
    import pandas as pd
    from week2_architect_agent import analyze_csv, generate_report_plan
    
    # Calculer un hash du fichier CSV
    df = pd.read_csv(csv_path)
    csv_hash = hashlib.md5(df.to_csv().encode()).hexdigest()
    
    cache_key = f"plan_{csv_hash}"
    
    # Vérifier le cache (sauf si force_refresh)
    if not force_refresh:
        cached_plan = cache.get(cache_key, max_age_hours=168)  # 7 jours
        if cached_plan:
            return cached_plan, True  # True = from cache
    
    # Générer le plan
    metadata = analyze_csv(csv_path)
    plan = generate_report_plan(metadata)
    
    # Sauvegarder dans le cache
    cache.set(cache_key, plan)
    
    return plan, False  # False = freshly generated


def cached_text_parsing(text: str, force_refresh: bool = False):
    """
    Parse un texte en JSON avec cache
    
    Utile quand l'utilisateur fait "Appliquer" plusieurs fois sur le même texte
    """
    text_hash = hashlib.md5(text.encode()).hexdigest()
    cache_key = f"parse_{text_hash}"
    
    if not force_refresh:
        cached_result = cache.get(cache_key, max_age_hours=1)  # 1 heure
        if cached_result:
            return cached_result, True
    
    # Parser (fonction à importer de votre app)
    # result = text_to_json_with_ai(text)
    # cache.set(cache_key, result)
    
    # return result, False
    return None, False  # Placeholder


@st.cache_data(ttl=3600, show_spinner=False)
def cached_data_analysis(csv_path: str):
    """
    Analyse des données avec cache Streamlit natif
    
    TTL = 1 heure
    """
    import pandas as pd
    
    df = pd.read_csv(csv_path)
    
    analysis = {
        'shape': df.shape,
        'dtypes': df.dtypes.to_dict(),
        'numeric_summary': df.describe().to_dict(),
        'missing': df.isnull().sum().to_dict(),
    }
    
    return analysis


def display_cache_info():
    """Affiche des infos sur le cache dans la sidebar"""
    cache_size = cache.get_size()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Cache**")
    st.sidebar.caption(f"Taille : {cache_size} Mo")
    
    if st.sidebar.button("Vider le cache"):
        cache.clear()
        st.sidebar.success("Cache vidé")
        st.rerun()