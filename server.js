// server.js
require('dotenv').config();
const express = require('express');
const { Octokit } = require('@octokit/rest');

const app = express();
app.use(express.json({ limit: '1mb' }));

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO_OWNER = process.env.REPO_OWNER; // ex: 'aaaaa1221aa'
const REPO_NAME = process.env.REPO_NAME;   // ex: 'CN14X-HUD'
const KEYS_PATH = process.env.KEYS_PATH || 'keys.json'; // caminho no repo

if (!GITHUB_TOKEN || !REPO_OWNER || !REPO_NAME) {
  console.error('Defina GITHUB_TOKEN, REPO_OWNER e REPO_NAME nas env vars');
  process.exit(1);
}

const octokit = new Octokit({ auth: GITHUB_TOKEN });

// Helper: pega conteúdo atual do arquivo no repo (retorna {content, sha})
async function getFileContent(path) {
  try {
    const resp = await octokit.repos.getContent({
      owner: REPO_OWNER,
      repo: REPO_NAME,
      path,
    });
    // resp.data.content é base64
    const base64 = resp.data.content;
    const sha = resp.data.sha;
    const buff = Buffer.from(base64, 'base64');
    const text = buff.toString('utf8');
    return { text, sha };
  } catch (err) {
    // 404 = arquivo não existe
    if (err.status === 404) return { text: null, sha: null };
    throw err;
  }
}

// Rota para receber e gravar key
app.post('/api/push-key', async (req, res) => {
  try {
    const payload = req.body;
    // validar payload mínimo
    if (!payload || typeof payload.id !== 'string' || typeof payload.key !== 'string') {
      return res.status(400).json({ error: 'payload inválido. deve conter id e key.' });
    }

    const id = payload.id;
    // dados opcionais:
    const entry = {
      key: payload.key,
      generated: payload.generated || new Date().toISOString(),
      expiry: typeof payload.expiry === 'number' ? payload.expiry : (payload.expiry ? Number(payload.expiry) : null),
      used: false,
      usedAt: null
    };

    // pega conteúdo atual
    const { text, sha } = await getFileContent(KEYS_PATH);

    let jsonObj;
    if (!text) {
      // arquivo não existe -> cria novo objeto
      jsonObj = {};
    } else {
      try {
        jsonObj = JSON.parse(text);
        if (typeof jsonObj !== 'object' || jsonObj === null) throw new Error('Formato inválido');
      } catch (err) {
        // Se estiver corrompido ou vazio -> log e tentar recuperar como objeto vazio
        console.warn('keys.json existente está inválido — vamos reescrever. Erro:', err.message);
        jsonObj = {};
      }
    }

    // adiciona/atualiza entry
    jsonObj[id] = entry;

    const newText = JSON.stringify(jsonObj, null, 2) + '\n';
    const newBase64 = Buffer.from(newText, 'utf8').toString('base64');

    // Faz PUT para criar/atualizar arquivo no repo
    const commitMessage = `Add/Update key ${id} via API`;
    const params = {
      owner: REPO_OWNER,
      repo: REPO_NAME,
      path: KEYS_PATH,
      message: commitMessage,
      content: newBase64,
      committer: {
        name: 'CN14X-HUD API',
        email: 'noreply@example.com'
      }
    };
    if (sha) params.sha = sha; // necessário para atualização

    const updateResp = await octokit.repos.createOrUpdateFileContents(params);

    return res.json({
      ok: true,
      commit: updateResp.data.commit.sha,
      id,
      entry
    });

  } catch (err) {
    console.error('Erro em /api/push-key:', err);
    return res.status(500).json({ error: 'erro interno', details: err.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`API rodando na porta ${PORT}`));
