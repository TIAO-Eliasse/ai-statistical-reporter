"""
Rate limiting pour AI Statistical Reporter
Protège contre les abus et limite les coûts API
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Optional
import json
from pathlib import Path


class RateLimiter:
    """Gestion du rate limiting par utilisateur"""
    
    def __init__(self, storage_file: str = "rate_limits.json"):
        self.storage_file = Path(storage_file)
        self.limits = self._load_limits()
        
        # Whitelist développeurs (pas de rate limit)
        # Ajoutez vos emails ou identifiants ici
        self.dev_whitelist = [
            'dev@example.com',
            'eliasse@aims.ac.za',
            'eliassetiao@gamil.com',  # Votre email
        ]
    
    def _load_limits(self) -> Dict:
        """Charge les limites depuis le fichier"""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_limits(self):
        """Sauvegarde les limites"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.limits, f)
        except Exception as e:
            print(f"Erreur sauvegarde rate limits: {e}")
    
    def _get_user_id(self) -> str:
        """
        Identifie l'utilisateur
        Note: En prod, utiliser authentication.
        Pour MVP, on utilise session_id Streamlit
        """
        if 'user_id' not in st.session_state:
            # Générer un ID unique pour la session
            import uuid
            st.session_state.user_id = str(uuid.uuid4())
        
        return st.session_state.user_id
    
    def _is_developer(self) -> bool:
        """
        Vérifie si l'utilisateur actuel est un développeur
        
        En développement : Utilise une variable d'environnement
        En production : Utilisera l'authentification
        """
        import os
        
        # Méthode 1 : Variable d'environnement
        is_dev_mode = os.getenv('DEV_MODE', 'false').lower() == 'true'
        
        # Méthode 2 : Email en session (si authentification active)
        user_email = st.session_state.get('user_email', None)
        is_whitelisted = user_email in self.dev_whitelist if user_email else False
        
        return is_dev_mode or is_whitelisted
    
    def _clean_old_entries(self, user_id: str, window_hours: int = 24):
        """Nettoie les entrées trop anciennes"""
        if user_id not in self.limits:
            return
        
        cutoff_time = datetime.now() - timedelta(hours=window_hours)
        
        self.limits[user_id] = [
            entry for entry in self.limits[user_id]
            if datetime.fromisoformat(entry['timestamp']) > cutoff_time
        ]
    
    def check_limit(
        self,
        action: str,
        max_calls: int,
        window_hours: int = 1
    ) -> tuple[bool, Optional[str]]:
        """
        Vérifie si l'action est autorisée
        
        Args:
            action: Type d'action ('plan_generation', 'text_parsing', etc.)
            max_calls: Nombre max d'appels dans la fenêtre
            window_hours: Fenêtre de temps en heures
        
        Returns:
            (allowed, error_message)
        """
        user_id = self._get_user_id()
        
        # Vérifier si c'est un développeur (whitelist)
        if self._is_developer():
            return (True, None)  # Pas de limite pour les devs
        
        # Initialiser si nécessaire
        if user_id not in self.limits:
            self.limits[user_id] = []
        
        # Nettoyer les anciennes entrées
        self._clean_old_entries(user_id, window_hours)
        
        # Compter les appels pour cette action
        action_calls = [
            entry for entry in self.limits[user_id]
            if entry['action'] == action
        ]
        
        if len(action_calls) >= max_calls:
            # Limite atteinte
            oldest_call = min(
                action_calls,
                key=lambda x: datetime.fromisoformat(x['timestamp'])
            )
            oldest_time = datetime.fromisoformat(oldest_call['timestamp'])
            next_available = oldest_time + timedelta(hours=window_hours)
            wait_time = (next_available - datetime.now()).total_seconds() / 60
            
            error_msg = f"""
            **Limite atteinte**
            
            Vous avez atteint la limite de {max_calls} appels par {window_hours}h pour cette action.
            
            Prochaine disponibilité dans : **{int(wait_time)} minutes**
            
            **Pourquoi cette limite ?**
            - Protéger contre les abus
            - Contrôler les coûts API
            - Garantir un service équitable pour tous
            
            **Solutions :**
            - Attendez quelques minutes
            - Utilisez le cache (plans déjà générés)
            - Contactez-nous pour augmenter vos limites
            """
            
            return False, error_msg
        
        # Enregistrer l'appel
        self.limits[user_id].append({
            'action': action,
            'timestamp': datetime.now().isoformat()
        })
        
        self._save_limits()
        
        return True, None
    
    def get_usage_stats(self, action: str, window_hours: int = 24) -> Dict:
        """Retourne les statistiques d'utilisation"""
        user_id = self._get_user_id()
        
        if user_id not in self.limits:
            return {'calls': 0, 'remaining': 'unlimited'}
        
        self._clean_old_entries(user_id, window_hours)
        
        action_calls = [
            entry for entry in self.limits[user_id]
            if entry['action'] == action
        ]
        
        return {
            'calls': len(action_calls),
            'window_hours': window_hours,
            'timestamps': [entry['timestamp'] for entry in action_calls]
        }


# Instance globale
rate_limiter = RateLimiter()


# Limites par défaut
RATE_LIMITS = {
    'plan_generation': {'max_calls': 10, 'window_hours': 1},  # 10 plans/heure
    'text_parsing': {'max_calls': 30, 'window_hours': 1},     # 30 parsing/heure
    'csv_upload': {'max_calls': 20, 'window_hours': 1},       # 20 uploads/heure
}


def rate_limit_decorator(action: str):
    """
    Décorateur pour appliquer le rate limiting
    
    Usage:
        @rate_limit_decorator('plan_generation')
        def generate_plan():
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            limits = RATE_LIMITS.get(action, {'max_calls': 100, 'window_hours': 1})
            
            allowed, error_msg = rate_limiter.check_limit(
                action,
                limits['max_calls'],
                limits['window_hours']
            )
            
            if not allowed:
                st.error(error_msg)
                return None
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def display_rate_limit_info():
    """Affiche les infos de rate limiting dans la sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Utilisation API**")
    
    # Stats pour génération de plan
    stats = rate_limiter.get_usage_stats('plan_generation', 1)
    limit = RATE_LIMITS['plan_generation']['max_calls']
    
    st.sidebar.progress(
        stats['calls'] / limit if stats['calls'] < limit else 1.0,
        text=f"Plans générés : {stats['calls']}/{limit} (1h)"
    )
    
    # Stats pour parsing
    stats_parsing = rate_limiter.get_usage_stats('text_parsing', 1)
    limit_parsing = RATE_LIMITS['text_parsing']['max_calls']
    
    st.sidebar.caption(
        f"Modifications : {stats_parsing['calls']}/{limit_parsing} (1h)"
    )