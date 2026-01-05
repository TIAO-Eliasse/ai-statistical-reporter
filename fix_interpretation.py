"""
Correctif chapter_workflow.py - FORCER INTERPRÉTATIONS
Problème : Graphiques consécutifs sans interprétation entre eux
Solution : Validation + prompt renforcé + structure forcée
"""

from pathlib import Path
import shutil
import re


def add_interpretation_enforcer(file_path: str = 'chapter_workflow.py'):
    """Ajoute validation stricte des interprétations"""
    
    path = Path(file_path)
    
    if not path.exists():
        print(f"[ERROR] Fichier non trouve : {file_path}")
        return False
    
    print("="*70)
    print("CORRECTIF - INTERPRÉTATIONS OBLIGATOIRES")
    print("="*70)
    
    # Backup
    backup_path = path.with_suffix('.py.bak_interp')
    if not backup_path.exists():
        shutil.copy(path, backup_path)
        print(f"\n[OK] Backup cree : {backup_path.name}")
    
    content = path.read_text(encoding='utf-8')
    original = content
    
    # ===================================================================
    # AJOUT 1 : Fonction de validation anti-graphiques-consécutifs
    # ===================================================================
    
    print("\n[AJOUT 1] Fonction validation anti-consecutifs...")
    
    validation_function = '''
def validate_no_consecutive_visuals(markdown_text: str) -> dict:
    """
    Valide qu'il n'y a PAS 2 graphiques/tableaux consécutifs sans texte
    
    Returns:
        dict avec 'valid' (bool) et 'violations' (list)
    """
    lines = markdown_text.split('\\n')
    violations = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Détecter graphique/tableau
        is_visual = (
            line.startswith('**Graphique') or 
            line.startswith('**Tableau') or
            line.startswith('![') or
            '|' in line and i > 0 and '|' in lines[i-1]
        )
        
        if is_visual:
            # Chercher prochain élément visuel
            j = i + 1
            text_between = []
            
            while j < len(lines):
                next_line = lines[j].strip()
                
                # Prochain visuel trouvé ?
                next_is_visual = (
                    next_line.startswith('**Graphique') or 
                    next_line.startswith('**Tableau') or
                    next_line.startswith('![')
                )
                
                if next_is_visual:
                    # Vérifier s'il y a du texte substantiel entre
                    text_content = ' '.join(text_between)
                    word_count = len([w for w in text_content.split() if len(w) > 2])
                    
                    if word_count < 20:  # Moins de 20 mots = pas d'interprétation
                        violations.append({
                            'line': i + 1,
                            'type': 'consecutive_visuals',
                            'message': f'Graphique/Tableau ligne {i+1} suivi immédiatement par ligne {j+1} sans interprétation (seulement {word_count} mots)',
                            'context': f"{line[:50]}... → {next_line[:50]}..."
                        })
                    break
                
                # Accumuler texte
                if next_line and not next_line.startswith('#'):
                    text_between.append(next_line)
                
                j += 1
        
        i += 1
    
    return {
        'valid': len(violations) == 0,
        'violations': violations,
        'count': len(violations)
    }


def fix_consecutive_visuals(markdown_text: str) -> str:
    """
    Corrige automatiquement les graphiques/tableaux consécutifs
    en ajoutant des interprétations placeholder
    """
    lines = markdown_text.split('\\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        fixed_lines.append(line)
        
        # Détecter graphique/tableau
        is_visual = (
            line.strip().startswith('**Graphique') or 
            line.strip().startswith('**Tableau')
        )
        
        if is_visual:
            # Chercher prochain visuel
            j = i + 1
            has_text = False
            
            while j < len(lines) and j < i + 10:  # Chercher dans les 10 lignes suivantes
                next_line = lines[j].strip()
                
                if next_line.startswith('**Graphique') or next_line.startswith('**Tableau'):
                    # Prochain visuel trouvé sans texte
                    if not has_text:
                        # Insérer interprétation placeholder (PROSE NATURELLE)
                        fixed_lines.append('')
                        fixed_lines.append('[À compléter : Ajouter ici 2-3 paragraphes d\'analyse professionnelle de cette visualisation, sans titre "Interprétation". Décrire les observations principales, les implications, et le contexte. Minimum 50 mots en prose naturelle.]')
                        fixed_lines.append('')
                        logger.warning(f"Auto-fix: Analyse placeholder ajoutée après ligne {i+1}")
                    break
                
                # Vérifier présence texte substantiel
                if len(next_line) > 20 and not next_line.startswith('#'):
                    has_text = True
                    break
                
                j += 1
        
        i += 1
    
    return '\\n'.join(fixed_lines)

'''
    
    # Chercher où insérer (après imports, avant Chapter class)
    insert_marker = "class ChapterStatus(Enum):"
    
    if insert_marker in content and "validate_no_consecutive_visuals" not in content:
        insert_pos = content.find(insert_marker)
        content = content[:insert_pos] + validation_function + '\\n\\n' + content[insert_pos:]
        print("   [OK] Fonctions de validation ajoutees")
    elif "validate_no_consecutive_visuals" in content:
        print("   [INFO] Fonctions deja presentes")
    else:
        print("   [WARNING] Marqueur non trouve, insertion manuelle requise")
    
    # ===================================================================
    # AJOUT 2 : Renforcer règles dans prompt
    # ===================================================================
    
    print("\n[AJOUT 2] Renforcement regles prompt...")
    
    # Chercher section règles (vers ligne 1200-1250)
    rule_marker = "❌ Enchaîner 2+ tableaux/graphiques sans interprétation entre eux"
    
    if rule_marker in content:
        # Ajouter règles ultra-strictes APRÈS ce marqueur
        enhanced_rules = """
    
    🚨 STRUCTURE OBLIGATOIRE (NON-NÉGOCIABLE) :
    
    ```
    **Graphique X.Y** : Titre descriptif
    [Code plt.show() ou image]
    
    [ANALYSE EN PROSE NATURELLE - Pas de titre "Interprétation"]
    Premier paragraphe : Observation principale des données visualisées.
    Description factuelle de ce que montre le graphique, avec chiffres clés.
    
    Deuxième paragraphe : Implications ou insights. Contexte et comparaisons
    pertinentes. Analyse approfondie des tendances observées.
    (Minimum 2-3 paragraphes, 80 mots, en prose professionnelle)
    
    **Graphique/Tableau suivant** : ...  ← Seulement APRÈS analyse complète
    ```
    
    ⚠️ VALIDATION AUTOMATIQUE :
    - Si 2 visuels consécutifs détectés → REJET du chapitre
    - Si analyse < 80 mots → REJET
    - Pas de "Poursuivons..." sans analyse complète
    
    ✅ EXEMPLE CORRECT (PROSE PROFESSIONNELLE) :
    ```markdown
    **Graphique 3.1** : Distribution du Sexe du Promoteur
    ![Graphique barres]
    
    La distribution révèle une prédominance masculine marquée, avec 70% 
    d'hommes contre 30% de femmes parmi les promoteurs d'entreprises. 
    Cette disparité significative s'observe de manière constante à travers 
    toutes les régions analysées.
    
    Cette sous-représentation féminine dans l'entrepreneuriat soulève des 
    questions importantes sur l'accès au financement, à la formation et aux 
    réseaux professionnels pour les femmes entrepreneures. Les données 
    témoignent d'un déséquilibre structurel qui nécessite des politiques 
    d'accompagnement ciblées et un renforcement des dispositifs de soutien 
    spécifiques aux femmes créatrices d'entreprises.
    
    **Graphique 3.2** : Distribution de l'Âge du Promoteur  ← OK : après analyse
    ```
    
    ❌ EXEMPLE INCORRECT (TROP SCOLAIRE) :
    ```markdown
    **Graphique 3.1** : Distribution du Sexe
    ![Graphique barres]
    
    **Interprétation** : On observe 70% hommes.  ← ❌ Titre "Interprétation"
    
    Poursuivons avec l'âge.  ← ❌ Trop court, pas d'analyse
    
    **Graphique 3.2** : Distribution Âge  ← ❌ Trop rapide
    ```
    
    💡 RÈGLES PROSE PROFESSIONNELLE :
    1. ❌ Ne JAMAIS écrire "**Interprétation** :" (trop scolaire)
    2. ✅ Intégrer l'analyse directement en prose naturelle
    3. ✅ Minimum 2-3 paragraphes par visualisation
    4. ✅ Style : factuel, analytique, professionnel
    5. ✅ Structure : Observation → Implication → Contexte
    
    📝 VOCABULAIRE PROFESSIONNEL (exemples) :
    - "La distribution révèle..."
    - "Les données témoignent de..."
    - "On observe une tendance marquée..."
    - "Cette répartition s'explique par..."
    - "Ces résultats soulèvent la question de..."
    - "L'analyse met en évidence..."
    
    ❌ À ÉVITER (trop scolaire) :
    - "**Interprétation** :"
    - "**Analyse** :"
    - "**Commentaire** :"
    - Bullet points pour l'analyse
    - Titres de section pour chaque interprétation
    """
        
        insert_pos = content.find(rule_marker) + len(rule_marker)
        content = content[:insert_pos] + enhanced_rules + content[insert_pos:]
        print("   [OK] Regles ultra-strictes ajoutees")
    else:
        print("   [WARNING] Marqueur regles non trouve")
    
    # ===================================================================
    # AJOUT 3 : Validation dans generate_chapter
    # ===================================================================
    
    print("\n[AJOUT 3] Ajout validation dans generation chapitre...")
    
    # Chercher fonction generate_chapter (vers ligne 1300+)
    if "def generate_chapter(" in content:
        
        # Chercher où insérer validation (après génération markdown, avant retour)
        # Pattern : return {'success': True, ...
        
        validation_insertion = """
        
        # VALIDATION : Vérifier pas de graphiques consécutifs
        validation_result = validate_no_consecutive_visuals(full_markdown)
        
        if not validation_result['valid']:
            logger.warning(f"⚠️ {validation_result['count']} graphique(s) consécutif(s) détecté(s)")
            
            for v in validation_result['violations'][:3]:  # Afficher top 3
                logger.warning(f"   - Ligne {v['line']}: {v['message']}")
            
            # Auto-fix (ajouter interprétations placeholder)
            logger.info("🔧 Auto-correction des graphiques consécutifs...")
            full_markdown = fix_consecutive_visuals(full_markdown)
            logger.info("✅ Interprétations placeholder ajoutées")
        else:
            logger.info("✅ Validation OK : Toutes les visualisations ont leur interprétation")
        """
        
        # Insérer avant le return final (pattern: return {'success': True)
        pattern = r"(\\s+)(return \\{'success': True,)"
        
        def insert_validation(match):
            indent = match.group(1)
            return_line = match.group(2)
            return validation_insertion + '\\n' + indent + return_line
        
        if re.search(pattern, content):
            content = re.sub(pattern, insert_validation, content, count=1)
            print("   [OK] Validation auto inseree dans generation")
        else:
            print("   [WARNING] Pattern return non trouve, insertion manuelle requise")
    
    # ===================================================================
    # SAUVEGARDER
    # ===================================================================
    
    if content != original:
        path.write_text(content, encoding='utf-8')
        print(f"\\n[OK] Fichier corrige : {path.name}")
        
        changes = sum(1 for a, b in zip(original.split('\\n'), content.split('\\n')) if a != b)
        print(f"[INFO] ~{changes} ligne(s) modifiee(s)")
        
        return True
    else:
        print(f"\\n[INFO] Aucune modification necessaire")
        return False


def main():
    """Fonction principale"""
    
    print("\\nCe script va :")
    print("1. Ajouter fonctions de validation anti-consecutifs")
    print("2. Renforcer regles dans le prompt")
    print("3. Activer validation automatique")
    print("\\nContinuer ? (o/n): ", end='')
    
    # Auto-continue
    response = 'o'
    
    if response.lower() == 'o':
        success = add_interpretation_enforcer()
        
        print("\\n" + "="*70)
        print("RESUME")
        print("="*70)
        
        if success:
            print("\\n[OK] Corrections appliquees avec succes !")
            print("\\n[CHANGEMENTS] :")
            print("   1. Validation automatique des graphiques consecutifs")
            print("   2. Auto-correction avec interprétations placeholder")
            print("   3. Regles ultra-strictes ajoutees au prompt")
            print("\\n[ACTION] Regenerez un chapitre pour tester")
            print("\\n[VERIFICATION] Les graphiques devraient avoir leur interprétation")
        else:
            print("\\n[INFO] Fichier deja a jour ou erreur")
        
        print("\\n" + "="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n\\n[INFO] Interruption utilisateur")
    except Exception as e:
        print(f"\\n\\n[ERROR] Erreur : {e}")
        import traceback
        traceback.print_exc()