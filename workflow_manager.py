"""
Système de workflow par étapes pour AI Statistical Reporter
Remplace la navigation par radio buttons par un système progressif
"""

import streamlit as st
from enum import Enum
from typing import Optional

class WorkflowStep(Enum):
    """Énumération des étapes du workflow"""
    UPLOAD = 1
    MODE_CHOICE = 2
    CONTEXT = 2.5  # Sous-étape optionnelle
    PLAN = 3
    CONFIG = 4
    GENERATION = 5

class WorkflowManager:
    """Gestionnaire du workflow progressif"""
    
    def __init__(self):
        """Initialise le gestionnaire de workflow"""
        if 'workflow_step' not in st.session_state:
            st.session_state.workflow_step = WorkflowStep.UPLOAD
        
        if 'workflow_history' not in st.session_state:
            st.session_state.workflow_history = [WorkflowStep.UPLOAD]
    
    @staticmethod
    def get_step_info(step: WorkflowStep) -> dict:
        """Retourne les informations d'une étape"""
        steps_info = {
            WorkflowStep.UPLOAD: {
                'number': 1,
                'total': 5,
                'title': 'Upload et analyse des données',
                'icon': '📂',
                'description': 'Uploadez votre fichier et visualisez les données'
            },
            WorkflowStep.MODE_CHOICE: {
                'number': 2,
                'total': 5,
                'title': 'Choix du mode d\'analyse',
                'icon': '🎯',
                'description': 'Avez-vous une problématique et des objectifs ?'
            },
            WorkflowStep.CONTEXT: {
                'number': 2,
                'total': 5,
                'title': 'Contexte de l\'étude',
                'icon': '📋',
                'description': 'Définissez votre problématique et vos objectifs'
            },
            WorkflowStep.PLAN: {
                'number': 3,
                'total': 5,
                'title': 'Génération du plan',
                'icon': '📝',
                'description': 'Génération et validation du plan du rapport'
            },
            WorkflowStep.CONFIG: {
                'number': 4,
                'total': 5,
                'title': 'Configuration du rapport',
                'icon': '📏',
                'description': 'Définissez la longueur de chaque chapitre'
            },
            WorkflowStep.GENERATION: {
                'number': 5,
                'total': 5,
                'title': 'Génération du rapport',
                'icon': '📄',
                'description': 'Génération des chapitres du rapport'
            }
        }
        return steps_info.get(step, {})
    
    @staticmethod
    def show_progress_bar(current_step: WorkflowStep):
        """Affiche la barre de progression"""
        info = WorkflowManager.get_step_info(current_step)
        
        if not info:
            return
        
        # Calculer le pourcentage (en tenant compte des sous-étapes)
        step_num = info['number']
        if current_step == WorkflowStep.CONTEXT:
            progress = (step_num + 0.5) / info['total']
        else:
            progress = step_num / info['total']
        
        # Afficher la barre de progression
        st.markdown(f"""
        <div style="margin-bottom: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-weight: 600; font-size: 1.1rem;">
                    {info['icon']} Étape {step_num}/{info['total']} : {info['title']}
                </span>
                <span style="color: #666; font-size: 0.9rem;">
                    {int(progress * 100)}%
                </span>
            </div>
            <div style="background-color: #e0e0e0; border-radius: 10px; height: 8px; overflow: hidden;">
                <div style="background: linear-gradient(90deg, #4CAF50 0%, #45a049 100%); 
                            height: 100%; width: {progress * 100}%; transition: width 0.3s ease;">
                </div>
            </div>
            <p style="color: #666; font-size: 0.9rem; margin-top: 0.5rem; font-style: italic;">
                {info['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def show_navigation_buttons(
        show_back: bool = True,
        show_next: bool = True,
        next_label: str = "Suivant →",
        next_type: str = "primary",
        back_callback = None,
        next_callback = None,
        next_disabled: bool = False
    ):
        """Affiche les boutons de navigation"""
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if show_back:
                if st.button("← Retour", use_container_width=True, key="nav_back"):
                    if back_callback:
                        back_callback()
                    else:
                        WorkflowManager.go_back()
        
        with col3:
            if show_next:
                if st.button(
                    next_label,
                    type=next_type,
                    use_container_width=True,
                    disabled=next_disabled,
                    key="nav_next"
                ):
                    if next_callback:
                        next_callback()
    
    @staticmethod
    def go_to_step(step: WorkflowStep):
        """Navigue vers une étape spécifique"""
        st.session_state.workflow_step = step
        if step not in st.session_state.workflow_history:
            st.session_state.workflow_history.append(step)
        st.rerun()
    
    @staticmethod
    def go_back():
        """Retourne à l'étape précédente"""
        history = st.session_state.workflow_history
        if len(history) > 1:
            history.pop()  # Enlever l'étape actuelle
            previous_step = history[-1]
            st.session_state.workflow_step = previous_step
            st.rerun()
    
    @staticmethod
    def validate_step(step: WorkflowStep) -> tuple[bool, str]:
        """
        Valide qu'une étape peut être franchie
        Retourne (est_valide, message_erreur)
        """
        if step == WorkflowStep.UPLOAD:
            if st.session_state.csv_data is None:
                return False, "Veuillez uploader un fichier de données"
            return True, ""
        
        elif step == WorkflowStep.MODE_CHOICE:
            if 'analysis_mode' not in st.session_state or st.session_state.analysis_mode is None:
                return False, "Veuillez choisir un mode d'analyse"
            return True, ""
        
        elif step == WorkflowStep.CONTEXT:
            # Vérifier que le contexte minimal est rempli
            ctx = st.session_state.get('study_context')
            if not ctx:
                return False, "Contexte non initialisé"
            if not ctx.research_question and not ctx.objectives:
                return False, "Remplissez au moins la question de recherche ou les objectifs"
            return True, ""
        
        elif step == WorkflowStep.PLAN:
            if st.session_state.plan is None:
                return False, "Le plan n'a pas encore été généré"
            return True, ""
        
        elif step == WorkflowStep.CONFIG:
            # Pas de validation stricte, on peut passer avec config par défaut
            return True, ""
        
        elif step == WorkflowStep.GENERATION:
            if 'workflow' not in st.session_state:
                return False, "Le workflow de génération n'est pas initialisé"
            return True, ""
        
        return True, ""


def show_step_upload():
    """Étape 1 : Upload et analyse des données"""
    from workflow_manager import WorkflowManager, WorkflowStep
    
    WorkflowManager.show_progress_bar(WorkflowStep.UPLOAD)
    
    st.title("📂 Étape 1 : Upload des données")
    
    st.info("""
    **Commençons par charger vos données !**
    
    Formats acceptés : CSV (.csv), Excel (.xlsx, .xls)
    """)
    
    # Utiliser le code d'upload existant (simplifié ici)
    uploaded_file = st.file_uploader(
        "📂 Uploadez votre fichier de données",
        type=['csv', 'xlsx', 'xls'],
        help="Formats acceptés : CSV, Excel"
    )
    
    if uploaded_file and st.session_state.csv_data is not None:
        # Afficher l'aperçu des données
        st.success("✅ Fichier chargé avec succès !")
        
        df = st.session_state.csv_data
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Lignes", f"{len(df):,}")
        with col2:
            st.metric("📋 Colonnes", len(df.columns))
        with col3:
            st.metric("💾 Taille", f"{uploaded_file.size / 1024:.1f} KB")
        
        # Bouton pour voir l'analyse détaillée
        with st.expander("🔍 Voir l'analyse détaillée des données"):
            st.dataframe(df.head(10), use_container_width=True)
            
            st.markdown("**Statistiques descriptives :**")
            st.dataframe(df.describe(), use_container_width=True)
        
        # Navigation
        WorkflowManager.show_navigation_buttons(
            show_back=False,
            next_label="Suivant : Choix du mode →",
            next_callback=lambda: WorkflowManager.go_to_step(WorkflowStep.MODE_CHOICE)
        )
    
    else:
        st.info("👆 Uploadez un fichier pour commencer")


def show_step_mode_choice():
    """Étape 2 : Choix du mode d'analyse"""
    from workflow_manager import WorkflowManager, WorkflowStep
    
    WorkflowManager.show_progress_bar(WorkflowStep.MODE_CHOICE)
    
    st.title("🎯 Étape 2 : Choix du mode d'analyse")
    
    st.markdown("""
    ### Avez-vous un contexte d'étude défini ?
    
    C'est-à-dire : une **problématique**, des **hypothèses**, des **objectifs** de recherche ?
    """)
    
    # Créer deux cartes pour les choix
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="border: 2px solid #4CAF50; border-radius: 10px; padding: 1.5rem; height: 100%;">
            <h3 style="color: #4CAF50;">✅ Oui, j'ai un contexte</h3>
            <p><strong>Mode Académique</strong></p>
            <ul>
                <li>Problématique définie</li>
                <li>Hypothèses à tester</li>
                <li>Objectifs clairs</li>
                <li>Analyse ciblée</li>
            </ul>
            <p style="color: #666; font-size: 0.9rem;">
                <em>Recommandé pour : études sérieuses, mémoires, recherches</em>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        if st.button(
            "✅ J'ai un contexte d'étude",
            type="primary",
            use_container_width=True,
            key="btn_has_context"
        ):
            st.session_state.analysis_mode = "academic"
            if STUDY_CONTEXT_AVAILABLE:
                if st.session_state.study_context is None:
                    st.session_state.study_context = StudyContext()
            WorkflowManager.go_to_step(WorkflowStep.CONTEXT)
    
    with col2:
        st.markdown("""
        <div style="border: 2px solid #2196F3; border-radius: 10px; padding: 1.5rem; height: 100%;">
            <h3 style="color: #2196F3;">⚡ Non, analyse rapide</h3>
            <p><strong>Mode Rapide</strong></p>
            <ul>
                <li>Pas de contexte prédéfini</li>
                <li>Analyse automatique</li>
                <li>Résultats génériques</li>
                <li>Rapide (5 minutes)</li>
            </ul>
            <p style="color: #666; font-size: 0.9rem;">
                <em>Recommandé pour : exploration, prototypage, premiers insights</em>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        if st.button(
            "⚡ Analyse rapide sans contexte",
            use_container_width=True,
            key="btn_no_context"
        ):
            st.session_state.analysis_mode = "quick"
            st.session_state.study_context = None
            WorkflowManager.go_to_step(WorkflowStep.PLAN)
    
    # Navigation
    WorkflowManager.show_navigation_buttons(
        show_next=False,
        back_callback=lambda: WorkflowManager.go_to_step(WorkflowStep.UPLOAD)
    )


def show_step_context():
    """Étape 2b : Définition du contexte (optionnel)"""
    from workflow_manager import WorkflowManager, WorkflowStep
    
    WorkflowManager.show_progress_bar(WorkflowStep.CONTEXT)
    
    # Afficher le formulaire de contexte complet
    # (Réutiliser le code de PAGE_CONTEXTE.py)
    
    st.title("📋 Étape 2b : Contexte de l'étude")
    
    st.info("""
    **Définissez votre contexte pour une analyse de qualité académique**
    
    Remplissez au minimum :
    - ✅ Question de recherche
    - ✅ Objectifs de l'étude
    """)
    
    # ... (Tout le formulaire de contexte ici) ...
    
    # À la fin, validation
    is_valid, error_msg = WorkflowManager.validate_step(WorkflowStep.CONTEXT)
    
    WorkflowManager.show_navigation_buttons(
        next_label="Valider et continuer →",
        next_disabled=not is_valid,
        next_callback=lambda: WorkflowManager.go_to_step(WorkflowStep.PLAN),
        back_callback=lambda: WorkflowManager.go_to_step(WorkflowStep.MODE_CHOICE)
    )
    
    if not is_valid and error_msg:
        st.warning(f"⚠️ {error_msg}")


def show_step_plan():
    """Étape 3 : Génération et validation du plan"""
    from workflow_manager import WorkflowManager, WorkflowStep
    
    WorkflowManager.show_progress_bar(WorkflowStep.PLAN)
    
    st.title("📝 Étape 3 : Génération du plan")
    
    # Si le plan n'existe pas encore
    if st.session_state.plan is None:
        st.info("Générez le plan de votre rapport basé sur vos données" + 
                (" et votre contexte" if st.session_state.analysis_mode == "academic" else ""))
        
        if st.button("🚀 Générer le plan", type="primary", use_container_width=True):
            with st.spinner("Génération du plan en cours..."):
                # Code de génération du plan
                pass
    
    # Si le plan existe
    else:
        st.success("✅ Plan généré avec succès !")
        
        # Afficher le plan
        st.markdown("### 📄 Plan du rapport")
        # ... affichage du plan ...
        
        # Options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Modifier le plan", use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()
        
        with col2:
            if st.button("🔄 Régénérer un nouveau plan", use_container_width=True):
                st.session_state.plan = None
                st.rerun()
        
        # Navigation
        is_valid, _ = WorkflowManager.validate_step(WorkflowStep.PLAN)
        
        WorkflowManager.show_navigation_buttons(
            next_label="Valider et continuer →",
            next_disabled=not is_valid,
            next_callback=lambda: WorkflowManager.go_to_step(WorkflowStep.CONFIG),
            back_callback=lambda: (
                WorkflowManager.go_to_step(WorkflowStep.CONTEXT)
                if st.session_state.analysis_mode == "academic"
                else WorkflowManager.go_to_step(WorkflowStep.MODE_CHOICE)
            )
        )


def show_step_config():
    """Étape 4 : Configuration des longueurs de chapitres"""
    from workflow_manager import WorkflowManager, WorkflowStep
    
    WorkflowManager.show_progress_bar(WorkflowStep.CONFIG)
    
    st.title("📏 Étape 4 : Configuration du rapport")
    
    st.info("""
    **Configurez la longueur de chaque chapitre**
    
    Définissez le nombre de pages souhaité pour chaque chapitre (1-30 pages).
    """)
    
    # ... (Code de configuration des longueurs avec cost_controller) ...
    
    # Afficher le résumé des coûts
    st.markdown("### 💰 Estimation des coûts")
    # ... affichage coûts ...
    
    # Navigation
    WorkflowManager.show_navigation_buttons(
        next_label="Lancer la génération →",
        next_callback=lambda: WorkflowManager.go_to_step(WorkflowStep.GENERATION),
        back_callback=lambda: WorkflowManager.go_to_step(WorkflowStep.PLAN)
    )


def show_step_generation():
    """Étape 5 : Génération des chapitres"""
    from workflow_manager import WorkflowManager, WorkflowStep
    
    WorkflowManager.show_progress_bar(WorkflowStep.GENERATION)
    
    st.title("📄 Étape 5 : Génération du rapport")
    
    st.info("Génération des chapitres en cours...")
    
    # ... (Code de génération existant) ...
    
    # Pas de bouton "Suivant" ici, c'est la dernière étape
    WorkflowManager.show_navigation_buttons(
        show_next=False,
        back_callback=lambda: WorkflowManager.go_to_step(WorkflowStep.CONFIG)
    )


# ═══ FONCTION PRINCIPALE DE ROUTAGE ═══

def main_workflow():
    """Fonction principale qui route vers la bonne étape"""
    
    # Obtenir l'étape actuelle
    current_step = st.session_state.get('workflow_step', WorkflowStep.UPLOAD)
    
    # Router vers la bonne fonction
    if current_step == WorkflowStep.UPLOAD:
        show_step_upload()
    
    elif current_step == WorkflowStep.MODE_CHOICE:
        show_step_mode_choice()
    
    elif current_step == WorkflowStep.CONTEXT:
        show_step_context()
    
    elif current_step == WorkflowStep.PLAN:
        show_step_plan()
    
    elif current_step == WorkflowStep.CONFIG:
        show_step_config()
    
    elif current_step == WorkflowStep.GENERATION:
        show_step_generation()