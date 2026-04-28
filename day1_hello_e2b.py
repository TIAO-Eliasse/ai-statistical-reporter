"""
Day 1-2: Hello World avec E2B + GMINI
Objectif: Uploader un CSV et faire un df.head() via le LLM
"""

import os
from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox
from google.genai import Client  # GMINI PRO

# Charger les variables d'environnement
load_dotenv()


def format_execution_result(execution):
    """Return a best-effort string for an Execution object."""
    try:
        if execution is None:
            return None
        # Prefer Execution.text (main result)
        text = None
        try:
            text = execution.text
        except Exception:
            text = None

        if text:
            return text

        # Aggregate Result.text from execution.results
        parts = []
        if hasattr(execution, "results") and execution.results:
            for r in execution.results:
                try:
                    if getattr(r, "text", None):
                        parts.append(r.text)
                    elif getattr(r, "markdown", None):
                        parts.append(r.markdown)
                    elif getattr(r, "html", None):
                        parts.append(r.html)
                except Exception:
                    parts.append(str(r))
        if parts:
            return "\n".join([p for p in parts if p])

        # Fallback to logs stdout
        if hasattr(execution, "logs") and execution.logs and getattr(execution.logs, "stdout", None):
            return "\n".join(execution.logs.stdout)

        # Final fallback: repr
        return repr(execution)
    except Exception:
        return str(execution)

def test_e2b_basic():
    """Test basique: créer une sandbox et exécuter du code simple"""
    print("🚀 Test 1: Création de sandbox E2B...")

    with Sandbox.create() as sandbox:
        # Exécuter du code Python simple
        execution = sandbox.run_code("print('Hello from E2B!')")
        print(f"✅ Résultat: {format_execution_result(execution)}")

        # Test avec pandas
        execution = sandbox.run_code("""
import pandas as pd
import sys
print(f"Python version: {sys.version}")
print(f"Pandas version: {pd.__version__}")
        """)
        print(f"✅ Versions:\n{format_execution_result(execution)}")


def test_csv_upload(csv_path: str):
    """Test upload d'un CSV et lecture avec pandas"""
    print(f"\n🚀 Test 2: Upload du fichier {csv_path}...")

    if not os.path.exists(csv_path):
        print(f"❌ Fichier {csv_path} introuvable!")
        print("💡 Créez un fichier CSV de test avec ces données:")
        print("nom,age,salaire,ville")
        print("Alice,25,45000,Paris")
        print("Bob,30,52000,Lyon")
        print("Charlie,35,48000,Marseille")
        return

    with Sandbox.create() as sandbox:
        # Upload du fichier dans la sandbox
        with open(csv_path, 'rb') as f:
            remote_path = sandbox.files.write("data.csv", f)

        print(f"✅ Fichier uploadé: {remote_path}")

        # Lire le CSV avec pandas
        code = """
import pandas as pd

# Lire le CSV
df = pd.read_csv('/home/user/data.csv')

# Afficher les premières lignes
print("=== df.head() ===")
print(df.head())

print("\\n=== df.info() ===")
df.info()

print("\\n=== df.describe() ===")
print(df.describe())
        """

        execution = sandbox.run_code(code)

        if execution.error:
            print(f"❌ Erreur: {execution.error}")
        else:
            print(f"✅ Résultat:\n{format_execution_result(execution)}")


def test_with_llm(csv_path: str):
    """Test avec GMINI: générer du code pour analyser le CSV"""
    print(f"\n🚀 Test 3: Utiliser GMINI pour générer du code d'analyse...")

    if not os.path.exists(csv_path):
        print(f"❌ Fichier {csv_path} introuvable!")
        return

    gmini_client = Client(api_key=os.getenv("GMINI_API_KEY"))

    with Sandbox.create() as sandbox:
        # Upload du CSV
        with open(csv_path, 'rb') as f:
            sandbox.files.write("data.csv", f)

        # Prompt pour GMINI
        prompt = """
Tu es un data analyst. Génère du code Python pour:
1. Lire le fichier CSV '/home/user/data.csv'
2. Afficher df.head()
3. Calculer quelques statistiques basiques

Retourne UNIQUEMENT le code Python, sans markdown ni explications.
"""

        # Créer une session chat puis envoyer le prompt
        # Utiliser un modèle supporté par l'API
        chat = gmini_client.chats.create(model="gemini-2.5-flash")
        response = chat.send_message(prompt)

        # Extraire le code généré de façon robuste
        generated_code = None
        try:
            if hasattr(response, "output_text"):
                generated_code = response.output_text
            elif hasattr(response, "candidates") and response.candidates:
                first = response.candidates[0]
                if hasattr(first, "content"):
                    generated_code = first.content
                elif hasattr(first, "text"):
                    generated_code = first.text
                elif isinstance(first, dict) and "content" in first:
                    generated_code = first["content"]
                else:
                    generated_code = str(first)
            elif isinstance(response, dict):
                for key in ("output_text", "output", "text", "candidates"):
                    if key in response:
                        val = response[key]
                        if isinstance(val, str):
                            generated_code = val
                            break
                        if isinstance(val, list) and val:
                            v0 = val[0]
                            if isinstance(v0, dict):
                                generated_code = v0.get("content") or v0.get("text") or str(v0)
                            else:
                                generated_code = str(v0)
                            break
        except Exception:
            generated_code = None

        if not generated_code:
            generated_code = str(response)

        # Si la réponse est un objet `Content` (google.genai.types.Content),
        # extraire le texte des `parts` pour obtenir une chaîne de code.
        try:
            if not isinstance(generated_code, str):
                if hasattr(generated_code, "parts"):
                    parts = getattr(generated_code, "parts") or []
                    texts = []
                    for p in parts:
                        txt = getattr(p, "text", None)
                        if txt:
                            texts.append(txt)
                    generated_code = "\n".join(texts).strip()
                elif isinstance(generated_code, dict):
                    generated_code = generated_code.get("content") or generated_code.get("text") or str(generated_code)
                else:
                    generated_code = str(generated_code)
        except Exception:
            generated_code = str(generated_code)

        print(f"📝 Code généré par GMINI:\n{generated_code}\n")

        # Exécuter le code généré
        execution = sandbox.run_code(generated_code)
        if execution.error:
            print(f"❌ Erreur d'exécution: {execution.error}")
        else:
            print(f"✅ Résultat:\n{format_execution_result(execution)}")


if __name__ == "__main__":
    print("=" * 60)
    print("JOUR 1-2: TESTS E2B + CSV + GMINI")
    print("=" * 60)

    # Test 1: Vérifier que E2B fonctionne
    test_e2b_basic()

    # Test 2: Upload et lecture d'un CSV
    csv_file = "test_data.csv"  # Créez ce fichier vous-même
    test_csv_upload(csv_file)

    # Test 3: Utiliser GMINI pour générer du code
    test_with_llm(csv_file)

    print("\n" + "=" * 60)
    print("✅ JOUR 1-2 TERMINÉ!")
    print("=" * 60)
