"""
Configuration centralisée pour AI Statistical Reporter
Transforme le LLM d'un "assistant intelligent" en "exécutant strictement cadré"

Auteur: AI Statistical Reporter Team
Version: 2.0 - Production Ready
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class ReportMode(Enum):
    """Type de rapport - Détermine TOUT le comportement du système"""
    ACADEMIC = "academic"           # Recherche universitaire, mémoires, thèses
    INSTITUTIONAL = "institutional" # INS, ministères, organismes publics
    BUSINESS = "business"           # Entreprises, décideurs, consultants
    EXPLORATORY = "exploratory"     # Analyse rapide, prototypage


class InterpretationLevel(Enum):
    """Niveau d'interprétation autorisé au LLM - CRITIQUE"""
    MINIMAL = "minimal"       # Juste les faits, aucune supposition
    MODERATE = "moderate"     # + Tendances observées
    DEEP = "deep"            # + Implications et hypothèses
    ACADEMIC = "academic"    # + Discussions théoriques et limites


class VerbosityLevel(Enum):
    """Niveau de détail du rapport"""
    CONCISE = "concise"      # Executive summary (5-10 pages)
    STANDARD = "standard"    # Rapport normal (15-25 pages)
    DETAILED = "detailed"    # Rapport exhaustif (30+ pages)


class ChartStyle(Enum):
    """Style des visualisations"""
    MINIMAL = "minimal"         # Graphiques simples, couleurs neutres
    PROFESSIONAL = "professional"  # Style business classique
    ACADEMIC = "academic"       # Graphiques scientifiques formels


