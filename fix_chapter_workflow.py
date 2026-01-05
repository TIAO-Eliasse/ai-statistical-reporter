"""
Script de correction automatique pour chapter_workflow.py
Corrige l'erreur horizontalalignment et ajoute règles anti-redondance
"""

from pathlib import Path
import shutil
import re


def fix_chapter_workflow(file_path: str = 'chapter_workflow.py'):
    """Corrige automatiquement chapter_workflow.py"""
    
    path = Path(file_path)
    
    if not path.exists():
        print(f"[ERROR] Fichier non trouve : {file_path}")
        print("[INFO] Assurez-vous d'executer ce script dans le dossier contenant chapter_workflow.py")
        return False
    
    print("="*70)
    print("CORRECTION AUTOMATIQUE - chapter_workflow.py")
    print("="*70)
    
    # Backup
    backup_path = path.with_suffix('.py.bak_matplotlib')
    if not backup_path.exists():
        shutil.copy(path, backup_path)
        print(f"\n[OK] Backup cree : {backup_path.name}")
    else:
        print(f"\n[INFO] Backup existe deja : {backup_path.name}")
    
    # Lire contenu
    content = path.read_text(encoding='utf-8')
    original_content = content
    
    # ===================================================================
    # CORRECTION 1 : horizontalalignment → ha
    # ===================================================================
    
    print("\n[CORRECTION 1] Fix parametres matplotlib...")
    
    corrections = 0
    
    # Pattern 1 : plt.xticks(..., horizontalalignment='...')
    pattern1 = r"plt\.xticks\([^)]*,\s*horizontalalignment\s*=\s*['\"](\w+)['\"]"
    def replace1(match):
        nonlocal corrections
        corrections += 1
        align = match.group(1)
        return match.group(0).replace('horizontalalignment', 'ha')
    
    content = re.sub(pattern1, replace1, content)
    
    # Pattern 2 : plt.yticks(..., verticalalignment='...')
    pattern2 = r"plt\.yticks\([^)]*,\s*verticalalignment\s*=\s*['\"](\w+)['\"]"
    def replace2(match):
        nonlocal corrections
        corrections += 1
        return match.group(0).replace('verticalalignment', 'va')
    
    content = re.sub(pattern2, replace2, content)
    
    # Pattern 3 : Corriger exemples dans le prompt
    # Ligne ~1088-1089
    old_example = """❌ INTERDIT (paramètres abrégés) :
    ```python
    plt.xticks(rotation=45, ha='center')  # ❌ 'ha' non reconnu
    plt.yticks(va='top')                   # ❌ 'va' non reconnu
    ```
    
    ✅ CORRECT (noms complets) :
    ```python
    plt.xticks(rotation=45, horizontalalignment='center')  # ✅
    plt.yticks(verticalalignment='top')                    # ✅
    ```"""
    
    new_example = """✅ CORRECT (rotation et alignement) :
    ```python
    plt.xticks(rotation=45, ha='right')   # ✅ ha = horizontal alignment
    plt.yticks(rotation=0, va='center')   # ✅ va = vertical alignment
    ```
    
    ❌ ERREURS COURANTES :
    ```python
    plt.xticks(horizontalalignment='center')  # ❌ parametre inconnu
    plt.yticks(verticalalignment='top')       # ❌ parametre inconnu
    ```"""
    
    if old_example in content:
        content = content.replace(old_example, new_example)
        corrections += 1
        print(f"   [OK] Exemple prompt corrige")
    
    if corrections > 0:
        print(f"   [OK] {corrections} correction(s) appliquee(s)")
    else:
        print(f"   [INFO] Aucune correction necessaire (deja fixe)")
    
    # ===================================================================
    # CORRECTION 2 : Ajouter règles anti-redondance
    # ===================================================================
    
    print("\n[CORRECTION 2] Ajout regles anti-redondance...")
    
    # Chercher où insérer (après règles matplotlib)
    marker = "🔧 BLOCS TRY/EXCEPT :"
    
    if marker in content and "📊 RÈGLES TABLEAU vs GRAPHIQUE" not in content:
        
        anti_redundancy_rules = """
    
    📊 RÈGLES TABLEAU vs GRAPHIQUE (éviter redondance) :
    
    ⚠️ PRINCIPE : Ne PAS créer tableau ET graphique pour la MÊME information simple
    
    ✅ GRAPHIQUE SEUL (pas de tableau) si :
    ```python
    # Variable catégorielle simple (< 10 modalités)
    # Exemple : Sexe (2), Region (10), Situation matrimoniale (5)
    plt.bar(categories, values)
    # → Graphique SUFFIT, PAS de tableau markdown
    ```
    
    ✅ TABLEAU SEUL (pas de graphique) si :
    ```python
    # Trop de modalités (> 15) OU chiffres précis essentiels
    # Exemple : 50 secteurs d'activité, montants financiers exacts
    # → Créer uniquement tableau markdown, PAS de plt
    ```
    
    ✅ TABLEAU + GRAPHIQUE ensemble si :
    ```python
    # Évolution temporelle OU comparaison multi-dimensionnelle
    # Exemple : CA par région sur 5 ans, performance multi-critères
    # → Graphique (tendance) + Tableau (valeurs précises)
    ```
    
    ❌ ERREUR FRÉQUENTE :
    ```python
    # Distribution simple Sexe (2 modalités)
    # Créer tableau : | Homme | 70% | Femme | 30% |
    # Créer graphique : barre chart
    # → REDONDANT ! Garder seulement le graphique
    ```
    
    🎯 DÉCISION RAPIDE :
    - Modalités < 10 + distribution simple ? → GRAPHIQUE seul
    - Modalités > 15 + précision importante ? → TABLEAU seul
    - Évolution temporelle ou complexe ? → GRAPHIQUE + TABLEAU
    
    """
        
        insert_pos = content.find(marker)
        content = content[:insert_pos] + anti_redundancy_rules + content[insert_pos:]
        print(f"   [OK] Regles anti-redondance ajoutees")
    
    elif "📊 RÈGLES TABLEAU vs GRAPHIQUE" in content:
        print(f"   [INFO] Regles deja presentes")
    else:
        print(f"   [WARNING] Marqueur non trouve, regles non ajoutees")
    
    # ===================================================================
    # SAUVEGARDER
    # ===================================================================
    
    if content != original_content:
        path.write_text(content, encoding='utf-8')
        print(f"\n[OK] Fichier corrige et sauvegarde : {path.name}")
        print(f"\n[INFO] Backup disponible : {backup_path.name}")
        
        # Statistiques
        lines_changed = sum(1 for a, b in zip(original_content.split('\n'), content.split('\n')) if a != b)
        print(f"[INFO] {lines_changed} ligne(s) modifiee(s)")
        
        return True
    else:
        print(f"\n[INFO] Aucune modification necessaire")
        return False


