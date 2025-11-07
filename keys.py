#!/usr/bin/env python3
"""
CN14X HUD - Sistema de Gerenciamento de Keys
Autor: 14x_ice
Repositório: https://github.com/aaaaa1221aa/CN14X-HUD
"""

import json
import os
import time
from datetime import datetime, timedelta

# Configurações
KEYS_FILE = 'keys.json'

def load_keys():
    """Carrega keys do arquivo JSON"""
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_keys(keys):
    """Salva keys no arquivo JSON"""
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)
    print(f"✅ {len(keys)} key(s) salva(s) em {KEYS_FILE}")

def generate_random_key():
    """Gera uma key aleatória de 20 caracteres"""
    import random
    import string
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=20))

def create_key(duration_hours=24):
    """Cria uma nova key"""
    now = datetime.now()
    expiry = now + timedelta(hours=duration_hours)
    
    key_data = {
        'key': generate_random_key(),
        'generated': now.isoformat(),
        'expiry': int(expiry.timestamp()),
        'used': False,
        'usedAt': None
    }
    
    return key_data

def add_key(duration_hours=24):
    """Adiciona uma nova key ao sistema"""
    keys = load_keys()
    new_key = create_key(duration_hours)
    keys.append(new_key)
    save_keys(keys)
    
    print(f"\n🔑 NOVA KEY GERADA:")
    print(f"   Key: {new_key['key']}")
    print(f"   Gerada em: {new_key['generated']}")
    print(f"   Expira em: {datetime.fromtimestamp(new_key['expiry'])}")
    print(f"   Duração: {duration_hours}h")
    
    return new_key

def list_keys():
    """Lista todas as keys"""
    keys = load_keys()
    now = int(time.time())
    
    print(f"\n📊 TOTAL DE KEYS: {len(keys)}")
    print("=" * 80)
    
    valid = 0
    used = 0
    expired = 0
    
    for i, key in enumerate(keys, 1):
        status = ""
        if key['used']:
            status = "❌ USADA"
            used += 1
        elif key['expiry'] < now:
            status = "⏰ EXPIRADA"
            expired += 1
        else:
            status = "✅ VÁLIDA"
            valid += 1
        
        print(f"{i}. {key['key']} - {status}")
        if key['used']:
            print(f"   Usada em: {key['usedAt']}")
    
    print("=" * 80)
    print(f"✅ Válidas: {valid} | ❌ Usadas: {used} | ⏰ Expiradas: {expired}")

def clean_expired():
    """Remove keys expiradas (não usadas)"""
    keys = load_keys()
    now = int(time.time())
    
    before = len(keys)
    keys = [k for k in keys if k['expiry'] > now or k['used']]
    after = len(keys)
    
    save_keys(keys)
    print(f"🗑️ {before - after} key(s) expirada(s) removida(s)")
    print(f"✅ {after} key(s) mantida(s)")

def find_key(key_string):
    """Busca uma key específica"""
    keys = load_keys()
    
    for key in keys:
        if key['key'] == key_string:
            now = int(time.time())
            
            print(f"\n🔑 KEY ENCONTRADA:")
            print(f"   Key: {key['key']}")
            print(f"   Gerada: {key['generated']}")
            print(f"   Expira: {datetime.fromtimestamp(key['expiry'])}")
            
            if key['used']:
                print(f"   Status: ❌ USADA")
                print(f"   Usada em: {key['usedAt']}")
            elif key['expiry'] < now:
                print(f"   Status: ⏰ EXPIRADA")
            else:
                print(f"   Status: ✅ VÁLIDA")
            
            return key
    
    print(f"❌ Key '{key_string}' não encontrada!")
    return None

def mark_as_used(key_string):
    """Marca uma key como usada"""
    keys = load_keys()
    
    for key in keys:
        if key['key'] == key_string:
            key['used'] = True
            key['usedAt'] = datetime.now().isoformat()
            save_keys(keys)
            print(f"✅ Key {key_string} marcada como usada!")
            return True
    
    print(f"❌ Key {key_string} não encontrada!")
    return False

def validate_key(key_string):
    """Valida se uma key pode ser usada"""
    keys = load_keys()
    now = int(time.time())
    
    for key in keys:
        if key['key'] == key_string:
            if key['used']:
                return False, "Key já foi usada!"
            elif key['expiry'] < now:
                return False, "Key expirada!"
            else:
                return True, "Key válida!"
    
    return False, "Key não encontrada!"

