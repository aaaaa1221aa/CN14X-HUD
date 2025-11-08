#!/usr/bin/env python3
"""
Script para limpar automaticamente keys expiradas (24h+)
Autor: 14x_ice
Uso: python3 clean-expired-keys.py
"""

import json
import os
from datetime import datetime
import subprocess

KEYS_FILE = 'keys.json'

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

def clean_expired_keys():
    """Remove keys expiradas (24 horas)"""
    print("\n🔄 Carregando keys...")
    keys = load_keys()
    original_count = len(keys)
    
    # Timestamp atual
    now = int(datetime.now().timestamp())
    
    # Filtrar apenas keys válidas (não expiradas)
    valid_keys = []
    expired_keys = []
    
    for key in keys:
        if key['expiry'] > now:
            valid_keys.append(key)
        else:
            expired_keys.append(key)
    
    # Exibir resultado
    print(f"\n📊 ANÁLISE:")
    print(f"   Total de keys: {original_count}")
    print(f"   Keys válidas: {len(valid_keys)}")
    print(f"   Keys expiradas: {len(expired_keys)}")
    
    if expired_keys:
        print(f"\n🗑️  KEYS EXPIRADAS REMOVIDAS:")
        for key in expired_keys:
            expiry_date = datetime.fromtimestamp(key['expiry']).strftime('%Y-%m-%d %H:%M:%S')
            print(f"   • {key['key']} (expirou em {expiry_date})")
        
        # Salvar arquivo atualizado
        save_keys(valid_keys)
        print(f"\n✅ Arquivo atualizado! {len(expired_keys)} key(s) removida(s)")
        
        # Commit automático no git
        try:
            print(f"\n📤 Fazendo commit no GitHub...")
            subprocess.run(['git', 'add', KEYS_FILE], check=True)
            subprocess.run([
                'git', 'commit', '-m', 
                f'🗑️ Auto-clean: Remove {len(expired_keys)} expired keys'
            ], check=True)
            subprocess.run(['git', 'push'], check=True)
            print(f"✅ Commit enviado com sucesso!")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Erro no git: {e}")
            print(f"   Arquivo salvo localmente. Faça commit manual.")
    else:
        print(f"\n✅ Nenhuma key expirada encontrada!")
    
    return len(expired_keys)

def main():
    print("=" * 60)
    print("🗑️  MM2 PROFESSIONAL - LIMPEZA DE KEYS EXPIRADAS")
    print("   Remove automaticamente keys com mais de 24 horas")
    print("=" * 60)
    
    # Verificar se está no diretório correto
    if not os.path.exists('.git'):
        print("\n❌ ERRO: Execute este script na raiz do repositório!")
        print("   Comando: cd CN14X-HUD")
        return
    
    if not os.path.exists(KEYS_FILE):
        print(f"\n❌ ERRO: Arquivo {KEYS_FILE} não encontrado!")
        return
    
    # Executar limpeza
    removed = clean_expired_keys()
    
    print("\n" + "=" * 60)
    if removed > 0:
        print(f"✅ Limpeza concluída! {removed} key(s) removida(s)")
    else:
        print("✅ Nenhuma ação necessária")
    print("=" * 60)

if __name__ == '__main__':
    main()
