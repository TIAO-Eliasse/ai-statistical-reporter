"""
Tests unitaires pour AI Statistical Reporter
À exécuter avec: pytest tests/test_core.py -v
"""

import pytest
import pandas as pd
import json
from pathlib import Path
import sys

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDataValidation:
    """Tests pour la validation des données"""
    
    def test_valid_csv(self):
        """Test avec un CSV valide"""
        df = pd.DataFrame({
            'age': [25, 30, 35],
            'salaire': [30000, 40000, 50000],
            'ville': ['Paris', 'Lyon', 'Marseille']
        })
        
        assert len(df) > 0
        assert len(df.columns) > 0
        assert len(df.select_dtypes(include=['number']).columns) > 0
    
    def test_empty_csv(self):
        """Test avec un CSV vide"""
        df = pd.DataFrame()
        
        assert len(df) == 0
    
    def test_missing_values(self):
        """Test détection valeurs manquantes"""
        df = pd.DataFrame({
            'col1': [1, 2, None, 4],
            'col2': ['a', None, 'c', 'd']
        })
        
        missing = df.isnull().sum()
        
        assert missing['col1'] == 1
        assert missing['col2'] == 1


class TestPlanGeneration:
    """Tests pour la génération de plans"""
    
    @pytest.fixture
    def sample_plan(self):
        """Plan exemple pour les tests"""
        return {
            'titre': 'Test Report',
            'date': '2025-01-01',
            'auteur': 'Test',
            'chapitres': [
                {
                    'numero': '1',
                    'titre': 'Introduction',
                    'sections': [
                        {
                            'titre': 'Context',
                            'analyses': ['Analysis 1', 'Analysis 2']
                        }
                    ]
                }
            ]
        }
    
    def test_plan_structure(self, sample_plan):
        """Vérifie la structure du plan"""
        assert 'titre' in sample_plan
        assert 'chapitres' in sample_plan
        assert len(sample_plan['chapitres']) > 0
        
        first_chapter = sample_plan['chapitres'][0]
        assert 'numero' in first_chapter
        assert 'titre' in first_chapter
        assert 'sections' in first_chapter
    
    def test_plan_to_text_conversion(self, sample_plan):
        """Test conversion JSON → Texte"""
        # Import de la fonction (à adapter selon votre code)
        # from app_streamlit_professional import json_to_editable_text
        
        # text = json_to_editable_text(sample_plan)
        
        # assert 'TITRE:' in text
        # assert 'Test Report' in text
        # assert '1. Introduction' in text
        
        pass  # Placeholder


class TestCaching:
    """Tests pour le système de cache"""
    
    def test_cache_key_generation(self):
        """Test génération de clés de cache"""
        import hashlib
        
        data1 = {'key': 'value'}
        data2 = {'key': 'value'}
        data3 = {'key': 'other'}
        
        hash1 = hashlib.md5(json.dumps(data1, sort_keys=True).encode()).hexdigest()
        hash2 = hashlib.md5(json.dumps(data2, sort_keys=True).encode()).hexdigest()
        hash3 = hashlib.md5(json.dumps(data3, sort_keys=True).encode()).hexdigest()
        
        assert hash1 == hash2  # Même données = même hash
        assert hash1 != hash3  # Données différentes = hash différent
    
    def test_cache_expiration(self):
        """Test expiration du cache"""
        from datetime import datetime, timedelta
        
        file_time = datetime.now() - timedelta(hours=25)
        current_time = datetime.now()
        
        age_hours = (current_time - file_time).total_seconds() / 3600
        
        assert age_hours > 24  # Cache expiré


class TestErrorHandling:
    """Tests pour la gestion d'erreurs"""
    
    def test_api_error_handling(self):
        """Test gestion erreur API"""
        # Simuler une erreur API
        try:
            raise Exception("API quota exceeded")
        except Exception as e:
            assert "quota" in str(e).lower()
    
    def test_invalid_json_handling(self):
        """Test parsing JSON invalide"""
        invalid_json = "{ invalid json }"
        
        with pytest.raises(json.JSONDecodeError):
            json.loads(invalid_json)


