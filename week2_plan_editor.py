"""
SEMAINE 2 - Jour 4-5: Éditeur de plan interactif
Permet de modifier, régénérer ou affiner le plan
"""

import os
import json
from dotenv import load_dotenv
from google.genai import Client as GminiClient
from langchain_anthropic import ChatAnthropic

load_dotenv()


def load_plan(plan_file: str = "report_plan.json") -> dict:
    """Charge un plan existant"""
    if not os.path.exists(plan_file):
        raise FileNotFoundError(f"Fichier {plan_file} introuvable. Générez d'abord un plan avec week2_architect_agent.py")
    
    with open(plan_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def display_plan(plan: dict):
    """Affiche le plan de manière lisible"""
    print("\n" + "="*70)
    print(f"📋 {plan['titre']}")
    print("="*70)
    
    for i, chapitre in enumerate(plan['chapitres'], 1):
        print(f"\n{chapitre['numero']}. {chapitre['titre']}")
        
        for j, section in enumerate(chapitre['sections'], 1):
            print(f"   {chapitre['numero']}.{j}. {section['titre']}")
            
            for analyse in section['analyses']:
                print(f"      • {analyse}")
    
    print("\n" + "="*70)


def modify_plan_with_ai(plan: dict, instruction: str) -> dict:
    """
    Modifie le plan en utilisant l'IA (Gemini ou Anthropic)
    selon les instructions de l'utilisateur
    """
    print("\n🤖 Modification du plan avec l'IA...")
    
    prompt = f"""
Tu es un expert en structuration de rapports statistiques.

Voici le plan actuel d'un rapport:
{json.dumps(plan, indent=2, ensure_ascii=False)}

L'utilisateur demande la modification suivante:
"{instruction}"

TÂCHE: Modifie le plan selon cette instruction en gardant la même structure JSON.

IMPORTANT:
- Garde la structure JSON identique (même format)
- Applique uniquement les modifications demandées
- Conserve le reste du plan intact
- Retourne UNIQUEMENT le nouveau JSON complet, sans markdown ni explications

"""
    
    # Essayer Gemini
    gmini_key = os.getenv("GMINI_API_KEY")
    modified_json = None
    
    if gmini_key:
        try:
            print("   Utilisation de Gemini 2.5 Flash...")
            gclient = GminiClient(api_key=gmini_key)
            chat = gclient.chats.create(model="gemini-2.5-flash")
            gres = chat.send_message(prompt)
            
            # Extraire le texte
            gen = None
            if hasattr(gres, "output_text"):
                gen = gres.output_text
            elif hasattr(gres, "candidates") and gres.candidates:
                first = gres.candidates[0]
                if hasattr(first, "content"):
                    gen = first.content
                    if not isinstance(gen, str) and hasattr(gen, "parts"):
                        parts = getattr(gen, "parts") or []
                        texts = [getattr(p, "text", "") for p in parts if getattr(p, "text", None)]
                        gen = "\n".join(texts).strip()
            
            if gen:
                modified_json = str(gen)
        except Exception as e:
            print(f"   ⚠️ Erreur Gemini: {e}")
    
    # Fallback Anthropic
    if not modified_json:
        try:
            print("   Utilisation de Claude (Anthropic)...")
            llm = ChatAnthropic(
                model="claude-sonnet-4-20250514",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                temperature=0.3
            )
            response = llm.invoke(prompt)
            modified_json = response.content
        except Exception as e:
            print(f"   ⚠️ Erreur Anthropic: {e}")
            return plan  # Retourner le plan original en cas d'échec
    
    # Nettoyer le JSON
    if "```json" in modified_json:
        modified_json = modified_json.split("```json")[1].split("```")[0].strip()
    elif "```" in modified_json:
        modified_json = modified_json.split("```")[1].split("```")[0].strip()
    
    # Parser le JSON
    try:
        new_plan = json.loads(modified_json)
        print("✅ Plan modifié avec succès")
        return new_plan
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {e}")
        print("⚠️ Conservation du plan original")
        return plan


def add_chapter(plan: dict) -> dict:
    """Ajoute un nouveau chapitre au plan"""
    print("\n➕ Ajout d'un nouveau chapitre")
    
    titre = input("Titre du nouveau chapitre: ")
    
    # Déterminer le numéro
    next_num = len(plan['chapitres']) + 1
    
    nouveau_chapitre = {
        "numero": str(next_num),
        "titre": titre,
        "sections": [
            {
                "titre": "Section à définir",
                "analyses": ["Analyse à détailler"]
            }
        ]
    }
    
    plan['chapitres'].append(nouveau_chapitre)
    print(f"✅ Chapitre {next_num} ajouté")
    
    return plan


def remove_chapter(plan: dict) -> dict:
    """Supprime un chapitre du plan"""
    print("\n➖ Suppression d'un chapitre")
    display_plan(plan)
    
    try:
        num = int(input("\nNuméro du chapitre à supprimer: "))
        
        if 1 <= num <= len(plan['chapitres']):
            removed = plan['chapitres'].pop(num - 1)
            print(f"✅ Chapitre '{removed['titre']}' supprimé")
            
            # Renumeroter
            for i, chap in enumerate(plan['chapitres'], 1):
                chap['numero'] = str(i)
        else:
            print("❌ Numéro invalide")
    except ValueError:
        print("❌ Entrée invalide")
    
    return plan


def save_plan(plan: dict, output_file: str = "report_plan.json"):
    """Sauvegarde le plan"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(plan, indent=2, ensure_ascii=False, fp=f)
    print(f"✅ Plan sauvegardé dans: {output_file}")


def interactive_menu(plan: dict) -> dict:
    """Menu interactif pour éditer le plan"""
    while True:
        print("\n" + "="*70)
        print("MENU D'ÉDITION DU PLAN")
        print("="*70)
        print("1. Afficher le plan complet")
        print("2. Modifier le plan avec l'IA (texte libre)")
        print("3. Ajouter un nouveau chapitre")
        print("4. Supprimer un chapitre")
        print("5. Changer le titre du rapport")
        print("6. Sauvegarder et quitter")
        print("7. Quitter sans sauvegarder")
        print("="*70)
        
        choix = input("\nVotre choix: ")
        
        if choix == "1":
            display_plan(plan)
        
        elif choix == "2":
            print("\nExemples d'instructions:")
            print("- 'Ajoute une section sur l'analyse de régression'")
            print("- 'Rends le chapitre 2 plus détaillé'")
            print("- 'Simplifie le chapitre 3'")
            print("- 'Ajoute des analyses de machine learning au chapitre 4'")
            
            instruction = input("\n📝 Votre instruction: ")
            plan = modify_plan_with_ai(plan, instruction)
            display_plan(plan)
        
        elif choix == "3":
            plan = add_chapter(plan)
            display_plan(plan)
        
        elif choix == "4":
            plan = remove_chapter(plan)
            display_plan(plan)
        
        elif choix == "5":
            nouveau_titre = input("\n📝 Nouveau titre du rapport: ")
            plan['titre'] = nouveau_titre
            print("✅ Titre modifié")
        
        elif choix == "6":
            save_plan(plan)
            print("\n✅ Plan sauvegardé! Au revoir.")
            break
        
        elif choix == "7":
            confirm = input("\n⚠️ Quitter sans sauvegarder ? (o/n): ")
            if confirm.lower() == 'o':
                print("Au revoir!")
                break
        
        else:
            print("❌ Choix invalide")
    
    return plan


def main():
    """Point d'entrée"""
    print("="*70)
    print("SEMAINE 2 - ÉDITEUR DE PLAN INTERACTIF")
    print("="*70)
    
    try:
        # Charger le plan existant
        plan = load_plan()
        print(" Plan chargé depuis report_plan.json")
        
        # Menu interactif
        plan = interactive_menu(plan)
        
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        print("💡 Générez d'abord un plan avec: python week2_architect_agent.py test_data.csv")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")


if __name__ == "__main__":
    main()