def generate_multiple(count=10, duration=24):
    """Gera múltiplas keys de uma vez"""
    print(f"\n🔄 Gerando {count} keys...")
    
    for i in range(count):
        add_key(duration)
        time.sleep(0.1)  # Pequeno delay
    
    print(f"\n✅ {count} keys geradas com sucesso!")

def export_valid_keys():
    """Exporta apenas keys válidas para um arquivo"""
    keys = load_keys()
    now = int(time.time())
    
    valid_keys = [k for k in keys if not k['used'] and k['expiry'] > now]
    
    filename = f"keys_validas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(valid_keys, f, indent=2)
    
    print(f"✅ {len(valid_keys)} key(s) válida(s) exportada(s) para {filename}")

def statistics():
    """Mostra estatísticas detalhadas"""
    keys = load_keys()
    now = int(time.time())
    
    if not keys:
        print("❌ Nenhuma key encontrada!")
        return
    
    valid = sum(1 for k in keys if not k['used'] and k['expiry'] > now)
    used = sum(1 for k in keys if k['used'])
    expired = sum(1 for k in keys if k['expiry'] < now and not k['used'])
    
    print("\n" + "=" * 80)
    print("📊 ESTATÍSTICAS CN14X HUD")
    print("=" * 80)
    print(f"Total de keys: {len(keys)}")
    print(f"✅ Válidas: {valid} ({valid/len(keys)*100:.1f}%)")
    print(f"❌ Usadas: {used} ({used/len(keys)*100:.1f}%)")
    print(f"⏰ Expiradas: {expired} ({expired/len(keys)*100:.1f}%)")
    print("=" * 80)
    
    # Keys mais recentes
    recent = sorted(keys, key=lambda x: x['generated'], reverse=True)[:5]
    print("\n🕐 ÚLTIMAS 5 KEYS GERADAS:")
    for i, k in enumerate(recent, 1):
        status = "❌ USADA" if k['used'] else ("⏰ EXPIRADA" if k['expiry'] < now else "✅ VÁLIDA")
        print(f"{i}. {k['key']} - {status}")

def menu():
    """Menu interativo"""
    while True:
        print("\n" + "=" * 80)
        print("🔐 CN14X HUD - GERENCIADOR DE KEYS")
        print("=" * 80)
        print("1. 🔑 Gerar nova key")
        print("2. 📋 Listar todas as keys")
        print("3. 🔍 Buscar key específica")
        print("4. ✅ Marcar key como usada")
        print("5. 🗑️ Limpar keys expiradas")
        print("6. 🔢 Gerar múltiplas keys")
        print("7. 📊 Estatísticas")
        print("8. 💾 Exportar keys válidas")
        print("9. ✓ Validar key")
        print("0. ❌ Sair")
        print("=" * 80)
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == '1':
            hours = input("Duração em horas (padrão 24): ").strip()
            hours = int(hours) if hours else 24
            add_key(hours)
        
        elif choice == '2':
            list_keys()
        
        elif choice == '3':
            key = input("Digite a key: ").strip()
            find_key(key)
        
        elif choice == '4':
            key = input("Digite a key para marcar como usada: ").strip()
            mark_as_used(key)
        
        elif choice == '5':
            clean_expired()
        
        elif choice == '6':
            count = input("Quantas keys gerar? ").strip()
            count = int(count) if count else 10
            hours = input("Duração em horas (padrão 24): ").strip()
            hours = int(hours) if hours else 24
            generate_multiple(count, hours)
        
        elif choice == '7':
            statistics()
        
        elif choice == '8':
            export_valid_keys()
        
        elif choice == '9':
            key = input("Digite a key para validar: ").strip()
            is_valid, message = validate_key(key)
            print(f"\n{'✅' if is_valid else '❌'} {message}")
        
        elif choice == '0':
            print("\n👋 Até logo!")
            break
        
        else:
            print("\n❌ Opção inválida!")

if __name__ == '__main__':
    # Criar arquivo keys.json se não existir
    if not os.path.exists(KEYS_FILE):
        print(f"📁 Criando {KEYS_FILE}...")
        save_keys([])
    
    # Iniciar menu
    menu()
