"""
Day 3-5: Introduction à LangGraph
Objectif: Créer un graphe Agent -> Tool (Python) -> Agent
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from e2b_code_interpreter import Sandbox
import operator
from google.genai import Client as GminiClient

load_dotenv()


def format_execution_result(execution):
    """Return a best-effort string for an Execution object (results, logs or repr)."""
    try:
        if execution is None:
            return None
        # Prefer Execution.text
        try:
            text = execution.text
        except Exception:
            text = None
        if text:
            return text

        # Aggregate r.text / markdown / html
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

        # Fallback to logs stdout
        if hasattr(execution, "logs") and execution.logs and getattr(execution.logs, "stdout", None):
            return "\n".join(execution.logs.stdout)

        return repr(execution)
    except Exception:
        return str(execution)

# 1. DÉFINIR L'ÉTAT DU GRAPHE
class AgentState(TypedDict):
    """État partagé entre tous les nœuds"""
    messages: Annotated[list, operator.add]  # Historique des messages
    user_query: str  # Question de l'utilisateur
    python_code: str  # Code Python généré
    execution_result: str  # Résultat de l'exécution
    final_answer: str  # Réponse finale


# 2. NŒUD 1: L'AGENT (Génère du code Python)
def agent_node(state: AgentState) -> AgentState:
    """L'agent analyse la question et génère du code Python"""
    print("\n🤖 AGENT: Génération du code Python...")
    
    prompt = f"""
Tu es un data analyst expert. L'utilisateur a posé cette question:
"{state['user_query']}"

Le fichier CSV est déjà chargé dans la variable 'df' (pandas DataFrame).

Génère du code Python qui:
1. Répond à la question
2. Print le résultat de façon claire

Retourne UNIQUEMENT le code Python, sans ```python ni explications.
"""
    # Prefer GMINI if available, then Anthropic, then local fallback
    code = None
    gmini_key = os.getenv("GMINI_API_KEY")
    if gmini_key:
        try:
            gclient = GminiClient(api_key=gmini_key)
            chat = gclient.chats.create(model="gemini-2.5-flash")
            gres = chat.send_message(prompt)

            # extract generated text from response
            gen = None
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

            if not gen:
                gen = str(gres)

            # If Content-like object, join parts
            if not isinstance(gen, str) and hasattr(gen, "parts"):
                parts = getattr(gen, "parts") or []
                texts = [getattr(p, "text", "") for p in parts if getattr(p, "text", None)]
                code = "\n".join(texts).strip()
            else:
                code = str(gen)
        except Exception as e:
            print(f"⚠️ GMINI error in agent_node: {e}. Falling back to Anthropic.")
            code = None

    if not code:
        try:
            llm = ChatAnthropic(
                model="claude-sonnet-4-20250514",
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
            response = llm.invoke(prompt)
            code = response.content
        except Exception as e:
            print(f"⚠️ Anthropic error in agent_node: {e}. Using local fallback code.")
            # Local fallback: simple mean of numeric column (prefer 'salaire')
            code = '''
try:
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
    
    print(f"📝 Code généré:\n{code}\n")
    
    msgs = list(state.get("messages") or [])
    msgs.append({"role": "agent", "content": f"Code généré: {code[:100]}..."})
    return {
        **state,
        "python_code": code,
        "messages": msgs
    }


# 3. NŒUD 2: TOOL (Exécute le code Python)
def python_tool_node(state: AgentState) -> AgentState:
    """Exécute le code Python dans E2B"""
    print("\n🔧 TOOL: Exécution du code dans E2B...")

    # Create sandbox via the recommended factory to ensure context/config
    with Sandbox.create() as sandbox:
        # Charger un CSV de démonstration
        setup_code = """
import pandas as pd
import numpy as np

# Créer un DataFrame de test
df = pd.DataFrame({
    'nom': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'age': [25, 30, 35, 28, 32],
    'salaire': [45000, 52000, 48000, 51000, 55000],
    'ville': ['Paris', 'Lyon', 'Marseille', 'Paris', 'Lyon']
})

print("DataFrame chargé:")
print(df.head())
        """
        
        sandbox.run_code(setup_code)

        # Exécuter le code généré par l'agent
        execution = sandbox.run_code(state.get("python_code", ""))

        if execution and getattr(execution, "error", None):
            result = f"❌ Erreur: {execution.error}"
            print(result)
        else:
            result = format_execution_result(execution)
            if not result:
                result = "(aucun output)"
            print(f"✅ Résultat:\n{result}")
    
    msgs = list(state.get("messages") or [])
    msgs.append({"role": "tool", "content": f"Exécution: {str(result)[:100]}..."})
    return {
        **state,
        "execution_result": result,
        "messages": msgs
    }


# 4. NŒUD 3: AGENT FINAL (Formule la réponse)
def answer_node(state: AgentState) -> AgentState:
    """L'agent formule une réponse en langage naturel"""
    print("\n💬 AGENT: Formulation de la réponse finale...")
    # Prefer GMINI for answer formatting, then Anthropic, then local fallback
    prompt = f"Question de l'utilisateur: \"{state['user_query']}\"\n\nRésultat de l'exécution du code:\n{state['execution_result']}\n\nFormule une réponse claire et concise en français pour l'utilisateur."

    gmini_key = os.getenv("GMINI_API_KEY")
    answer = None
    if gmini_key:
        try:
            gclient = GminiClient(api_key=gmini_key)
            chat = gclient.chats.create(model="gemini-2.5-flash")
            gres = chat.send_message(prompt)

            if hasattr(gres, "output_text"):
                answer = gres.output_text
            elif hasattr(gres, "candidates") and gres.candidates:
                first = gres.candidates[0]
                if hasattr(first, "content"):
                    answer = first.content
                elif hasattr(first, "text"):
                    answer = first.text
                elif isinstance(first, dict) and "content" in first:
                    answer = first["content"]
                else:
                    answer = str(first)
            elif isinstance(gres, dict):
                for key in ("output_text", "output", "text", "candidates"):
                    if key in gres:
                        val = gres[key]
                        if isinstance(val, str):
                            answer = val
                            break
                        if isinstance(val, list) and val:
                            v0 = val[0]
                            if isinstance(v0, dict):
                                answer = v0.get("content") or v0.get("text") or str(v0)
                            else:
                                answer = str(v0)
                            break

            if not answer:
                answer = str(gres)

            if not isinstance(answer, str) and hasattr(answer, "parts"):
                parts = getattr(answer, "parts") or []
                texts = [getattr(p, "text", "") for p in parts if getattr(p, "text", None)]
                answer = "\n".join(texts).strip()
        except Exception as e:
            print(f"⚠️ GMINI error in answer_node: {e}. Falling back to Anthropic.")
            answer = None

    if not answer:
        try:
            llm = ChatAnthropic(
                model="claude-sonnet-4-20250514",
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
            resp = llm.invoke(prompt)
            answer = resp.content
        except Exception as e:
            print(f"⚠️ Anthropic error in answer_node: {e}. Using local fallback answer.")
            exec_res = state.get("execution_result") or ""
            if "Salaire moyen" in exec_res or "salaire moyen" in exec_res or "Le salaire moyen" in exec_res:
                import re
                m = re.search(r"([0-9]+[\.,]?[0-9]*)", exec_res)
                if m:
                    val = m.group(1)
                    answer = f"Le salaire moyen est {val}."
                else:
                    answer = exec_res
            else:
                snippet = exec_res.splitlines()[0] if exec_res else "Pas de résultat disponible."
                answer = f"Résultat de l'analyse: {snippet}"

    print(f"✅ Réponse: {answer}\n")

    msgs = list(state.get("messages") or [])
    msgs.append({"role": "agent", "content": f"Réponse finale: {str(answer)[:100]}..."})

    return {
        **state,
        "final_answer": answer,
        "messages": msgs
    }


# 5. CONSTRUIRE LE GRAPHE
def create_graph():
    """Construit le graphe LangGraph"""
    workflow = StateGraph(AgentState)
    
    # Ajouter les nœuds
    workflow.add_node("agent", agent_node)
    workflow.add_node("tool", python_tool_node)
    workflow.add_node("answer", answer_node)
    
    # Définir les connexions
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", "tool")
    workflow.add_edge("tool", "answer")
    workflow.add_edge("answer", END)
    
    return workflow.compile()


# 6. TESTER LE GRAPHE
def test_graph():
    """Test du graphe avec une question simple"""
    print("=" * 60)
    print("TEST LANGGRAPH: Agent -> Tool -> Answer")
    print("=" * 60)
    
    graph = create_graph()
    
    # Question test
    initial_state = {
        "user_query": "Quel est le salaire moyen ?",
        "messages": [],
        "python_code": "",
        "execution_result": "",
        "final_answer": ""
    }
    
    # Exécuter le graphe
    final_state = graph.invoke(initial_state)
    
    print("\n" + "=" * 60)
    print("RÉSULTAT FINAL")
    print("=" * 60)
    print(f"Question: {final_state['user_query']}")
    print(f"Réponse: {final_state['final_answer']}")


if __name__ == "__main__":
    test_graph()