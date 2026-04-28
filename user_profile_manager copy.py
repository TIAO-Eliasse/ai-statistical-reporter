"""
User Profile Manager — Gestion dynamique des profils utilisateurs
Permet d'adapter automatiquement le style, la structure et le niveau de détail
selon le type d'utilisateur (Académique, Industrie, INS, etc.)

VERSION : 2.0
DATE : 2025-12-28
"""

from enum import Enum
from typing import Dict, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════
# ÉNUMÉRATIONS DES PROFILS
# ════════════════════════════════════════════════════════════════════════

class UserProfile(Enum):
    """Profils utilisateurs disponibles"""
    ACADEMIC = "academic"
    INDUSTRY = "industry"
    INS = "ins"  # Institut National de Statistique
    EXPLORATORY = "exploratory"
    DECISION_MAKER = "decision_maker"


class ReportLength(Enum):
    """Longueur du rapport"""
    CONCISE = "concise"      # 1-3 pages/chapitre
    STANDARD = "standard"    # 4-7 pages/chapitre
    DETAILED = "detailed"    # 8-15 pages/chapitre
    EXHAUSTIVE = "exhaustive"  # 16-30 pages/chapitre


class VisualizationPreference(Enum):
    """Préférence de visualisation"""
    GRAPHS_HEAVY = "graphs_heavy"      # 70% graphiques, 30% tableaux
    BALANCED = "balanced"              # 50-50
    TABLES_HEAVY = "tables_heavy"      # 70% tableaux, 30% graphiques


# ════════════════════════════════════════════════════════════════════════
# CONFIGURATION PAR PROFIL
# ════════════════════════════════════════════════════════════════════════

@dataclass
class ProfileConfiguration:
    """Configuration complète d'un profil utilisateur"""
    
    # Identité
    profile: UserProfile
    display_name: str
    description: str
    
    # Style rédactionnel
    tone: str  # "formal", "professional", "neutral", "conversational"
    technical_level: str  # "high", "medium", "low"
    jargon_allowed: bool
    
    # Structure du rapport
    include_methodology: bool
    include_theory: bool
    include_recommendations: bool
    include_executive_summary: bool
    include_limitations: bool
    
    # Analyses
    statistical_rigor: str  # "high", "medium", "low"
    hypothesis_testing: bool
    exploratory_analysis: bool
    predictive_modeling: bool
    
    # Visuels
    visualization_preference: VisualizationPreference
    min_graphs_percent: int  # Pourcentage minimum de graphiques
    
    # Longueur par défaut
    default_length: ReportLength
    
    # Sections obligatoires
    mandatory_sections: List[str]
    
    # Sections interdites
    forbidden_sections: List[str]
    
    # Priorités d'analyse
    analysis_priorities: List[str]


# ════════════════════════════════════════════════════════════════════════
# CONFIGURATIONS PRÉDÉFINIES
# ════════════════════════════════════════════════════════════════════════

