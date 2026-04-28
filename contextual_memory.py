"""
Contextual Memory System - Mémoire contextuelle pour génération de chapitres
Permet à l'IA de se souvenir des chapitres précédents pour éviter les répétitions
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class ChapterSummary:
    """Résumé d'un chapitre généré"""
    chapter_number: str
    chapter_title: str
    content_summary: str  # Résumé du contenu (2-3 phrases)
    key_findings: List[str]  # Points clés mentionnés
    variables_analyzed: List[str]  # Variables statistiques utilisées
    graphs_created: List[str]  # Types de graphiques créés
    generated_at: str
    word_count: int
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class ContextualMemory:
    """
    Système de mémoire contextuelle pour la génération de rapports
    
    Fonctionnalités:
    - Stocke résumés des chapitres générés
    - Fournit contexte cumulatif à l'IA
    - Détecte répétitions potentielles
    - Suggère contenu complémentaire
    """
    
    def __init__(self, storage_dir: str = "memory"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.memories: Dict[str, List[ChapterSummary]] = {}  # user_id -> [summaries]
    
    def add_chapter(
        self,
        user_id: str,
        chapter_number: str,
        chapter_title: str,
        content: str,
        metadata: Dict = None
    ) -> ChapterSummary:
        """
        Ajoute un chapitre à la mémoire
        
        Args:
            user_id: ID utilisateur
            chapter_number: Numéro du chapitre (ex: "1", "2.1")
            chapter_title: Titre du chapitre
            content: Contenu complet du chapitre (Markdown)
            metadata: Métadonnées additionnelles
        
        Returns:
            ChapterSummary créé
        """
        logger.info(f"Adding chapter {chapter_number} to memory for user {user_id}")
        
        # Extraire informations du contenu
        summary = self._generate_summary(content)
        key_findings = self._extract_key_findings(content)
        variables = self._extract_variables(content, metadata)
        graphs = self._extract_graphs(content)
        
        chapter_summary = ChapterSummary(
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            content_summary=summary,
            key_findings=key_findings,
            variables_analyzed=variables,
            graphs_created=graphs,
            generated_at=datetime.now().isoformat(),
            word_count=len(content.split())
        )
        
        # Ajouter à la mémoire
        if user_id not in self.memories:
            self.memories[user_id] = []
        
        self.memories[user_id].append(chapter_summary)
        
        # Sauvegarder sur disque
        self._save_memory(user_id)
        
        return chapter_summary
    
    def get_context_for_next_chapter(
        self,
        user_id: str,
        next_chapter_number: str
    ) -> str:
        """
        Génère le contexte à fournir à l'IA pour le prochain chapitre
        
        Args:
            user_id: ID utilisateur
            next_chapter_number: Numéro du prochain chapitre
        
        Returns:
            Contexte formaté en texte
        """
        if user_id not in self.memories or not self.memories[user_id]:
            return "C'est le premier chapitre du rapport. Aucun chapitre précédent."
        
        summaries = self.memories[user_id]
        
        context = f"""
CONTEXTE DES CHAPITRES PRÉCÉDENTS :

Tu vas générer le Chapitre {next_chapter_number}. Voici ce qui a déjà été écrit :

"""
        
        for i, summary in enumerate(summaries, 1):
            context += f"""
─────────────────────────────────────────────
CHAPITRE {summary.chapter_number} : {summary.chapter_title}

Résumé du contenu :
{summary.content_summary}

Points clés mentionnés :
{chr(10).join(f"• {finding}" for finding in summary.key_findings)}

Variables analysées :
{", ".join(summary.variables_analyzed) if summary.variables_analyzed else "Aucune"}

Graphiques créés :
{", ".join(summary.graphs_created) if summary.graphs_created else "Aucun"}

Longueur : {summary.word_count} mots
─────────────────────────────────────────────

"""
        
        context += f"""
INSTRUCTIONS POUR LE CHAPITRE {next_chapter_number} :

1. NE PAS RÉPÉTER les analyses déjà faites dans les chapitres précédents
2. FAIRE RÉFÉRENCE aux chapitres précédents si nécessaire ("Comme vu au Chapitre X...")
3. APPORTER des analyses COMPLÉMENTAIRES et NOUVELLES
4. UTILISER des variables pas encore analysées en profondeur
5. CRÉER des graphiques DIFFÉRENTS de ceux déjà créés

Variables déjà analysées : {self._get_all_analyzed_variables(user_id)}
Graphiques déjà créés : {self._get_all_created_graphs(user_id)}

Maintenant, génère le Chapitre {next_chapter_number} en tenant compte de tout ce contexte.
"""
        
        return context
    
    def _generate_summary(self, content: str) -> str:
        """Génère un résumé court du contenu (2-3 phrases)"""
        # Pour l'instant, extraction simple des premières lignes
        # TODO: Utiliser un modèle de summarization si besoin
        
        lines = content.split('\n')
        paragraphs = [line for line in lines if len(line.strip()) > 50]
        
        if len(paragraphs) >= 3:
            summary = ' '.join(paragraphs[:3])
        elif paragraphs:
            summary = ' '.join(paragraphs)
        else:
            summary = content[:300]
        
        # Limiter à 300 caractères
        if len(summary) > 300:
            summary = summary[:297] + "..."
        
        return summary
    
    def _extract_key_findings(self, content: str) -> List[str]:
        """Extrait les points clés du contenu"""
        findings = []
        
        # Chercher des patterns comme "On observe que...", "Il apparaît que..."
        patterns = [
            "on observe que",
            "il apparaît que",
            "les résultats montrent",
            "en conclusion",
            "nous constatons que"
        ]
        
        for line in content.split('\n'):
            line_lower = line.lower()
            for pattern in patterns:
                if pattern in line_lower:
                    # Nettoyer et ajouter
                    finding = line.strip().lstrip('-•*').strip()
                    if finding and len(finding) < 200:
                        findings.append(finding)
                    break
        
        return findings[:5]  # Max 5 findings
    
    def _extract_variables(self, content: str, metadata: Dict = None) -> List[str]:
        """Extrait les variables statistiques mentionnées"""
        variables = set()
        
        # Si metadata fourni avec liste de colonnes
        if metadata and 'columns' in metadata:
            for col in metadata['columns']:
                if col.lower() in content.lower():
                    variables.add(col)
        
        # Sinon, chercher des patterns statistiques
        else:
            # Patterns communs : "variable X", "la variable X", etc.
            import re
            pattern = r"(?:variable|colonne)\s+['\"]?(\w+)['\"]?"
            matches = re.findall(pattern, content, re.IGNORECASE)
            variables.update(matches)
        
        return list(variables)
    
    def _extract_graphs(self, content: str) -> List[str]:
        """Extrait les types de graphiques créés"""
        graphs = []
        
        graph_keywords = {
            'histogramme': 'Histogramme',
            'histogram': 'Histogramme',
            'scatter': 'Nuage de points',
            'boxplot': 'Boîte à moustaches',
            'barplot': 'Diagramme en barres',
            'bar chart': 'Diagramme en barres',
            'pie chart': 'Camembert',
            'line plot': 'Graphique linéaire',
            'heatmap': 'Carte de chaleur'
        }
        
        content_lower = content.lower()
        
        for keyword, graph_name in graph_keywords.items():
            if keyword in content_lower:
                graphs.append(graph_name)
        
        return list(set(graphs))  # Enlever doublons
    
    def _get_all_analyzed_variables(self, user_id: str) -> str:
        """Retourne toutes les variables déjà analysées"""
        if user_id not in self.memories:
            return "Aucune"
        
        all_vars = set()
        for summary in self.memories[user_id]:
            all_vars.update(summary.variables_analyzed)
        
        return ", ".join(sorted(all_vars)) if all_vars else "Aucune"
    
    def _get_all_created_graphs(self, user_id: str) -> str:
        """Retourne tous les graphiques déjà créés"""
        if user_id not in self.memories:
            return "Aucun"
        
        all_graphs = []
        for summary in self.memories[user_id]:
            all_graphs.extend(summary.graphs_created)
        
        # Compter occurrences
        from collections import Counter
        graph_counts = Counter(all_graphs)
        
        result = ", ".join(f"{graph} (×{count})" for graph, count in graph_counts.most_common())
        
        return result if result else "Aucun"
    
    def _save_memory(self, user_id: str):
        """Sauvegarde la mémoire sur disque"""
        if user_id not in self.memories:
            return
        
        filepath = self.storage_dir / f"{user_id}_memory.json"
        
        data = {
            'user_id': user_id,
            'updated_at': datetime.now().isoformat(),
            'chapters': [summary.to_dict() for summary in self.memories[user_id]]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Memory saved for user {user_id}: {len(self.memories[user_id])} chapters")
    
    def load_memory(self, user_id: str) -> bool:
        """Charge la mémoire depuis le disque"""
        filepath = self.storage_dir / f"{user_id}_memory.json"
        
        if not filepath.exists():
            logger.info(f"No saved memory for user {user_id}")
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.memories[user_id] = [
                ChapterSummary.from_dict(chapter_data)
                for chapter_data in data['chapters']
            ]
            
            logger.info(f"Memory loaded for user {user_id}: {len(self.memories[user_id])} chapters")
            return True
        
        except Exception as e:
            logger.error(f"Failed to load memory for user {user_id}: {e}")
            return False
    
    def clear_memory(self, user_id: str):
        """Efface la mémoire d'un utilisateur"""
        if user_id in self.memories:
            del self.memories[user_id]
        
        filepath = self.storage_dir / f"{user_id}_memory.json"
        if filepath.exists():
            filepath.unlink()
        
        logger.info(f"Memory cleared for user {user_id}")
    
    def get_summary(self, user_id: str) -> Dict:
        """Retourne un résumé de la mémoire"""
        if user_id not in self.memories or not self.memories[user_id]:
            return {
                'total_chapters': 0,
                'total_words': 0,
                'variables_analyzed': [],
                'graphs_created': []
            }
        
        summaries = self.memories[user_id]
        
        all_vars = set()
        all_graphs = []
        total_words = 0
        
        for summary in summaries:
            all_vars.update(summary.variables_analyzed)
            all_graphs.extend(summary.graphs_created)
            total_words += summary.word_count
        
        return {
            'total_chapters': len(summaries),
            'total_words': total_words,
            'variables_analyzed': sorted(all_vars),
            'graphs_created': list(set(all_graphs)),
            'chapters': [
                {
                    'number': s.chapter_number,
                    'title': s.chapter_title,
                    'words': s.word_count
                }
                for s in summaries
            ]
        }


# Instance globale
contextual_memory = ContextualMemory()


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def add_chapter_to_memory(
    user_id: str,
    chapter_number: str,
    chapter_title: str,
    content: str,
    metadata: Dict = None
) -> ChapterSummary:
    """
    Ajoute un chapitre à la mémoire contextuelle
    
    Usage:
        summary = add_chapter_to_memory(
            user_id='user123',
            chapter_number='1',
            chapter_title='Introduction',
            content='# Introduction\n\nCe rapport analyse...',
            metadata={'columns': ['age', 'salaire', 'ville']}
        )
    """
    return contextual_memory.add_chapter(
        user_id, chapter_number, chapter_title, content, metadata
    )


def get_context_for_chapter(user_id: str, next_chapter: str) -> str:
    """
    Récupère le contexte pour générer le prochain chapitre
    
    Usage:
        context = get_context_for_chapter('user123', '2')
        
        prompt = f'''
        {context}
        
        Génère maintenant le Chapitre 2 en tenant compte du contexte ci-dessus.
        '''
    """
    return contextual_memory.get_context_for_next_chapter(user_id, next_chapter)


def display_memory_in_streamlit(user_id: str):
    """
    Affiche la mémoire contextuelle dans Streamlit
    
    Usage:
        display_memory_in_streamlit(st.session_state.user_id)
    """
    try:
        import streamlit as st
    except ImportError:
        # Streamlit pas disponible, fonction ne fait rien
        return
    
    summary = contextual_memory.get_summary(user_id)
    
    if summary['total_chapters'] == 0:
        st.info("Aucun chapitre généré pour l'instant")
        return
    
    with st.expander(f"🧠 Mémoire Contextuelle ({summary['total_chapters']} chapitres)", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Chapitres", summary['total_chapters'])
        with col2:
            st.metric("Mots totaux", f"{summary['total_words']:,}")
        with col3:
            st.metric("Variables", len(summary['variables_analyzed']))
        
        st.markdown("**Chapitres générés:**")
        for chapter in summary['chapters']:
            st.caption(f"• {chapter['number']}. {chapter['title']} ({chapter['words']} mots)")
        
        st.markdown("**Variables analysées:**")
        st.caption(", ".join(summary['variables_analyzed']) if summary['variables_analyzed'] else "Aucune")
        
        st.markdown("**Graphiques créés:**")
        st.caption(", ".join(summary['graphs_created']) if summary['graphs_created'] else "Aucun")
        
        if st.button("Effacer la mémoire"):
            contextual_memory.clear_memory(user_id)
            st.success("Mémoire effacée")
            st.rerun()


# ============================================
# TESTS
# ============================================

if __name__ == "__main__":
    """Tests du système de mémoire"""
    
    print("="*60)
    print("TEST CONTEXTUAL MEMORY")
    print("="*60)
    
    # Test 1: Ajouter chapitre 1
    print("\n1. Ajout Chapitre 1...")
    content1 = """
    # Introduction
    
    Ce rapport analyse les données démographiques et salariales.
    On observe que l'âge moyen est de 35 ans.
    
    La variable age montre une distribution normale.
    Un histogramme a été créé pour visualiser la distribution.
    """
    
    summary1 = add_chapter_to_memory(
        'test_user',
        '1',
        'Introduction',
        content1,
        {'columns': ['age', 'salaire', 'ville']}
    )
    
    print(f"✅ Chapitre 1 ajouté")
    print(f"   Résumé: {summary1.content_summary}")
    print(f"   Variables: {summary1.variables_analyzed}")
    print(f"   Graphiques: {summary1.graphs_created}")
    
    # Test 2: Ajouter chapitre 2
    print("\n2. Ajout Chapitre 2...")
    content2 = """
    # Analyse descriptive
    
    Comme vu au Chapitre 1, l'âge moyen est de 35 ans.
    
    Nous analysons maintenant la variable salaire.
    Un boxplot montre la distribution des salaires.
    Les résultats montrent une forte variabilité.
    """
    
    summary2 = add_chapter_to_memory(
        'test_user',
        '2',
        'Analyse descriptive',
        content2,
        {'columns': ['age', 'salaire', 'ville']}
    )
    
    print(f"✅ Chapitre 2 ajouté")
    
    # Test 3: Générer contexte pour chapitre 3
    print("\n3. Contexte pour Chapitre 3...")
    context = get_context_for_chapter('test_user', '3')
    print("✅ Contexte généré:")
    print(context[:500] + "...\n")
    
    # Test 4: Résumé mémoire
    print("\n4. Résumé de la mémoire...")
    summary = contextual_memory.get_summary('test_user')
    print(f"✅ Total chapitres: {summary['total_chapters']}")
    print(f"   Total mots: {summary['total_words']}")
    print(f"   Variables: {summary['variables_analyzed']}")
    print(f"   Graphiques: {summary['graphs_created']}")
    
    # Test 5: Sauvegarde/Chargement
    print("\n5. Test sauvegarde/chargement...")
    contextual_memory._save_memory('test_user')
    contextual_memory.clear_memory('test_user')
    print("   Mémoire effacée")
    
    contextual_memory.load_memory('test_user')
    summary_after_load = contextual_memory.get_summary('test_user')
    print(f"✅ Mémoire rechargée: {summary_after_load['total_chapters']} chapitres")
    
    # Cleanup
    contextual_memory.clear_memory('test_user')
    print("\n✅ Tests terminés")