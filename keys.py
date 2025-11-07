// ============================================
// SCRIPT PARA EXPORTAR KEYS DO NAVEGADOR
// ============================================
// Execute este código no Console do navegador (F12)
// para exportar todas as keys geradas

(function exportKeys() {
    console.log('🔐 MM2 Professional - Exportador de Keys');
    console.log('==========================================\n');
    
    // Pegar todas as keys do localStorage
    const allKeys = JSON.parse(localStorage.getItem('mm2_all_keys') || '[]');
    
    if (allKeys.length === 0) {
        console.log('❌ Nenhuma key encontrada!');
        console.log('💡 Gere algumas keys primeiro no site.');
        return;
    }
    
    console.log(`✅ ${allKeys.length} key(s) encontrada(s)!\n`);
    
    // Formatar JSON bonito
    const jsonOutput = JSON.stringify(allKeys, null, 2);
    
    // Mostrar no console
    console.log('📋 JSON para copiar:');
    console.log('====================');
    console.log(jsonOutput);
    console.log('====================\n');
    
    // Criar arquivo para download
    const blob = new Blob([jsonOutput], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mm2_keys_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    console.log('✅ Arquivo baixado com sucesso!');
    console.log('📁 Nome: mm2_keys_' + Date.now() + '.json');
    console.log('\n💡 PRÓXIMOS PASSOS:');
    console.log('1. Faça upload deste arquivo no GitHub');
    console.log('2. Renomeie para "keys.json"');
    console.log('3. Atualize a URL no script Roblox');
    
    // Estatísticas
    const now = Math.floor(Date.now() / 1000);
    const validKeys = allKeys.filter(k => !k.used && k.expiry > now);
    const usedKeys = allKeys.filter(k => k.used);
    const expiredKeys = allKeys.filter(k => k.expiry <= now);
    
    console.log('\n📊 ESTATÍSTICAS:');
    console.log(`   Total: ${allKeys.length}`);
    console.log(`   ✅ Válidas: ${validKeys.length}`);
    console.log(`   ❌ Usadas: ${usedKeys.length}`);
    console.log(`   ⏰ Expiradas: ${expiredKeys.length}`);
    
    // Mostrar últimas 5 keys
    console.log('\n🔑 ÚLTIMAS 5 KEYS GERADAS:');
    allKeys.slice(-5).forEach((k, i) => {
        const status = k.used ? '❌ USADA' : (k.expiry > now ? '✅ VÁLIDA' : '⏰ EXPIRADA');
        console.log(`   ${i + 1}. ${k.key} - ${status}`);
    });
})();

// ============================================
// LIMPAR KEYS ANTIGAS/EXPIRADAS
// ============================================
// Use este código para limpar keys expiradas

function cleanExpiredKeys() {
    const allKeys = JSON.parse(localStorage.getItem('mm2_all_keys') || '[]');
    const now = Math.floor(Date.now() / 1000);
    
    const validKeys = allKeys.filter(k => k.expiry > now || k.used);
    const removed = allKeys.length - validKeys.length;
    
    localStorage.setItem('mm2_all_keys', JSON.stringify(validKeys));
    
    console.log(`🗑️ ${removed} key(s) expirada(s) removida(s)!`);
    console.log(`✅ ${validKeys.length} key(s) mantida(s).`);
}

// ============================================
// RESETAR SISTEMA (CUIDADO!)
// ============================================
// Use este código para limpar TODAS as keys

function resetAllKeys() {
    if (confirm('⚠️ ATENÇÃO! Isso vai deletar TODAS as keys. Continuar?')) {
        localStorage.removeItem('mm2_all_keys');
        console.log('✅ Sistema resetado! Todas as keys foram removidas.');
    }
}

// ============================================
// BUSCAR KEY ESPECÍFICA
// ============================================

function findKey(keyString) {
    const allKeys = JSON.parse(localStorage.getItem('mm2_all_keys') || '[]');
    const found = allKeys.find(k => k.key === keyString);
    
    if (found) {
        console.log('🔑 KEY ENCONTRADA:');
        console.log(JSON.stringify(found, null, 2));
        
        const now = Math.floor(Date.now() / 1000);
        if (found.used) {
            console.log('❌ Status: USADA');
            console.log('⏰ Usada em:', new Date(found.usedAt).toLocaleString());
        } else if (found.expiry < now) {
            console.log('⏰ Status: EXPIRADA');
        } else {
            console.log('✅ Status: VÁLIDA');
        }
    } else {
        console.log('❌ Key não encontrada!');
    }
}

// ============================================
// MARCAR KEY COMO USADA
// ============================================

function markKeyAsUsed(keyString) {
    const allKeys = JSON.parse(localStorage.getItem('mm2_all_keys') || '[]');
    const keyIndex = allKeys.findIndex(k => k.key === keyString);
    
    if (keyIndex !== -1) {
        allKeys[keyIndex].used = true;
        allKeys[keyIndex].usedAt = new Date().toISOString();
        localStorage.setItem('mm2_all_keys', JSON.stringify(allKeys));
        console.log('✅ Key marcada como usada!');
    } else {
        console.log('❌ Key não encontrada!');
    }
}

// ============================================
// INSTRUÇÕES DE USO
// ============================================

console.log('\n📖 COMANDOS DISPONÍVEIS:');
console.log('   exportKeys()           - Exportar todas as keys');
console.log('   cleanExpiredKeys()     - Limpar keys expiradas');
console.log('   resetAllKeys()         - Resetar sistema (CUIDADO!)');
console.log('   findKey("KEY")         - Buscar key específica');
console.log('   markKeyAsUsed("KEY")   - Marcar key como usada');
console.log('\n💡 Cole estes comandos no console e pressione Enter!');
