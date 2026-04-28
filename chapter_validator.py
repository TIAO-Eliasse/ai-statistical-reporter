"""
Validation post-génération avancée
Système de contrôle qualité pour les chapitres générés

Utilisation standalone ou intégré dans le workflow
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Niveau de gravité d'un problème"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Représente un problème détecté"""
    severity: ValidationSeverity
    category: str
    message: str
    line_number: Optional[int] = None
    context: Optional[str] = None


class ChapterValidator:
    """
    Validateur avancé de chapitres
    Détecte problèmes de qualité avant livraison
    """
    
    def __init__(self, config=None):
        """
        Args:
            config: ReportConfig (optionnel, pour validations spécifiques au mode)
        """
        self.config = config
        self.issues: List[ValidationIssue] = []
    
    def validate(self, content: str, chapter_number: str = None) -> Dict:
        """
        Validation complète d'un chapitre
        
        Returns:
            {
                'is_valid': bool,
                'score': float (0-100),
                'issues': List[ValidationIssue],
                'summary': Dict
            }
        """
        self.issues = []
        
        logger.info(f"Validating chapter {chapter_number}...")
        
        # Exécuter toutes les validations
        self._validate_structure(content)
        self._validate_duplications(content)
        self._validate_code_visibility(content)
        self._validate_data_consistency(content)
        self._validate_style(content)
        self._validate_length(content)
        self._validate_content_quality(content)
        
        if self.config:
            self._validate_mode_compliance(content)
        
        # Calculer score
        score = self._calculate_score()
        
        # Résumé
        summary = self._generate_summary()
        
        logger.info(f"Validation complete: score={score:.1f}/100, issues={len(self.issues)}")
        
        return {
            'is_valid': score >= 70,
            'score': score,
            'issues': self.issues,
            'summary': summary
        }
    
    # ═════════════════════════════════════════════════════════════
    # VALIDATIONS INDIVIDUELLES
    # ═════════════════════════════════════════════════════════════
    
    def _validate_structure(self, content: str):
        """Valide la structure Markdown"""
        
        # Vérifier présence titre principal ##
        if not re.search(r'^##\s+\d+\.', content, re.MULTILINE):
            self.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category="Structure",
                message="Titre principal manquant (## X. Titre)"
            ))
        
        # Vérifier hiérarchie headers (## puis ### puis ####)
        headers = re.findall(r'^(#{2,4})\s+', content, re.MULTILINE)
        
        previous_level = 0
        for header in headers:
            level = len(header)
            if level > previous_level + 1:
                self.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="Structure",
                    message=f"Saut de niveau de header : {previous_level} → {level}"
                ))
            previous_level = level
        
        # Vérifier sections vides
        sections = re.split(r'^###\s+', content, flags=re.MULTILINE)
        for i, section in enumerate(sections[1:], 1):  # Skip intro
            section_content = section.split('\n\n', 1)
            if len(section_content) < 2 or len(section_content[1].strip()) < 50:
                self.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="Structure",
                    message=f"Section {i} très courte ou vide"
                ))
    
    def _validate_duplications(self, content: str):
        """Détecte duplications de contenu"""
        
        # 1. Titres en double
        titles = re.findall(r'\*\*(.*?)\*\*', content)
        title_counts = {}
        for t in titles:
            title_counts[t] = title_counts.get(t, 0) + 1
        
        duplicates = {t: c for t, c in title_counts.items() if c > 1}
        for title, count in duplicates.items():
            self.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category="Duplication",
                message=f"Titre dupliqué {count}x : '{title[:50]}...'"
            ))
        
        # 2. Tableaux identiques
        tables = re.findall(r'(\|.*?\|(?:\n\|.*?\|)+)', content, re.MULTILINE)
        if len(tables) != len(set(tables)):
            self.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category="Duplication",
                message=f"Tableaux identiques répétés"
            ))
        
        # 3. Paragraphes longs dupliqués
        paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 100]
        if len(paragraphs) != len(set(paragraphs)):
            duplicated = [p for p in paragraphs if paragraphs.count(p) > 1]
            for para in set(duplicated):
                self.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="Duplication",
                    message=f"Paragraphe dupliqué : '{para[:50]}...'"
                ))
    
    def _validate_code_visibility(self, content: str):
        """Vérifie que le code Python n'est pas visible"""
        
        # Blocs ```python
        python_blocks = re.findall(r'```python', content)
        if python_blocks:
            self.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="Code",
                message=f"{len(python_blocks)} blocs Python visibles dans le texte!"
            ))
        
        # Code inline suspect
        inline_code = re.findall(r'df\[.*?\]|pd\.read_csv|plt\.', content)
        if inline_code:
            self.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="Code",
                message=f"Code Python potentiellement visible : {inline_code[:3]}"
            ))
    
    def _validate_data_consistency(self, content: str):
        """Vérifie cohérence des données citées"""
        
        # Extraire tous les pourcentages
        percentages = re.findall(r'(\w+).*?(\d+\.?\d*)%', content)
        
        # Vérifier cohérence (même entité = même %)
        entity_pcts = {}
        for entity, pct in percentages:
            if entity in entity_pcts:
                if abs(float(pct) - entity_pcts[entity]) > 0.1:
                    self.issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category="Cohérence",
                        message=f"Pourcentages incohérents pour '{entity}': {entity_pcts[entity]}% vs {pct}%"
                    ))
            else:
                entity_pcts[entity] = float(pct)
        
        # Vérifier totaux (somme = 100%)
        # Rechercher patterns "Total : X%"
        totals = re.findall(r'Total.*?(\d+\.?\d*)%', content)
        for total in totals:
            total_val = float(total)
            if abs(total_val - 100.0) > 0.5:
                self.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="Cohérence",
                    message=f"Total ne fait pas 100% : {total_val}%"
                ))
    
    def _validate_style(self, content: str):
        """Valide le style rédactionnel"""
        
        # Détecter marqueurs scolaires (si pas mode académique)
        if self.config and self.config.mode.value != "academic":
            school_markers = re.findall(
                r'\*\*(Interprétation|Analyse|Discussion|Résultat)\s*:\*\*',
                content
            )
            if school_markers:
                self.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="Style",
                    message=f"Marqueurs scolaires détectés : {set(school_markers)}"
                ))
        
        # Détecter jargon excessif (mode INS)
        if self.config and self.config.mode.value == "institutional":
            jargon_terms = [
                'endogénéité', 'hétéroscédasticité', 'multicolinéarité',
                'autocorrélation', 'régression OLS', 'p-value'
            ]
            
            for term in jargon_terms:
                if term.lower() in content.lower():
                    self.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category="Style",
                        message=f"Jargon technique en mode INS : '{term}'"
                    ))
        
        # Vérifier phrases trop longues (>40 mots)
        sentences = re.split(r'[.!?]+', content)
        long_sentences = [s for s in sentences if len(s.split()) > 40]
        if len(long_sentences) > 5:
            self.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="Style",
                message=f"{len(long_sentences)} phrases très longues (>40 mots)"
            ))
    
    def _validate_length(self, content: str):
        """Valide la longueur selon config"""
        
        word_count = len(content.split())
        char_count = len(content)
        
        # Longueurs attendues selon verbosity
        expected_ranges = {
            'concise': (3000, 8000),
            'standard': (8000, 20000),
            'detailed': (20000, 50000)
        }
        
        if self.config:
            verbosity = self.config.verbosity.value
            min_words, max_words = expected_ranges.get(verbosity, (5000, 30000))
            
            if word_count < min_words * 0.5:
                self.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="Longueur",
                    message=f"Chapitre court : {word_count} mots (attendu: {min_words}-{max_words})"
                ))
            elif word_count > max_words * 1.5:
                self.issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="Longueur",
                    message=f"Chapitre long : {word_count} mots (attendu: {min_words}-{max_words})"
                ))
        
        # Minimum absolu
        if word_count < 200:
            self.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="Longueur",
                message=f"Contenu trop court : {word_count} mots (min: 200)"
            ))
    
    def _validate_content_quality(self, content: str):
        """Valide qualité du contenu"""
        
        # Vérifier présence de chiffres/données
        numbers = re.findall(r'\d+\.?\d*', content)
        if len(numbers) < 10:
            self.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="Qualité",
                message="Peu de données chiffrées dans le chapitre"
            ))
        
        # Vérifier graphiques mentionnés vs présents
        graph_mentions = len(re.findall(
            r'graphique|Graphique|figure|Figure|visualisation|histogramme',
            content,
            re.IGNORECASE
        ))
        graph_images = len(re.findall(r'!\[.*?\]\(data:image', content))
        
        if graph_mentions > graph_images + 5:
            self.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="Qualité",
                message=f"{graph_mentions} mentions graphiques mais {graph_images} images"
            ))
        
        # Vérifier tableaux présents
        tables = len(re.findall(r'\|.*?\|', content))
        if tables < 2:
            self.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                category="Qualité",
                message="Peu de tableaux dans le chapitre"
            ))
    
    def _validate_mode_compliance(self, content: str):
        """Valide conformité au mode configuré"""
        
        mode = self.config.mode.value
        
        if mode == "institutional":
            # Vérifier absence de méthodologie détaillée
            if not self.config.include_methodology:
                if 'méthodologie' in content.lower() and len(re.findall(r'méthodologie', content, re.I)) > 2:
                    self.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category="Mode",
                        message="Méthodologie détaillée en mode INS (non souhaité)"
                    ))
        
        elif mode == "academic":
            # Vérifier présence méthodologie
            if self.config.include_methodology:
                if 'méthodologie' not in content.lower():
                    self.issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category="Mode",
                        message="Section méthodologie manquante (requise en mode académique)"
                    ))
        
        elif mode == "business":
            # Vérifier présence recommandations
            if self.config.include_recommendations:
                if 'recommandation' not in content.lower():
                    self.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category="Mode",
                        message="Recommandations manquantes (attendues en mode business)"
                    ))
    
    # ═════════════════════════════════════════════════════════════
    # SCORING ET RÉSUMÉ
    # ═════════════════════════════════════════════════════════════
    
    def _calculate_score(self) -> float:
        """Calcule score de qualité 0-100"""
        
        # Pénalités selon gravité
        penalties = {
            ValidationSeverity.INFO: 1,
            ValidationSeverity.WARNING: 5,
            ValidationSeverity.ERROR: 15,
            ValidationSeverity.CRITICAL: 30
        }
        
        total_penalty = sum(penalties[issue.severity] for issue in self.issues)
        
        score = max(0, 100 - total_penalty)
        
        return score
    
    def _generate_summary(self) -> Dict:
        """Génère résumé des problèmes"""
        
        summary = {
            'total_issues': len(self.issues),
            'by_severity': {},
            'by_category': {},
            'critical_issues': []
        }
        
        for issue in self.issues:
            # Par gravité
            severity_key = issue.severity.value
            summary['by_severity'][severity_key] = summary['by_severity'].get(severity_key, 0) + 1
            
            # Par catégorie
            summary['by_category'][issue.category] = summary['by_category'].get(issue.category, 0) + 1
            
            # Problèmes critiques
            if issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]:
                summary['critical_issues'].append(issue.message)
        
        return summary
    
    # ═════════════════════════════════════════════════════════════
    # EXPORT / REPORTING
    # ═════════════════════════════════════════════════════════════
    
    def generate_report(self) -> str:
        """Génère rapport de validation lisible"""
        
        report = """
═══════════════════════════════════════════════════════════════
📋 RAPPORT DE VALIDATION
═══════════════════════════════════════════════════════════════

"""
        
        score = self._calculate_score()
        summary = self._generate_summary()
        
        # Score
        report += f"🎯 SCORE QUALITÉ : {score:.1f}/100\n\n"
        
        # Résumé par gravité
        report += "📊 PROBLÈMES DÉTECTÉS :\n"
        for severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR, 
                        ValidationSeverity.WARNING, ValidationSeverity.INFO]:
            count = summary['by_severity'].get(severity.value, 0)
            if count > 0:
                emoji = {"critical": "🔴", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
                report += f"  {emoji[severity.value]} {severity.value.upper()}: {count}\n"
        
        report += f"\n  TOTAL: {summary['total_issues']} problèmes\n\n"
        
        # Détail par catégorie
        if summary['by_category']:
            report += "📂 PAR CATÉGORIE :\n"
            for category, count in sorted(summary['by_category'].items(), key=lambda x: -x[1]):
                report += f"  • {category}: {count}\n"
            report += "\n"
        
        # Problèmes critiques
        if summary['critical_issues']:
            report += "🔴 PROBLÈMES CRITIQUES À CORRIGER :\n"
            for i, msg in enumerate(summary['critical_issues'], 1):
                report += f"  {i}. {msg}\n"
            report += "\n"
        
        # Liste complète
        if self.issues:
            report += "═══════════════════════════════════════════════════════════════\n"
            report += "LISTE COMPLÈTE DES PROBLÈMES\n"
            report += "═══════════════════════════════════════════════════════════════\n\n"
            
            for i, issue in enumerate(self.issues, 1):
                emoji = {"critical": "🔴", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
                report += f"{i}. {emoji[issue.severity.value]} [{issue.category}] {issue.message}\n"
        
        else:
            report += "✅ Aucun problème détecté !\n"
        
        report += "\n═══════════════════════════════════════════════════════════════\n"
        
        return report


# ═══════════════════════════════════════════════════════════════
# UTILISATION STANDALONE
# ═══════════════════════════════════════════════════════════════

def validate_chapter_file(filepath: str, config=None) -> Dict:
    """
    Valide un fichier Markdown chapitre
    
    Usage:
        result = validate_chapter_file("chapter_1.md")
        print(f"Score: {result['score']}/100")
    """
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    validator = ChapterValidator(config=config)
    result = validator.validate(content)
    
    # Afficher rapport
    print(validator.generate_report())
    
    return result


if __name__ == "__main__":
    
    print("="*70)
    print("TEST CHAPTER VALIDATOR")
    print("="*70)
    
    # Test avec contenu exemple
    test_content = """
## 1. Introduction

### 1.1. Contexte

Ceci est un test.

**Aperçu des données :**

| Variable | Valeur |
|----------|--------|
| Total | 100% |

Les données montrent que...

**Aperçu des données :**

| Variable | Valeur |
|----------|--------|
| Total | 100% |

```python
print("Code visible!")
```
    """
    
    validator = ChapterValidator()
    result = validator.validate(test_content, chapter_number="1")
    
    print(validator.generate_report())
    
    print(f"\n✅ Score: {result['score']:.1f}/100")
    print(f"✅ Valide: {result['is_valid']}")
    print(f"✅ Problèmes: {result['summary']['total_issues']}")