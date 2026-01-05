"""
Writing Profiles - Blocs de style de rédaction
Définit les contraintes de style selon le profil du public cible
"""

from study_context import WritingProfile


def get_writing_style_block(profile: WritingProfile) -> str:
    """
    Retourne le bloc de style d'écriture à injecter dans le prompt
    
    Args:
        profile: Profil de rédaction (ACADEMIC, CONSULTANT, INSTITUTIONAL)
    
    Returns:
        Bloc de texte formaté pour le prompt
    """
    
    blocks = {
        WritingProfile.ACADEMIC: get_academic_block(),
        WritingProfile.CONSULTANT: get_consultant_block(),
        WritingProfile.INSTITUTIONAL: get_institutional_block()
    }
    
    return blocks.get(profile, get_academic_block())


def get_academic_block() -> str:
    """Bloc de style académique (référence)"""
    return """
╔══════════════════════════════════════════════════════════════════════════════╗
║ 🎓 PROFIL DE RÉDACTION : ACADÉMIQUE                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 OBJECTIF : Expliquer, analyser, interpréter en profondeur

📝 STYLE D'ÉCRITURE :
- Ton académique et analytique
- Emphase sur l'interprétation et la rigueur méthodologique
- Mise en évidence des patterns, hétérogénéités et limites
- Phrases de 15-25 mots
- Connecteurs logiques (cependant, néanmoins, par ailleurs)
- Éviter les recommandations managériales directes

📊 ANALYSES ATTENDUES :
- Statistiques descriptives détaillées
- Corrélations et relations bivariées
- Comparaisons fines entre groupes
- Vérification systématique des variables encodées
- Discussion des limites et biais potentiels

🔍 INTERPRÉTATION :
- 3-4 phrases par élément visuel
- Explication des mécanismes sous-jacents
- Références implicites à la littérature
- Nuances et mises en garde

✅ EXEMPLE BON STYLE :
"L'analyse révèle une forte concentration dans la région du LITTORAL (37%), 
qui reflète vraisemblablement le dynamisme économique côtier avec Douala comme 
hub commercial. Cette prédominance contraste avec les régions septentrionales 
qui affichent des effectifs nettement plus faibles, suggérant des disparités 
régionales marquées nécessitant une investigation approfondie."

❌ À ÉVITER :
- "Il faut investir dans le LITTORAL" (trop prescriptif)
- "Le LITTORAL est le meilleur" (jugement de valeur)
- "37% = région dominante" (trop succinct)
"""


def get_consultant_block() -> str:
    """Bloc de style consultant (orienté décision)"""
    return """
╔══════════════════════════════════════════════════════════════════════════════╗
║ 💼 PROFIL DE RÉDACTION : CONSULTANT (ORIENTÉ DÉCISION)                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 OBJECTIF : Produire des insights actionnables pour la prise de décision

📝 STYLE D'ÉCRITURE :
- Clair, direct et orienté action
- Phrases plus courtes (12-18 mots)
- Verbes d'action (identifier, prioriser, cibler)
- Messages clés en début de section
- Éviter les justifications théoriques longues
- Hiérarchiser l'information (Top/Bottom, Dominant/Marginal)

📊 ANALYSES ATTENDUES :
- Classements (Top 5, Bottom 3)
- Écarts significatifs vs moyennes
- Segmentation claire
- Comparaisons simples
- Focus sur les effets dominants
- Réduire les corrélations non actionnables

🔍 INTERPRÉTATION :
- 2-3 phrases concises
- **OBLIGATOIRE** : Terminer chaque section par un "💡 KEY INSIGHT"
- Priorisation claire (important vs secondaire)
- Implications pratiques

💡 FORMAT KEY INSIGHT (OBLIGATOIRE) :
Après chaque analyse, ajouter :

**💡 KEY INSIGHT :** [1 phrase résumant ce qu'un décideur doit retenir]

✅ EXEMPLE BON STYLE :
"Le LITTORAL concentre 37% des entreprises, suivi du CENTRE (26%). 
Ces deux régions représentent 63% de l'échantillon total. Les régions 
septentrionales restent marginales (< 5% chacune).

**💡 KEY INSIGHT :** Toute stratégie d'intervention doit prioritairement 
cibler le duo LITTORAL-CENTRE pour maximiser l'impact."

❌ À ÉVITER :
- Discussions méthodologiques longues
- "Cela nécessite une investigation approfondie" (pas actionnable)
- Corrélations faibles non significatives
- Analyses sans implication claire
"""


