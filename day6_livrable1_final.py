"""
LIVRABLE 1 (Jour 6-7): Script CLI complet
Prend un CSV + une question, exécute du code Python, retourne la réponse
"""

import os
import sys
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from e2b_code_interpreter import Sandbox
import operator
from google.genai import Client as GminiClient

load_dotenv()


def format_execution_result(execution):
    """Best-effort extraction of text from an Execution object (results, logs)."""
    try:
        if execution is None:
            return None
        try:
            text = execution.text
        except Exception:
            text = None
        if text:
            return text

        parts = []
        if hasattr(execution, "results") and execution.results:
            for r in execution.results:
                if getattr(r, "text", None):
                    parts.append(r.text)
                elif getattr(r, "markdown", None):
                    parts.append(r.markdown)
                elif getattr(r, "html", None):
                    parts.append(r.html)
        if parts:
            return "\n".join(parts)

        if hasattr(execution, "logs") and execution.logs and getattr(execution.logs, "stdout", None):
            return "\n".join(execution.logs.stdout)

        return repr(execution)
    except Exception:
        return str(execution)


class AnalysisState(TypedDict):
    csv_path: str
    user_question: str
    python_code: str
    execution_result: str
    final_answer: str
    error: str


def load_csv_node(state: AnalysisState) -> AnalysisState:
    """Charge le CSV dans E2B et retourne les infos de base"""
    print(f"📂 Chargement du fichier: {state['csv_path']}")
    
    if not os.path.exists(state['csv_path']):
        return {**state, "error": f"Fichier {state['csv_path']} introuvable"}
    
    with Sandbox.create() as sandbox:
        # Upload du CSV
        with open(state['csv_path'], 'rb') as f:
            sandbox.files.write("data.csv", f)
        
        # Charger et analyser le CSV
        setup_code = """
import pandas as pd
df = pd.read_csv('/home/user/data.csv')
print("=== Aperçu des données ===")
print(df.head())
print("\\n=== Info ===")
print(df.info())
        """
        
        execution = sandbox.run_code(setup_code)
        print(format_execution_result(execution))
    
    return state