PROFILE_CONFIGS = {
    UserProfile.ACADEMIC: ProfileConfiguration(
        profile=UserProfile.ACADEMIC,
        display_name="Académique",
        description="Rapports pour publications scientifiques, thèses, mémoires",
        
        # Style
        tone="formal",
        technical_level="high",
        jargon_allowed=True,
        
        # Structure
        include_methodology=True,
        include_theory=True,
        include_recommendations=True,
        include_executive_summary=False,
        include_limitations=True,
        
        # Analyses
        statistical_rigor="high",
        hypothesis_testing=True,
        exploratory_analysis=True,
        predictive_modeling=True,
        
        # Visuels
        visualization_preference=VisualizationPreference.BALANCED,
        min_graphs_percent=40,
        
        # Longueur
        default_length=ReportLength.DETAILED,
        
        # Sections
        mandatory_sections=[
            "Introduction",
            "Revue de littérature",
            "Méthodologie",
            "Résultats",
            "Discussion",
            "Conclusion",
            "Limites"
        ],
        forbidden_sections=[
            "Résumé exécutif"
        ],
        
        # Priorités
        analysis_priorities=[
            "Tests d'hypothèses",
            "Modélisation statistique",
            "Analyses multivariées",
            "Robustesse des résultats"
        ]
    ),
    
    UserProfile.INDUSTRY: ProfileConfiguration(
        profile=UserProfile.INDUSTRY,
        display_name="Industrie / Business",
        description="Rapports pour entreprises, consultants, décideurs",
        
        # Style
        tone="professional",
        technical_level="medium",
        jargon_allowed=False,
        
        # Structure
        include_methodology=False,
        include_theory=False,
        include_recommendations=True,
        include_executive_summary=True,
        include_limitations=False,
        
        # Analyses
        statistical_rigor="medium",
        hypothesis_testing=False,
        exploratory_analysis=True,
        predictive_modeling=True,
        
        # Visuels
        visualization_preference=VisualizationPreference.GRAPHS_HEAVY,
        min_graphs_percent=60,
        
        # Longueur
        default_length=ReportLength.STANDARD,
        
        # Sections
        mandatory_sections=[
            "Résumé exécutif",
            "Indicateurs clés",
            "Analyses visuelles",
            "Insights actionnables",
            "Recommandations"
        ],
        forbidden_sections=[
            "Revue de littérature",
            "Méthodologie détaillée",
            "Tests statistiques formels"
        ],
        
        # Priorités
        analysis_priorities=[
            "Patterns business",
            "Opportunités et risques",
            "Prédictions et tendances",
            "ROI et impact"
        ]
    ),
    
    UserProfile.INS: ProfileConfiguration(
        profile=UserProfile.INS,
        display_name="Institut Statistique",
        description="Rapports pour organismes officiels (INS, Banque Centrale, etc.)",
        
        # Style
        tone="neutral",
        technical_level="high",
        jargon_allowed=True,
        
        # Structure
        include_methodology=True,
        include_theory=False,
        include_recommendations=False,
        include_executive_summary=True,
        include_limitations=True,
        
        # Analyses
        statistical_rigor="high",
        hypothesis_testing=False,
        exploratory_analysis=False,
        predictive_modeling=False,
        
        # Visuels
        visualization_preference=VisualizationPreference.BALANCED,
        min_graphs_percent=40,
        
        # Longueur
        default_length=ReportLength.DETAILED,
        
        # Sections
        mandatory_sections=[
            "Présentation de l'échantillon",
            "Caractéristiques structurelles",
            "Distributions et répartitions",
            "Indicateurs statistiques",
            "Notes méthodologiques"
        ],
        forbidden_sections=[
            "Recommandations",
            "Prédictions",
            "Interprétations spéculatives"
        ],
        
        # Priorités
        analysis_priorities=[
            "Représentativité",
            "Distributions",
            "Indicateurs structurels",
            "Transparence méthodologique"
        ]
    ),
    
    UserProfile.EXPLORATORY: ProfileConfiguration(
        profile=UserProfile.EXPLORATORY,
        display_name="Exploratoire",
        description="Analyse de données sans hypothèses pré-définies",
        
        # Style
        tone="conversational",
        technical_level="medium",
        jargon_allowed=False,
        
        # Structure
        include_methodology=False,
        include_theory=False,
        include_recommendations=False,
        include_executive_summary=False,
        include_limitations=False,
        
        # Analyses
        statistical_rigor="medium",
        hypothesis_testing=False,
        exploratory_analysis=True,
        predictive_modeling=False,
        
        # Visuels
        visualization_preference=VisualizationPreference.GRAPHS_HEAVY,
        min_graphs_percent=70,
        
        # Longueur
        default_length=ReportLength.STANDARD,
        
        # Sections
        mandatory_sections=[
            "Vue d'ensemble",
            "Exploration multivariée",
            "Patterns identifiés",
            "Pistes d'investigation"
        ],
        forbidden_sections=[
            "Tests d'hypothèses",
            "Conclusions définitives"
        ],
        
        # Priorités
        analysis_priorities=[
            "Découverte de patterns",
            "Anomalies",
            "Corrélations inattendues",
            "Questions ouvertes"
        ]
    ),
    
    UserProfile.DECISION_MAKER: ProfileConfiguration(
        profile=UserProfile.DECISION_MAKER,
        display_name="Décideur / Executive",
        description="Synthèse ultra-concise pour dirigeants",
        
        # Style
        tone="professional",
        technical_level="low",
        jargon_allowed=False,
        
        # Structure
        include_methodology=False,
        include_theory=False,
        include_recommendations=True,
        include_executive_summary=True,
        include_limitations=False,
        
        # Analyses
        statistical_rigor="low",
        hypothesis_testing=False,
        exploratory_analysis=False,
        predictive_modeling=False,
        
        # Visuels
        visualization_preference=VisualizationPreference.GRAPHS_HEAVY,
        min_graphs_percent=80,
        
        # Longueur
        default_length=ReportLength.CONCISE,
        
        # Sections
        mandatory_sections=[
            "Synthèse (3-5 points)",
            "Chiffres clés",
            "Actions recommandées"
        ],
        forbidden_sections=[
            "Méthodologie",
            "Analyses détaillées",
            "Tests statistiques",
            "Tableaux complexes"
        ],
        
        # Priorités
        analysis_priorities=[
            "Chiffres clés uniquement",
            "Décisions à prendre",
            "Risques majeurs",
            "Opportunités immédiates"
        ]
    )
}


