"""
Configuration centralisée pour les types de rapports et modes d'analyse
Répond aux insuffisances identifiées dans l'analyse critique
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class ReportMode(Enum):
    """Types de rapports avec contraintes spécifiques"""
    ACADEMIC = "academic"  # Scientifique, rigoureux
    INSTITUTIONAL = "institutional"  # INS, administrations
    BUSINESS = "business"  # Entreprises, décideurs
    EXPLORATORY = "exploratory"  # Analyse exploratoire libre


class InterpretationLevel(Enum):
    """Niveau d'interprétation autorisé"""
    NONE = "none"  # Chiffres uniquement
    LOW = "low"  # Constatations factuelles
    MEDIUM = "medium"  # Interprétations prudentes
    HIGH = "high"  # Analyses approfondies


class VerbosityLevel(Enum):
    """Niveau de verbosité du rapport"""
    MINIMAL = "minimal"  # Ultra concis
    MEDIUM = "medium"  # Équilibré
    DETAILED = "detailed"  # Complet


@dataclass
class ReportConfig:
    """
    Configuration complète d'un rapport
    Cette classe centralise TOUS les paramètres qui influencent le comportement du LLM
    """
    
    # TYPE DE RAPPORT (OBLIGATOIRE)
    mode: ReportMode = ReportMode.INSTITUTIONAL
    
    # LANGUE
    language: str = "fr"
    
    # NIVEAU D'INTERPRÉTATION
    interpretation_level: InterpretationLevel = InterpretationLevel.LOW
    
    # NIVEAU DE VERBOSITÉ
    verbosity: VerbosityLevel = VerbosityLevel.MEDIUM
    
    # GRAPHIQUES
    include_charts: bool = True
    chart_style: str = "professional"  # "professional", "academic", "simple"
    
    # SECTIONS OPTIONNELLES
    include_methodology_discussion: bool = False
    include_limitations: bool = False
    include_theoretical_background: bool = False
    include_recommendations: bool = True
    
    # STYLE D'ÉCRITURE
    tone: str = "neutral"  # "neutral", "formal", "accessible"
    avoid_jargon: bool = True
    
    # CONTRAINTES
    max_pages_per_chapter: Optional[int] = None
    target_audience: str = "general"  # "general", "technical", "executive"
    
    def get_mode_constraints(self) -> Dict:
        """
        Retourne les contraintes spécifiques selon le mode de rapport
        Ces contraintes sont CONTRACTUELLES et ne peuvent être violées par le LLM
        """
        
        if self.mode == ReportMode.ACADEMIC:
            return {
                "style": "scientifique rigoureux",
                "interpretation_level": "high",
                "require_methodology": True,
                "require_limitations": True,
                "require_references": True,
                "allow_theoretical_discussion": True,
                "tone": "formal",
                "avoid_causal_claims_without_proof": True,
                "statistical_tests_required": True,
                "verbosity": "detailed"
            }
        
        elif self.mode == ReportMode.INSTITUTIONAL:
            return {
                "style": "clair et neutre",
                "interpretation_level": "low",
                "require_methodology": False,
                "require_limitations": False,
                "require_references": False,
                "allow_theoretical_discussion": False,
                "tone": "neutral",
                "avoid_causal_claims_without_proof": True,
                "statistical_tests_required": False,
                "verbosity": "medium",
                "focus_on_facts": True,
                "no_long_introductions": True
            }
        
        elif self.mode == ReportMode.BUSINESS:
            return {
                "style": "concis et actionnable",
                "interpretation_level": "medium",
                "require_methodology": False,
                "require_limitations": False,
                "require_references": False,
                "allow_theoretical_discussion": False,
                "tone": "accessible",
                "avoid_causal_claims_without_proof": False,  # Plus de flexibilité
                "statistical_tests_required": False,
                "verbosity": "minimal",
                "focus_on_insights": True,
                "include_key_takeaways": True
            }
        
        elif self.mode == ReportMode.EXPLORATORY:
            return {
                "style": "exploratoire",
                "interpretation_level": "high",
                "require_methodology": False,
                "require_limitations": True,
                "require_references": False,
                "allow_theoretical_discussion": True,
                "tone": "accessible",
                "avoid_causal_claims_without_proof": True,
                "statistical_tests_required": False,
                "verbosity": "detailed",
                "allow_hypotheses": True
            }
        
        return {}
    
    def get_system_prompt_additions(self) -> str:
        """
        Génère les additions au system prompt selon le mode
        C'est ici que le LLM reçoit ses ORDRES STRICTS
        """
        
        constraints = self.get_mode_constraints()
        
        prompt_additions = f"""
# CONFIGURATION DU RAPPORT (OBLIGATOIRE)

**Type de rapport :** {self.mode.value.upper()}
**Niveau d'interprétation autorisé :** {self.interpretation_level.value}
**Niveau de verbosité :** {self.verbosity.value}
**Public cible :** {self.target_audience}

# CONTRAINTES STRICTES (NON NÉGOCIABLES)

"""
        
        # Contraintes selon le mode
        if self.mode == ReportMode.INSTITUTIONAL:
            prompt_additions += """
**RÈGLES ABSOLUES - MODE INSTITUTIONNEL :**

1. ❌ INTERDIT :
   - Toute discussion théorique ou méthodologique longue
   - Les interprétations causales ("X cause Y")
   - Les extrapolations au-delà des données
   - Le jargon statistique non expliqué
   - Les sections "Limitations" longues (max 2-3 phrases si nécessaire)
   - Les introductions théoriques (aller droit au but)

2. ✅ OBLIGATOIRE :
   - Langage clair et accessible
   - Chiffres clés mis en évidence
   - Graphiques simples et lisibles
   - Constatations factuelles uniquement
   - Structure concise (introduction brève, résultats, conclusion)

3. 📊 INTERPRÉTATION :
   - Dire : "Les données montrent que..."
   - NE PAS dire : "Cela suggère que... / On peut en déduire que..."
   - Se limiter aux observations directes
"""
        
        elif self.mode == ReportMode.ACADEMIC:
            prompt_additions += """
**RÈGLES ABSOLUES - MODE ACADÉMIQUE :**

1. ✅ OBLIGATOIRE :
   - Discussion méthodologique complète
   - Section "Limitations" détaillée
   - Tests statistiques appropriés avec p-values
   - Contexte théorique si pertinent
   - Références aux travaux antérieurs (si disponibles)
   - Langage scientifique précis

2. 📊 INTERPRÉTATION :
   - Analyses approfondies autorisées
   - Hypothèses explicites
   - Nuances et prudence scientifique
   - Discussion des résultats inattendus

3. ⚠️ GARDE-FOUS :
   - Jamais affirmer de causalité sans preuve expérimentale
   - Toujours mentionner les limites des analyses observationnelles
   - Être transparent sur les choix méthodologiques
"""
        
        elif self.mode == ReportMode.BUSINESS:
            prompt_additions += """
**RÈGLES ABSOLUES - MODE BUSINESS :**

1. ✅ OBLIGATOIRE :
   - Messages clés en début de chaque section
   - Langage accessible (éviter jargon statistique)
   - Focus sur les insights actionnables
   - Graphiques avec messages clairs
   - Synthèse exécutive concise

2. ❌ ÉVITER :
   - Discussions méthodologiques longues
   - Sections théoriques
   - Avertissements méthodologiques répétitifs
   - Jargon technique non nécessaire

3. 📊 INTERPRÉTATION :
   - Insights business autorisés
   - Recommandations pragmatiques
   - Tendances et patterns mis en évidence
"""
        
        # Contraintes communes
        prompt_additions += f"""

# CONTRAINTES TECHNIQUES

- **Graphiques :** {"Oui" if self.include_charts else "Non"}
- **Ton :** {constraints.get('tone', 'neutral')}
- **Style :** {constraints.get('style', 'standard')}
- **Tests statistiques requis :** {"Oui" if constraints.get('statistical_tests_required') else "Non"}

"""
        
        return prompt_additions
    
    def to_dict(self) -> Dict:
        """Sérialise la config en dict"""
        return {
            "mode": self.mode.value,
            "language": self.language,
            "interpretation_level": self.interpretation_level.value,
            "verbosity": self.verbosity.value,
            "include_charts": self.include_charts,
            "chart_style": self.chart_style,
            "include_methodology_discussion": self.include_methodology_discussion,
            "include_limitations": self.include_limitations,
            "include_theoretical_background": self.include_theoretical_background,
            "include_recommendations": self.include_recommendations,
            "tone": self.tone,
            "avoid_jargon": self.avoid_jargon,
            "max_pages_per_chapter": self.max_pages_per_chapter,
            "target_audience": self.target_audience
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ReportConfig':
        """Désérialise depuis un dict"""
        return cls(
            mode=ReportMode(data.get("mode", "institutional")),
            language=data.get("language", "fr"),
            interpretation_level=InterpretationLevel(data.get("interpretation_level", "low")),
            verbosity=VerbosityLevel(data.get("verbosity", "medium")),
            include_charts=data.get("include_charts", True),
            chart_style=data.get("chart_style", "professional"),
            include_methodology_discussion=data.get("include_methodology_discussion", False),
            include_limitations=data.get("include_limitations", False),
            include_theoretical_background=data.get("include_theoretical_background", False),
            include_recommendations=data.get("include_recommendations", True),
            tone=data.get("tone", "neutral"),
            avoid_jargon=data.get("avoid_jargon", True),
            max_pages_per_chapter=data.get("max_pages_per_chapter"),
            target_audience=data.get("target_audience", "general")
        )


# Configurations pré-définies
PRESET_CONFIGS = {
    "ins_report": ReportConfig(
        mode=ReportMode.INSTITUTIONAL,
        interpretation_level=InterpretationLevel.LOW,
        verbosity=VerbosityLevel.MEDIUM,
        include_charts=True,
        chart_style="professional",
        include_methodology_discussion=False,
        include_limitations=False,
        tone="neutral",
        avoid_jargon=True,
        target_audience="general"
    ),
    
    "academic_thesis": ReportConfig(
        mode=ReportMode.ACADEMIC,
        interpretation_level=InterpretationLevel.HIGH,
        verbosity=VerbosityLevel.DETAILED,
        include_charts=True,
        chart_style="academic",
        include_methodology_discussion=True,
        include_limitations=True,
        include_theoretical_background=True,
        tone="formal",
        avoid_jargon=False,
        target_audience="technical"
    ),
    
    "business_report": ReportConfig(
        mode=ReportMode.BUSINESS,
        interpretation_level=InterpretationLevel.MEDIUM,
        verbosity=VerbosityLevel.MINIMAL,
        include_charts=True,
        chart_style="simple",
        include_methodology_discussion=False,
        include_limitations=False,
        include_recommendations=True,
        tone="accessible",
        avoid_jargon=True,
        target_audience="executive"
    ),
    
    "exploratory_analysis": ReportConfig(
        mode=ReportMode.EXPLORATORY,
        interpretation_level=InterpretationLevel.HIGH,
        verbosity=VerbosityLevel.DETAILED,
        include_charts=True,
        chart_style="professional",
        include_methodology_discussion=False,
        include_limitations=True,
        tone="accessible",
        avoid_jargon=True,
        target_audience="technical"
    )
}


# ============================================
# TESTS
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("TEST REPORT CONFIGURATION SYSTEM")
    print("="*60)
    
    # Test 1: Configuration INS
    print("\n1. Configuration INS :")
    ins_config = PRESET_CONFIGS["ins_report"]
    print(f"   Mode: {ins_config.mode.value}")
    print(f"   Interprétation: {ins_config.interpretation_level.value}")
    print(f"   Verbosité: {ins_config.verbosity.value}")
    
    constraints = ins_config.get_mode_constraints()
    print(f"   Contraintes clés:")
    print(f"   - Style: {constraints['style']}")
    print(f"   - Tests stats requis: {constraints['statistical_tests_required']}")
    print(f"   - Focus: {constraints.get('focus_on_facts', False)}")
    
    # Test 2: Configuration Académique
    print("\n2. Configuration Académique :")
    academic_config = PRESET_CONFIGS["academic_thesis"]
    print(f"   Mode: {academic_config.mode.value}")
    
    constraints_ac = academic_config.get_mode_constraints()
    print(f"   Contraintes clés:")
    print(f"   - Méthodologie requise: {constraints_ac['require_methodology']}")
    print(f"   - Limitations requises: {constraints_ac['require_limitations']}")
    
    # Test 3: System Prompt
    print("\n3. System Prompt Additions (INS) :")
    prompt_additions = ins_config.get_system_prompt_additions()
    print(prompt_additions[:500] + "...")
    
    print("\n✅ Tests terminés")