"""
Study Context Management
Gère le contexte de l'étude et les profils de rédaction
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum
import json


class WritingProfile(Enum):
    """Profils de rédaction selon le public cible"""
    ACADEMIC = "academic"
    CONSULTANT = "consultant"
    INSTITUTIONAL = "institutional"
    
    @property
    def display_name(self) -> str:
        names = {
            "academic": "🎓 Académique (Chercheurs, Universitaires)",
            "consultant": "💼 Consultant (Décideurs, Managers)",
            "institutional": "🏛️ Institutionnel (Bailleurs, Administrations)"
        }
        return names.get(self.value, self.value)
    
    @property
    def description(self) -> str:
        descriptions = {
            "academic": "Analyse détaillée, méthodologique, ton scientifique",
            "consultant": "Insights actionnables, messages clés, orienté décision",
            "institutional": "Factuel, transparent, formel, évite le jargon"
        }
        return descriptions.get(self.value, "")


@dataclass
class StudyContext:
    """
    Contexte complet de l'étude
    
    Attributes:
        study_title: Titre de l'étude
        research_question: Question de recherche principale
        objectives: Liste des objectifs spécifiques
        hypotheses: Liste des hypothèses à tester
        target_audience: Public cible du rapport
        writing_profile: Profil de rédaction (academic/consultant/institutional)
        reporting_style: Style de rapport (détaillé, synthétique, exécutif)
        specific_instructions: Instructions spécifiques pour la génération
    """
    study_title: Optional[str] = None
    research_question: Optional[str] = None
    objectives: List[str] = field(default_factory=list)
    hypotheses: List[str] = field(default_factory=list)
    target_audience: Optional[str] = None
    writing_profile: WritingProfile = WritingProfile.ACADEMIC
    reporting_style: str = "Détaillé"
    specific_instructions: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire"""
        return {
            'study_title': self.study_title,
            'research_question': self.research_question,
            'objectives': self.objectives,
            'hypotheses': self.hypotheses,
            'target_audience': self.target_audience,
            'writing_profile': self.writing_profile.value if isinstance(self.writing_profile, WritingProfile) else self.writing_profile,
            'reporting_style': self.reporting_style,
            'specific_instructions': self.specific_instructions
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StudyContext':
        """Crée depuis un dictionnaire"""
        # Convertir writing_profile string → Enum
        writing_profile = data.get('writing_profile', 'academic')
        if isinstance(writing_profile, str):
            try:
                writing_profile = WritingProfile(writing_profile)
            except ValueError:
                writing_profile = WritingProfile.ACADEMIC
        
        return cls(
            study_title=data.get('study_title'),
            research_question=data.get('research_question'),
            objectives=data.get('objectives', []),
            hypotheses=data.get('hypotheses', []),
            target_audience=data.get('target_audience'),
            writing_profile=writing_profile,
            reporting_style=data.get('reporting_style', 'Détaillé'),
            specific_instructions=data.get('specific_instructions')
        )
    
    def to_json(self, filepath: str):
        """Sauvegarde en JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, filepath: str) -> 'StudyContext':
        """Charge depuis JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def to_prompt_context(self) -> str:
        """
        Génère le contexte à injecter dans le prompt
        Inclut le profil de rédaction
        """
        sections = []
        
        if self.study_title:
            sections.append(f"📌 **TITRE** : {self.study_title}")
        
        if self.research_question:
            sections.append(f"❓ **QUESTION DE RECHERCHE** : {self.research_question}")
        
        if self.objectives:
            obj_list = "\n".join(f"  {i+1}. {obj}" for i, obj in enumerate(self.objectives))
            sections.append(f"🎯 **OBJECTIFS** :\n{obj_list}")
        
        if self.hypotheses:
            hyp_list = "\n".join(f"  H{i+1}. {hyp}" for i, hyp in enumerate(self.hypotheses))
            sections.append(f"🔬 **HYPOTHÈSES** :\n{hyp_list}")
        
        if self.target_audience:
            sections.append(f"👥 **PUBLIC CIBLE** : {self.target_audience}")
        
        # NOUVEAU : Ajouter le profil de rédaction
        sections.append(f"✍️ **PROFIL DE RÉDACTION** : {self.writing_profile.display_name}")
        
        if self.specific_instructions:
            sections.append(f"📝 **INSTRUCTIONS SPÉCIFIQUES** :\n{self.specific_instructions}")
        
        return "\n\n".join(sections)
    
    def get_writing_style_block(self) -> str:
        """
        Retourne le bloc de style d'écriture selon le profil
        À injecter dans le prompt de génération
        """
        from writing_profiles import get_writing_style_block
        return get_writing_style_block(self.writing_profile)
    
    def is_empty(self) -> bool:
        """Vérifie si le contexte est vide"""
        return not any([
            self.study_title,
            self.research_question,
            self.objectives,
            self.hypotheses
        ])


# Instance globale (pour compatibilité avec code existant)
study_context = None