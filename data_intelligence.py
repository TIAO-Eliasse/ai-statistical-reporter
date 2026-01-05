"""
Module d'intelligence pré-processing
Analyse les données AVANT génération pour guider Claude
"""

import pandas as pd
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class DataIntelligence:
    """Analyse intelligente des données pour guider la génération"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.analysis = self._analyze()
    
    def _analyze(self) -> Dict:
        """Analyse complète du DataFrame"""
        return {
            'shape': self.df.shape,
            'numeric_vars': self._detect_numeric_vars(),
            'categorical_vars': self._detect_categorical_vars(),
            'encoded_vars': self._detect_encoded_vars(),
            'recommended_vars': self._recommend_variables(),
            'quality_issues': self._detect_quality_issues()
        }
    
    def _detect_numeric_vars(self) -> List[Dict]:
        """Détecte variables numériques réelles (non encodées)"""
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        
        result = []
        for col in numeric_cols:
            unique_count = self.df[col].nunique()
            
            # Si > 10 valeurs uniques → probablement continue
            if unique_count > 10:
                result.append({
                    'name': col,
                    'type': 'continuous',
                    'unique_count': unique_count,
                    'min': float(self.df[col].min()),
                    'max': float(self.df[col].max()),
                    'mean': float(self.df[col].mean()),
                    'std': float(self.df[col].std())
                })
        
        return result
    
    def _detect_categorical_vars(self) -> List[Dict]:
        """Détecte variables catégorielles"""
        cat_cols = self.df.select_dtypes(include=['object', 'category']).columns
        
        result = []
        for col in cat_cols:
            unique_count = self.df[col].nunique()
            
            # Limiter à 50 modalités pour éviter explosion
            if unique_count <= 50:
                result.append({
                    'name': col,
                    'unique_count': unique_count,
                    'top_values': self.df[col].value_counts().head(10).to_dict()
                })
        
        return result
    
    def _detect_encoded_vars(self) -> List[Dict]:
        """Détecte variables encodées (numériques mais catégorielles)"""
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        
        result = []
        for col in numeric_cols:
            unique_count = self.df[col].nunique()
            
            # Si < 10 valeurs uniques → probablement encodée
            if unique_count < 10:
                values = sorted(self.df[col].unique())
                labels = self._guess_labels(col, values)
                
                result.append({
                    'name': col,
                    'values': values,
                    'suggested_labels': labels,
                    'distribution': self.df[col].value_counts().to_dict()
                })
        
        return result
    
    def _guess_labels(self, col_name: str, values: List) -> List[str]:
        """Devine les labels contextuels pour variables encodées"""
        col_lower = col_name.lower()
        n = len(values)
        
        # Âge
        if 'age' in col_lower or 'âge' in col_lower:
            if n == 5:
                return ["< 25 ans", "25-35 ans", "35-45 ans", "45-55 ans", "> 55 ans"]
            elif n == 4:
                return ["< 30 ans", "30-45 ans", "45-60 ans", "> 60 ans"]
        
        # Diplôme
        if 'diplome' in col_lower or 'diplôme' in col_lower or 'education' in col_lower:
            if n == 5:
                return ["Aucun/Primaire", "Secondaire", "Bac", "Licence", "Master+"]
            elif n == 4:
                return ["Primaire", "Secondaire", "Licence", "Master+"]
        
        # Expérience
        if 'experience' in col_lower or 'expérience' in col_lower or 'anciennete' in col_lower:
            if n == 5:
                return ["< 2 ans", "2-5 ans", "5-10 ans", "10-15 ans", "> 15 ans"]
        
        # Effectifs
        if 'effectif' in col_lower or 'employe' in col_lower or 'taille' in col_lower:
            if n == 5:
                return ["1-5", "6-10", "11-20", "21-50", "> 50"]
        
        # Par défaut : Tranche 1, 2, 3...
        return [f"Tranche {int(v)}" for v in values]
    
    def _recommend_variables(self, max_vars: int = 10) -> Dict:
        """Recommande les variables les plus pertinentes à analyser"""
        # Exclure colonnes inutiles
        exclude_keywords = ['id', 'index', 'unnamed', 'key', 'code', 'numero']
        
        numeric_relevant = [
            v for v in self._detect_numeric_vars()
            if not any(kw in v['name'].lower() for kw in exclude_keywords)
        ]
        
        categorical_relevant = [
            v for v in self._detect_categorical_vars()
            if not any(kw in v['name'].lower() for kw in exclude_keywords)
        ]
        
        # Trier par pertinence (variance pour numériques, diversité pour catégorielles)
        numeric_sorted = sorted(
            numeric_relevant,
            key=lambda x: x['std'] / (x['mean'] + 1e-10),  # Coefficient de variation
            reverse=True
        )[:max_vars]
        
        categorical_sorted = sorted(
            categorical_relevant,
            key=lambda x: x['unique_count'],
            reverse=True
        )[:max_vars]
        
        return {
            'numeric': [v['name'] for v in numeric_sorted],
            'categorical': [v['name'] for v in categorical_sorted]
        }
    
    def _detect_quality_issues(self) -> Dict:
        """Détecte problèmes de qualité"""
        issues = {
            'missing_values': {},
            'duplicates': int(self.df.duplicated().sum()),
            'constant_columns': [],
            'high_cardinality': []
        }
        
        # Valeurs manquantes
        for col in self.df.columns:
            missing = self.df[col].isnull().sum()
            if missing > 0:
                issues['missing_values'][col] = {
                    'count': int(missing),
                    'percent': round(missing / len(self.df) * 100, 2)
                }
        
        # Colonnes constantes
        for col in self.df.columns:
            if self.df[col].nunique() == 1:
                issues['constant_columns'].append(col)
        
        # Cardinalité trop élevée
        for col in self.df.select_dtypes(include=['object']).columns:
            if self.df[col].nunique() > 50:
                issues['high_cardinality'].append({
                    'column': col,
                    'unique_count': self.df[col].nunique()
                })
        
        return issues
    
    def to_prompt_context(self) -> str:
        """Convertit l'analyse en contexte pour le prompt"""
        ctx = f"""
════════════════════════════════════════════
ANALYSE INTELLIGENTE DES DONNÉES
════════════════════════════════════════════

📊 DIMENSIONS : {self.analysis['shape'][0]} lignes × {self.analysis['shape'][1]} colonnes

🔢 VARIABLES NUMÉRIQUES CONTINUES ({len(self.analysis['numeric_vars'])}) :
"""
        for v in self.analysis['numeric_vars'][:5]:  # Top 5
            ctx += f"  • {v['name']} : [{v['min']:.2f} - {v['max']:.2f}], moyenne={v['mean']:.2f}\n"
        
        ctx += f"\n🏷️ VARIABLES CATÉGORIELLES ({len(self.analysis['categorical_vars'])}) :\n"
        for v in self.analysis['categorical_vars'][:5]:
            ctx += f"  • {v['name']} : {v['unique_count']} modalités\n"
        
        if self.analysis['encoded_vars']:
            ctx += f"\n⚠️ VARIABLES ENCODÉES DÉTECTÉES ({len(self.analysis['encoded_vars'])}) :\n"
            for v in self.analysis['encoded_vars']:
                ctx += f"  • {v['name']} : valeurs {v['values']} → {v['suggested_labels']}\n"
        
        ctx += f"\n🎯 VARIABLES RECOMMANDÉES POUR ANALYSE :\n"
        ctx += f"  Numériques : {', '.join(self.analysis['recommended_vars']['numeric'][:5])}\n"
        ctx += f"  Catégorielles : {', '.join(self.analysis['recommended_vars']['categorical'][:5])}\n"
        
        # Problèmes qualité
        quality = self.analysis['quality_issues']
        if quality['missing_values']:
            ctx += f"\n⚠️ VALEURS MANQUANTES DÉTECTÉES :\n"
            for col, info in list(quality['missing_values'].items())[:3]:
                ctx += f"  • {col} : {info['percent']}%\n"
        
        ctx += "\n════════════════════════════════════════════\n"
        
        return ctx


# 🧪 TEST
if __name__ == "__main__":
    # Créer DataFrame de test
    data = {
        'ID': range(100),
        'Age': [1, 2, 3, 4, 5] * 20,  # Encodée
        'Salaire': [30000 + i*1000 for i in range(100)],  # Continue
        'Secteur': ['IT', 'Finance', 'Santé'] * 33 + ['IT']  # Catégorielle
    }
    df = pd.DataFrame(data)
    
    intel = DataIntelligence(df)
    
    print("="*60)
    print("TEST DATA INTELLIGENCE")
    print("="*60)
    print(intel.to_prompt_context())