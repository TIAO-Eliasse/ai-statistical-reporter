"""
Système de traduction pour AI Statistical Reporter
Support : Français et Anglais
"""

TRANSLATIONS = {
    # ===== INTERFACE PRINCIPALE =====
    'app_title': {
        'fr': '📊 AI Statistical Reporter',
        'en': '📊 AI Statistical Reporter'
    },
    'select_language': {
        'fr': '🌍 Langue / Language',
        'en': '🌍 Language / Langue'
    },
    
    # ===== BIENVENUE =====
    'welcome_title': {
        'fr': '👋 Bienvenue sur AI Statistical Reporter !',
        'en': '👋 Welcome to AI Statistical Reporter!'
    },
    'quick_guide': {
        'fr': 'Guide rapide :',
        'en': 'Quick guide:'
    },
    'step1': {
        'fr': 'Uploadez votre fichier CSV',
        'en': 'Upload your CSV file'
    },
    'step2': {
        'fr': 'Cliquez sur "Générer le plan"',
        'en': 'Click on "Generate outline"'
    },
    'step3': {
        'fr': 'Modifiez le plan si nécessaire',
        'en': 'Modify the outline if needed'
    },
    'step4': {
        'fr': 'Exportez au format de votre choix',
        'en': 'Export in your preferred format'
    },
    'help_text': {
        'fr': "Besoin d'aide ? Consultez la documentation ou contactez le support.",
        'en': "Need help? Check the documentation or contact support."
    },
    
    # ===== ÉTAPE 1 : UPLOAD =====
    'step1_title': {
        'fr': '📂 Étape 1 : Upload du fichier',
        'en': '📂 Step 1: File Upload'
    },
    'upload_csv': {
        'fr': '📂 Uploadez votre fichier CSV',
        'en': '📂 Upload your CSV file'
    },
    'file_uploaded': {
        'fr': '✅ Fichier chargé avec succès',
        'en': '✅ File loaded successfully'
    },
    'preview_title': {
        'fr': '👁️ Aperçu des données',
        'en': '👁️ Data Preview'
    },
    'rows': {
        'fr': 'lignes',
        'en': 'rows'
    },
    'columns': {
        'fr': 'colonnes',
        'en': 'columns'
    },
    
    # ===== ÉTAPE 2 : PLAN =====
    'step2_title': {
        'fr': '📋 Étape 2 : Génération du plan',
        'en': '📋 Step 2: Outline Generation'
    },
    'preferences_title': {
        'fr': '⚙️ Préférences du rapport',
        'en': '⚙️ Report Preferences'
    },
    'report_focus': {
        'fr': 'Focus du rapport :',
        'en': 'Report focus:'
    },
    'focus_descriptive': {
        'fr': '📊 Analyse descriptive (statistiques, distributions)',
        'en': '📊 Descriptive analysis (statistics, distributions)'
    },
    'focus_inferential': {
        'fr': '🔬 Analyse inférentielle (tests, corrélations)',
        'en': '🔬 Inferential analysis (tests, correlations)'
    },
    'focus_predictive': {
        'fr': '🎯 Analyse prédictive (modèles, prévisions)',
        'en': '🎯 Predictive analysis (models, forecasts)'
    },
    'detail_level': {
        'fr': 'Niveau de détail :',
        'en': 'Detail level:'
    },
    'detail_concise': {
        'fr': 'Concis (5 chapitres)',
        'en': 'Concise (5 chapters)'
    },
    'detail_detailed': {
        'fr': 'Détaillé (7-8 chapitres)',
        'en': 'Detailed (7-8 chapters)'
    },
    'detail_comprehensive': {
        'fr': 'Exhaustif (10+ chapitres)',
        'en': 'Comprehensive (10+ chapters)'
    },
    'target_audience': {
        'fr': 'Public cible :',
        'en': 'Target audience:'
    },
    'audience_general': {
        'fr': 'Grand public',
        'en': 'General public'
    },
    'audience_technical': {
        'fr': 'Public technique',
        'en': 'Technical audience'
    },
    'audience_academic': {
        'fr': 'Public académique',
        'en': 'Academic audience'
    },
    'generate_plan': {
        'fr': '🎯 Générer le plan',
        'en': '🎯 Generate outline'
    },
    'generating_plan': {
        'fr': 'Génération du plan en cours...',
        'en': 'Generating outline...'
    },
    'plan_generated': {
        'fr': '✅ Plan généré avec succès !',
        'en': '✅ Outline generated successfully!'
    },
    'edit_plan': {
        'fr': '✏️ Modifier le plan (YAML)',
        'en': '✏️ Edit outline (YAML)'
    },
    'save_plan': {
        'fr': '💾 Sauvegarder les modifications',
        'en': '💾 Save changes'
    },
    'plan_saved': {
        'fr': '✅ Plan sauvegardé !',
        'en': '✅ Outline saved!'
    },
    'validate_plan': {
        'fr': '✅ Valider le plan',
        'en': '✅ Validate outline'
    },
    'download_plan': {
        'fr': '📥 Télécharger le plan',
        'en': '📥 Download outline'
    },
    
    # ===== ÉTAPE 3 : GÉNÉRATION =====
    'step3_title': {
        'fr': '📝 Étape 3 : Génération du rapport',
        'en': '📝 Step 3: Report Generation'
    },
    'progress_title': {
        'fr': '📊 Progression',
        'en': '📊 Progress'
    },
    'progression': {
        'fr': 'Progression :',
        'en': 'Progress:'
    },
    'chapters_validated': {
        'fr': 'chapitres validés',
        'en': 'chapters validated'
    },
    'validated': {
        'fr': 'Validé',
        'en': 'Validated'
    },
    'generated': {
        'fr': 'Généré (en attente validation)',
        'en': 'Generated (awaiting validation)'
    },
    'pending': {
        'fr': 'En attente',
        'en': 'Pending'
    },
    'intermediate_save': {
        'fr': '💾 Sauvegarde intermédiaire',
        'en': '💾 Intermediate Save'
    },
    'intermediate_save_info': {
        'fr': '💡 Vous avez {count} chapitre(s) validé(s). Vous pouvez les télécharger dès maintenant.',
        'en': '💡 You have {count} validated chapter(s). You can download them now.'
    },
    'download_validated': {
        'fr': '📥 Télécharger les chapitres validés',
        'en': '📥 Download validated chapters'
    },
    'chapter': {
        'fr': 'Chapitre',
        'en': 'Chapter'
    },
    'generate_chapter': {
        'fr': '▶️ Générer ce chapitre',
        'en': '▶️ Generate this chapter'
    },
    'generating_chapter': {
        'fr': 'Génération du chapitre en cours...',
        'en': 'Generating chapter...'
    },
    'generated_content': {
        'fr': '📄 Contenu généré',
        'en': '📄 Generated Content'
    },
    'edit_content': {
        'fr': '✏️ Modifier le contenu',
        'en': '✏️ Edit content'
    },
    'preview': {
        'fr': 'Aperçu :',
        'en': 'Preview:'
    },
    'validate_chapter': {
        'fr': '✅ Valider ce chapitre',
        'en': '✅ Validate this chapter'
    },
    'regenerate_chapter': {
        'fr': '🔄 Regénérer',
        'en': '🔄 Regenerate'
    },
    'all_chapters_done': {
        'fr': '🎉 Tous les chapitres ont été générés et validés !',
        'en': '🎉 All chapters have been generated and validated!'
    },
    'compile_report': {
        'fr': '📄 Compiler le rapport final',
        'en': '📄 Compile final report'
    },
    'compiling': {
        'fr': 'Compilation en cours...',
        'en': 'Compiling...'
    },
    'compiled_success': {
        'fr': '✅ Rapport compilé avec succès !',
        'en': '✅ Report compiled successfully!'
    },
    'final_report_preview': {
        'fr': '📄 Aperçu du rapport final',
        'en': '📄 Final Report Preview'
    },
    'download_report': {
        'fr': '📥 Télécharger le rapport',
        'en': '📥 Download report'
    },
    
    # ===== FORMATS D'EXPORT =====
    'markdown': {
        'fr': 'Markdown',
        'en': 'Markdown'
    },
    'html': {
        'fr': 'HTML',
        'en': 'HTML'
    },
    'word': {
        'fr': 'Word',
        'en': 'Word'
    },
    'pdf': {
        'fr': 'PDF',
        'en': 'PDF'
    },
    'pdf_at_end': {
        'fr': 'PDF au final',
        'en': 'PDF at end'
    },
    
    # ===== ERREURS =====
    'error': {
        'fr': 'Erreur',
        'en': 'Error'
    },
    'warning': {
        'fr': 'Avertissement',
        'en': 'Warning'
    },
    'error_file_read': {
        'fr': '❌ Erreur lors de la lecture du fichier',
        'en': '❌ Error reading file'
    },
    'error_plan_generation': {
        'fr': '❌ Erreur lors de la génération du plan',
        'en': '❌ Error generating outline'
    },
    'error_chapter_generation': {
        'fr': '❌ Erreur lors de la génération du chapitre',
        'en': '❌ Error generating chapter'
    },
    'error_code_execution': {
        'fr': '⚠️ Erreur lors de l\'exécution du code Python :',
        'en': '⚠️ Error executing Python code:'
    },
    'html_unavailable': {
        'fr': 'HTML indisponible',
        'en': 'HTML unavailable'
    },
    'word_unavailable': {
        'fr': 'Word indisponible',
        'en': 'Word unavailable'
    },
    'pdf_unavailable': {
        'fr': 'PDF non disponible',
        'en': 'PDF unavailable'
    },
    'e2b_unavailable': {
        'fr': '⚠️ e2b_session_manager.py non disponible',
        'en': '⚠️ e2b_session_manager.py unavailable'
    },
    
    # ===== SESSION E2B =====
    'e2b_session': {
        'fr': '🖥️ Session E2B',
        'en': '🖥️ E2B Session'
    },
    'sandbox_id': {
        'fr': 'Sandbox ID',
        'en': 'Sandbox ID'
    },
    'created': {
        'fr': 'Créée',
        'en': 'Created'
    },
    'last_used': {
        'fr': 'Dernière utilisation',
        'en': 'Last used'
    },
    'inactivity': {
        'fr': 'Inactivité',
        'en': 'Inactivity'
    },
    'session_expiring': {
        'fr': '⚠️ Session proche de l\'expiration',
        'en': '⚠️ Session about to expire'
    },
}


def get_text(key: str, lang: str = 'fr', **kwargs) -> str:
    """
    Récupère un texte traduit
    
    Args:
        key: Clé du texte à traduire
        lang: Code langue ('fr' ou 'en')
        **kwargs: Variables à injecter dans le texte (format)
    
    Returns:
        Texte traduit
    
    Example:
        >>> get_text('intermediate_save_info', 'en', count=5)
        '💡 You have 5 validated chapter(s). You can download them now.'
    """
    if key not in TRANSLATIONS:
        return f"[MISSING: {key}]"
    
    if lang not in TRANSLATIONS[key]:
        lang = 'fr'  # Fallback
    
    text = TRANSLATIONS[key][lang]
    
    # Remplacer les variables
    if kwargs:
        text = text.format(**kwargs)
    
    return text


def get_language_name(lang_code: str) -> str:
    """Retourne le nom complet de la langue"""
    names = {
        'fr': 'Français 🇫🇷',
        'en': 'English 🇬🇧'
    }
    return names.get(lang_code, 'Français 🇫🇷')


# Alias pour faciliter l'usage
t = get_text