# ════════════════════════════════════════════════════════════════════════
# GESTIONNAIRE DE PROFILS
# ════════════════════════════════════════════════════════════════════════

class UserProfileManager:
    """Gestionnaire central des profils utilisateurs"""
    
    def __init__(self, profile: UserProfile = UserProfile.INDUSTRY):
        """
        Initialise le gestionnaire avec un profil par défaut
        
        Args:
            profile: Profil utilisateur (par défaut: INDUSTRY)
        """
        self.current_profile = profile
        self.config = PROFILE_CONFIGS[profile]
        
        logger.info(f"Profile Manager initialized: {self.config.display_name}")
    
    def set_profile(self, profile: UserProfile):
        """Change le profil actif"""
        self.current_profile = profile
        self.config = PROFILE_CONFIGS[profile]
        logger.info(f"Profile changed to: {self.config.display_name}")
    
    def get_config(self) -> ProfileConfiguration:
        """Retourne la configuration du profil actuel"""
        return self.config
    
    def to_prompt_context(self) -> str:
        """
        Génère le contexte de profil pour injection dans le prompt
        Format : section à insérer dans le prompt système
        """
        config = self.config
        
        context = f"""
════════════════════════════════════════════════════════════════════════
PROFIL UTILISATEUR ACTIF : {config.display_name.upper()}
════════════════════════════════════════════════════════════════════════

📋 DESCRIPTION : {config.description}

🎯 STYLE RÉDACTIONNEL :
- Ton : {config.tone}
- Niveau technique : {config.technical_level}
- Jargon autorisé : {"OUI" if config.jargon_allowed else "NON"}

📊 STRUCTURE DU RAPPORT :
- Méthodologie : {"INCLURE" if config.include_methodology else "EXCLURE"}
- Théorie : {"INCLURE" if config.include_theory else "EXCLURE"}
- Recommandations : {"INCLURE" if config.include_recommendations else "EXCLURE"}
- Résumé exécutif : {"INCLURE" if config.include_executive_summary else "EXCLURE"}
- Limites : {"INCLURE" if config.include_limitations else "EXCLURE"}

🔬 ANALYSES :
- Rigueur statistique : {config.statistical_rigor}
- Tests d'hypothèses : {"OUI" if config.hypothesis_testing else "NON"}
- Analyse exploratoire : {"OUI" if config.exploratory_analysis else "NON"}
- Modélisation prédictive : {"OUI" if config.predictive_modeling else "NON"}

📈 VISUALISATIONS :
- Préférence : {config.visualization_preference.value}
- Minimum graphiques : {config.min_graphs_percent}%

📏 LONGUEUR PAR DÉFAUT : {config.default_length.value}

✅ SECTIONS OBLIGATOIRES :
{chr(10).join(f"  • {section}" for section in config.mandatory_sections)}

❌ SECTIONS INTERDITES :
{chr(10).join(f"  • {section}" for section in config.forbidden_sections)}

🎯 PRIORITÉS D'ANALYSE :
{chr(10).join(f"  {i+1}. {priority}" for i, priority in enumerate(config.analysis_priorities))}

════════════════════════════════════════════════════════════════════════
INSTRUCTION CRITIQUE : 
Vous DEVEZ adapter TOUT votre rapport selon ce profil.
Respectez SCRUPULEUSEMENT les sections obligatoires et interdites.
════════════════════════════════════════════════════════════════════════
"""
        return context
    
    def get_chapter_guidelines(self, chapter_title: str) -> str:
        """
        Génère des guidelines spécifiques pour un chapitre selon le profil
        
        Args:
            chapter_title: Titre du chapitre
        
        Returns:
            Guidelines contextualisées pour ce chapitre
        """
        config = self.config
        
        guidelines = f"""
🎯 GUIDELINES POUR CE CHAPITRE (Profil : {config.display_name})

"""
        
        # Adapter selon le type de chapitre
        chapter_lower = chapter_title.lower()
        
        # Introduction
        if "introduction" in chapter_lower:
            if config.include_executive_summary:
                guidelines += "✅ INCLURE : Résumé exécutif (3-5 points clés)\n"
            if config.include_methodology:
                guidelines += "✅ INCLURE : Aperçu méthodologique\n"
            else:
                guidelines += "❌ EXCLURE : Détails méthodologiques\n"
        
        # Méthodologie
        elif "méthodologie" in chapter_lower or "methodology" in chapter_lower:
            if not config.include_methodology:
                guidelines += "⚠️ ATTENTION : Ce chapitre ne devrait pas exister pour ce profil !\n"
            else:
                if config.profile == UserProfile.ACADEMIC:
                    guidelines += "✅ Détails complets : échantillonnage, instruments, procédures\n"
                elif config.profile == UserProfile.INS:
                    guidelines += "✅ Notes méthodologiques : représentativité, collecte, validité\n"
        
        # Analyses/Résultats
        elif any(kw in chapter_lower for kw in ["analyse", "résultat", "result", "analysis"]):
            if config.visualization_preference == VisualizationPreference.GRAPHS_HEAVY:
                guidelines += f"📊 MINIMUM {config.min_graphs_percent}% de graphiques\n"
            
            if config.statistical_rigor == "high":
                guidelines += "🔬 Rigueur maximale : p-values, intervalles de confiance, tests\n"
            elif config.statistical_rigor == "low":
                guidelines += "💡 Insights clairs : éviter jargon statistique\n"
            
            if config.hypothesis_testing:
                guidelines += "✅ Tests d'hypothèses REQUIS\n"
            else:
                guidelines += "❌ Pas de tests formels d'hypothèses\n"
        
        # Conclusion
        elif "conclusion" in chapter_lower:
            if config.include_recommendations:
                guidelines += "✅ INCLURE : Recommandations actionnables\n"
            else:
                guidelines += "❌ EXCLURE : Recommandations (rester factuel)\n"
            
            if config.include_limitations:
                guidelines += "✅ INCLURE : Limites de l'étude\n"
            else:
                guidelines += "❌ EXCLURE : Limites (focus sur résultats)\n"
        
        # Longueur
        length_words = {
            ReportLength.CONCISE: (300, 900),
            ReportLength.STANDARD: (1200, 2100),
            ReportLength.DETAILED: (2400, 4500),
            ReportLength.EXHAUSTIVE: (4800, 9000)
        }
        
        min_words, max_words = length_words[config.default_length]
        guidelines += f"\n📏 LONGUEUR CIBLE : {min_words}-{max_words} mots\n"
        
        return guidelines
    
    def validate_chapter_structure(self, chapter_title: str) -> Dict:
        """
        Valide si un chapitre est autorisé selon le profil
        
        Returns:
            {
                'allowed': bool,
                'reason': str (si not allowed),
                'warnings': List[str]
            }
        """