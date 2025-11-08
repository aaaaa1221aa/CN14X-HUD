// server.js
const express = require('express');
const fs = require('fs').promises;
const path = require('path');

const app = express();
app.use(express.json());

const KEYS_FILE = path.join(__dirname, 'keys.json');
const TEMP_FILE = path.join(__dirname, 'keys.json.tmp');

async function readKeysFile() {
  try {
    const raw = await fs.readFile(KEYS_FILE, 'utf8');
    const parsed = JSON.parse(raw);
    if (typeof parsed !== 'object' || parsed === null) throw new Error('Formato inválido');
    return parsed;
  } catch (err) {
    // Se arquivo não existe, começamos com objeto vazio
    if (err.code === 'ENOENT') return {};
    throw err;
  }
}

async function writeKeysFile(obj) {
  const json = JSON.stringify(obj, null, 2) + '\n';
  // escrito de forma atômica
  await fs.writeFile(TEMP_FILE, json, 'utf8');
  await fs.rename(TEMP_FILE, KEYS_FILE);
}

// Validação simples dos dados recebidos
function validatePayload(p) {
  if (!p) return 'Payload vazio';
  if (typeof p.id !== 'string' || p.id.trim() === '') return 'Campo id inválido';
  if (typeof p.key !== 'string' || p.key.trim() === '') return 'Campo key inválido';
  if (typeof p.generated !== 'string') return 'Campo generated deve ser string ISO';
  if (typeof p.expiry !== 'number') return 'Campo expiry deve ser número (timestamp)';
  return null;
}

app.post('/add-key', async (req, res) => {
  try {
    const err = validatePayload(req.body);
    if (err) return res.status(400).json({ error: err });

    const { id, key, generated, expiry } = req.body;
    const entry = {
      key,
      generated,
      expiry,
      used: false,
      usedAt: null
    };

    const data = await readKeysFile();

    // Se já existir id, sobrescreve (ou você pode recusar; modifique aqui)
    data[id] = entry;

    await writeKeysFile(data);

    return res.json({ ok: true, id, entry });
  } catch (e) {
    console.error('Erro /add-key:', e);
    return res.status(500).json({ error: 'erro interno' });
  }
});

// Endpoint para marcar uma key como usada (ex.: quando jogador resgata)
app.post('/use-key', async (req, res) => {
  try {
    const { id } = req.body;
    if (typeof id !== 'string' || id.trim() === '') return res.status(400).json({ error: 'id inválido' });

    const data = await readKeysFile();
    if (!data[id]) return res.status(404).json({ error: 'id não encontrado' });

    if (data[id].used) return res.status(400).json({ error: 'já usada' });

    data[id].used = true;
    data[id].usedAt = new Date().toISOString();

    await writeKeysFile(data);
    return res.json({ ok: true, id, entry: data[id] });
  } catch (e) {
    console.error('Erro /use-key:', e);
    return res.status(500).json({ error: 'erro interno' });
  }
});

// Opcional: pegar keys.json (leitura pública, proteja se for necessário)
app.get('/keys.json', async (req, res) => {
  try {
    const raw = await fs.readFile(KEYS_FILE, 'utf8');
    res.type('application/json').send(raw);
  } catch (e) {
    if (e.code === 'ENOENT') return res.status(404).send('{}');
    console.error('Erro GET /keys.json', e);
    res.status(500).send('{}');
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`API rodando na porta ${PORT}`));
