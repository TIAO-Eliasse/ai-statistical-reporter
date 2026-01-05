# ═══════════════════════════════════════════════════════════════════════
# PAGE : CONTEXTE DE L'ÉTUDE + GÉNÉRATION DU PLAN (CODE COMPLET)
# À INSÉRER EN REMPLACEMENT de "if page == 'Génération du plan':" (ligne ~1305)
# ═══════════════════════════════════════════════════════════════════════

if page == "📋 Contexte de l'étude":
    st.title("📋 Contexte de l'Étude")
    st.markdown("*Fournissez le contexte pour une analyse de qualité académique*")
    
    if st.session_state.csv_data is None:
        st.warning("⚠️ Veuillez d'abord uploader un fichier de données")
        st.stop()
    
    if not STUDY_CONTEXT_AVAILABLE:
        st.error("❌ Module study_context.py non disponible")
        st.info("Ajoutez le fichier `study_context.py` à votre projet")
        st.stop()
    
    st.info("""
💡 **Pourquoi c'est important ?**

Plus vous fournissez de contexte, meilleure sera l'analyse :
- ✅ Analyses ciblées sur vos objectifs
- ✅ Interprétations adaptées à votre problématique
- ✅ Rapport structuré selon vos besoins
- ✅ Recommandations pertinentes

Remplissez au minimum la **Question de recherche** et les **Objectifs**.
    """)
    
    # Initialiser le contexte si nécessaire
    if st.session_state.study_context is None:
        st.session_state.study_context = StudyContext()
    
    ctx = st.session_state.study_context
    
    # ═══ SECTION 1 : INFORMATIONS GÉNÉRALES ═══
    st.markdown("## 📋 Informations Générales")
    
    with st.expander("ℹ️ Informations de base", expanded=True):
        ctx.study_title = st.text_input(
            "📌 Titre de l'étude",
            value=ctx.study_title,
            placeholder="Ex: Analyse de la satisfaction client 2024",
            help="Titre descriptif de votre étude"
        )
        
        ctx.study_description = st.text_area(
            "📝 Description de l'étude",
            value=ctx.study_description,
            height=100,
            placeholder="Décrivez brièvement votre étude, son contexte, et ce que vous cherchez à comprendre...",
            help="Description générale du contexte et des enjeux"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            domains = ["", "Santé", "RH", "Marketing", "Finance", "Éducation", "Sciences Sociales", "Technologie", "Environnement", "Autre"]
            ctx.study_domain = st.selectbox(
                "🏷️ Domaine d'étude",
                options=domains,
                index=domains.index(ctx.study_domain) if ctx.study_domain in domains else 0,
                help="Domaine principal de votre étude"
            )
        
        with col2:
            study_types = ["", "Exploratoire", "Descriptive", "Explicative", "Prédictive"]
            ctx.study_type = st.selectbox(
                "🔍 Type d'étude",
                options=study_types,
                index=study_types.index(ctx.study_type) if ctx.study_type in study_types else 0,
                help="Nature de votre recherche"
            )
    
    # ═══ SECTION 2 : PROBLÉMATIQUE ET OBJECTIFS ═══
    st.markdown("## ❓ Problématique et Objectifs")
    
    with st.expander("🎯 Question de recherche et hypothèses", expanded=True):
        ctx.research_question = st.text_area(
            "❓ Question de recherche principale ⭐ (Important)",
            value=ctx.research_question,
            height=100,
            placeholder="Ex: Quel est l'impact de l'âge sur le salaire dans le secteur tech ?",
            help="La question centrale que vous cherchez à répondre"
        )
        
        st.markdown("**🔬 Hypothèses à tester** *(une par ligne)*")
        hypotheses_text = st.text_area(
            "Hypothèses",
            value="\n".join(ctx.hypotheses) if ctx.hypotheses else "",
            height=100,
            placeholder="H1: Plus l'âge augmente, plus le salaire augmente\nH2: Cette relation est modérée par l'expérience",
            label_visibility="collapsed",
            help="Vos hypothèses de recherche, une par ligne"
        )
        ctx.hypotheses = [h.strip() for h in hypotheses_text.split('\n') if h.strip()]
        
        st.markdown("**🎯 Objectifs de l'étude** *(un par ligne)* ⭐ (Important)")
        objectives_text = st.text_area(
            "Objectifs",
            value="\n".join(ctx.objectives) if ctx.objectives else "",
            height=100,
            placeholder="1. Analyser la corrélation âge-salaire\n2. Identifier les facteurs confondants\n3. Proposer des recommandations",
            label_visibility="collapsed",
            help="Vos objectifs spécifiques, un par ligne"
        )
        ctx.objectives = [o.strip() for o in objectives_text.split('\n') if o.strip()]
    
    # ═══ SECTION 3 : MÉTHODOLOGIE ═══
    st.markdown("## 🔬 Méthodologie")
    
    with st.expander("📊 Collecte et échantillonnage", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            ctx.data_collection_method = st.text_input(
                "📋 Méthode de collecte",
                value=ctx.data_collection_method,
                placeholder="Ex: Enquête en ligne, Observation...",
                help="Comment les données ont été collectées"
            )
            
            ctx.sampling_method = st.text_input(
                "🎲 Méthode d'échantillonnage",
                value=ctx.sampling_method,
                placeholder="Ex: Aléatoire simple, Stratifié...",
                help="Méthode utilisée pour sélectionner l'échantillon"
            )
        
        with col2:
            ctx.data_source = st.text_input(
                "📁 Source des données",
                value=ctx.data_source,
                placeholder="Ex: Base RH interne, API publique...",
                help="Origine des données"
            )
            
            ctx.data_collection_period = st.text_input(
                "📅 Période de collecte",
                value=ctx.data_collection_period,
                placeholder="Ex: Janvier-Mars 2024",
                help="Période durant laquelle les données ont été collectées"
            )
        
        ctx.population_description = st.text_area(
            "👥 Description de la population étudiée",
            value=ctx.population_description,
            height=80,
            placeholder="Ex: Employés du secteur tech à Paris, âgés de 25 à 55 ans...",
            help="Caractéristiques de la population cible"
        )
        
        sample_size_input = st.number_input(
            "📊 Taille de l'échantillon",
            value=ctx.sample_size if ctx.sample_size else 0,
            min_value=0,
            help="Nombre d'observations dans votre échantillon"
        )
        ctx.sample_size = sample_size_input if sample_size_input > 0 else None
    
    # ═══ SECTION 4 : STRUCTURE DES DONNÉES ═══
    st.markdown("## 🗂️ Structure des Données")
    
    with st.expander("📊 Variables et structure", expanded=True):
        ctx.data_structure_description = st.text_area(
            "🗂️ Description de la structure des données",
            value=ctx.data_structure_description,
            height=100,
            placeholder="Ex: Chaque ligne = un employé. Les colonnes contiennent : informations démographiques, salaire annuel, ancienneté...",
            help="Expliquez comment vos données sont organisées"
        )
        
        # Afficher les colonnes disponibles
        df = st.session_state.csv_data
        st.markdown(f"**Colonnes disponibles** ({len(df.columns)} colonnes) :")
        cols_display = ", ".join([f"`{col}`" for col in df.columns])
        st.caption(cols_display)
        
        col1, col2 = st.columns(2)
        
        with col1:
            dep_var_options = [""] + list(df.columns)
            dep_var_index = 0
            if ctx.dependent_variable and ctx.dependent_variable in df.columns:
                dep_var_index = dep_var_options.index(ctx.dependent_variable)
            
            selected_dep_var = st.selectbox(
                "🎯 Variable dépendante (Y)",
                options=dep_var_options,
                index=dep_var_index,
                help="La variable que vous cherchez à expliquer/prédire"
            )
            ctx.dependent_variable = selected_dep_var if selected_dep_var else None
        
        with col2:
            independent_vars = st.multiselect(
                "📈 Variables indépendantes (X)",
                options=list(df.columns),
                default=ctx.independent_variables if ctx.independent_variables else [],
                help="Les variables explicatives"
            )
            ctx.independent_variables = independent_vars
        
        variables_of_interest = st.multiselect(
            "🔑 Variables d'intérêt principal",
            options=list(df.columns),
            default=ctx.variables_of_interest if ctx.variables_of_interest else [],
            help="Les variables les plus importantes pour votre analyse"
        )
        ctx.variables_of_interest = variables_of_interest
    
    # ═══ SECTION 5 : ATTENTES ═══
    st.markdown("## 🎯 Attentes et Analyses Souhaitées")
    
    with st.expander("💭 Résultats attendus et analyses", expanded=False):
        ctx.expected_findings = st.text_area(
            "💭 Résultats attendus",
            value=ctx.expected_findings,
            height=80,
            placeholder="Ex: On s'attend à trouver une corrélation positive entre âge et salaire...",
            help="Ce que vous vous attendez à découvrir"
        )
        
        st.markdown("**📊 Analyses spécifiques requises** *(une par ligne)*")
        analyses_text = st.text_area(
            "Analyses",
            value="\n".join(ctx.key_analyses_needed) if ctx.key_analyses_needed else "",
            height=100,
            placeholder="Ex: Test t de Student\nRégression linéaire multiple\nANOVA",
            label_visibility="collapsed",
            help="Tests statistiques ou analyses particulières à réaliser"
        )
        ctx.key_analyses_needed = [a.strip() for a in analyses_text.split('\n') if a.strip()]
        
        col1, col2 = st.columns(2)
        
        with col1:
            reporting_styles = ["academic", "business", "technical", "general"]
            ctx.reporting_style = st.selectbox(
                "📖 Style de rapport",
                options=reporting_styles,
                index=reporting_styles.index(ctx.reporting_style) if ctx.reporting_style in reporting_styles else 0,
                help="Ton et style du rapport généré"
            )
        
        with col2:
            ctx.target_audience = st.text_input(
                "👥 Public cible",
                value=ctx.target_audience,
                placeholder="Ex: Comité de direction, Chercheurs...",
                help="Pour qui est destiné ce rapport"
            )
    
    # ═══ BOUTONS D'ACTION ═══
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Sauvegarder le contexte", type="primary", use_container_width=True):
            st.session_state.study_context = ctx
            
            # Sauvegarder en fichier JSON
            from pathlib import Path
            context_path = Path("temp") / "study_context.json"
            context_path.parent.mkdir(exist_ok=True)
            ctx.to_json(str(context_path))
            
            st.success("✅ Contexte sauvegardé !")
            
            if LOGGING_AVAILABLE:
                log_user_action('study_context_saved', {
                    'has_research_question': bool(ctx.research_question),
                    'num_hypotheses': len(ctx.hypotheses),
                    'num_objectives': len(ctx.objectives)
                })
    
    with col2:
        if st.button("👁️ Prévisualiser", use_container_width=True):
            st.session_state['show_context_preview'] = True
    
    with col3:
        if st.button("🔄 Réinitialiser", use_container_width=True):
            st.session_state.study_context = StudyContext()
            st.rerun()
    
    # Prévisualisation du contexte
    if st.session_state.get('show_context_preview'):
        with st.expander("📋 Contexte formaté pour l'IA", expanded=True):
            st.code(ctx.to_prompt_context(), language="text")
            if st.button("✖️ Fermer", key="close_preview"):
                st.session_state['show_context_preview'] = False
                st.rerun()
    
    # Résumé du contexte
    if ctx.study_title or ctx.research_question:
        st.markdown("---")
        st.markdown("### 📊 Résumé du contexte")
        st.info(ctx.get_summary())
        
        # Indicateur de complétude
        completeness = 0
        if ctx.study_title: completeness += 15
        if ctx.research_question: completeness += 25
        if ctx.objectives: completeness += 20
        if ctx.hypotheses: completeness += 15
        if ctx.dependent_variable: completeness += 10
        if ctx.independent_variables: completeness += 10
        if ctx.population_description: completeness += 5
        
        st.progress(completeness / 100)
        st.caption(f"Complétude du contexte : {completeness}%")
        
        if completeness >= 60:
            st.success("✅ Contexte suffisant pour une bonne analyse !")
        elif completeness >= 30:
            st.info("ℹ️ Contexte minimal. Ajoutez plus de détails pour améliorer la qualité.")
        else:
            st.warning("⚠️ Contexte incomplet. Remplissez au moins la question de recherche et les objectifs.")


# ═══════════════════════════════════════════════════════════════════════
# PAGE : GÉNÉRATION DU PLAN (CODE EXISTANT - NE PAS MODIFIER)
# ═══════════════════════════════════════════════════════════════════════

elif page == "📝 Génération du plan" or page == "Génération du plan":
    # TOUT LE CODE EXISTANT DE LA PAGE "GÉNÉRATION DU PLAN" CONTINUE ICI
    # Ne modifiez rien dans cette section, c'est déjà dans votre fichier
    st.title("Génération du Plan de Rapport")
    
    if st.session_state.csv_data is None:
        st.info("Commencez par uploader un fichier CSV dans la barre latérale")
    
    # ... (tout le reste du code existant continue normalement)