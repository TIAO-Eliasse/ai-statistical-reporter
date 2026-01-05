"""
Composants UI personnalisés pour AI Statistical Reporter
Améliore l'expérience utilisateur avec des feedbacks clairs
"""

import streamlit as st
from typing import List, Dict
import time


def show_progress_steps(steps: List[str], current_step: int):
    """
    Affiche une barre de progression avec étapes
    
    Args:
        steps: Liste des étapes
        current_step: Index de l'étape actuelle (0-based)
    
    Example:
        show_progress_steps(
            ['Upload CSV', 'Analyse données', 'Génération plan', 'Validation'],
            current_step=1
        )
    """
    progress = (current_step + 1) / len(steps)
    
    st.progress(progress, text=f"Étape {current_step + 1}/{len(steps)}: {steps[current_step]}")
    
    # Afficher toutes les étapes avec statut
    cols = st.columns(len(steps))
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if i < current_step:
                st.markdown(f"✅ ~~{step}~~")
            elif i == current_step:
                st.markdown(f"**▶️ {step}**")
            else:
                st.markdown(f"⏳ {step}")


def show_loading_animation(message: str, duration: int = 30):
    """
    Affiche une animation de chargement avec estimation
    
    Args:
        message: Message à afficher
        duration: Durée estimée en secondes
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    start_time = time.time()
    
    while time.time() - start_time < duration:
        elapsed = time.time() - start_time
        progress = min(elapsed / duration, 0.99)
        
        progress_bar.progress(progress)
        
        remaining = int(duration - elapsed)
        status_text.text(f"{message} ({remaining}s restantes)")
        
        time.sleep(0.5)
    
    progress_bar.progress(1.0)
    status_text.text(f"{message} - Terminé !")


def show_success_message(title: str, details: List[str] = None):
    """Affiche un message de succès stylisé"""
    st.success(f"**{title}**")
    
    if details:
        with st.expander("Voir les détails"):
            for detail in details:
                st.markdown(f"- {detail}")


def show_warning_box(title: str, message: str, actions: List[Dict] = None):
    """
    Affiche un avertissement avec actions possibles
    
    Example:
        show_warning_box(
            "Attention",
            "Votre fichier contient des valeurs manquantes",
            actions=[
                {'label': 'Voir les détails', 'callback': show_details},
                {'label': 'Continuer quand même', 'callback': continue_anyway}
            ]
        )
    """
    st.warning(f"**{title}**\n\n{message}")
    
    if actions:
        cols = st.columns(len(actions))
        for col, action in zip(cols, actions):
            with col:
                if st.button(action['label'], use_container_width=True):
                    action['callback']()


def show_info_tooltip(text: str, tooltip: str):
    """
    Affiche un texte avec tooltip informatif
    
    Example:
        show_info_tooltip("Génération du plan", "Analyse vos données et crée une structure")
    """
    st.markdown(f"{text} ℹ️")
    st.caption(tooltip)


def show_metric_card(title: str, value: str, delta: str = None, help_text: str = None):
    """
    Affiche une métrique stylisée
    
    Example:
        show_metric_card("Plans générés", "127", "+23 cette semaine")
    """
    st.metric(
        label=title,
        value=value,
        delta=delta,
        help=help_text
    )


def show_file_upload_zone(
    accepted_types: List[str] = None,
    max_size_mb: int = 200,
    help_text: str = None
):
    """
    Zone d'upload stylisée avec instructions claires
    
    Returns:
        uploaded_file or None
    """
    st.markdown("""
    <div style='border: 2px dashed #ccc; padding: 20px; border-radius: 10px; text-align: center;'>
        <p style='font-size: 1.2em; color: #666;'>
            📁 Glissez-déposez votre fichier CSV ici
        </p>
        <p style='color: #999;'>ou cliquez pour parcourir</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choisir un fichier",
        type=accepted_types or ['csv'],
        help=help_text,
        label_visibility="collapsed"
    )
    
    if accepted_types:
        st.caption(f"Formats acceptés : {', '.join(accepted_types)} (Max {max_size_mb}MB)")
    
    return uploaded_file


def show_action_buttons(
    actions: List[Dict],
    layout: str = 'horizontal'
):
    """
    Affiche des boutons d'action stylisés
    
    Args:
        actions: Liste de dicts avec 'label', 'callback', 'type' (primary/secondary)
        layout: 'horizontal' ou 'vertical'
    
    Example:
        show_action_buttons([
            {'label': 'Générer', 'callback': generate, 'type': 'primary'},
            {'label': 'Annuler', 'callback': cancel, 'type': 'secondary'}
        ])
    """
    if layout == 'horizontal':
        cols = st.columns(len(actions))
        containers = cols
    else:
        containers = [st.container() for _ in actions]
    
    for container, action in zip(containers, actions):
        with container:
            button_type = action.get('type', 'secondary')
            
            if st.button(
                action['label'],
                type=button_type,
                use_container_width=True,
                disabled=action.get('disabled', False)
            ):
                action['callback']()


def show_stat_comparison(
    title: str,
    current: float,
    previous: float,
    format_str: str = "{:.1f}"
):
    """
    Affiche une comparaison de statistique avec évolution
    
    Example:
        show_stat_comparison("Temps de génération", 45.2, 52.1, "{:.1f}s")
    """
    delta = current - previous
    delta_pct = (delta / previous * 100) if previous != 0 else 0
    
    st.metric(
        label=title,
        value=format_str.format(current),
        delta=f"{delta_pct:+.1f}%"
    )


def show_timeline(events: List[Dict]):
    """
    Affiche une timeline d'événements
    
    Example:
        show_timeline([
            {'time': '10:30', 'event': 'Upload CSV', 'status': 'completed'},
            {'time': '10:31', 'event': 'Génération plan', 'status': 'completed'},
            {'time': '10:35', 'event': 'Export PDF', 'status': 'in_progress'}
        ])
    """
    for event in events:
        status_icon = {
            'completed': '✅',
            'in_progress': '▶️',
            'pending': '⏳',
            'failed': '❌'
        }.get(event['status'], '•')
        
        st.markdown(f"{status_icon} **{event['time']}** - {event['event']}")


def show_keyboard_shortcuts():
    """Affiche les raccourcis clavier disponibles"""
    with st.expander("⌨️ Raccourcis clavier"):
        st.markdown("""
        | Raccourci | Action |
        |-----------|--------|
        | `Ctrl + Enter` | Appliquer les modifications |
        | `Ctrl + S` | Sauvegarder le plan |
        | `Ctrl + Z` | Annuler |
        | `Ctrl + /` | Afficher l'aide |
        | `Escape` | Fermer les modales |
        """)


def show_onboarding_tour():
    """Affiche un tutoriel pour nouveaux utilisateurs"""
    if 'seen_tour' not in st.session_state:
        st.info("""
        **👋 Bienvenue sur AI Statistical Reporter !**
        
        **Guide rapide :**
        1. Uploadez votre fichier CSV
        2. Cliquez sur "Générer le plan"
        3. Modifiez le plan si nécessaire
        4. Exportez au format de votre choix
        
        **Besoin d'aide ?** Consultez la documentation ou contactez le support.
        """)
        
        if st.button("C'est compris, ne plus afficher"):
            st.session_state.seen_tour = True
            st.rerun()