#!/usr/bin/env python3
"""
Script d'intégration automatique du workflow par étapes
Transforme app_streamlit_professional.py en version avec workflow
"""

import re
from pathlib import Path

def integrate_workflow(input_file: str, output_file: str):
    """
    Intègre le système de workflow dans l'application
    
    Args:
        input_file: Chemin vers app_streamlit_professional.py original
        output_file: Chemin vers le fichier de sortie
    """
    
    print("🚀 Début de l'intégration du workflow...")
    
    # Lire le fichier original
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # ═══════════════════════════════════════════════════════════
    # MODIFICATION 1 : Ajouter l'import
    # ═══════════════════════════════════════════════════════════
    
    print("✓ Modification 1 : Ajout de l'import workflow_manager...")
    
    # Trouver la ligne avec "from week2_architect_agent import"
    import_added = False
    for i, line in enumerate(lines):
        if 'from week2_architect_agent import' in line:
            # Ajouter l'import après
            workflow_import = """
# Workflow Manager
try:
    from workflow_manager import WorkflowManager, WorkflowStep
    WORKFLOW_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ workflow_manager.py non disponible: {e}")
    WORKFLOW_MANAGER_AVAILABLE = False
"""
            lines.insert(i + 1, workflow_import)
            import_added = True
            break
    
    if not import_added:
        print("⚠️ Import non ajouté (ligne d'import non trouvée)")
    
    # ═══════════════════════════════════════════════════════════
    # MODIFICATION 2 : Initialiser le workflow
    # ═══════════════════════════════════════════════════════════
    
    print("✓ Modification 2 : Initialisation du workflow...")
    
    # Trouver "if 'study_context' not in st.session_state:"
    workflow_init_added = False
    for i, line in enumerate(lines):
        if "'study_context' not in st.session_state" in line:
            # Ajouter après le bloc study_context
            workflow_init = """
# Initialiser le workflow
if 'workflow_step' not in st.session_state:
    st.session_state.workflow_step = 1  # Étape 1 : Upload

if 'workflow_history' not in st.session_state:
    st.session_state.workflow_history = [1]
"""
            # Trouver la fin du bloc (2 lignes après)
            lines.insert(i + 2, workflow_init)
            workflow_init_added = True
            break
    
    if not workflow_init_added:
        print("⚠️ Initialisation non ajoutée")
    
    # ═══════════════════════════════════════════════════════════
    # MODIFICATION 3 : Simplifier la sidebar
    # ═══════════════════════════════════════════════════════════
    
    print("✓ Modification 3 : Simplification de la sidebar...")
    
    # Trouver et remplacer la navigation radio
    navigation_found = False
    i = 0
    while i < len(lines):
        if 'st.header("Navigation")' in lines[i] or 'Navigation' in lines[i]:
            # Trouver le début et la fin du bloc de navigation
            start = i - 2  # Ligne avec "st.markdown("---")"
            
            # Chercher la fin (prochain st.markdown("---"))
            end = i + 1
            while end < len(lines) and 'st.markdown("---")' not in lines[end]:
                end += 1
            
            # Remplacer tout le bloc
            simplified_nav = """st.markdown("---")

# Workflow progressif - pas de navigation manuelle dans la sidebar
st.info("📊 Suivez les étapes affichées dans l'écran principal")

st.markdown("---")
"""
            lines[start:end+1] = [simplified_nav]
            navigation_found = True
            break
        i += 1
    
    if not navigation_found:
        print("⚠️ Navigation non modifiée")
    
    # ═══════════════════════════════════════════════════════════
    # MODIFICATION 4 : Remplacer la section principale
    # ═══════════════════════════════════════════════════════════
    
    print("✓ Modification 4 : Remplacement de la section principale...")
    
    # Trouver "# ========== PAGE PRINCIPALE =========="
    main_section_start = -1
    for i, line in enumerate(lines):
        if '# ========== PAGE PRINCIPALE ==========' in line or '# ========== WORKFLOW PRINCIPAL ==========' in line:
            main_section_start = i
            break
    
    if main_section_start == -1:
        print("❌ Section principale non trouvée!")
        return False
    
    # Tout supprimer après cette ligne
    lines = lines[:main_section_start]
    
    # Ajouter le nouveau code du workflow
    workflow_code = get_workflow_main_section()
    lines.append(workflow_code)
    
    # ═══════════════════════════════════════════════════════════
    # ÉCRIRE LE FICHIER DE SORTIE
    # ═══════════════════════════════════════════════════════════
    
    output_content = '\n'.join(lines)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"✅ Intégration terminée ! Fichier créé : {output_file}")
    print(f"📊 Taille originale : {len(content)} caractères")
    print(f"📊 Taille nouvelle : {len(output_content)} caractères")
    
    return True