@dataclass
class ReportConfig:
    """
    Configuration complète du rapport
    LE CERVEAU DU SYSTÈME - Contrôle TOUT le comportement du LLM
    
    Cette classe remplace les prompts génériques par des instructions précises
    """
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 1 : TYPE DE RAPPORT (PARAMÈTRE CRITIQUE)
    # ═══════════════════════════════════════════════════════════
    
    mode: ReportMode = ReportMode.INSTITUTIONAL
    """Type de rapport - Change radicalement le style et le contenu"""
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 2 : NIVEAU D'ANALYSE
    # ═══════════════════════════════════════════════════════════
    
    interpretation_level: InterpretationLevel = InterpretationLevel.MODERATE
    """Jusqu'où le LLM peut interpréter - Évite les hallucinations"""
    
    verbosity: VerbosityLevel = VerbosityLevel.STANDARD
    """Longueur cible du rapport"""
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 3 : LANGUE ET STYLE
    # ═══════════════════════════════════════════════════════════
    
    language: str = "fr"
    """Langue du rapport (fr, en)"""
    
    target_audience: str = "general"
    """Public cible : general, technical, executive, academic"""
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 4 : CONTENU (Sections conditionnelles)
    # ═══════════════════════════════════════════════════════════
    
    include_methodology: bool = True
    """Inclure section méthodologie détaillée"""
    
    include_limitations: bool = False
    """Inclure discussion des limites (académique uniquement)"""
    
    include_theoretical_intro: bool = False
    """Inclure introduction théorique (académique uniquement)"""
    
    include_recommendations: bool = True
    """Inclure section recommandations"""
    
    include_executive_summary: bool = False
    """Inclure résumé exécutif en tête"""
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 5 : VISUALISATIONS
    # ═══════════════════════════════════════════════════════════
    
    charts_enabled: bool = True
    """Générer des graphiques"""
    
    chart_style: ChartStyle = ChartStyle.PROFESSIONAL
    """Style des graphiques"""
    
    max_charts_per_section: int = 3
    """Limite de graphiques par section (évite surcharge)"""
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 6 : CONTRAINTES ET VALIDATIONS
    # ═══════════════════════════════════════════════════════════
    
    max_pages: Optional[int] = None
    """Limite de pages (si coût contrôlé)"""
    
    strict_mode: bool = True
    """Mode strict : validation rigoureuse, détection anomalies"""
    
    allow_causal_inference: bool = False
    """CRITIQUE : Autoriser inférence causale (très dangereux)"""
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 7 : MÉTADONNÉES
    # ═══════════════════════════════════════════════════════════
    
    created_at: Optional[str] = None
    created_by: Optional[str] = None
    
    def __post_init__(self):
        """Validation et ajustements automatiques"""
        
        # Ajustements selon le mode
        if self.mode == ReportMode.ACADEMIC:
            # Mode académique : activer tout
            self.include_methodology = True
            self.include_limitations = True
            self.include_theoretical_intro = True
            self.interpretation_level = InterpretationLevel.ACADEMIC
            
        elif self.mode == ReportMode.INSTITUTIONAL:
            # Mode INS : simplifier au maximum
            self.include_methodology = False
            self.include_limitations = False
            self.include_theoretical_intro = False
            self.interpretation_level = InterpretationLevel.MODERATE
            self.allow_causal_inference = False  # INTERDIT
            
        elif self.mode == ReportMode.BUSINESS:
            # Mode business : actionnable
            self.include_methodology = False
            self.include_limitations = False
            self.include_recommendations = True
            self.include_executive_summary = True
            self.interpretation_level = InterpretationLevel.DEEP
        
        logger.info(f"📋 Report config initialized: {self.mode.value}")
        logger.info(f"   - Interpretation level: {self.interpretation_level.value}")
        logger.info(f"   - Verbosity: {self.verbosity.value}")
        logger.info(f"   - Causal inference: {self.allow_causal_inference}")
    
    # ═══════════════════════════════════════════════════════════
    # MÉTHODES : GÉNÉRATION DES DIRECTIVES POUR LE LLM
    # ═══════════════════════════════════════════════════════════
    
    def get_system_prompt(self) -> str:
        """
        PROMPT SYSTÈME FORT - Borne strictement le rôle du LLM
        C'est ici qu'on transforme Claude en "exécutant cadré"
        """
        
        return f"""
═══════════════════════════════════════════════════════════════════════════
🤖 RÔLE ET CONTRAINTES DU SYSTÈME
═══════════════════════════════════════════════════════════════════════════

TU ES UN SYSTÈME DE GÉNÉRATION DE RAPPORTS STATISTIQUES.

TU N'ES PAS :
❌ Un chercheur libre
❌ Un consultant autonome
❌ Un analyste qui improvise

TU ES :
✅ Un exécutant strictement guidé
✅ Un générateur de contenu contraint
✅ Un système qui respecte des règles précises

═══════════════════════════════════════════════════════════════════════════
🎯 MODE ACTUEL : {self.mode.value.upper()}
═══════════════════════════════════════════════════════════════════════════

{self.get_mode_specific_guidelines()}

═══════════════════════════════════════════════════════════════════════════
🚫 INTERDICTIONS ABSOLUES (TOUS MODES)
═══════════════════════════════════════════════════════════════════════════

1. ❌ JAMAIS supposer de causalité
   - ✅ "X et Y sont corrélés"
   - ❌ "X cause Y"
   
2. ❌ JAMAIS extrapoler hors des données
   - ✅ "Dans cet échantillon..."
   - ❌ "Cela signifie que dans toute la population..."
   
3. ❌ JAMAIS inventer des variables
   - Utiliser UNIQUEMENT les colonnes fournies
   
4. ❌ JAMAIS interpréter au-delà du niveau autorisé
   - Niveau actuel : {self.interpretation_level.value}
   
5. ❌ JAMAIS afficher du code Python dans le rapport
   - Le code est exécuté en arrière-plan
   - Seuls les résultats apparaissent

═══════════════════════════════════════════════════════════════════════════
✅ OBLIGATIONS
═══════════════════════════════════════════════════════════════════════════

1. ✅ Rester factuel et proche des données
2. ✅ Citer les chiffres précis
3. ✅ Distinguer clairement observation vs interprétation
4. ✅ Utiliser un langage adapté au public : {self.target_audience}
5. ✅ Respecter le niveau de verbosité : {self.verbosity.value}

═══════════════════════════════════════════════════════════════════════════
"""
    
    def get_mode_specific_guidelines(self) -> str:
        """Directives spécifiques selon le mode de rapport"""
        
        if self.mode == ReportMode.ACADEMIC:
            return """
📚 DIRECTIVES MODE ACADÉMIQUE

STYLE :
- Ton formel et rigoureux
- Terminologie scientifique appropriée
- Phrases complexes autorisées
- Références bibliographiques encouragées

STRUCTURE OBLIGATOIRE :
1. Introduction théorique (contexte scientifique)
2. Revue de littérature (si pertinent)
3. Méthodologie détaillée
4. Résultats avec nuances statistiques
5. Discussion approfondie
6. Limites méthodologiques
7. Conclusion prudente

INTERPRÉTATIONS :
- Niveau ACADEMIC autorisé
- Discussions théoriques acceptées
- Prudence obligatoire ("Ces résultats suggèrent...")
- Toujours mentionner les limites

EXEMPLE DE TON :
"Les résultats de cette analyse révèlent une corrélation positive 
significative (r=0.67, p<0.01) entre X et Y. Cette association, bien 
que robuste dans notre échantillon, doit être interprétée avec prudence 
compte tenu de la nature transversale des données..."
"""
        
        elif self.mode == ReportMode.INSTITUTIONAL:
            return """
🏛️ DIRECTIVES MODE INSTITUTIONNEL (INS / Organismes publics)

STYLE :
- Langage clair et accessible
- Ton neutre et factuel
- Phrases courtes et directes
- AUCUN jargon technique
- Vocabulaire grand public

STRUCTURE OBLIGATOIRE :
1. Messages clés (bullet points en tête)
2. Chiffres principaux (encadrés)
3. Graphiques simples et explicites
4. Interprétation factuelle
5. Conclusion opérationnelle

CONTENU INTERDIT :
❌ Discussions théoriques longues
❌ Méthodologie technique détaillée
❌ Limites méthodologiques excessives
❌ Références académiques
❌ Formules statistiques complexes

INTERPRÉTATIONS :
- Niveau MODERATE uniquement
- Rester strictement factuel
- "Les données montrent que..." (pas "Il semble que...")
- Pas de spéculation

EXEMPLE DE TON :
"Les données révèlent que 78% des entreprises sont dirigées par des 
hommes. Cette répartition varie selon les régions, avec une proportion 
plus élevée de femmes entrepreneures dans la région du Littoral (25%)."
"""
        
        elif self.mode == ReportMode.BUSINESS:
            return """
💼 DIRECTIVES MODE BUSINESS

STYLE :
- Direct et actionnable
- Ton professionnel
- Focus sur les insights
- Vocabulaire business

STRUCTURE OBLIGATOIRE :
1. Executive summary (1 page max)
2. Chiffres clés (KPIs)
3. Insights actionnables
4. Recommandations concrètes
5. Next steps

FOCUS :
- Impact business
- Décisions à prendre
- Opportunités identifiées
- Risques à gérer

CONTENU INTERDIT :
❌ Méthodologie technique longue
❌ Discussions académiques
❌ Avertissements méthodologiques excessifs

INTERPRÉTATIONS :
- Niveau DEEP autorisé
- Focus sur "Que faire avec ces données ?"
- Implications stratégiques
- ROI potentiel

EXEMPLE DE TON :
"L'analyse révèle une opportunité significative dans la région du 
Littoral, où la productivité par employé est 30% supérieure à la 
moyenne nationale. Recommandation : concentrer les investissements 
sur cette zone pour maximiser le ROI."
"""
        
        else:  # EXPLORATORY
            return """
🔍 DIRECTIVES MODE EXPLORATOIRE

STYLE :
- Flexible et itératif
- Ton curieux
- Focus découverte

CONTENU :
- Patterns intéressants
- Anomalies à investiguer
- Questions pour analyses futures
- Hypothèses (clairement marquées comme telles)

INTERPRÉTATIONS :
- Niveau MODERATE
- Hypothèses autorisées mais marquées
- "À explorer :", "Hypothèse :", etc.
"""
    
    def get_anti_duplication_rules(self) -> str:
        """Règles anti-duplication renforcées"""
        return """
🔴 RÈGLES ANTI-DUPLICATION ABSOLUES

1. ❌ INTERDIT de créer 2 tableaux avec le MÊME titre
   
   MAUVAIS EXEMPLE :
   **Aperçu des données :**
   [Tableau 1]
   
   **Aperçu des données :**  ← ❌ VIOLATION GRAVE
   [Tableau 2]

2. ✅ SI tu dois montrer des données différentes :
   - Utilise des titres EXPLICITEMENT DIFFÉRENTS
   - Justifie pourquoi 2 tableaux
   
   BON EXEMPLE :
   **Vue d'ensemble (toutes les variables) :**
   [Tableau complet 28 colonnes]
   
   **Variables clés pour l'analyse principale :**
   [Tableau filtré 5 colonnes]
   
   Nous nous concentrons maintenant sur les 5 variables clés...

3. 🔴 AVANT de générer un tableau, pose-toi ces questions :
   □ Ai-je déjà montré exactement ces statistiques ?
   □ Ce tableau apporte-t-il une information NOUVELLE ?
   □ Si les réponses sont NON → NE PAS générer le tableau

4. LIMITES STRICTES par section :
   - Maximum 1 aperçu des données (df.head())
   - Maximum 1 tableau de statistiques descriptives par type
   - Maximum 1 tableau de valeurs manquantes
   - Maximum {self.max_charts_per_section} graphiques

5. ❌ JAMAIS recalculer les mêmes statistiques
   - Si tu as déjà fait df['Sexe'].value_counts()
   - NE LE REFAIS PAS plus tard dans le même chapitre
   - Les données ne changent pas entre 2 sections !

6. 🔴 VALIDATION FINALE OBLIGATOIRE :
   Avant de retourner le chapitre :
   □ Pas de titre en double ?
   □ Pas de tableau identique répété ?
   □ Chiffres cohérents partout ?
"""
    
    def get_code_generation_rules(self) -> str:
        """Règles strictes pour la génération de code Python"""
        return """
🔴 RÈGLES ABSOLUES DE GÉNÉRATION DE CODE PYTHON

1. LE CODE SERA EXÉCUTÉ MAIS RESTERA INVISIBLE

   Le code Python que tu génères sera :
   - ✅ Exécuté automatiquement par le système
   - ✅ Remplacé par ses résultats (tableaux, graphiques)
   - ❌ JAMAIS visible dans le rapport final

2. STRUCTURE OBLIGATOIRE

   [Texte narratif d'introduction]
   
   ```python
   # Ce code sera exécuté invisiblement
   # Seuls les résultats apparaîtront
   ```
   
   [Interprétation narrative des résultats]

3. IMPORTS AUTOMATIQUES (NE PAS RÉIMPORTER)

   Bibliothèques DÉJÀ disponibles :
   - pandas (as pd)
   - matplotlib.pyplot (as plt)
   - numpy (as np)
   - seaborn (as sns)
   - io

4. DATAFRAME DÉJÀ CHARGÉ

   ❌ INTERDIT :
   ```python
   df = pd.read_csv('fichier.csv')  # ❌ df existe déjà !
   import pandas as pd              # ❌ déjà importé !
   ```
   
   ✅ CORRECT :
   ```python
   # df est déjà disponible, utilise-le directement
   print(df['colonne'].mean())
   ```

5. INTERDICTIONS FORMELLES

   ❌ print(df.info())        # Sortie brute non formatée
   ❌ print(df.describe())    # Créer tableau Markdown à la place
   ❌ print(df.to_string())   # Idem
   ❌ print(df.to_markdown()) # Tabulate non installé
   ❌ df['col_inexistante']   # Vérifier existence d'abord

6. OBLIGATIONS

   ✅ Vérifier existence des colonnes avant utilisation
   ✅ Gérer les valeurs manquantes
   ✅ Créer tableaux Markdown manuellement
   ✅ Utiliser détection automatique des colonnes
   ✅ Utiliser print() pour sortie Markdown propre

7. EXEMPLE CORRECT

   ```python
   # Détection automatique colonnes numériques
   numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
   
   # Exclusion colonnes inutiles (ID, index, etc.)
   exclude_kw = ['id', 'index', 'unnamed', 'key', 'code']
   numeric_cols = [c for c in numeric_cols 
                   if not any(kw in c.lower() for kw in exclude_kw)]
   
   # Création tableau Markdown manuel
   print("| Variable | Moyenne | Écart-type |")
   print("|----------|---------|------------|")
   for col in numeric_cols[:10]:
       print(f"| {{col}} | {{df[col].mean():.2f}} | {{df[col].std():.2f}} |")
   ```
"""
    
    def get_interpretation_guidelines(self) -> str:
        """Directives d'interprétation selon le niveau"""
        
        level = self.interpretation_level
        
        if level == InterpretationLevel.MINIMAL:
            return """
📊 NIVEAU D'INTERPRÉTATION : MINIMAL

TU DOIS RESTER STRICTEMENT FACTUEL.

✅ AUTORISÉ :
- "Les données montrent que..."
- "On observe une moyenne de X"
- "La distribution présente une asymétrie vers la droite"
- "78% des entreprises sont dirigées par des hommes"

❌ INTERDIT :
- AUCUNE supposition
- AUCUNE causalité
- AUCUNE extrapolation
- AUCUNE hypothèse
- AUCUN "cela suggère que..."

EXEMPLE DE PHRASE CORRECTE :
"Les données révèlent que les entreprises de la région du Littoral 
affichent un chiffre d'affaires moyen de 130 000 FCFA, soit 30% 
supérieur à la moyenne nationale de 100 000 FCFA."

EXEMPLE DE PHRASE INCORRECTE (trop d'interprétation) :
"Le chiffre d'affaires élevé dans le Littoral suggère que cette 
région bénéficie d'un meilleur environnement économique."  ← ❌
"""
        
        elif level == InterpretationLevel.MODERATE:
            return """
📊 NIVEAU D'INTERPRÉTATION : MODERATE

Tu peux décrire les TENDANCES OBSERVÉES.

✅ AUTORISÉ :
- Décrire patterns et tendances
- "On observe une corrélation positive..."
- "Cette distribution suggère..."
- Proposer des pistes d'explication (clairement marquées)

❌ INTERDIT :
- Affirmer des causalités
- Extrapoler hors échantillon
- Faire des prédictions

⚠️ DISTINCTION OBLIGATOIRE :
- ✅ "X et Y sont corrélés (r=0.67)"
- ❌ "X cause Y"

EXEMPLE CORRECT :
"L'analyse révèle une corrélation positive entre l'âge de l'entreprise 
et sa productivité (r=0.45). Cette association pourrait s'expliquer 
par l'accumulation d'expérience et l'optimisation des processus au 
fil du temps, bien que d'autres facteurs non mesurés puissent 
également jouer un rôle."

STRUCTURE TYPE :
1. Fait observé
2. Interprétation prudente ("pourrait", "suggère")
3. Nuance ("bien que", "cependant")
"""
        
        elif level == InterpretationLevel.DEEP:
            return """
📊 NIVEAU D'INTERPRÉTATION : DEEP

Tu peux analyser les IMPLICATIONS et proposer des HYPOTHÈSES.

✅ AUTORISÉ :
- Discuter les mécanismes possibles
- Proposer des hypothèses (clairement marquées)
- Analyser les implications pratiques
- "Ces résultats suggèrent que..."
- "Une explication plausible serait..."

❌ TOUJOURS INTERDIT :
- Affirmer des causalités sans preuve
- Confusion corrélation ≠ causalité

⚠️ FORMULATIONS OBLIGATOIRES :
- "Une hypothèse serait que..."
- "Cela pourrait s'expliquer par..."
- "Sans pouvoir établir de causalité, on peut supposer..."

EXEMPLE CORRECT :
"La forte corrélation observée entre le niveau de diplôme du promoteur 
et la productivité de l'entreprise (r=0.58) soulève plusieurs pistes 
d'explication. D'une part, un capital humain élevé pourrait favoriser 
une meilleure gestion et une adoption plus rapide d'innovations. 
D'autre part, cette association pourrait également refléter un biais 
de sélection, les entrepreneurs diplômés ayant potentiellement accès 
à des secteurs plus productifs. Des analyses complémentaires seraient 
nécessaires pour démêler ces mécanismes."
"""
        
        elif level == InterpretationLevel.ACADEMIC:
            return """
📊 NIVEAU D'INTERPRÉTATION : ACADEMIC

Analyse académique complète avec discussion théorique.

✅ AUTORISÉ :
- Discussion théorique approfondie
- Références aux littératures
- Analyse des limites méthodologiques
- Propositions pour recherches futures
- Nuances statistiques

STRUCTURE TYPE :
1. Résultat observé
2. Contexte théorique
3. Interprétation avec nuances
4. Limites de l'analyse
5. Implications pour la recherche

⚠️ PRUDENCE OBLIGATOIRE :
- "Ces résultats doivent être interprétés avec prudence..."
- "Dans les limites de cette étude transversale..."
- "D'autres facteurs non mesurés pourraient..."

EXEMPLE COMPLET :
"L'analyse révèle une corrélation positive significative entre le 
diplôme du promoteur et la productivité (r=0.58, p<0.001). Ce résultat 
s'inscrit dans le cadre théorique du capital humain (Becker, 1964) et 
confirme les observations de Smith et al. (2020) dans un contexte 
similaire. Toutefois, plusieurs limites méthodologiques méritent 
d'être soulignées. Premièrement, la nature transversale des données 
ne permet pas d'établir de relation causale. Deuxièmement, des biais 
de sélection et d'endogénéité ne peuvent être exclus. Des analyses 
longitudinales avec variables instrumentales seraient nécessaires 
pour approfondir ces mécanismes."
"""
        
        else:
            return "Interprétation standard"


