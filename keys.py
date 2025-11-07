#!/usr/bin/env python3
"""
Script para adicionar keys automaticamente no GitHub
Autor: 14x_ice
"""

import json
import os
import random
import string
from datetime import datetime, timedelta
import subprocess

# Configurações
KEYS_FILE = 'keys.json'
REPO_PATH = '.'  # Diretório do repositório

def generate_random_key():
    """Gera uma key aleatória de 20 caracteres"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=20))

def load_keys():
    """Carrega keys do arquivo"""
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_keys(keys):
    """Salva keys no arquivo"""
    with open(KEYS_FILE, 'w', encoding='utf-8') as f:
        json.dump(keys, f, indent=2, ensure_ascii=False)

def clean_expired_keys(keys):
    """Remove keys expiradas"""
    now = int(datetime.now().timestamp())
    return [k for k in keys if k['expiry'] > now]

def create_key(duration_hours=24):
    """Cria uma nova key"""
    now = datetime.now()
    expiry = now + timedelta(hours=duration_hours)
    
    return {
        'key': generate_random_key(),
        'generated': now.isoformat(),
        'expiry': int(expiry.timestamp()),
        'used': False,
        'usedAt': None
    }

def git_commit_and_push(message):
    """Faz commit e push para o GitHub"""
    try:
        subprocess.run(['git', 'add', KEYS_FILE], check=True)
        subprocess.run(['git', 'commit', '-m', message], check=True)
        subprocess.run(['git', 'push'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no git: {e}")
        return False

def add_keys_and_commit(count=10, duration=24):
    """Adiciona keys e faz commit automático"""
    print(f"\n🔄 Gerando {count} keys...")
    
    # Carregar keys existentes
    keys = load_keys()
    original_count = len(keys)
    
    # Limpar expiradas
    keys = clean_expired_keys(keys)
    removed = original_count - len(keys)
    if removed > 0:
        print(f"🗑️  {removed} key(s) expirada(s) removida(s)")
    
    # Gerar novas keys
    new_keys = []
    for i in range(count):
        key = create_key(duration)
        keys.append(key)
        new_keys.append(key)
        print(f"   {i+1}/{count} - {key['key']}")
    
    # Salvar
    save_keys(keys)
    
    # Commit e push
    print(f"\n📤 Fazendo commit no GitHub...")
    commit_message = f"🔑 Add {count} new keys | Total: {len(keys)} keys"
    
    if git_commit_and_push(commit_message):
        print(f"✅ Keys adicionadas com sucesso!")
        print(f"\n📊 Estatísticas:")
        print(f"   Total de keys: {len(keys)}")
        print(f"   Keys novas: {count}")
        print(f"   Válidas: {len([k for k in keys if not k['used']])}")
        print(f"   Usadas: {len([k for k in keys if k['used']])}")
        
        print(f"\n🌐 As keys estarão disponíveis em:")
        print(f"   https://aaaaa1221aa.github.io/CN14X-HUD/")
        print(f"   (aguarde ~1 minuto para atualizar)")
        
        return True
    else:
        print(f"❌ Erro ao fazer commit!")
        return False

def main():
    """Menu principal"""
    print("=" * 80)
    print("🔐 MM2 PROFESSIONAL - GERADOR AUTOMÁTICO DE KEYS")
    print("   Repositório: aaaaa1221aa/CN14X-HUD")
    print("=" * 80)
    
    while True:
        print("\n📋 OPÇÕES:")
        print("1. 🔑 Gerar 10 keys (padrão)")
        print("2. 🔢 Gerar quantidade personalizada")
        print("3. 📊 Ver estatísticas atuais")
        print("4. 🗑️ Limpar keys expiradas")
        print("0. ❌ Sair")
        
        choice = input("\n👉 Escolha uma opção: ").strip()
        
        if choice == '1':
            add_keys_and_commit(10, 24)
        
        elif choice == '2':
            try:
                count = int(input("Quantas keys gerar? "))
                hours = int(input("Validade (horas, padrão 24): ") or "24")
                add_keys_and_commit(count, hours)
            except ValueError:
                print("❌ Valor inválido!")
        
        elif choice == '3':
            keys = load_keys()
            keys = clean_expired_keys(keys)
            now = int(datetime.now().timestamp())
            
            valid = len([k for k in keys if not k['used'] and k['expiry'] > now])
            used = len([k for k in keys if k['used']])
            
            print(f"\n📊 ESTATÍSTICAS:")
            print(f"   Total: {len(keys)}")
            print(f"   Válidas: {valid}")
            print(f"   Usadas: {used}")
        
        elif choice == '4':
            keys = load_keys()
            before = len(keys)
            keys = clean_expired_keys(keys)
            after = len(keys)
            
            save_keys(keys)
            removed = before - after
            
            if removed > 0:
                print(f"\n🗑️  {removed} key(s) removida(s)")
                
                if git_commit_and_push(f"🗑️ Clean {removed} expired keys"):
                    print("✅ Atualizado no GitHub!")
            else:
                print("✅ Nenhuma key expirada!")
        
        elif choice == '0':
            print("\n👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida!")

if __name__ == '__main__':
    # Verificar se está no diretório do repositório
    if not os.path.exists('.git'):
        print("❌ ERRO: Este script deve ser executado na raiz do repositório!")
        print("   Navegue até: cd CN14X-HUD")
        exit(1)
    
    main()
