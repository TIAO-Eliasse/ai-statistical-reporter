"""
Inspection de la classe Sandbox de e2b_code_interpreter
Pour comprendre quels paramètres sont acceptés
"""

import inspect
import e2b_code_interpreter
from e2b_code_interpreter import Sandbox

print("=" * 80)
print("INSPECTION DE E2B_CODE_INTERPRETER")
print("=" * 80)

# 1. Vérifier le package
print(f"\n📦 Package e2b_code_interpreter:")
print(f"   Location: {e2b_code_interpreter.__file__}")
print(f"   Version: {getattr(e2b_code_interpreter, '__version__', 'Non disponible')}")

# 2. Lister tout ce qui est dans le package
print(f"\n📋 Contenu du package:")
for name in dir(e2b_code_interpreter):
    if not name.startswith('_'):
        obj = getattr(e2b_code_interpreter, name)
        print(f"   - {name}: {type(obj).__name__}")

# 3. Inspecter la classe Sandbox
print(f"\n🔍 Classe Sandbox:")
print(f"   Type: {type(Sandbox)}")
print(f"   Module: {Sandbox.__module__}")
print(f"   File: {inspect.getfile(Sandbox)}")

# 4. Signature du __init__
print(f"\n📝 Signature de Sandbox.__init__():")
try:
    sig = inspect.signature(Sandbox.__init__)
    print(f"   {sig}")
    
    print(f"\n   Paramètres:")
    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue
        default = param.default
        if default == inspect.Parameter.empty:
            default = "REQUIS"
        print(f"   - {param_name}: {param.annotation if param.annotation != inspect.Parameter.empty else 'Any'} = {default}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# 5. MRO (Method Resolution Order)
print(f"\n🔗 Hiérarchie des classes (MRO):")
for i, cls in enumerate(Sandbox.__mro__):
    print(f"   {i}. {cls.__module__}.{cls.__name__}")

# 6. Attributs et méthodes de Sandbox
print(f"\n🛠️ Méthodes principales de Sandbox:")
for name in dir(Sandbox):
    if not name.startswith('_'):
        attr = getattr(Sandbox, name)
        if callable(attr):
            try:
                sig = inspect.signature(attr)
                print(f"   - {name}{sig}")
            except:
                print(f"   - {name}(...)")

# 7. Documentation
print(f"\n📚 Documentation de Sandbox.__init__:")
if Sandbox.__init__.__doc__:
    print(Sandbox.__init__.__doc__)
else:
    print("   Aucune documentation disponible")

# 8. Vérifier si c'est une factory function
print(f"\n🏭 Vérification factory pattern:")
if 'Sandbox' in dir(e2b_code_interpreter):
    actual_sandbox = e2b_code_interpreter.Sandbox
    print(f"   e2b_code_interpreter.Sandbox est: {type(actual_sandbox)}")
    if callable(actual_sandbox):
        print(f"   C'est une fonction/classe callable")
        try:
            sig = inspect.signature(actual_sandbox)
            print(f"   Signature: {sig}")
        except:
            print(f"   Signature non disponible")

print("\n" + "=" * 80)
print("FIN DE L'INSPECTION")
print("=" * 80)