# ═══════════════════════════════════════════════════════════════
# FONCTIONS HELPER
# ═══════════════════════════════════════════════════════════════

def create_config_for_audience(audience_type: str) -> ReportConfig:
    """
    Crée une configuration adaptée au public cible
    
    Args:
        audience_type: "academic", "ins", "business", "exploratory"
    
    Returns:
        ReportConfig avec paramètres optimisés
    """
    
    configs = {
        "academic": ReportConfig(
            mode=ReportMode.ACADEMIC,
            interpretation_level=InterpretationLevel.ACADEMIC,
            verbosity=VerbosityLevel.DETAILED,
            include_methodology=True,
            include_limitations=True,
            include_theoretical_intro=True,
            chart_style=ChartStyle.ACADEMIC,
            target_audience="academic",
            allow_causal_inference=False  # Même en académique
        ),
        
        "ins": ReportConfig(
            mode=ReportMode.INSTITUTIONAL,
            interpretation_level=InterpretationLevel.MODERATE,
            verbosity=VerbosityLevel.STANDARD,
            include_methodology=False,
            include_limitations=False,
            include_theoretical_intro=False,
            chart_style=ChartStyle.PROFESSIONAL,
            target_audience="general",
            allow_causal_inference=False,  # INTERDIT en INS
            strict_mode=True
        ),
        
        "business": ReportConfig(
            mode=ReportMode.BUSINESS,
            interpretation_level=InterpretationLevel.DEEP,
            verbosity=VerbosityLevel.CONCISE,
            include_methodology=False,
            include_limitations=False,
            include_recommendations=True,
            include_executive_summary=True,
            chart_style=ChartStyle.MINIMAL,
            target_audience="executive",
            max_charts_per_section=2
        ),
        
        "exploratory": ReportConfig(
            mode=ReportMode.EXPLORATORY,
            interpretation_level=InterpretationLevel.MODERATE,
            verbosity=VerbosityLevel.STANDARD,
            include_methodology=True,
            target_audience="technical"
        )
    }
    
    config = configs.get(audience_type.lower(), configs["ins"])
    
    logger.info(f"✅ Config created for audience: {audience_type}")
    
    return config


