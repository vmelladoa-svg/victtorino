import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from orchestrator import Orchestrator

app = FastAPI()
orchestrator = Orchestrator()

AGENT_STYLES = {
    "ventas":           {"emoji": "📈", "name": "Ventas",           "color": "#22c55e"},
    "inventario":       {"emoji": "📦", "name": "Inventario",       "color": "#eab308"},
    "marketing":        {"emoji": "📣", "name": "Marketing",        "color": "#a855f7"},
    "finanzas":         {"emoji": "💰", "name": "Finanzas",         "color": "#06b6d4"},
    "operaciones":      {"emoji": "⚙️",  "name": "Operaciones",     "color": "#3b82f6"},
    "atencion_cliente": {"emoji": "🎧", "name": "Atención Cliente", "color": "#ef4444"},
    "estrategico":      {"emoji": "🧭", "name": "Estratégico",      "color": "#f8fafc"},
}

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Victoria — Victtorino</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #0f172a;
    color: #e2e8f0;
    height: 100dvh;
    display: flex;
    flex-direction: column;
  }
  header {
    padding: 12px 16px;
    background: #1e293b;
    border-bottom: 1px solid #334155;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
  }
  header h1 { font-size: 1rem; font-weight: 600; }
  header span { font-size: 0.75rem; color: #64748b; }
  button#resetBtn {
    background: none;
    border: 1px solid #334155;
    color: #94a3b8;
    padding: 4px 10px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.75rem;
  }
  button#resetBtn:hover { border-color: #64748b; color: #e2e8f0; }
  #chat {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .msg { max-width: 85%; }
  .msg.user { align-self: flex-end; }
  .msg.agent { align-self: flex-start; }
  .bubble {
    padding: 10px 14px;
    border-radius: 12px;
    line-height: 1.5;
    font-size: 0.9rem;
    word-wrap: break-word;
  }
  .msg.user .bubble {
    background: #1d4ed8;
    color: #fff;
    border-bottom-right-radius: 3px;
  }
  .msg.agent .bubble {
    background: #1e293b;
    border: 1px solid #334155;
    border-bottom-left-radius: 3px;
  }
  .msg.agent .bubble p { margin-bottom: 8px; }
  .msg.agent .bubble p:last-child { margin-bottom: 0; }
  .msg.agent .bubble ul, .msg.agent .bubble ol { padding-left: 18px; margin-bottom: 8px; }
  .msg.agent .bubble li { margin-bottom: 3px; }
  .msg.agent .bubble strong { color: #f1f5f9; }
  .msg.agent .bubble code {
    background: #0f172a;
    padding: 2px 5px;
    border-radius: 4px;
    font-size: 0.85em;
  }
  .agent-label {
    font-size: 0.72rem;
    margin-bottom: 4px;
    font-weight: 600;
    opacity: 0.9;
  }
  .typing {
    display: flex;
    gap: 4px;
    align-items: center;
    padding: 10px 14px;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    border-bottom-left-radius: 3px;
    width: fit-content;
  }
  .typing span {
    width: 6px; height: 6px;
    background: #64748b;
    border-radius: 50%;
    animation: bounce 1.2s infinite;
  }
  .typing span:nth-child(2) { animation-delay: 0.2s; }
  .typing span:nth-child(3) { animation-delay: 0.4s; }
  @keyframes bounce {
    0%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-5px); }
  }
  #inputArea {
    padding: 12px 16px;
    background: #1e293b;
    border-top: 1px solid #334155;
    display: flex;
    gap: 8px;
    flex-shrink: 0;
  }
  #msg {
    flex: 1;
    background: #0f172a;
    border: 1px solid #334155;
    color: #e2e8f0;
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 0.9rem;
    outline: none;
    resize: none;
    height: 42px;
    max-height: 120px;
    overflow-y: auto;
    font-family: inherit;
  }
  #msg:focus { border-color: #1d4ed8; }
  #sendBtn {
    background: #1d4ed8;
    border: none;
    color: #fff;
    width: 42px;
    height: 42px;
    border-radius: 10px;
    cursor: pointer;
    font-size: 1.1rem;
    flex-shrink: 0;
  }
  #sendBtn:hover { background: #1e40af; }
  #sendBtn:disabled { background: #334155; cursor: not-allowed; }
