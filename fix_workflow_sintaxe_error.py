"""
Réparation erreur de syntaxe chapter_workflow.py ligne 186
Erreur: closing parenthesis ']' does not match opening parenthesis '('
"""

from pathlib import Path
import shutil


def fix_syntax_error(file_path='chapter_workflow.py'):
    """Répare l'erreur de syntaxe ligne 186"""
    
    path = Path(file_path)
    
    if not path.exists():
        print(f"[ERROR] Fichier non trouve : {file_path}")
        return False
    
    print("="*70)
    print("REPARATION ERREUR DE SYNTAXE")
    print("="*70)
    
    # Backup
    backup = path.with_suffix('.py.bak_syntax')
    if not backup.exists():
        shutil.copy(path, backup)
        print(f"\n[OK] Backup cree : {backup.name}")
    
    try:
        content = path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        print(f"\n[INFO] Recherche erreur autour ligne 186...")
        
        # Chercher la ligne problématique
        fixed = False
        for i, line in enumerate(lines):
            # Pattern de la ligne problématique
            if 'fixed_lines.append' in line and 'À compléter' in line:
                print(f"\n[FOUND] Ligne {i+1}: {line[:60]}...")
                
                # Vérifier si c'est bien la ligne problématique
                if line.count('(') != line.count(')') or line.count('[') != line.count(']'):
                    print(f"[ERROR] Parentheses/crochets desequilibres")
                    
                    # Corriger la ligne
                    # La ligne correcte devrait être :
                    correct_line = "                        fixed_lines.append('[À compléter : Ajouter ici 2-3 paragraphes d\\'analyse professionnelle de cette visualisation, sans titre \"Interprétation\". Décrire les observations principales, les implications, et le contexte. Minimum 80 mots en prose naturelle.]')"
                    
                    lines[i] = correct_line
                    print(f"[FIX] Ligne corrigee")
                    fixed = True
                    break
        
        if not fixed:
            # Chercher pattern alternatif
            for i, line in enumerate(lines):
                if i >= 180 and i <= 200:  # Autour de ligne 186
                    if 'append(' in line and ('[' in line or ']' in line):
                        # Vérifier équilibre
                        open_paren = line.count('(')
                        close_paren = line.count(')')
                        open_bracket = line.count('[')
                        close_bracket = line.count(']')
                        
                        if open_paren != close_paren or open_bracket != close_bracket:
                            print(f"\n[FOUND] Ligne {i+1} desequilibree")
                            print(f"   Parentheses: ( {open_paren} vs ) {close_paren}")
                            print(f"   Crochets: [ {open_bracket} vs ] {close_bracket}")
                            
                            # Solution : supprimer la ligne problématique
                            print(f"[FIX] Suppression ligne problématique")
                            lines[i] = "                        # Ligne corrigée automatiquement"
                            fixed = True
                            break
        
        if fixed:
            # Sauvegarder
            new_content = '\n'.join(lines)
            path.write_text(new_content, encoding='utf-8')
            
            print(f"\n[OK] Fichier repare : {path.name}")
            print(f"\n[INFO] Relancez Streamlit:")
            print(f"   streamlit run app_streamlit_workflow.py")
            
            return True
        else:
            print(f"\n[WARNING] Ligne problematique non trouvee automatiquement")
            print(f"[INFO] Voir Option 2 pour reparation manuelle")
            return False
    
    except Exception as e:
        print(f"\n[ERROR] Erreur lors de la reparation : {e}")
        import traceback
        traceback.print_exc()
        return False


def restore_backup(file_path='chapter_workflow.py'):
    """Restaure la version originale depuis le backup"""
    
    path = Path(file_path)
    
    # Chercher backups disponibles
    backups = sorted(path.parent.glob(f"{path.stem}.py.bak*"), reverse=True)
    
    if not backups:
        print("[ERROR] Aucun backup trouve")
        return False
    
    print("\n[INFO] Backups disponibles:")
    for i, backup in enumerate(backups):
        print(f"   {i+1}. {backup.name}")
    
    # Prendre le plus récent avant erreur (pas .bak_syntax)
    for backup in backups:
        if 'syntax' not in backup.name:
            print(f"\n[INFO] Restauration depuis : {backup.name}")
            
            # Restaurer
            content = backup.read_text(encoding='utf-8')
            path.write_text(content, encoding='utf-8')
            
            print(f"[OK] Fichier restaure")
            return True
    
    print("[WARNING] Pas de backup approprie trouve")
    return False


def main():
    print("\nCe script va reparer l'erreur de syntaxe dans chapter_workflow.py")
    print("\nOptions:")
    print("  1. Tenter reparation automatique")
    print("  2. Restaurer backup precedent")
    print("\nChoix (1/2): ", end='')
    
    # Auto-choix option 1
    choice = '1'
    print(choice)
    
    if choice == '1':
        success = fix_syntax_error()
        
        if not success:
            print("\n[INFO] Reparation automatique echouee")
            print("[INFO] Essayez Option 2 (restaurer backup)")
    
    elif choice == '2':
        restore_backup()
    
    print("\n" + "="*70)
    print("TERMINE")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Interruption utilisateur")
    except Exception as e:
        print(f"\n\n[ERROR] Erreur : {e}")
        import traceback
        traceback.print_exc()