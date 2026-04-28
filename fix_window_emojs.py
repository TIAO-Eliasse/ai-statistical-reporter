"""
Fix Windows emoji logging issue
Remplace emojis par texte dans les logs
"""

import re
from pathlib import Path

def remove_emojis_from_logs(file_path: str) -> None:
    """Enlève emojis des logger.info/debug/warning"""
    
    path = Path(file_path)
    if not path.exists():
        print(f"❌ Fichier non trouvé : {file_path}")
        return
    
    content = path.read_text(encoding='utf-8')
    
    # Remplacements emojis → texte
    replacements = {
        '✅': '[OK]',
        '❌': '[ERROR]',
        '⚠️': '[WARNING]',
        '🔄': '[REFRESH]',
        '💾': '[SAVE]',
        '🗑️': '[DELETE]',
        '📊': '[DATA]',
        '🔍': '[SEARCH]',
        '⏰': '[TIME]',
        'ℹ️': '[INFO]',
    }
    
    modified = content
    for emoji, text in replacements.items():
        # Remplacer dans logger.info, logger.debug, etc.
        modified = modified.replace(emoji, text)
    
    if modified != content:
        # Backup
        backup = path.with_suffix('.py.bak')
        path.rename(backup)
        print(f"[OK] Backup créé : {backup}")
        
        # Écrire version corrigée
        path.write_text(modified, encoding='utf-8')
        print(f"[OK] Emojis remplacés dans : {file_path}")
        
        # Compter changements
        changes = sum(content.count(emoji) for emoji in replacements)
        print(f"[OK] {changes} emoji(s) remplacé(s)")
    else:
        print(f"[INFO] Aucun emoji trouvé dans {file_path}")


if __name__ == "__main__":
    # Fixer les fichiers problématiques
    files_to_fix = [
        'e2b_session_manager.py',
        'week2_architect_agent.py',
        'chapter_workflow.py',
        'app_streamlit_workflow.py'
    ]
    
    print("="*60)
    print("FIX WINDOWS EMOJI LOGGING")
    print("="*60)
    
    for file in files_to_fix:
        print(f"\n[INFO] Traitement : {file}")
        remove_emojis_from_logs(file)
    
    print("\n" + "="*60)
    print("[OK] Fix terminé !")
    print("="*60)
    print("\n[INFO] Relancez Streamlit : streamlit run app_streamlit_workflow.py")