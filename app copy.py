"""
AI Statistical Reporter - Interface Chainlit "Gamma-Like"
Architecture Stateful pour l'édition de plan interactive
"""

import chainlit as cl
import pandas as pd
import json
import os
import asyncio
from typing import List, Dict, Optional, Union
from copy import deepcopy
from dotenv import load_dotenv

# Simulation ou import de vos agents existants
try:
    from week2_architect_agent import generate_report_plan, analyze_csv
except ImportError:
    # Fallback pour que le code fonctionne même sans le fichier week2
    def analyze_csv(path): return {"columns":, "rows": 0}
    def generate_report_plan(meta): 
        return {
            "titre": "Rapport Analyse Données",
            "date": "2023-10-27",
            "auteur": "AI Agent",
            "chapitres": [
                {
                    "titre": "Introduction",
                    "sections": [
                        {"titre": "Contexte", "analyses": ["Analyse globale"]},
                        {"titre": "Objectifs", "analyses": ["KPIs principaux"]}
                    ]
                }
            ]
        }

load_dotenv()

# --- GESTIONNAIRE D'ÉTAT (Le Cerveau du Plan) ---

class PlanManager:
    """
    Classe responsable de la manipulation structurelle du plan.
    Agit comme une 'Source de Vérité' pour l'interface.
    """
    def __init__(self, plan_json: dict):
        self.plan = plan_json
        self.history =  # Pour le Undo/Redo (bonus)

    def get_plan(self) -> dict:
        return self.plan

    def update_plan(self, new_plan: dict):
        self.history.append(deepcopy(self.plan))
        self.plan = new_plan

    def render_markdown(self) -> str:
        """Transforme le JSON en une représentation Markdown visuelle et numérotée"""
        p = self.plan
        md = f"# 📋 {p.get('titre', 'Plan du Rapport')}\n\n"
        md += f"*Auteur: {p.get('auteur', 'IA')} | Date: {p.get('date', 'N/A')}*\n\n---\n\n"

        for i, chap in enumerate(p.get('chapitres',), 1):
            md += f"### {i}. {chap.get('titre', 'Sans titre')}\n"
            
            for j, sec in enumerate(chap.get('sections',), 1):
                analyses_count = len(sec.get('analyses',))
                # On ajoute un ID visuel pour que l'utilisateur puisse le référencer
                md += f"> **{i}.{j}** {sec.get('titre', 'Sans titre')} "
                md += f"*(Analyses: {analyses_count})*\n"
                
                # Afficher les détails en mode 'collapsible' pour ne pas surcharger
                if analyses_count > 0:
                    details = ", ".join(sec.get('analyses',)[:2])
                    if analyses_count > 2: details += "..."
                    md += f"> └─ *{details}*\n"
            md += "\n"
        
        return md

    def get_section_context(self, chapter_idx: int, section_idx: int) -> str:
        """Récupère le contenu d'une section spécifique pour l'IA"""
        try:
            chap = self.plan['chapitres'][chapter_idx - 1]
            sec = chap['sections'][section_idx - 1]
            return json.dumps(sec, ensure_ascii=False)
        except IndexError:
            return None

# --- AGENTS D'ÉDITION CHIRURGICALE (Les Outils) ---

async def ai_edit_operation(operation: str, target_context: str, user_instruction: str) -> Union[dict, list]:
    """
    Agent spécialisé qui ne fait QUE manipuler du JSON selon une instruction.
    Simule la logique de 'Split', 'Merge', 'Rewrite' des outils de présentation.
    """
    # Dans une vraie implémentation, appel à OpenAI/Anthropic/Gemini ici
    # Simulation de la réponse pour l'exemple
    await asyncio.sleep(1.5) # Simulation latence IA
    
    if operation == "split":
        # Simule une division de section
        original = json.loads(target_context)
        return [
            {"titre": f"{original['titre']} (Partie 1)", "analyses": original.get('analyses',)[:1]},
            {"titre": f"{original['titre']} (Partie 2)", "analyses": ["Nouvelle analyse approfondie"]}
        ]
    
    elif operation == "rename":
        return user_instruction # Le nouveau titre
        
    return None

# --- LOGIQUE CHAINLIT ---

@cl.on_chat_start
async def start():
    welcome = """# 📊 AI Statistical Reporter
**Mode Éditeur Interactif**

Uploadez votre CSV pour générer une structure de rapport que nous pourrons co-éditer.
"""
    await cl.Message(content=welcome).send()
    
    files = await cl.AskFileMessage(
        content="📁 **Uploadez votre CSV**", 
        accept=["text/csv", ".csv"],
        max_size_mb=20
    ).send()
    
    if files:
        file = files
        cl.user_session.set("csv_path", file.path)
        
        # 1. Analyse et Génération Initiale
        msg = cl.Message(content="⏳ **Analyse des données et génération du plan...**")
        await msg.send()
        
        # Appel synchrone vers l'agent architecte (existant)
        plan_dict = await cl.make_async(generate_plan_from_csv)(file.path)
        
        # 2. Initialisation du Manager
        manager = PlanManager(plan_dict)
        cl.user_session.set("manager", manager)
        
        # 3. Affichage du "Panneau de Contrôle"
        await msg.remove()
        await send_plan_interface(manager)