</style>
</head>
<body>
<header>
  <div>
    <h1>🏢 Victoria — Victtorino</h1>
    <span>Sistema multi-agente · 7 especialistas</span>
  </div>
  <button id="resetBtn" onclick="resetChat()">↺ Reset</button>
</header>
<div id="chat"></div>
<div id="inputArea">
  <textarea id="msg" placeholder="Escribe tu consulta..." rows="1"></textarea>
  <button id="sendBtn" onclick="sendMsg()">➤</button>
</div>

<script>
const chat = document.getElementById('chat');
const msgEl = document.getElementById('msg');
const sendBtn = document.getElementById('sendBtn');

const COLORS = {
  ventas: "#22c55e", inventario: "#eab308", marketing: "#a855f7",
  finanzas: "#06b6d4", operaciones: "#3b82f6", atencion_cliente: "#ef4444",
  estrategico: "#f8fafc"
};
const AGENTS = {
  ventas: "📈 Ventas", inventario: "📦 Inventario", marketing: "📣 Marketing",
  finanzas: "💰 Finanzas", operaciones: "⚙️ Operaciones",
  atencion_cliente: "🎧 Atención Cliente", estrategico: "🧭 Estratégico"
};

msgEl.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMsg(); }
});
msgEl.addEventListener('input', () => {
  msgEl.style.height = '42px';
  msgEl.style.height = Math.min(msgEl.scrollHeight, 120) + 'px';
});

function addMsg(role, text, agentKey) {
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  if (role === 'agent' && agentKey) {
    const label = document.createElement('div');
    label.className = 'agent-label';
    label.style.color = COLORS[agentKey] || '#94a3b8';
    label.textContent = AGENTS[agentKey] || agentKey;
    div.appendChild(label);
  }
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = role === 'agent' ? marked.parse(text) : escapeHtml(text);
  div.appendChild(bubble);
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}

function escapeHtml(t) {
  return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function showTyping() {
  const div = document.createElement('div');
  div.className = 'msg agent';
  div.id = 'typing';
  div.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function removeTyping() {
  const el = document.getElementById('typing');
  if (el) el.remove();
}

async function sendMsg() {
  const text = msgEl.value.trim();
  if (!text) return;
  msgEl.value = '';
  msgEl.style.height = '42px';
  sendBtn.disabled = true;

  addMsg('user', text);
  showTyping();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text})
    });
    const data = await res.json();
    removeTyping();
    addMsg('agent', data.response, data.agent);
  } catch (err) {
    removeTyping();
    addMsg('agent', '❌ Error al conectar con el servidor.', null);
  }

  sendBtn.disabled = false;
  msgEl.focus();
}

async function resetChat() {
  await fetch('/reset', {method: 'POST'});
  chat.innerHTML = '';
  addMsg('agent', 'Historial borrado. ¿En qué te puedo ayudar?', 'estrategico');
}

// Mensaje de bienvenida
addMsg('agent', '¡Hola! Soy **Victoria**, el sistema de inteligencia de **Victtorino**. Tengo 7 agentes especialistas listos: ventas, inventario, marketing, finanzas, operaciones, atención al cliente y estrategia. ¿Qué necesitas?', 'estrategico');
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat(req: ChatRequest):
    agent_key, response = orchestrator.chat(req.message)
    style = AGENT_STYLES.get(agent_key, {"emoji": "🤖", "name": agent_key, "color": "#94a3b8"})
    return {"agent": agent_key, "response": response, "style": style}


@app.post("/reset")
async def reset():
    orchestrator.reset_history()
    return {"ok": True}