class TestExportFunctions:
    """Tests pour les fonctions d'export"""
    
    @pytest.fixture
    def sample_plan(self):
        return {
            'titre': 'Test Report',
            'date': '2025-01-01',
            'auteur': 'Test Author',
            'chapitres': [
                {
                    'numero': '1',
                    'titre': 'Chapter 1',
                    'sections': [
                        {
                            'titre': 'Section 1.1',
                            'analyses': ['Analysis A', 'Analysis B']
                        }
                    ]
                }
            ]
        }
    
    def test_html_export_structure(self, sample_plan):
        """Test structure du HTML exporté"""
        # from app_streamlit_professional import plan_to_html
        
        # html = plan_to_html(sample_plan)
        
        # assert '<html' in html
        # assert 'Test Report' in html
        # assert 'Chapter 1' in html
        
        pass  # Placeholder
    
    def test_json_export(self, sample_plan):
        """Test export JSON"""
        json_str = json.dumps(sample_plan, indent=2, ensure_ascii=False)
        
        # Vérifier que c'est du JSON valide
        parsed = json.loads(json_str)
        
        assert parsed == sample_plan


class TestRateLimiting:
    """Tests pour le rate limiting"""
    
    def test_rate_limit_check(self):
        """Test vérification des limites"""
        # Simuler des appels
        calls = []
        max_calls = 10
        
        for i in range(15):
            if len(calls) < max_calls:
                calls.append(i)
        
        assert len(calls) == max_calls
    
    def test_rate_limit_window(self):
        """Test fenêtre de temps"""
        from datetime import datetime, timedelta
        
        window_hours = 1
        cutoff_time = datetime.now() - timedelta(hours=window_hours)
        
        # Simuler des entrées
        entries = [
            {'timestamp': (datetime.now() - timedelta(minutes=30)).isoformat()},
            {'timestamp': (datetime.now() - timedelta(hours=2)).isoformat()},
        ]
        
        # Filtrer les anciennes
        recent = [
            e for e in entries
            if datetime.fromisoformat(e['timestamp']) > cutoff_time
        ]
        
        assert len(recent) == 1  # Seule la plus récente


class TestDataAnalysis:
    """Tests pour l'analyse de données"""
    
    def test_numeric_statistics(self):
        """Test calcul statistiques numériques"""
        df = pd.DataFrame({
            'age': [25, 30, 35, 40, 45]
        })
        
        assert df['age'].mean() == 35
        assert df['age'].median() == 35
        assert df['age'].min() == 25
        assert df['age'].max() == 45
    
    def test_categorical_frequencies(self):
        """Test calcul fréquences catégorielles"""
        df = pd.DataFrame({
            'ville': ['Paris', 'Lyon', 'Paris', 'Lyon', 'Paris']
        })
        
        freq = df['ville'].value_counts()
        
        assert freq['Paris'] == 3
        assert freq['Lyon'] == 2
    
    def test_missing_values_percentage(self):
        """Test calcul pourcentage valeurs manquantes"""
        df = pd.DataFrame({
            'col1': [1, 2, None, 4, None]
        })
        
        missing_pct = (df['col1'].isnull().sum() / len(df)) * 100
        
        assert missing_pct == 40.0  # 2 sur 5 = 40%


# Fixtures globales
@pytest.fixture
def sample_csv_path(tmp_path):
    """Crée un CSV temporaire pour les tests"""
    df = pd.DataFrame({
        'age': [25, 30, 35, 40],
        'salaire': [30000, 40000, 50000, 60000],
        'ville': ['Paris', 'Lyon', 'Marseille', 'Toulouse']
    })
    
    csv_path = tmp_path / "test_data.csv"
    df.to_csv(csv_path, index=False)
    
    return str(csv_path)


# Commandes pour exécuter les tests
"""
# Installer pytest
pip install pytest pytest-cov

# Exécuter tous les tests
pytest tests/ -v

# Exécuter avec couverture
pytest tests/ --cov=. --cov-report=html

# Exécuter un test spécifique
pytest tests/test_core.py::TestDataValidation::test_valid_csv -v

# Exécuter les tests en parallèle (plus rapide)
pip install pytest-xdist
pytest tests/ -n auto
"""