async def send_plan_interface(manager: PlanManager, message_object=None):
    """
    Affiche ou met à jour le plan avec les contrôles interactifs.
    C'est le coeur de l'UX 'Gamma-like'.
    """
    plan_md = manager.render_markdown()
    
    actions =
    
    # Si on a déjà un message affiché, on le met à jour (App-like experience)
    if message_object:
        message_object.content = plan_md
        message_object.actions = actions
        await message_object.update()
    else:
        # Sinon on crée le message principal qui servira d'interface
        msg = await cl.Message(content=plan_md, actions=actions).send()
        cl.user_session.set("plan_message_id", msg.id)

# --- GESTION DES ACTIONS (Workflow Interactif) ---

@cl.action_callback("edit_split")
async def handle_split(action: cl.Action):
    """Workflow pour diviser une section"""
    manager = cl.user_session.get("manager")
    
    # 1. Demander quelle section cibler
    res = await cl.AskUserMessage(
        content="Quelle section voulez-vous diviser? (ex: tapez '1.2')", 
        timeout=60
    ).send()
    
    if not res: return
    
    section_id = res['output'].strip()
    try:
        chap_idx, sec_idx = map(int, section_id.split('.'))
        
        # 2. Feedback visuel
        loading = cl.Message(content=f"🤖 **L'IA analyse la section {section_id} pour la scinder...**")
        await loading.send()
        
        # 3. Récupérer le contexte et appeler l'IA
        context = manager.get_section_context(chap_idx, sec_idx)
        if not context: raise ValueError("Section introuvable")
        
        new_sections = await ai_edit_operation("split", context, "")
        
        # 4. Appliquer la modification au JSON (Logique métier)
        # Ici on remplace l'élément unique par une liste de deux éléments
        plan = manager.get_plan()
        plan['chapitres'][chap_idx-1]['sections'][sec_idx-1:sec_idx] = new_sections
        manager.update_plan(plan)
        
        # 5. Rafraîchir l'interface principale
        await loading.remove()
        msg_id = cl.user_session.get("plan_message_id")
        # Astuce : récupérer l'objet message par son ID n'est pas direct en API simple,
        # donc on renvoie souvent un nouveau message ou on stocke l'objet si possible.
        # Ici, on ré-affiche le plan complet pour garantir la cohérence.
        await send_plan_interface(manager)
        
        await cl.Message(content=f"✅ Section {section_id} divisée avec succès!").send()
        
    except Exception as e:
        await cl.Message(content=f"❌ Erreur : {str(e)}. Vérifiez le format (ex: 1.2)").send()

@cl.action_callback("edit_rename")
async def handle_rename(action: cl.Action):
    """Workflow pour renommer"""
    manager = cl.user_session.get("manager")
    
    # Demande double : ID + Nouveau nom
    res = await cl.AskUserMessage(content="Indiquez l'ID de section et le nouveau titre (ex: '1.1 Contexte du marché')").send()
    if not res: return
    
    txt = res['output']
    try:
        parts = txt.split(' ', 1)
        if len(parts) < 2: raise ValueError("Format incorrect")
        
        s_id, new_title = parts, parts[1]
        c_idx, s_idx = map(int, s_id.split('.'))
        
        plan = manager.get_plan()
        plan['chapitres'][c_idx-1]['sections'][s_idx-1]['titre'] = new_title
        manager.update_plan(plan)
        
        await send_plan_interface(manager)
        
    except Exception as e:
        await cl.Message(content=f"❌ Erreur : {str(e)}").send()

@cl.action_callback("validate_final")
async def handle_validation(action: cl.Action):
    manager = cl.user_session.get("manager")
    final_json = manager.get_plan()
    
    # Sauvegarde
    with open("report_plan_validated.json", "w", encoding='utf-8') as f:
        json.dump(final_json, f, indent=2, ensure_ascii=False)
        
    await cl.Message(content="""# 🎉 Plan Validé!
Le plan a été figé. La génération du rapport complet va commencer.
Tapez `/generate` pour lancer la rédaction.""").send()

# --- WRAPPERS EXISTANTS ---

def generate_plan_from_csv(csv_path: str) -> dict:
    # Votre logique existante
    meta = analyze_csv(csv_path)
    return generate_report_plan(meta)

@cl.on_message
async def on_message(message: cl.Message):
    """Gestion des commandes textuelles pour les power-users"""
    txt = message.content.lower()
    
    if txt.startswith("/undo"):
        # Logique d'annulation (Bonus)
        await cl.Message(content="Fonctionnalité Undo non implémentée dans cette démo").send()
    
    elif txt == "/generate":
        # Lancer le script de génération final
        await cl.Message(content="🚀 Lancement de la rédaction des chapitres...").send()
    
    else:
        # Chat normal avec l'assistant sur le plan
        await cl.Message(content="Utilisez les boutons ci-dessus pour modifier le plan, ou tapez une commande spécifique.").send()