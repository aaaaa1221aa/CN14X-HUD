#!/usr/bin/env python3
"""
CN14X HUD - Sistema de Gerenciamento de Keys
Autor: 14x_ice
Repositório: https://github.com/aaaaa1221aa/CN14X-HUD

NOVO: Sincronizado com GitHub Actions
"""

import json
import os
import time
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Configurações
KEYS_FILE = 'keys.json'
BACKUP_DIR = 'backups'

class KeyManager:
    def __init__(self):
        self.keys: List[Dict] = []
        self.load_keys()
    
    def load_keys(self) -> List[Dict]:
        """Carrega keys do arquivo JSON"""
        if os.path.exists(KEYS_FILE):
            try:
                with open(KEYS_FILE, 'r', encoding='utf-8') as f:
                    self.keys = json.load(f)
                print(f"✅ {len(self.keys)} key(s) carregada(s)")
            except json.JSONDecodeError:
                print("⚠️ Arquivo JSON corrompido, criando novo...")
                self.keys = []
        else:
            print("📁 Criando novo arquivo de keys...")
            self.keys = []
        return self.keys
    
    def save_keys(self) -> None:
        """Salva keys no arquivo JSON"""
        # Criar backup antes de salvar
        self._create_backup()
        
        with open(KEYS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.keys, f, indent=2, ensure_ascii=False)
        print(f"✅ {len(self.keys)} key(s) salva(s)")
    
    def _create_backup(self) -> None:
        """Cria backup do arquivo de keys"""
        if not os.path.exists(KEYS_FILE):
            return
        
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{BACKUP_DIR}/keys_backup_{timestamp}.json"
        
        try:
            with open(KEYS_FILE, 'r') as source:
                with open(backup_file, 'w') as dest:
                    dest.write(source.read())
            print(f"💾 Backup criado: {backup_file}")
        except Exception as e:
            print(f"⚠️ Erro ao criar backup: {e}")
    
    @staticmethod
    def generate_random_key() -> str:
        """Gera uma key aleatória de 20 caracteres"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=20))
    
    def create_key(self, duration_hours: int = 24) -> Dict:
        """Cria uma nova key"""
        now = datetime.now()
        expiry = now + timedelta(hours=duration_hours)
        
        key_data = {
            'key': self.generate_random_key(),
            'generated': now.isoformat(),
            'expiry': int(expiry.timestamp()),
            'used': False,
            'usedAt': None
        }
        
        return key_data
    
    def add_keys(self, count: int = 1, duration_hours: int = 24) -> List[Dict]:
        """Adiciona múltiplas keys ao sistema"""
        new_keys = []
        
        print(f"\n🔄 Gerando {count} key(s)...")
        for i in range(count):
            key = self.create_key(duration_hours)
            self.keys.append(key)
            new_keys.append(key)
            print(f"   {i+1}/{count} - {key['key']}")
        
        self.save_keys()
        return new_keys
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas das keys"""
        now = int(time.time())
        
        total = len(self.keys)
        valid = sum(1 for k in self.keys if not k['used'] and k['expiry'] > now)
        used = sum(1 for k in self.keys if k['used'])
        expired = sum(1 for k in self.keys if k['expiry'] < now and not k['used'])
        
        return {
            'total': total,
            'valid': valid,
            'used': used,
            'expired': expired
        }
    
    def list_keys(self, filter_type: str = 'all') -> None:
        """Lista keys com filtro"""
        now = int(time.time())
        
        filtered_keys = self.keys
        
        if filter_type == 'valid':
            filtered_keys = [k for k in self.keys if not k['used'] and k['expiry'] > now]
        elif filter_type == 'used':
            filtered_keys = [k for k in self.keys if k['used']]
        elif filter_type == 'expired':
            filtered_keys = [k for k in self.keys if k['expiry'] < now and not k['used']]
        
        print(f"\n📊 {'TODAS AS' if filter_type == 'all' else filter_type.upper()} KEYS: {len(filtered_keys)}")
        print("=" * 90)
        
        for i, key in enumerate(filtered_keys, 1):
            status = self._get_key_status(key)
            expiry_date = datetime.fromtimestamp(key['expiry']).strftime('%d/%m/%Y %H:%M')
            
            print(f"{i:3}. {key['key']} | {status} | Expira: {expiry_date}")
            
            if key['used'] and key['usedAt']:
                used_date = datetime.fromisoformat(key['usedAt']).strftime('%d/%m/%Y %H:%M')
                print(f"     └─ Usada em: {used_date}")
        
        print("=" * 90)
    
    def _get_key_status(self, key: Dict) -> str:
        """Retorna o status formatado de uma key"""
        now = int(time.time())
        
        if key['used']:
            return "❌ USADA"
        elif key['expiry'] < now:
            return "⏰ EXPIRADA"
        else:
            return "✅ VÁLIDA"
    
    def clean_expired(self) -> int:
        """Remove keys expiradas não usadas"""
        now = int(time.time())
        before = len(self.keys)
        
        self.keys = [k for k in self.keys if k['expiry'] > now or k['used']]
        removed = before - len(self.keys)
        
        if removed > 0:
            self.save_keys()
        
        return removed
    
    def find_key(self, key_string: str) -> Optional[Dict]:
        """Busca uma key específica"""
        for key in self.keys:
            if key['key'] == key_string:
                return key
        return None
    
    def mark_as_used(self, key_string: str) -> bool:
        """Marca uma key como usada"""
        for key in self.keys:
            if key['key'] == key_string:
                key['used'] = True
                key['usedAt'] = datetime.now().isoformat()
                self.save_keys()
                return True
        return False
    
    def validate_key(self, key_string: str) -> tuple:
        """Valida se uma key pode ser usada"""
        key = self.find_key(key_string)
        
        if not key:
            return False, "Key não encontrada!"
        
        now = int(time.time())
        
        if key['used']:
            return False, "Key já foi usada!"
        elif key['expiry'] < now:
            return False, "Key expirada!"
        else:
            return True, "Key válida!"
    
    def export_valid_keys(self) -> str:
        """Exporta keys válidas para um arquivo"""
        now = int(time.time())
        valid_keys = [k for k in self.keys if not k['used'] and k['expiry'] > now]
        
        filename = f"keys_validas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(valid_keys, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def show_statistics(self) -> None:
        """Mostra estatísticas detalhadas"""
        stats = self.get_statistics()
        
        print("\n" + "=" * 90)
        print("📊 ESTATÍSTICAS CN14X HUD")
        print("=" * 90)
        print(f"Total de keys:     {stats['total']:5}")
        print(f"✅ Válidas:        {stats['valid']:5} ({stats['valid']/stats['total']*100 if stats['total'] > 0 else 0:.1f}%)")
        print(f"❌ Usadas:         {stats['used']:5} ({stats['used']/stats['total']*100 if stats['total'] > 0 else 0:.1f}%)")
        print(f"⏰ Expiradas:      {stats['expired']:5} ({stats['expired']/stats['total']*100 if stats['total'] > 0 else 0:.1f}%)")
        print("=" * 90)
        
        # Keys mais recentes
        if self.keys:
            recent = sorted(self.keys, key=lambda x: x['generated'], reverse=True)[:5]
            print("\n🕐 ÚLTIMAS 5 KEYS GERADAS:")
            for i, key in enumerate(recent, 1):
                status = self._get_key_status(key)
                gen_date = datetime.fromisoformat(key['generated']).strftime('%d/%m/%Y %H:%M')
                print(f"{i}. {key['key']} | {status} | Gerada: {gen_date}")
        
        print()