def generate_code_node(state: AnalysisState) -> AnalysisState:
    """Génère le code Python pour répondre à la question"""
    print(f"\n🤖 Génération du code pour: {state['user_question']}")
    
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0
    )
    
    prompt = f"""
Tu es un data analyst. Le CSV est chargé dans 'df' (pandas DataFrame).

Question: {state['user_question']}

Génère du code Python qui:
1. Répond précisément à la question
2. Print les résultats de façon claire
3. Gère les erreurs potentielles (colonnes inexistantes, etc.)

Retourne UNIQUEMENT le code Python, sans markdown.
"""
    
    code = None
    # Prefer GMINI if API key present
    gmini_key = os.getenv("GMINI_API_KEY")
    if gmini_key:
        try:
            gclient = GminiClient(api_key=gmini_key)
            chat = gclient.chats.create(model="gemini-2.5-flash")
            gres = chat.send_message(prompt)

            # extract generated text
            gen = None
            try:
                if hasattr(gres, "output_text"):
                    gen = gres.output_text
                elif hasattr(gres, "candidates") and gres.candidates:
                    first = gres.candidates[0]
                    if hasattr(first, "content"):
                        gen = first.content
                    elif hasattr(first, "text"):
                        gen = first.text
                    elif isinstance(first, dict) and "content" in first:
                        gen = first["content"]
                    else:
                        gen = str(first)
                elif isinstance(gres, dict):
                    for key in ("output_text", "output", "text", "candidates"):
                        if key in gres:
                            val = gres[key]
                            if isinstance(val, str):
                                gen = val
                                break
                            if isinstance(val, list) and val:
                                v0 = val[0]
                                if isinstance(v0, dict):
                                    gen = v0.get("content") or v0.get("text") or str(v0)
                                else:
                                    gen = str(v0)
                                break
            except Exception:
                gen = None

            if not gen:
                gen = str(gres)

            # If it's a Content object, join parts
            if not isinstance(gen, str) and hasattr(gen, "parts"):
                parts = getattr(gen, "parts") or []
                texts = [getattr(p, "text", "") for p in parts if getattr(p, "text", None)]
                code = "\n".join(texts).strip()
            else:
                code = str(gen)
        except Exception as e:
            print(f"⚠️ GMINI error: {e}. Falling back to Anthropic.")
            code = None

    # If GMINI not used or failed, try Anthropic
    if not code:
        try:
            response = llm.invoke(prompt)
            code = response.content.strip()
        except Exception as e:
            # LLM failed (e.g., billing / quota). Use a safe fallback that computes
            # a mean on a numeric column (prefer 'salaire' if present).
            print(f"⚠️ LLM error: {e}. Using fallback code.")
            fallback_code = '''
try:
    import pandas as pd
    num_cols = df.select_dtypes(include='number').columns
    if 'salaire' in df.columns and df['salaire'].dtype.kind in 'biufc':
        mean = df['salaire'].mean()
        print(f"Salaire moyen: {mean}")
    elif len(num_cols) > 0:
        col = num_cols[0]
        mean = df[col].mean()
        print(f"Moyenne de {col}: {mean}")
    else:
        print('Aucune colonne numérique trouvée.')
except Exception as e:
    print('Erreur lors du calcul:', e)
'''
            code = fallback_code
            # record error in state via a temporary variable; actual state update happens on return
            state = {**state, "error": str(e)}

    # If the LLM returned a non-str object (some SDKs), try to extract text
    if not isinstance(code, str):
        try:
            code = getattr(response, "content", None) or getattr(response, "text", None) or str(response)
        except Exception:
            code = str(response)
    
    # Nettoyer le code si markdown
    if code.startswith("```python"):
        code = code.split("```python")[1].split("```")[0].strip()
    elif code.startswith("```"):
        code = code.split("```")[1].split("```")[0].strip()
    
    print(f"📝 Code généré:\n{code}\n")
    
    return {**state, "python_code": code}


def execute_code_node(state: AnalysisState) -> AnalysisState:
    """Exécute le code dans E2B"""
    print("🔧 Exécution du code...")
    
    with Sandbox.create() as sandbox:
        # Recharger le CSV
        with open(state['csv_path'], 'rb') as f:
            sandbox.files.write("data.csv", f)
        
        # Setup
        sandbox.run_code("import pandas as pd\ndf = pd.read_csv('/home/user/data.csv')")
        
        # Exécuter le code généré
        execution = sandbox.run_code(state['python_code'])

        if execution and getattr(execution, "error", None):
            err = execution.error
            result = f"❌ Erreur: {err}"
            print(result)
            return {**state, "execution_result": result, "error": str(err)}
        else:
            result = format_execution_result(execution)
            if not result:
                result = "(aucun output)"
            print(f"✅ Résultat:\n{result}\n")
            return {**state, "execution_result": result}


