"""
Interface Streamlit pour configuration du rapport
Permet à l'utilisateur de choisir facilement le type de rapport

Auteur: AI Statistical Reporter Team
Version: 2.0
"""

import streamlit as st
from report_config import (
    ReportConfig,
    ReportMode,
    InterpretationLevel,
    VerbosityLevel,
    ChartStyle,
    create_config_for_audience,
    validate_config
)


def setup_report_configuration() -> ReportConfig:
    """
    Interface de configuration du rapport dans Streamlit
    
    Returns:
        ReportConfig configurée selon choix utilisateur
    """
    
    st.sidebar.header("🎯 Configuration du rapport")
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 1 : TYPE DE RAPPORT (CRITIQUE)
    # ═══════════════════════════════════════════════════════════
    
    st.sidebar.subheader("1️⃣ Type de rapport")
    
    report_type = st.sidebar.selectbox(
        "Quel type de rapport voulez-vous ?",
        options=[
            "🏛️ INS / Institutionnel",
            "📚 Académique (Recherche)",
            "💼 Business (Entreprise)",
            "🔍 Exploratoire"
        ],
        help="""
        • INS : Langage clair, chiffres clés, pas de jargon
        • Académique : Rigoureux, méthodologie, limites
        • Business : Direct, actionnable, recommandations
        • Exploratoire : Flexible, découverte de patterns
        """,
        index=0  # Par défaut : INS
    )
    
    # Map vers config
    type_map = {
        "🏛️ INS / Institutionnel": "ins",
        "📚 Académique (Recherche)": "academic",
        "💼 Business (Entreprise)": "business",
        "🔍 Exploratoire": "exploratory"
    }
    
    # Créer config de base
    config = create_config_for_audience(type_map[report_type])
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 2 : OPTIONS AVANCÉES (Optionnel)
    # ═══════════════════════════════════════════════════════════
    
    with st.sidebar.expander("⚙️ Options avancées (optionnel)"):
        
        st.markdown("**Niveau de détail**")
        verbosity = st.radio(
            "Longueur du rapport",
            options=["📄 Concis (5-10 pages)", "📋 Standard (15-25 pages)", "📚 Détaillé (30+ pages)"],
            index=1,
            horizontal=True
        )
        
        verbosity_map = {
            "📄 Concis (5-10 pages)": VerbosityLevel.CONCISE,
            "📋 Standard (15-25 pages)": VerbosityLevel.STANDARD,
            "📚 Détaillé (30+ pages)": VerbosityLevel.DETAILED
        }
        config.verbosity = verbosity_map[verbosity]
        
        st.markdown("---")
        st.markdown("**Sections à inclure**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            config.include_methodology = st.checkbox(
                "Méthodologie",
                value=config.include_methodology,
                help="Section méthodologique détaillée"
            )
            
            config.include_limitations = st.checkbox(
                "Limites",
                value=config.include_limitations,
                help="Discussion des limites méthodologiques"
            )
        
        with col2:
            config.include_recommendations = st.checkbox(
                "Recommandations",
                value=config.include_recommendations,
                help="Section avec recommandations concrètes"
            )
            
            config.include_executive_summary = st.checkbox(
                "Résumé exécutif",
                value=config.include_executive_summary,
                help="Résumé d'une page en tête"
            )
        
        st.markdown("---")
        st.markdown("**Visualisations**")
        
        config.charts_enabled = st.checkbox(
            "Générer des graphiques",
            value=True,
            help="Activer la génération automatique de graphiques"
        )
        
        if config.charts_enabled:
            chart_style = st.select_slider(
                "Style des graphiques",
                options=["Minimal", "Professionnel", "Académique"],
                value="Professionnel"
            )
            
            style_map = {
                "Minimal": ChartStyle.MINIMAL,
                "Professionnel": ChartStyle.PROFESSIONAL,
                "Académique": ChartStyle.ACADEMIC
            }
            config.chart_style = style_map[chart_style]
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 3 : VALIDATION ET RÉSUMÉ
    # ═══════════════════════════════════════════════════════════
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Résumé de la configuration")
    
    # Valider config
    warnings = validate_config(config)
    
    if warnings:
        for w in warnings:
            st.sidebar.warning(w)
    
    # Afficher résumé
    mode_icons = {
        ReportMode.INSTITUTIONAL: "🏛️",
        ReportMode.ACADEMIC: "📚",
        ReportMode.BUSINESS: "💼",
        ReportMode.EXPLORATORY: "🔍"
    }
    
    st.sidebar.success(f"""
**Configuration actuelle :**

{mode_icons.get(config.mode, '📊')} **Mode :** {config.mode.value}

**Détails :**
- Interprétation : {config.interpretation_level.value}
- Verbosité : {config.verbosity.value}
- Graphiques : {'✅' if config.charts_enabled else '❌'}
- Méthodologie : {'✅' if config.include_methodology else '❌'}
- Recommandations : {'✅' if config.include_recommendations else '❌'}
    """)
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 4 : AIDE ET EXEMPLES
    # ═══════════════════════════════════════════════════════════
    
    with st.sidebar.expander("❓ Aide - Quel mode choisir ?"):
        st.markdown("""
**🏛️ Mode INS / Institutionnel**

*Pour qui ?* Organismes publics, INS, ministères

*Caractéristiques :*
- Langage clair et accessible
- Chiffres clés en avant
- Pas de jargon technique
- Messages principaux nets

*Exemple :* Rapport démographique annuel

---

**📚 Mode Académique**

*Pour qui ?* Chercheurs, thèses, articles scientifiques

*Caractéristiques :*
- Rigoureusement scientifique
- Méthodologie détaillée
- Discussion des limites
- Références bibliographiques

*Exemple :* Mémoire de master, article de recherche

---

**💼 Mode Business**

*Pour qui ?* Entreprises, consultants, décideurs

*Caractéristiques :*
- Direct et actionnable
- Résumé exécutif
- Recommandations claires
- Focus ROI/Impact

*Exemple :* Étude de marché, rapport stratégique

---

**🔍 Mode Exploratoire**

*Pour qui ?* Analyse rapide, découverte de données

*Caractéristiques :*
- Flexible et itératif
- Identification de patterns
- Hypothèses marquées
- Questions pour suivi

*Exemple :* Premier examen d'un nouveau dataset
        """)
    
    return config