def get_institutional_block() -> str:
    """Bloc de style institutionnel (formel et justificatif)"""
    return """
╔══════════════════════════════════════════════════════════════════════════════╗
║ 🏛️ PROFIL DE RÉDACTION : INSTITUTIONNEL (FORMEL & TRANSPARENT)             ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 OBJECTIF : Documenter, rendre compte, justifier de manière transparente

📝 STYLE D'ÉCRITURE :
- Formel et neutre
- Impersonnel ("On observe", "Les données révèlent")
- Phrases longues mais simples (éviter subordination complexe)
- Vocabulaire accessible (éviter jargon statistique)
- Emphase sur la transparence et la traçabilité
- AUCUNE recommandation directe

📊 ANALYSES ATTENDUES :
- Distributions simples et claires
- Évolutions globales (pas de détails micro)
- Indicateurs clés agrégés
- Éviter corrélations complexes
- Focus sur la conformité et l'exhaustivité
- Tableaux plutôt que graphiques complexes

🔍 INTERPRÉTATION :
- 2-3 phrases factuelles
- Structure : Constat → Chiffres clés → Lecture neutre
- Pas de spéculation
- Pas de recommandation
- Transparence méthodologique

📊 STRUCTURE RECOMMANDÉE PAR SECTION :
1. **Constat factuel** : "Les données révèlent que..."
2. **Chiffres clés** : "X% des entreprises..."
3. **Lecture neutre** : "Cette répartition reflète..."

✅ EXEMPLE BON STYLE :
"Les données révèlent que la région du LITTORAL regroupe 3 869 entreprises, 
soit 37% de l'échantillon total. La région du CENTRE suit avec 2 704 unités 
(26%). Les huit autres régions représentent collectivement 37% de l'échantillon. 
Cette répartition géographique constitue une caractéristique fondamentale de 
la structure de l'échantillon étudié."

❌ À ÉVITER :
- "Il faut..." (prescriptif)
- Termes techniques (hétéroscédasticité, kurtosis)
- "Cela suggère qu'il serait judicieux de..." (recommandation)
- Graphiques complexes (heatmaps, scatter 3D)
- Interprétations subjectives

🔍 VOCABULAIRE PRÉFÉRÉ :
✅ Utiliser : répartition, distribution, proportion, effectif
❌ Éviter : corrélation, significativité, hétérogénéité, outliers
"""


def get_profile_summary() -> dict:
    """Résumé des 3 profils pour aide utilisateur"""
    return {
        WritingProfile.ACADEMIC: {
            'emoji': '🎓',
            'name': 'Académique',
            'phrase_cle': 'Comprendre et expliquer les mécanismes',
            'public': 'Chercheurs, universitaires, analystes',
            'caracteristiques': [
                'Rigueur méthodologique',
                'Interprétations approfondies',
                'Discussions des limites',
                'Ton scientifique'
            ]
        },
        WritingProfile.CONSULTANT: {
            'emoji': '💼',
            'name': 'Consultant',
            'phrase_cle': 'Identifier ce qui compte et agir',
            'public': 'Décideurs, managers, comités de direction',
            'caracteristiques': [
                'Insights actionnables',
                'Messages clés',
                'Priorisation claire',
                'Orienté décision'
            ]
        },
        WritingProfile.INSTITUTIONAL: {
            'emoji': '🏛️',
            'name': 'Institutionnel',
            'phrase_cle': 'Rendre compte de manière claire et conforme',
            'public': 'Bailleurs, administrations, instances publiques',
            'caracteristiques': [
                'Transparence totale',
                'Neutralité factuelle',
                'Vocabulaire accessible',
                'Conformité'
            ]
        }
    }


# ═══════════════════════════════════════════════════════════════
# TESTS
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """Tests des blocs de style"""
    
    print("="*70)
    print("TEST DES PROFILS DE RÉDACTION")
    print("="*70)
    
    for profile in WritingProfile:
        print(f"\n{'='*70}")
        print(f"{profile.display_name}")
        print(f"{'='*70}")
        print(get_writing_style_block(profile))
    
    print("\n" + "="*70)
    print("RÉSUMÉ DES PROFILS")
    print("="*70)
    
    summary = get_profile_summary()
    for profile, info in summary.items():
        print(f"\n{info['emoji']} {info['name']}")
        print(f"   Phrase clé : {info['phrase_cle']}")
        print(f"   Public : {info['public']}")
        print(f"   Caractéristiques :")
        for car in info['caracteristiques']:
            print(f"      - {car}")