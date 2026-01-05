"""
Système de contrôle des coûts et de la longueur des chapitres
Permet à l'utilisateur de définir la longueur de chaque chapitre (1-30 pages)
"""

from dataclasses import dataclass
from typing import Dict, Optional
import json
from pathlib import Path


@dataclass
class ChapterConfig:
    """Configuration de longueur pour un chapitre"""
    chapter_number: int
    chapter_title: str
    target_pages: int  # 1-30 pages
    words_per_page: int = 300  # Standard académique
    
    @property
    def target_words(self) -> int:
        """Calcule le nombre de mots cible basé sur les pages"""
        return self.target_pages * self.words_per_page
    
    @property
    def min_words(self) -> int:
        """Minimum de mots (90% de la cible)"""
        return int(self.target_words * 0.9)
    
    @property
    def max_words(self) -> int:
        """Maximum de mots (110% de la cible)"""
        return int(self.target_words * 1.1)
    
    @property
    def estimated_tokens(self) -> int:
        """Estime les tokens nécessaires (mots × 1.3 en moyenne)"""
        return int(self.target_words * 1.3)
    
    @property
    def estimated_cost_usd(self) -> float:
        """Estime le coût en USD (basé sur Gemini 2.0 Flash)"""
        # Gemini 2.0 Flash : $0.075 / 1M input tokens, $0.30 / 1M output tokens
        # En moyenne : ~2000 tokens input + output tokens
        input_tokens = 2000  # Context + prompt
        output_tokens = self.estimated_tokens
        
        input_cost = (input_tokens / 1_000_000) * 0.075
        output_cost = (output_tokens / 1_000_000) * 0.30
        
        return input_cost + output_cost