def test_correction():
    """Test rapide après correction"""
    
    print("\n" + "="*70)
    print("TEST CORRECTION")
    print("="*70)
    
    try:
        # Test matplotlib syntax
        import matplotlib
        matplotlib.use('Agg')  # Backend sans GUI
        import matplotlib.pyplot as plt
        
        print("\n[TEST 1] Syntaxe matplotlib...")
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(['A', 'B', 'C'], [10, 20, 15])
        
        # Test ha= parameter
        plt.xticks(rotation=45, ha='right')  # ✅ Devrait fonctionner
        plt.yticks(va='center')  # ✅ Devrait fonctionner
        
        plt.title("Test correction matplotlib")
        plt.tight_layout()
        plt.savefig('test_correction.png', dpi=100, bbox_inches='tight')
        plt.close()
        
        print("   [OK] Syntaxe matplotlib correcte")
        print("   [OK] Image test generee : test_correction.png")
        
        return True
    
    except Exception as e:
        print(f"   [ERROR] Test echoue : {e}")
        return False


def main():
    """Fonction principale"""
    
    import sys
    
    # Correction
    success = fix_chapter_workflow()
    
    if success:
        # Test
        print("\n" + "="*70)
        print("Voulez-vous executer un test de validation ? (o/n)")
        
        # Auto-test
        test_correction()
    
    print("\n" + "="*70)
    print("RESUME")
    print("="*70)
    
    if success:
        print("\n[OK] Correction appliquee avec succes !")
        print("\n[ACTION] Relancez votre generation de rapport pour tester")
        print("\n[VERIFICATION] Le graphique devrait se generer sans erreur")
        print("[VERIFICATION] Moins de redondance tableau+graphique")
    else:
        print("\n[INFO] Aucune correction necessaire (deja a jour)")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Interruption utilisateur")
    except Exception as e:
        print(f"\n\n[ERROR] Erreur inattendue : {e}")
        import traceback
        traceback.print_exc()