def display_config_summary(config: ReportConfig):
    """
    Affiche un résumé de la configuration dans le corps de la page
    
    Args:
        config: Configuration à afficher
    """
    
    st.info(f"""
    **📊 Rapport configuré en mode : {config.mode.value.upper()}**
    
    Le système générera un rapport adapté à un public **{config.target_audience}** 
    avec un niveau d'interprétation **{config.interpretation_level.value}**.
    """)


def get_config_from_session() -> ReportConfig:
    """
    Récupère ou crée la configuration depuis st.session_state
    
    Returns:
        ReportConfig active
    """
    
    if 'report_config' not in st.session_state:
        st.session_state.report_config = create_config_for_audience("ins")
    
    return st.session_state.report_config


# ═══════════════════════════════════════════════════════════
# EXEMPLE D'UTILISATION DANS APP STREAMLIT
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    
    st.set_page_config(
        page_title="AI Statistical Reporter - Config",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("🎯 Test de l'interface de configuration")
    
    # Sidebar avec config
    config = setup_report_configuration()
    
    # Corps de page
    st.header("Configuration active")
    
    display_config_summary(config)
    
    # Afficher détails techniques
    with st.expander("🔧 Détails techniques"):
        st.json({
            'mode': config.mode.value,
            'interpretation_level': config.interpretation_level.value,
            'verbosity': config.verbosity.value,
            'target_audience': config.target_audience,
            'include_methodology': config.include_methodology,
            'include_limitations': config.include_limitations,
            'include_recommendations': config.include_recommendations,
            'charts_enabled': config.charts_enabled,
            'chart_style': config.chart_style.value if config.charts_enabled else None
        })
    
    st.success("✅ Configuration prête à être utilisée dans le workflow !")