def get_workflow_main_section():
    """Retourne le code complet de la section workflow"""
    
    return """
# ========== WORKFLOW PRINCIPAL PAR ÉTAPES ==========

# Vérifier que le workflow manager est disponible
if not WORKFLOW_MANAGER_AVAILABLE:
    st.error("❌ Module workflow_manager.py manquant")
    st.info("Ajoutez le fichier `workflow_manager.py` à votre projet")
    st.stop()

# Obtenir l'étape actuelle
current_step = st.session_state.get('workflow_step', 1)


# ═══════════════════════════════════════════════════════════════
# AFFICHER LA BARRE DE PROGRESSION
# ═══════════════════════════════════════════════════════════════

step_names = {
    1: ("📂 Upload des données", "Chargez votre fichier CSV/Excel"),
    2: ("🎯 Choix du mode", "Avez-vous une problématique définie ?"),
    2.5: ("📋 Contexte de l'étude", "Définissez votre contexte (optionnel)"),
    3: ("📝 Génération du plan", "Créez le plan de votre rapport"),
    4: ("📏 Configuration", "Définissez la longueur des chapitres"),
    5: ("📄 Génération du rapport", "Générez les chapitres")
}

# Calculer le pourcentage
if current_step == 2.5:
    progress = 0.5  # Entre étape 2 et 3
else:
    progress = (current_step - 1) / 4  # 4 étapes principales

step_info = step_names.get(current_step, ("Étape inconnue", ""))
icon_title, description = step_info

st.markdown(f'''
<div style="margin-bottom: 2rem;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
        <span style="font-weight: 600; font-size: 1.2rem;">
            {icon_title}
        </span>
        <span style="color: #666; font-size: 0.9rem;">
            {int(progress * 100)}%
        </span>
    </div>
    <div style="background-color: #e0e0e0; border-radius: 10px; height: 10px; overflow: hidden;">
        <div style="background: linear-gradient(90deg, #4CAF50 0%, #45a049 100%); 
                    height: 100%; width: {progress * 100}%; transition: width 0.3s ease;">
        </div>
    </div>
    <p style="color: #666; font-size: 0.95rem; margin-top: 0.5rem; font-style: italic;">
        {description}
    </p>
</div>
''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# ÉTAPE 1 : UPLOAD DES DONNÉES
# ═══════════════════════════════════════════════════════════════

if current_step == 1:
    st.title("📂 Étape 1 : Upload des données")
    
    st.info('''
**Commençons par charger vos données !**

Formats acceptés : CSV (.csv), Excel (.xlsx, .xls)
    ''')
    
    # Le fichier est déjà uploadé dans la sidebar
    if st.session_state.csv_data is not None:
        df = st.session_state.csv_data
        
        st.success("✅ Fichier chargé avec succès !")
        
        # Métriques
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Lignes", f"{len(df):,}")
        with col2:
            st.metric("📋 Colonnes", len(df.columns))
        with col3:
            # Calculer la taille estimée
            size_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
            st.metric("💾 Taille", f"{size_mb:.2f} MB")
        
        # Aperçu des données
        with st.expander("🔍 Voir l'aperçu des données", expanded=True):
            st.dataframe(df.head(10), use_container_width=True)
        
        # Statistiques descriptives
        with st.expander("📊 Voir les statistiques descriptives"):
            st.dataframe(df.describe(), use_container_width=True)
        
        st.markdown("---")
        
        # Bouton suivant
        col1, col2, col3 = st.columns([1, 2, 1])
        with col3:
            if st.button("Suivant : Choix du mode →", type="primary", use_container_width=True):
                st.session_state.workflow_step = 2
                st.session_state.workflow_history.append(2)
                st.rerun()
    
    else:
        st.info("👆 Uploadez un fichier dans la barre latérale pour commencer")


# ═══════════════════════════════════════════════════════════════
# ÉTAPE 2 : CHOIX DU MODE
# ═══════════════════════════════════════════════════════════════

elif current_step == 2:
    st.title("🎯 Étape 2 : Choix du mode d'analyse")
    
    st.markdown('''
### Avez-vous un contexte d'étude défini ?

C'est-à-dire : une **problématique**, des **hypothèses**, des **objectifs** de recherche ?
    ''')
    
    # Deux cartes de choix
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('''
<div style="border: 2px solid #4CAF50; border-radius: 10px; padding: 1.5rem; min-height: 300px;">
    <h3 style="color: #4CAF50;">✅ Oui, j'ai un contexte</h3>
    <p><strong>Mode Académique</strong></p>
    <ul>
        <li>Problématique définie</li>
        <li>Hypothèses à tester</li>
        <li>Objectifs clairs</li>
        <li>Analyse ciblée</li>
        <li>Rapport de haute qualité</li>
    </ul>
    <p style="color: #666; font-size: 0.9rem; margin-top: 1rem;">
        <em>📚 Recommandé pour : études sérieuses, mémoires, recherches, rapports professionnels</em>
    </p>
</div>
        ''', unsafe_allow_html=True)
        
        st.markdown("")
        if st.button("✅ J'ai un contexte d'étude", type="primary", use_container_width=True, key="btn_academic"):
            st.session_state.analysis_mode = "academic"
            if STUDY_CONTEXT_AVAILABLE:
                if st.session_state.study_context is None:
                    from study_context import StudyContext
                    st.session_state.study_context = StudyContext()
            st.session_state.workflow_step = 2.5  # Aller au contexte
            st.session_state.workflow_history.append(2.5)
            st.rerun()
    
    with col2:
        st.markdown('''
<div style="border: 2px solid #2196F3; border-radius: 10px; padding: 1.5rem; min-height: 300px;">
    <h3 style="color: #2196F3;">⚡ Non, analyse rapide</h3>
    <p><strong>Mode Rapide</strong></p>
    <ul>
        <li>Pas de contexte prédéfini</li>
        <li>Analyse automatique</li>
        <li>Résultats génériques</li>
        <li>Rapide (5-10 minutes)</li>
        <li>Exploration des données</li>
    </ul>
    <p style="color: #666; font-size: 0.9rem; margin-top: 1rem;">
        <em>⚡ Recommandé pour : exploration rapide, prototypage, premiers insights</em>
    </p>
</div>
        ''', unsafe_allow_html=True)
        
        st.markdown("")
        if st.button("⚡ Analyse rapide sans contexte", use_container_width=True, key="btn_quick"):
            st.session_state.analysis_mode = "quick"
            st.session_state.study_context = None
            st.session_state.workflow_step = 3  # Aller directement au plan
            st.session_state.workflow_history.append(3)
            st.rerun()
    
    st.markdown("---")
    
    # Bouton retour
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Retour", use_container_width=True):
            st.session_state.workflow_step = 1
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# ÉTAPE 2.5 : CONTEXTE DE L'ÉTUDE (si mode académique)
# ═══════════════════════════════════════════════════════════════

elif current_step == 2.5:
    st.title("📋 Étape 2b : Contexte de l'étude")
    
    if not STUDY_CONTEXT_AVAILABLE:
        st.error("❌ Module study_context.py non disponible")
        st.info("Ajoutez le fichier `study_context.py` à votre projet")
        
        # Boutons de navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("← Retour", use_container_width=True):
                st.session_state.workflow_step = 2
                st.rerun()
        with col3:
            if st.button("Passer cette étape →", use_container_width=True):
                st.session_state.workflow_step = 3
                st.session_state.workflow_history.append(3)
                st.rerun()
        st.stop()
    
    from study_context import StudyContext
    
    st.info('''
**Définissez votre contexte pour une analyse de qualité académique**

Remplissez au minimum :
- ✅ Question de recherche
- ✅ Objectifs de l'étude
    ''')
    
    # Initialiser le contexte
    if st.session_state.study_context is None:
        st.session_state.study_context = StudyContext()
    
    ctx = st.session_state.study_context
    
    # ═══ SECTION 1 : INFORMATIONS GÉNÉRALES ═══
    st.markdown("## 📋 Informations Générales")
    
    with st.expander("ℹ️ Informations de base", expanded=True):
        ctx.study_title = st.text_input(
            "📌 Titre de l'étude",
            value=ctx.study_title,
            placeholder="Ex: Analyse de la satisfaction client 2024"
        )
        
        ctx.research_question = st.text_area(
            "❓ Question de recherche principale ⭐",
            value=ctx.research_question,
            height=100,
            placeholder="Ex: Quel est l'impact de l'âge sur le salaire ?"
        )
    
    # ═══ SECTION 2 : OBJECTIFS ═══
    st.markdown("## 🎯 Objectifs")
    
    with st.expander("🎯 Définissez vos objectifs", expanded=True):
        st.markdown("**Objectifs de l'étude** *(un par ligne)* ⭐")
        objectives_text = st.text_area(
            "Objectifs",
            value="\\n".join(ctx.objectives) if ctx.objectives else "",
            height=100,
            placeholder="1. Analyser\\n2. Identifier\\n3. Proposer",
            label_visibility="collapsed"
        )
        ctx.objectives = [o.strip() for o in objectives_text.split('\\n') if o.strip()]
    
    # Validation
    is_valid = bool(ctx.research_question or ctx.objectives)
    
    # Indicateur
    if ctx.research_question and ctx.objectives:
        st.success("✅ Contexte minimal rempli !")
    elif ctx.research_question or ctx.objectives:
        st.info("ℹ️ Vous pouvez continuer")
    else:
        st.warning("⚠️ Remplissez au moins la question ou les objectifs")
    
    st.markdown("---")
    
    # Boutons de navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Retour", use_container_width=True, key="back_context"):
            st.session_state.workflow_step = 2
            st.rerun()
    with col3:
        if st.button(
            "Valider et continuer →",
            type="primary",
            use_container_width=True,
            disabled=not is_valid,
            key="next_context"
        ):
            st.session_state.workflow_step = 3
            st.session_state.workflow_history.append(3)
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# ÉTAPE 3 : GÉNÉRATION DU PLAN
# ═══════════════════════════════════════════════════════════════

elif current_step == 3:
    st.title("📝 Étape 3 : Génération du plan")
    
    st.info("Génération du plan du rapport basé sur vos données" + 
            (" et votre contexte" if st.session_state.analysis_mode == "academic" else ""))
    
    # TODO: Insérer ici le code complet de la génération du plan
    st.warning("⚠️ Section en construction - Code de génération du plan à insérer")
    
    # Boutons de navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Retour", use_container_width=True, key="back_plan"):
            if st.session_state.analysis_mode == "academic":
                st.session_state.workflow_step = 2.5
            else:
                st.session_state.workflow_step = 2
            st.rerun()
    with col3:
        if st.button("Continuer →", type="primary", use_container_width=True, key="next_plan"):
            st.session_state.workflow_step = 4
            st.session_state.workflow_history.append(4)
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# ÉTAPE 4 : CONFIGURATION
# ═══════════════════════════════════════════════════════════════

elif current_step == 4:
    st.title("📏 Étape 4 : Configuration du rapport")
    
    st.info("Configuration de la longueur des chapitres")
    
    # TODO: Insérer ici le code de configuration
    st.warning("⚠️ Section en construction - Code de configuration à insérer")
    
    # Boutons de navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Retour", use_container_width=True, key="back_config"):
            st.session_state.workflow_step = 3
            st.rerun()
    with col3:
        if st.button("Lancer la génération →", type="primary", use_container_width=True, key="next_config"):
            st.session_state.workflow_step = 5
            st.session_state.workflow_history.append(5)
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# ÉTAPE 5 : GÉNÉRATION DU RAPPORT
# ═══════════════════════════════════════════════════════════════

elif current_step == 5:
    st.title("📄 Étape 5 : Génération du rapport")
    
    st.info("Génération des chapitres en cours")
    
    # TODO: Insérer ici le code de génération
    st.warning("⚠️ Section en construction - Code de génération à insérer")
    
    # Bouton retour
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Retour", use_container_width=True, key="back_generation"):
            st.session_state.workflow_step = 4
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# ÉTAPE INCONNUE
# ═══════════════════════════════════════════════════════════════

else:
    st.error(f"❌ Étape inconnue : {current_step}")
    if st.button("🔄 Recommencer", type="primary"):
        st.session_state.workflow_step = 1
        st.session_state.workflow_history = [1]
        st.rerun()
"""


if __name__ == "__main__":
    # Chemins des fichiers
    input_file = "app_streamlit_professional.py"
    output_file = "app_streamlit_workflow.py"
    
    print("="* 60)
    print("SCRIPT D'INTÉGRATION AUTOMATIQUE DU WORKFLOW")
    print("="* 60)
    print()
    
    # Vérifier que le fichier d'entrée existe
    if not Path(input_file).exists():
        print(f"❌ Fichier {input_file} non trouvé!")
        print(f"📁 Placez ce script dans le même dossier que {input_file}")
        exit(1)
    
    # Effectuer l'intégration
    success = integrate_workflow(input_file, output_file)
    
    if success:
        print()
        print("="* 60)
        print("✅ INTÉGRATION RÉUSSIE !")
        print("="* 60)
        print()
        print(f"📄 Nouveau fichier créé : {output_file}")
        print()
        print("🚀 Pour tester :")
        print(f"   streamlit run {output_file}")
        print()
        print("⚠️  NOTE : Les étapes 3, 4, 5 contiennent des placeholders")
        print("   Il faudra copier le code des anciennes pages manuellement")
    else:
        print("❌ Échec de l'intégration")
        exit(1)