class CostController:
    """Contrôleur de coûts pour tout le rapport"""
    
    def __init__(self):
        self.chapter_configs: Dict[int, ChapterConfig] = {}
        self.default_pages = 5  # Par défaut : 5 pages par chapitre
    
    def set_chapter_length(self, chapter_number: int, chapter_title: str, pages: int):
        """
        Définit la longueur d'un chapitre
        
        Args:
            chapter_number: Numéro du chapitre
            chapter_title: Titre du chapitre
            pages: Nombre de pages souhaité (1-30)
        """
        if not 1 <= pages <= 30:
            raise ValueError("Le nombre de pages doit être entre 1 et 30")
        
        self.chapter_configs[chapter_number] = ChapterConfig(
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            target_pages=pages
        )
    
    def get_chapter_config(self, chapter_number: int) -> Optional[ChapterConfig]:
        """Récupère la config d'un chapitre"""
        return self.chapter_configs.get(chapter_number)
    
    def get_total_pages(self) -> int:
        """Calcule le nombre total de pages du rapport"""
        return sum(config.target_pages for config in self.chapter_configs.values())
    
    def get_total_words(self) -> int:
        """Calcule le nombre total de mots du rapport"""
        return sum(config.target_words for config in self.chapter_configs.values())
    
    def get_total_estimated_cost(self) -> float:
        """Calcule le coût total estimé en USD"""
        return sum(config.estimated_cost_usd for config in self.chapter_configs.values())
    
    def get_summary(self) -> Dict:
        """Retourne un résumé complet des coûts"""
        return {
            'total_chapters': len(self.chapter_configs),
            'total_pages': self.get_total_pages(),
            'total_words': self.get_total_words(),
            'estimated_cost_usd': self.get_total_estimated_cost(),
            'chapters': [
                {
                    'number': config.chapter_number,
                    'title': config.chapter_title,
                    'pages': config.target_pages,
                    'words': config.target_words,
                    'cost_usd': config.estimated_cost_usd
                }
                for config in sorted(self.chapter_configs.values(), key=lambda x: x.chapter_number)
            ]
        }
    
    def save_to_file(self, filepath: str):
        """Sauvegarde la configuration dans un fichier JSON"""
        data = {
            'default_pages': self.default_pages,
            'chapters': {
                str(num): {
                    'chapter_number': config.chapter_number,
                    'chapter_title': config.chapter_title,
                    'target_pages': config.target_pages
                }
                for num, config in self.chapter_configs.items()
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, filepath: str):
        """Charge la configuration depuis un fichier JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.default_pages = data.get('default_pages', 5)
        
        for num_str, config_data in data.get('chapters', {}).items():
            self.chapter_configs[int(num_str)] = ChapterConfig(
                chapter_number=config_data['chapter_number'],
                chapter_title=config_data['chapter_title'],
                target_pages=config_data['target_pages']
            )


def get_length_guidelines(pages: int) -> str:
    """
    Retourne des guidelines de longueur pour Gemini
    
    Args:
        pages: Nombre de pages cible
    
    Returns:
        Instructions formatées pour le prompt
    """
    config = ChapterConfig(
        chapter_number=0,
        chapter_title="",
        target_pages=pages
    )
    
    if pages <= 2:
        detail_level = "concis et synthétique"
        sections = "2-3 sections principales"
        graphs = "1-2 graphiques maximum"
    elif pages <= 5:
        detail_level = "standard et équilibré"
        sections = "3-5 sections"
        graphs = "2-3 graphiques"
    elif pages <= 10:
        detail_level = "détaillé et approfondi"
        sections = "5-7 sections"
        graphs = "3-5 graphiques"
    elif pages <= 20:
        detail_level = "très détaillé et exhaustif"
        sections = "7-10 sections"
        graphs = "5-8 graphiques"
    else:  # > 20
        detail_level = "extrêmement détaillé et complet"
        sections = "10+ sections"
        graphs = "8+ graphiques"
    
    guidelines = f"""
CONTRAINTES DE LONGUEUR :
- Longueur cible : {pages} pages ({config.target_words} mots environ)
- Minimum acceptable : {config.min_words} mots
- Maximum acceptable : {config.max_words} mots
- Style : {detail_level}
- Structure : {sections}
- Visualisations : {graphs}

INSTRUCTIONS DE RÉDACTION :
- Rédigez un chapitre de EXACTEMENT {pages} pages (±10%)
- Soyez {detail_level}
- Incluez {sections} bien structurées
- Ajoutez {graphs} pour illustrer vos analyses
- NE PAS dépasser {config.max_words} mots
- NE PAS être en dessous de {config.min_words} mots
"""
    
    return guidelines


# Instance globale
cost_controller = CostController()


# Fonction helper pour Streamlit
def display_cost_summary_in_streamlit(controller: CostController):
    """
    Affiche un résumé des coûts dans Streamlit
    
    Usage:
        display_cost_summary_in_streamlit(cost_controller)
    """
    try:
        import streamlit as st
    except ImportError:
        return
    
    summary = controller.get_summary()
    
    if summary['total_chapters'] == 0:
        st.info("Aucune configuration de longueur définie")
        return
    
    with st.expander("💰 Estimation des coûts et longueur", expanded=True):
        # Métriques globales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Chapitres", summary['total_chapters'])
        
        with col2:
            st.metric("Pages totales", summary['total_pages'])
        
        with col3:
            st.metric("Mots totaux", f"{summary['total_words']:,}")
        
        with col4:
            cost = summary['estimated_cost_usd']
            st.metric("Coût estimé", f"${cost:.3f}")
        
        # Détails par chapitre
        st.markdown("#### 📊 Détails par chapitre")
        
        for chapter in summary['chapters']:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.caption(f"**Ch. {chapter['number']}** : {chapter['title']}")
            
            with col2:
                st.caption(f"📄 {chapter['pages']} pages")
            
            with col3:
                st.caption(f"📝 {chapter['words']:,} mots")
            
            with col4:
                st.caption(f"💰 ${chapter['cost_usd']:.3f}")
        
        # Avertissement si coût élevé
        if cost > 0.10:
            st.warning(f"⚠️ Coût estimé élevé : ${cost:.3f}. Considérez réduire la longueur de certains chapitres.")
        elif cost > 0.05:
            st.info(f"ℹ️ Coût modéré : ${cost:.3f}")
        else:
            st.success(f"✅ Coût faible : ${cost:.3f}")


if __name__ == "__main__":
    # Tests
    controller = CostController()
    
    # Définir la longueur de quelques chapitres
    controller.set_chapter_length(1, "Introduction", 3)
    controller.set_chapter_length(2, "Analyse descriptive", 8)
    controller.set_chapter_length(3, "Analyse inférentielle", 10)
    controller.set_chapter_length(4, "Modélisation", 12)
    controller.set_chapter_length(5, "Conclusion", 2)
    
    # Afficher le résumé
    summary = controller.get_summary()
    print(f"Total pages: {summary['total_pages']}")
    print(f"Total mots: {summary['total_words']:,}")
    print(f"Coût estimé: ${summary['estimated_cost_usd']:.3f}")
    
    # Test des guidelines
    print("\n" + get_length_guidelines(5))