def menu():
    """Menu interativo melhorado"""
    manager = KeyManager()
    
    while True:
        print("\n" + "=" * 90)
        print("🔐 CN14X HUD - GERENCIADOR DE KEYS v2.0")
        print("=" * 90)
        print(" 1. 🔑 Gerar nova key")
        print(" 2. 📋 Listar todas as keys")
        print(" 3. ✅ Listar apenas keys válidas")
        print(" 4. ❌ Listar apenas keys usadas")
        print(" 5. ⏰ Listar apenas keys expiradas")
        print(" 6. 🔍 Buscar key específica")
        print(" 7. ✓ Marcar key como usada")
        print(" 8. 🗑️ Limpar keys expiradas")
        print(" 9. 🔢 Gerar múltiplas keys")
        print("10. 📊 Estatísticas")
        print("11. 💾 Exportar keys válidas")
        print("12. 🔄 Recarregar keys do arquivo")
        print("13. ✓ Validar key")
        print(" 0. ❌ Sair")
        print("=" * 90)
        
        choice = input("\n👉 Escolha uma opção: ").strip()
        
        try:
            if choice == '1':
                hours = input("⏱️  Duração em horas (padrão 24): ").strip()
                hours = int(hours) if hours else 24
                key = manager.add_keys(1, hours)[0]
                print(f"\n✅ Key gerada: {key['key']}")
                print(f"   Expira em: {datetime.fromtimestamp(key['expiry']).strftime('%d/%m/%Y %H:%M')}")
            
            elif choice == '2':
                manager.list_keys('all')
            
            elif choice == '3':
                manager.list_keys('valid')
            
            elif choice == '4':
                manager.list_keys('used')
            
            elif choice == '5':
                manager.list_keys('expired')
            
            elif choice == '6':
                key_str = input("🔍 Digite a key: ").strip().upper()
                key = manager.find_key(key_str)
                if key:
                    print(f"\n🔑 KEY ENCONTRADA:")
                    print(f"   Key: {key['key']}")
                    print(f"   Status: {manager._get_key_status(key)}")
                    print(f"   Gerada: {datetime.fromisoformat(key['generated']).strftime('%d/%m/%Y %H:%M')}")
                    print(f"   Expira: {datetime.fromtimestamp(key['expiry']).strftime('%d/%m/%Y %H:%M')}")
                    if key['used']:
                        print(f"   Usada em: {datetime.fromisoformat(key['usedAt']).strftime('%d/%m/%Y %H:%M')}")
                else:
                    print("\n❌ Key não encontrada!")
            
            elif choice == '7':
                key_str = input("✓ Digite a key para marcar como usada: ").strip().upper()
                if manager.mark_as_used(key_str):
                    print(f"\n✅ Key {key_str} marcada como usada!")
                else:
                    print(f"\n❌ Key {key_str} não encontrada!")
            
            elif choice == '8':
                removed = manager.clean_expired()
                print(f"\n🗑️ {removed} key(s) expirada(s) removida(s)")
            
            elif choice == '9':
                count = input("🔢 Quantas keys gerar? ").strip()
                count = int(count) if count else 10
                hours = input("⏱️  Duração em horas (padrão 24): ").strip()
                hours = int(hours) if hours else 24
                manager.add_keys(count, hours)
            
            elif choice == '10':
                manager.show_statistics()
            
            elif choice == '11':
                filename = manager.export_valid_keys()
                stats = manager.get_statistics()
                print(f"\n💾 {stats['valid']} key(s) válida(s) exportada(s) para {filename}")
            
            elif choice == '12':
                manager.load_keys()
                print("\n🔄 Keys recarregadas do arquivo!")
            
            elif choice == '13':
                key_str = input("✓ Digite a key para validar: ").strip().upper()
                is_valid, message = manager.validate_key(key_str)
                print(f"\n{'✅' if is_valid else '❌'} {message}")
            
            elif choice == '0':
                print("\n👋 Até logo!")
                break
            
            else:
                print("\n❌ Opção inválida!")
        
        except ValueError as e:
            print(f"\n❌ Erro: Entrada inválida! {e}")
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")


if __name__ == '__main__':
    # Criar arquivo keys.json se não existir
    if not os.path.exists(KEYS_FILE):
        print(f"📁 Criando {KEYS_FILE}...")
        with open(KEYS_FILE, 'w') as f:
            json.dump([], f)
    
    # Iniciar menu
    try:
        menu()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido pelo usuário. Até logo!")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
