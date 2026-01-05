"""
Système d'autosave pour AI Statistical Reporter
Sauvegarde automatique des brouillons pour éviter les pertes
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import threading
import time


class AutoSave:
    """Gestion de la sauvegarde automatique"""
    
    def __init__(self, save_dir: str = "autosave"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        self.autosave_interval = 60  # secondes
        self._stop_autosave = False
    
    def get_user_id(self) -> str:
        """Récupère l'ID utilisateur depuis la session"""
        if 'user_id' not in st.session_state:
            import uuid
            st.session_state.user_id = str(uuid.uuid4())
        return st.session_state.user_id
    
    def save_draft(self, content: Dict, draft_type: str = "plan"):
        """
        Sauvegarde un brouillon
        
        Args:
            content: Contenu à sauvegarder (dict)
            draft_type: Type de brouillon ('plan', 'chapter', etc.)
        """
        user_id = self.get_user_id()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        filename = f"{user_id}_{draft_type}_{timestamp}.json"
        filepath = self.save_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'content': content,
                    'type': draft_type,
                    'timestamp': timestamp,
                    'user_id': user_id
                }, f, indent=2, ensure_ascii=False)
            
            return filepath
        
        except Exception as e:
            print(f"Erreur autosave: {e}")
            return None
    
    def load_latest_draft(self, draft_type: str = "plan") -> Optional[Dict]:
        """
        Charge le brouillon le plus récent
        
        Args:
            draft_type: Type de brouillon à charger
        
        Returns:
            Dict avec le contenu ou None
        """
        user_id = self.get_user_id()
        
        # Trouver tous les brouillons de cet utilisateur et ce type
        pattern = f"{user_id}_{draft_type}_*.json"
        drafts = list(self.save_dir.glob(pattern))
        
        if not drafts:
            return None
        
        # Trier par date (plus récent en premier)
        latest_draft = max(drafts, key=lambda p: p.stat().st_mtime)
        
        try:
            with open(latest_draft, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data['content']
        except Exception as e:
            print(f"Erreur chargement draft: {e}")
            return None
    
    def get_all_drafts(self, draft_type: str = None) -> list:
        """
        Récupère tous les brouillons de l'utilisateur
        
        Args:
            draft_type: Filtrer par type (optionnel)
        
        Returns:
            Liste de dicts avec info sur chaque brouillon
        """
        user_id = self.get_user_id()
        
        if draft_type:
            pattern = f"{user_id}_{draft_type}_*.json"
        else:
            pattern = f"{user_id}_*.json"
        
        drafts = []
        
        for filepath in self.save_dir.glob(pattern):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    drafts.append({
                        'filename': filepath.name,
                        'filepath': filepath,
                        'type': data.get('type'),
                        'timestamp': data.get('timestamp'),
                        'date': datetime.strptime(data.get('timestamp'), '%Y%m%d_%H%M%S')
                    })
            except:
                continue
        
        # Trier par date (plus récent en premier)
        drafts.sort(key=lambda x: x['date'], reverse=True)
        
        return drafts
    
    def delete_draft(self, filepath: Path):
        """Supprime un brouillon"""
        try:
            filepath.unlink()
            return True
        except Exception as e:
            print(f"Erreur suppression draft: {e}")
            return False
    
    def cleanup_old_drafts(self, days: int = 7):
        """
        Nettoie les brouillons de plus de X jours
        
        Args:
            days: Nombre de jours à conserver
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        deleted_count = 0
        
        for filepath in self.save_dir.glob("*.json"):
            file_time = datetime.fromtimestamp(filepath.stat().st_mtime)
            
            if file_time < cutoff_date:
                try:
                    filepath.unlink()
                    deleted_count += 1
                except:
                    pass
        
        return deleted_count


# Instance globale
autosave = AutoSave()


def enable_autosave_for_plan():
    """
    Active l'autosave pour le plan en cours d'édition
    
    À appeler dans l'app Streamlit
    """
    if 'autosave_enabled' not in st.session_state:
        st.session_state.autosave_enabled = False
    
    # Checkbox pour activer/désactiver
    enable = st.sidebar.checkbox(
        "Sauvegarde automatique",
        value=st.session_state.autosave_enabled,
        help="Sauvegarde automatique toutes les 60 secondes"
    )
    
    st.session_state.autosave_enabled = enable
    
    # Si un plan existe et autosave activé
    if enable and 'plan' in st.session_state and st.session_state.plan:
        # Vérifier dernière sauvegarde
        if 'last_autosave' not in st.session_state:
            st.session_state.last_autosave = datetime.now()
        
        time_since_save = (datetime.now() - st.session_state.last_autosave).total_seconds()
        
        if time_since_save > 60:  # 60 secondes
            # Sauvegarder
            autosave.save_draft(st.session_state.plan, 'plan')
            st.session_state.last_autosave = datetime.now()
            
            st.sidebar.caption(f"✅ Sauvegarde auto : {datetime.now().strftime('%H:%M:%S')}")


def show_draft_recovery():
    """
    Affiche l'option de récupération de brouillon
    
    À appeler au démarrage de l'app
    """
    latest_draft = autosave.load_latest_draft('plan')
    
    if latest_draft and 'draft_recovered' not in st.session_state:
        st.info("""
        **📋 Brouillon détecté**
        
        Un brouillon non sauvegardé a été trouvé. Souhaitez-vous le récupérer ?
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Récupérer le brouillon", use_container_width=True):
                st.session_state.plan = latest_draft
                st.session_state.draft_recovered = True
                st.success("Brouillon récupéré !")
                st.rerun()
        
        with col2:
            if st.button("Ignorer", use_container_width=True):
                st.session_state.draft_recovered = True
                st.rerun()


def show_draft_manager():
    """
    Affiche le gestionnaire de brouillons dans la sidebar
    """
    drafts = autosave.get_all_drafts()
    
    if drafts:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**Brouillons ({len(drafts)})**")
        
        for draft in drafts[:5]:  # Afficher les 5 plus récents
            with st.sidebar.expander(f"{draft['type']} - {draft['date'].strftime('%d/%m %H:%M')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Charger", key=f"load_{draft['filename']}", use_container_width=True):
                        content = autosave.load_latest_draft(draft['type'])
                        if content:
                            st.session_state.plan = content
                            st.success("Brouillon chargé")
                            st.rerun()
                
                with col2:
                    if st.button("Supprimer", key=f"del_{draft['filename']}", use_container_width=True):
                        autosave.delete_draft(draft['filepath'])
                        st.rerun()
        
        if len(drafts) > 5:
            st.sidebar.caption(f"... et {len(drafts) - 5} autres")


from datetime import timedelta