def format_answer_node(state: AnalysisState) -> AnalysisState:
    """Formate la réponse finale"""
    
    if state.get("error"):
        return {**state, "final_answer": f"Erreur lors de l'analyse: {state['error']}"}

    # Prefer GMINI if available
    gmini_key = os.getenv("GMINI_API_KEY")
    if gmini_key:
        try:
            gclient = GminiClient(api_key=gmini_key)
            chat = gclient.chats.create(model="gemini-2.5-flash")
            prompt = f"Question: {state['user_question']}\nRésultat du code: {state['execution_result']}\nRédige une réponse claire en français (2-3 phrases maximum)."
            gres = chat.send_message(prompt)

            # extract text
            ans = None
            if hasattr(gres, "output_text"):
                ans = gres.output_text
            elif hasattr(gres, "candidates") and gres.candidates:
                first = gres.candidates[0]
                if hasattr(first, "content"):
                    ans = first.content
                elif hasattr(first, "text"):
                    ans = first.text
                elif isinstance(first, dict) and "content" in first:
                    ans = first["content"]
                else:
                    ans = str(first)
            elif isinstance(gres, dict):
                for key in ("output_text", "output", "text", "candidates"):
                    if key in gres:
                        val = gres[key]
                        if isinstance(val, str):
                            ans = val
                            break
                        if isinstance(val, list) and val:
                            v0 = val[0]
                            if isinstance(v0, dict):
                                ans = v0.get("content") or v0.get("text") or str(v0)
                            else:
                                ans = str(v0)
                            break

            if not ans:
                ans = str(gres)

            # If Content object, join parts
            if not isinstance(ans, str) and hasattr(ans, "parts"):
                parts = getattr(ans, "parts") or []
                texts = [getattr(p, "text", "") for p in parts if getattr(p, "text", None)]
                ans = "\n".join(texts).strip()

            return {**state, "final_answer": str(ans)}
        except Exception as e:
            print(f"⚠️ GMINI formatting error: {e}. Falling back to Anthropic/local formatting.")

    # Try Anthropic
    try:
        llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        prompt = f"Question: {state['user_question']}\nRésultat du code: {state['execution_result']}\nRédige une réponse claire en français (2-3 phrases maximum)."
        response = llm.invoke(prompt)
        answer = response.content
        return {**state, "final_answer": answer}
    except Exception as e:
        # Both LLMs failed — produce a simple local answer based on execution_result
        print(f"⚠️ Anthropic formatting error: {e}. Using local formatter.")
        exec_res = state.get("execution_result") or ""
        # Simple heuristics: if execution printed 'Salaire moyen' or similar, reuse it.
        if "Salaire moyen" in exec_res or "salaire moyen" in exec_res or "Le salaire moyen" in exec_res:
            # extract number
            import re
            m = re.search(r"([0-9]+[\.,]?[0-9]*)", exec_res)
            if m:
                val = m.group(1)
                answer = f"Le salaire moyen est {val}."
            else:
                answer = exec_res
        else:
            # fallback generic
            snippet = exec_res.splitlines()[0] if exec_res else "Pas de résultat disponible."
            answer = f"Résultat de l'analyse: {snippet}"
        return {**state, "final_answer": answer}


def create_analysis_graph():
    """Crée le graphe d'analyse"""
    workflow = StateGraph(AnalysisState)
    
    workflow.add_node("load_csv", load_csv_node)
    workflow.add_node("generate_code", generate_code_node)
    workflow.add_node("execute_code", execute_code_node)
    workflow.add_node("format_answer", format_answer_node)
    
    workflow.set_entry_point("load_csv")
    workflow.add_edge("load_csv", "generate_code")
    workflow.add_edge("generate_code", "execute_code")
    workflow.add_edge("execute_code", "format_answer")
    workflow.add_edge("format_answer", END)
    
    return workflow.compile()


def main():
    """Point d'entrée CLI"""
    print("=" * 70)
    print("AI STATISTICAL REPORTER - LIVRABLE 1")
    print("=" * 70)
    
    # Argument parsing simple
    if len(sys.argv) < 2:
        print("\nUsage: python day6_livrable1_final.py <fichier.csv> [question]")
        print("\nExemples:")
        print("  python day6_livrable1_final.py data.csv 'Quel est le salaire moyen ?'")
        print("  python day6_livrable1_final.py data.csv 'Quelle est la moyenne de la colonne age ?'")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    if len(sys.argv) > 2:
        question = " ".join(sys.argv[2:])
    else:
        question = input("\n❓ Votre question: ")
    
    # Exécuter l'analyse
    graph = create_analysis_graph()
    
    initial_state = {
        "csv_path": csv_path,
        "user_question": question,
        "python_code": "",
        "execution_result": "",
        "final_answer": "",
        "error": ""
    }
    
    final_state = graph.invoke(initial_state)
    
    # Afficher le résultat
    print("\n" + "=" * 70)
    print("RÉPONSE FINALE")
    print("=" * 70)
    print(final_state['final_answer'])
    print("=" * 70)


if __name__ == "__main__":
    main()