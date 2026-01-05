#!/usr/bin/env python3
"""
Script pour corriger l'erreur d'indentation ligne 2799-2802
À lancer dans le dossier de votre projet
"""

import sys
from pathlib import Path

def fix_indentation_error():
    """Corrige l'erreur d'indentation dans app_streamlit_workflow.py"""
    
    filename = "app_streamlit_workflow.py"
    
    if not Path(filename).exists():
        print(f"❌ Fichier {filename} non trouvé dans ce dossier")
        print(f"📂 Dossier actuel : {Path.cwd()}")
        return False
    
    print(f"📂 Correction de {filename}...")
    
    # Lire le fichier
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 Total lignes : {len(lines)}")
    
    # Trouver et afficher la zone problématique
    if len(lines) >= 2802:
        print("\n🔍 Zone problématique (lignes 2797-2805):")
        for i in range(2796, min(2805, len(lines))):
            print(f"  {i+1}: {repr(lines[i][:50])}")
        
        # L'erreur dit : "expected an indented block after 'if' statement on line 2799"
        # Cela signifie que ligne 2799 a un if: mais ligne 2800 n'est pas indentée
        
        print("\n🔧 Correction...")
        
        # Vérifier ligne 2799 (index 2798)
        if 'if' in lines[2798] and lines[2798].strip().endswith(':'):
            print(f"  Ligne 2799: {lines[2798].strip()}")
            
            # Vérifier ligne 2800 (index 2799)
            if len(lines[2799].strip()) == 0:
                # Ligne vide - il faut soit l'indenter soit ajouter du contenu
                print("  ⚠️ Ligne 2800 est vide après un 'if:'")
                print("  Solution : Ajouter 'pass' ou du contenu indenté")
                
                # Ajouter un pass
                lines[2799] = "        pass  # TODO: Compléter cette section\n"
                print("  ✓ Ajout de 'pass' ligne 2800")
            
            elif not lines[2799].startswith(' '):
                # Ligne non indentée après if:
                print(f"  ⚠️ Ligne 2800 non indentée: {lines[2799].strip()}")
                print("  Solution : Indenter la ligne")
                
                # Indenter (ajouter 4 espaces)
                lines[2799] = '    ' + lines[2799]
                print("  ✓ Ligne 2800 indentée")
        
        # Sauvegarder
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("\n✅ Fichier corrigé !")
        print(f"📝 Fichier sauvegardé : {filename}")
        return True
    
    else:
        print(f"❌ Fichier trop court ({len(lines)} lignes)")
        return False


if __name__ == "__main__":
    print("="*70)
    print("CORRECTION DE L'ERREUR D'INDENTATION")
    print("="*70)
    print()
    
    success = fix_indentation_error()
    
    if success:
        print()
        print("="*70)
        print("✅ CORRECTION TERMINÉE")
        print("="*70)
        print()
        print("🚀 Relancez votre application :")
        print("   streamlit run app_streamlit_workflow.py")
    else:
        print()
        print("❌ Échec de la correction")
        print()
        print("📝 Correction manuelle :")
        print("   1. Ouvrez app_streamlit_workflow.py")
        print("   2. Allez à la ligne 2799")
        print("   3. Vérifiez que la ligne après 'if:' est indentée")
        print("   4. Si ligne vide, ajoutez 'pass'")