def validate_config(config: ReportConfig) -> List[str]:
    """
    Valide la cohérence de la configuration
    
    Returns:
        Liste des warnings (vide si tout OK)
    """
    warnings = []
    
    # Vérifier cohérence mode vs interprétation
    if config.mode == ReportMode.INSTITUTIONAL:
        if config.interpretation_level == InterpretationLevel.ACADEMIC:
            warnings.append(
                "⚠️ Mode INSTITUTIONAL avec interprétation ACADEMIC : incohérent"
            )
        if config.include_limitations:
            warnings.append(
                "⚠️ Mode INSTITUTIONAL ne devrait pas inclure limites détaillées"
            )
    
    # Vérifier causalité
    if config.allow_causal_inference:
        warnings.append(
            "⚠️ Inférence causale activée : TRÈS RISQUÉ, hallucinations probables"
        )
    
    return warnings


# ═══════════════════════════════════════════════════════════════
# TESTS
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    
    print("="*70)
    print("TEST CONFIGURATION SYSTÈME")
    print("="*70)
    
    # Test 1 : Config INS
    print("\n📋 Test 1 : Configuration INS")
    config_ins = create_config_for_audience("ins")
    print(f"   Mode: {config_ins.mode.value}")
    print(f"   Interprétation: {config_ins.interpretation_level.value}")
    print(f"   Limites incluses: {config_ins.include_limitations}")
    print(f"   Causalité: {config_ins.allow_causal_inference}")
    
    warnings = validate_config(config_ins)
    if warnings:
        for w in warnings:
            print(f"   {w}")
    else:
        print("   ✅ Config valide")
    
    # Test 2 : Config académique
    print("\n📋 Test 2 : Configuration Academic")
    config_acad = create_config_for_audience("academic")
    print(f"   Mode: {config_acad.mode.value}")
    print(f"   Interprétation: {config_acad.interpretation_level.value}")
    print(f"   Limites incluses: {config_acad.include_limitations}")
    
    # Test 3 : Afficher prompt système
    print("\n📋 Test 3 : System Prompt (extrait)")
    prompt = config_ins.get_system_prompt()
    print(prompt[:500] + "...")
    
    print("\n✅ Tests terminés")