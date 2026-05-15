"""
Neuroxa - A dual-model AI assistant
Brand: Neuroxa
Models (both via Groq):
    Piko (Llama 3.3 70B) - General conversation
    Mano (GPT-OSS 120B) - Coding & technical
"""

import json
import os
import uuid
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI


# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="Neuroxa",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============ STORAGE ============
HISTORY_FILE = "chat_history.json"


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ============ AVATARS ============
PIKO_AVATAR = """data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 240 240'><defs><radialGradient id='b' cx='38%25' cy='35%25' r='75%25'><stop offset='0%25' stop-color='%23FFB59B'/><stop offset='60%25' stop-color='%23FF8B6F'/><stop offset='100%25' stop-color='%23E86F50'/></radialGradient></defs><path d='M 120 50 C 165 50 200 78 202 118 C 204 158 188 195 158 208 C 132 219 100 219 78 206 C 48 190 38 150 44 112 C 50 75 80 50 120 50 Z' fill='url(%23b)'/><ellipse cx='98' cy='128' rx='6.5' ry='9' fill='%232A1208'/><ellipse cx='142' cy='128' rx='6.5' ry='9' fill='%232A1208'/><path d='M 108 162 Q 120 172 132 162' stroke='%232A1208' stroke-width='3.5' fill='none' stroke-linecap='round'/></svg>"""

MANO_AVATAR = """data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 240 240'><defs><linearGradient id='b' x1='20%25' y1='0%25' x2='80%25' y2='100%25'><stop offset='0%25' stop-color='%23EBFF6B'/><stop offset='55%25' stop-color='%23DAFF3D'/><stop offset='100%25' stop-color='%23A8C920'/></linearGradient></defs><path d='M 120 46 L 184 82 L 184 162 L 120 198 L 56 162 L 56 82 Z' fill='url(%23b)' stroke='%231F2A00' stroke-width='2.5'/><polyline points='100,108 88,122 100,136' stroke='%231F2A00' stroke-width='5' fill='none' stroke-linecap='round' stroke-linejoin='round'/><polyline points='140,108 152,122 140,136' stroke='%231F2A00' stroke-width='5' fill='none' stroke-linecap='round' stroke-linejoin='round'/><line x1='108' y1='160' x2='132' y2='160' stroke='%231F2A00' stroke-width='4.5' stroke-linecap='round'/></svg>"""


# ============ STYLING ============
st.markdown(
    """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Fraunces:opsz,wght@9..144,400;9..144,500&display=swap" rel="stylesheet">

<style>
    :root {
        /* Slate-tinted dark, warmer than pure black */
        --bg: #0F1014;
        --bg-2: #14161C;
        --surface: #181A21;
        --surface-2: #1F222B;
        --surface-3: #272A35;
        --border: #2A2D38;
        --border-strong: #3A3E4B;
        --text: #F2F3F5;
        --text-dim: #9CA0AC;
        --text-mute: #5C6070;
        --piko: #FF9B7A;
        --piko-soft: rgba(255, 155, 122, 0.08);
        --mano: #D4F542;
        --mano-soft: rgba(212, 245, 66, 0.08);
        --accent: #8B7CF6;
    }

    html, body, .stApp, [data-testid="stAppViewContainer"],
    [data-testid="stMain"], .main {
        background: var(--bg) !important;
        color: var(--text) !important;
    }

    .stApp, .stApp p, .stApp span, .stApp div, .stApp label {
        font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
        color: var(--text);
    }

    /* ===== Hide ONLY what we don't need — leave sidebar controls alone ===== */
    #MainMenu,
    footer,
    header[data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stDeployButton"],
    .stDeployButton,
    .stAppDeployButton {
        display: none !important;
    }

    /* Main container */
    .main .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 8rem !important;
        max-width: 860px !important;
    }

    /* ===== Sidebar — minimal styling, let Streamlit control visibility ===== */
    section[data-testid="stSidebar"] {
        background: var(--bg-2) !important;
        border-right: 1px solid var(--border) !important;
    }

    /* Native sidebar toggle / close button — make visible and styled */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"],
    button[kind="headerNoPadding"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text) !important;
        opacity: 1 !important;
        visibility: visible !important;
    }

    [data-testid="stSidebarCollapseButton"]:hover,
    [data-testid="collapsedControl"]:hover {
        background: var(--surface-2) !important;
        border-color: var(--border-strong) !important;
    }

    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="collapsedControl"] svg {
        color: var(--text) !important;
        fill: var(--text) !important;
    }

    /* Sidebar brand */
    .brand {
        font-family: 'Fraunces', serif;
        font-size: 26px;
        line-height: 1;
        color: var(--text);
        letter-spacing: -0.02em;
        font-weight: 500;
        padding: 0.5rem 0.25rem 0;
        margin-bottom: 1.5rem;
        display: inline-block;
    }

    .brand .x {
        color: var(--mano);
        font-weight: 500;
        font-style: normal;
        display: inline-block;
        padding: 0 1px;
    }

    .section-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        color: var(--text-mute);
        margin: 1.5rem 0.25rem 0.5rem;
        font-weight: 500;
    }

    /* All sidebar buttons */
    section[data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        color: var(--text-dim) !important;
        border: 1px solid transparent !important;
        border-radius: 8px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 13px !important;
        font-weight: 400 !important;
        padding: 8px 12px !important;
        text-align: left !important;
        white-space: normal !important;
        line-height: 1.4 !important;
        transition: all 0.15s ease !important;
        min-height: 36px !important;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: var(--surface) !important;
        color: var(--text) !important;
        border-color: var(--border) !important;
    }

    section[data-testid="stSidebar"] .stButton > button:focus {
        box-shadow: none !important;
        outline: none !important;
    }

    /* Primary button — New chat */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--piko) 0%, var(--mano) 100%) !important;
        color: #0F1014 !important;
        border: 1px solid transparent !important;
        font-weight: 600 !important;
        text-align: center !important;
    }

    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        opacity: 0.92 !important;
        filter: brightness(1.05) !important;
    }

    section[data-testid="stSidebar"] .stButton > button[kind="primary"] p,
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] div {
        color: #0F1014 !important;
    }

    section[data-testid="stSidebar"] hr {
        border-color: var(--border) !important;
        margin: 1rem 0 !important;
    }

    /* ===== Top bar inside main area ===== */
    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 0 1.25rem 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 2rem;
    }

    .topbar-brand {
        font-family: 'Fraunces', serif;
        font-size: 22px;
        font-weight: 500;
        color: var(--text);
        letter-spacing: -0.01em;
        line-height: 1;
    }

    .topbar-brand .x {
        color: var(--mano);
        font-style: normal;
        display: inline-block;
        padding: 0 1px;
    }

    .topbar-status {
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: var(--text-mute);
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    .topbar-status .dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #4ADE80;
        box-shadow: 0 0 8px rgba(74, 222, 128, 0.5);
    }

    /* ===== Empty state — model cards ===== */
    .welcome {
        padding: 2rem 0 0;
    }

    .welcome-title {
        font-family: 'Fraunces', serif;
        font-size: 2.5rem;
        font-weight: 400;
        color: var(--text);
        letter-spacing: -0.025em;
        line-height: 1.1;
        margin-bottom: 0.4rem;
    }

    .welcome-subtitle {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.95rem;
        color: var(--text-dim);
        margin-bottom: 2rem;
    }

    .model-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 14px;
        margin-bottom: 1.75rem;
    }

    .model-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 18px 20px;
        transition: all 0.2s ease;
    }

    .model-card.piko {
        border-color: rgba(255, 155, 122, 0.15);
        background: linear-gradient(180deg, var(--piko-soft) 0%, var(--surface) 100%);
    }

    .model-card.mano {
        border-color: rgba(212, 245, 66, 0.15);
        background: linear-gradient(180deg, var(--mano-soft) 0%, var(--surface) 100%);
    }

    .model-card-head {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
    }

    .model-card-avatar {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        overflow: hidden;
        flex-shrink: 0;
    }

    .model-card-avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }

    .model-card-name {
        font-weight: 600;
        font-size: 15px;
        color: var(--text);
    }

    .model-card-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 2px 7px;
        border-radius: 4px;
        margin-left: auto;
    }

    .model-card.piko .model-card-tag {
        color: var(--piko);
        background: rgba(255, 155, 122, 0.1);
    }

    .model-card.mano .model-card-tag {
        color: var(--mano);
        background: rgba(212, 245, 66, 0.1);
    }

    .model-card-desc {
        font-size: 13px;
        color: var(--text-dim);
        line-height: 1.5;
        margin: 0;
    }

    .router-hint {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 14px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        font-size: 13px;
        color: var(--text-dim);
    }

    .router-hint-icon {
        width: 16px;
        height: 16px;
        flex-shrink: 0;
        color: var(--accent);
    }

    /* ===== Chat: user bubble ===== */
    .user-row {
        display: flex;
        justify-content: flex-end;
        margin: 1.25rem 0;
    }

    .user-bubble {
        max-width: 78%;
        padding: 11px 16px;
        background: var(--surface-2);
        border: 1px solid var(--border);
        border-radius: 16px;
        border-top-right-radius: 4px;
        font-size: 15px;
        line-height: 1.55;
        color: var(--text);
        word-wrap: break-word;
        white-space: pre-wrap;
    }

    /* ===== Chat: assistant ===== */
    .assistant-avatar {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        overflow: hidden;
        margin-top: 4px;
        flex-shrink: 0;
        border: 1px solid var(--border);
    }

    .assistant-avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }

    .assistant-content {
        font-size: 15px;
        line-height: 1.65;
        color: var(--text);
    }

    .assistant-content p {
        margin: 0 0 0.7rem 0 !important;
    }
    .assistant-content p:last-child { margin-bottom: 0 !important; }

    .assistant-content code {
        background: var(--surface-2) !important;
        color: var(--mano) !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        border: 1px solid var(--border) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.88em !important;
    }

    .assistant-content pre {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 14px 16px !important;
        margin: 0.75rem 0 !important;
        overflow-x: auto !important;
    }

    .assistant-content pre code {
        background: transparent !important;
        color: var(--text) !important;
        border: none !important;
        padding: 0 !important;
        font-size: 13px !important;
        line-height: 1.6 !important;
    }

    .assistant-content strong { color: var(--text); font-weight: 600; }
    .assistant-content a { color: var(--piko); text-decoration: none; border-bottom: 1px solid transparent; }
    .assistant-content a:hover { border-bottom-color: var(--piko); }

    /* ===== Typing dots loading ===== */
    .typing-dots {
        display: inline-flex;
        gap: 4px;
        padding: 8px 0;
    }

    .typing-dots span {
        width: 7px;
        height: 7px;
        background: var(--text-dim);
        border-radius: 50%;
        animation: typing-bounce 1.4s infinite ease-in-out both;
    }

    .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s; }

    @keyframes typing-bounce {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
        40% { transform: scale(1); opacity: 1; }
    }

    /* ===== Chat input ===== */
    [data-testid="stChatInput"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        transition: border-color 0.15s !important;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: var(--border-strong) !important;
    }

    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: var(--text) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 15px !important;
        line-height: 1.5 !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: var(--text-mute) !important;
    }

    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottom"] {
        background: var(--bg) !important;
    }

    [data-testid="stChatInput"] button {
        background: var(--text) !important;
        color: var(--bg) !important;
        border-radius: 8px !important;
    }

    [data-testid="stChatInput"] button:hover {
        background: var(--mano) !important;
    }

    [data-testid="stChatInput"] button svg {
        color: var(--bg) !important;
        fill: var(--bg) !important;
    }

    /* Hide default chat message containers */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        padding: 0 !important;
        gap: 0 !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--border-strong); }

    /* Hide the components.html iframe used for JS injection */
    iframe[title="streamlit_components.v1.html.html"],
    iframe[height="0"] {
        display: none !important;
    }

    /* ===== Sidebar EXPAND button (visible when sidebar is collapsed) ===== */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    button[kind="header"],
    button[kind="headerNoPadding"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text) !important;
        padding: 8px 12px !important;
        top: 0.75rem !important;
        left: 0.75rem !important;
        z-index: 999 !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }

    [data-testid="collapsedControl"]:hover,
    [data-testid="stSidebarCollapsedControl"]:hover,
    [data-testid="stSidebarCollapseButton"]:hover,
    button[kind="header"]:hover,
    button[kind="headerNoPadding"]:hover {
        background: var(--surface-2) !important;
        border-color: var(--border-strong) !important;
    }

    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="stSidebarCollapseButton"] svg,
    button[kind="header"] svg,
    button[kind="headerNoPadding"] svg {
        color: var(--text) !important;
        fill: var(--text) !important;
        width: 18px !important;
        height: 18px !important;
    }

    /* ===== Custom MENU TOGGLE button (main page, when sidebar collapsed) ===== */
    div[data-testid="stVerticalBlock"] > div:first-child .stButton {
        margin-bottom: 0.75rem !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ============ MODELS ============
MODELS = {
    "Piko": {
        "model_id": "llama-3.3-70b-versatile",
        "avatar": PIKO_AVATAR,
        "system_prompt": (
            "You are Piko, one of two models that power Neuroxa. "
            "Your role is general conversation: friendly, warm, concise. "
            "Match the user's language exactly. If they write in English, reply in English. "
            "If they write in Hindi or Hinglish, reply in the same style. "
            "Do not use emojis. "
            "If you must show code, always wrap it in markdown fenced blocks with a language tag. "
            "Your training data has a knowledge cutoff. For current events, recent news, "
            "or facts that change over time, tell the user to verify rather than guess."
        ),
    },
    "Mano": {
        "model_id": "openai/gpt-oss-120b",
        "avatar": MANO_AVATAR,
        "system_prompt": (
            "You are Mano, one of two models that power Neuroxa. "
            "You are a senior software engineer focused on clean, production-ready code. "
            "Do not use emojis. "
            "MANDATORY: always wrap code in markdown fenced blocks with the correct language tag. "
            "Structure: brief intro, code block, short explanation. "
            "Use `inline code` for variable and function names. "
            "Match the user's natural language in prose; keep code itself in English. "
            "Your training data has a knowledge cutoff. For framework versions or library APIs "
            "that may have changed recently, tell the user to verify against current docs."
        ),
    },
}

CODE_KEYWORDS = [
    "code", "function", "bug", "error", "exception", "debug", "script", "compile",
    "python", "javascript", "typescript", "java", "c++", "cpp", "html", "css",
    "react", "vue", "angular", "node", "api", "endpoint", "rest", "graphql",
    "sql", "database", "query", "algorithm", "syntax", "variable", "loop",
    "array", "list", "dict", "class", "method", "framework", "library", "package",
    "git", "github", "deploy", "server", "regex", "json", "xml", "yaml",
    "frontend", "backend", "fullstack", "devops", "docker", "kubernetes", "aws",
    "import", "module", "npm", "pip", "install", "terminal", "command", "shell",
    "runtime", "async", "await", "promise", "recursion", "fibonacci", "sort",
    "binary tree", "linked list", "rust", "go", "kotlin", "swift", "ruby", "php",
]


def route_message(msg: str) -> str:
    msg_lower = msg.lower()
    if any(kw in msg_lower for kw in CODE_KEYWORDS):
        return "Mano"
    if "```" in msg or msg.count("`") >= 2:
        return "Mano"
    code_phrases = [
        "write a function", "write a program", "create a function",
        "make a program", "fix this code", "debug this",
        "likh ke de", "likh do", "code de", "function bana",
    ]
    if any(p in msg_lower for p in code_phrases):
        return "Mano"
    return "Piko"


# ============ KEY LOADING ============
def is_placeholder(key: str) -> bool:
    if not key:
        return True
    return any(m in key.lower() for m in ["paste_your", "_here"])


def load_key():
    try:
        import config
        groq = getattr(config, "GROQ_API_KEY", "")
        if groq and not is_placeholder(groq):
            return groq
    except ImportError:
        pass
    try:
        groq = st.secrets.get("GROQ_API_KEY", "")
        if groq:
            return groq
    except Exception:
        pass
    return ""


# ============ API ============
def get_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")


def stream_response(model_name: str, history: list, api_key: str):
    cfg = MODELS[model_name]
    client = get_client(api_key)
    messages = [{"role": "system", "content": cfg["system_prompt"]}] + history
    stream = client.chat.completions.create(
        model=cfg["model_id"],
        messages=messages,
        stream=True,
        temperature=0.7,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


# ============ HELPERS ============
def make_chat_title(first_message: str) -> str:
    title = first_message.strip().replace("\n", " ")
    if len(title) > 32:
        title = title[:32] + "..."
    return title or "New chat"


def new_chat():
    chat_id = str(uuid.uuid4())[:8]
    return chat_id, {
        "id": chat_id,
        "title": "New chat",
        "messages": [],
        "created_at": datetime.now().isoformat(),
    }


# ============ STATE ============
if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_history()

if "current_chat_id" not in st.session_state:
    if st.session_state.all_chats:
        sorted_chats = sorted(
            st.session_state.all_chats.values(),
            key=lambda c: c.get("created_at", ""),
            reverse=True,
        )
        st.session_state.current_chat_id = sorted_chats[0]["id"]
    else:
        cid, chat = new_chat()
        st.session_state.all_chats[cid] = chat
        st.session_state.current_chat_id = cid

groq_key = load_key()


# ============ SIDEBAR ============
with st.sidebar:
    st.markdown(
        '<div class="brand">Neuro<span class="x">x</span>a</div>',
        unsafe_allow_html=True,
    )

    if st.button("+ New chat", use_container_width=True, type="primary"):
        cid, chat = new_chat()
        st.session_state.all_chats[cid] = chat
        st.session_state.current_chat_id = cid
        save_history(st.session_state.all_chats)
        st.rerun()

    st.markdown('<div class="section-label">Recent</div>', unsafe_allow_html=True)

    sorted_chats = sorted(
        st.session_state.all_chats.values(),
        key=lambda c: c.get("created_at", ""),
        reverse=True,
    )

    visible_chats = [
        c for c in sorted_chats
        if c.get("messages") or c["id"] == st.session_state.current_chat_id
    ]

    for chat in visible_chats:
        is_current = chat["id"] == st.session_state.current_chat_id
        title = chat.get("title", "New chat")
        prefix = "› " if is_current else "  "
        if st.button(
            prefix + title,
            key=f"chat_{chat['id']}",
            use_container_width=True,
        ):
            st.session_state.current_chat_id = chat["id"]
            st.rerun()

    st.markdown("---")

    if st.button("Delete this chat", use_container_width=True):
        cid = st.session_state.current_chat_id
        if cid in st.session_state.all_chats:
            del st.session_state.all_chats[cid]
            save_history(st.session_state.all_chats)
            if st.session_state.all_chats:
                remaining = sorted(
                    st.session_state.all_chats.values(),
                    key=lambda c: c.get("created_at", ""),
                    reverse=True,
                )
                st.session_state.current_chat_id = remaining[0]["id"]
            else:
                cid2, chat = new_chat()
                st.session_state.all_chats[cid2] = chat
                st.session_state.current_chat_id = cid2
                save_history(st.session_state.all_chats)
            st.rerun()


# ============ CUSTOM SIDEBAR TOGGLE (injected via parent-page JS) ============
# Bypass Streamlit's hidden toggle entirely. We directly manipulate the
# sidebar element's CSS via setProperty(name, value, 'important').
components.html(
    """
    <script>
    (function() {
        const parentDoc = window.parent.document;

        function setupToggle() {
            if (parentDoc.getElementById('neuroxa-sidebar-toggle')) return;

            const btn = parentDoc.createElement('button');
            btn.id = 'neuroxa-sidebar-toggle';
            btn.innerHTML = '☰';
            btn.title = 'Toggle sidebar';
            btn.setAttribute('aria-label', 'Toggle sidebar');
            btn.style.cssText = `
                position: fixed;
                top: 14px;
                left: 14px;
                z-index: 999999;
                background: #1F222B;
                color: #F2F3F5;
                border: 1px solid #2A2D38;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 18px;
                cursor: pointer;
                font-family: system-ui, sans-serif;
                line-height: 1;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                transition: all 0.15s ease;
                min-width: 40px;
            `;

            btn.onmouseover = () => {
                btn.style.background = '#272A35';
                btn.style.borderColor = '#3A3E4B';
            };
            btn.onmouseout = () => {
                btn.style.background = '#1F222B';
                btn.style.borderColor = '#2A2D38';
            };

            btn.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();

                const sidebar = parentDoc.querySelector('section[data-testid="stSidebar"]');
                if (!sidebar) {
                    console.log('[Neuroxa] Sidebar element not found in DOM');
                    return;
                }

                // Determine current state by measuring actual width
                const rect = sidebar.getBoundingClientRect();
                const isCurrentlyHidden = rect.width < 50 || rect.left < -50;

                if (isCurrentlyHidden) {
                    // SHOW sidebar — force via inline !important
                    sidebar.style.setProperty('transform', 'none', 'important');
                    sidebar.style.setProperty('width', '280px', 'important');
                    sidebar.style.setProperty('min-width', '280px', 'important');
                    sidebar.style.setProperty('max-width', '280px', 'important');
                    sidebar.style.setProperty('margin-left', '0', 'important');
                    sidebar.style.setProperty('display', 'flex', 'important');
                    sidebar.style.setProperty('visibility', 'visible', 'important');
                    sidebar.style.setProperty('opacity', '1', 'important');
                    sidebar.style.setProperty('left', '0', 'important');
                    sidebar.style.setProperty('position', 'relative', 'important');
                    btn.innerHTML = '✕';
                } else {
                    // HIDE sidebar
                    sidebar.style.setProperty('transform', 'translateX(-100%)', 'important');
                    sidebar.style.setProperty('width', '0', 'important');
                    sidebar.style.setProperty('min-width', '0', 'important');
                    sidebar.style.setProperty('max-width', '0', 'important');
                    sidebar.style.setProperty('margin-left', '-280px', 'important');
                    sidebar.style.setProperty('opacity', '0', 'important');
                    btn.innerHTML = '☰';
                }
            };

            parentDoc.body.appendChild(btn);
        }

        // Initial setup
        setupToggle();

        // Re-inject button if Streamlit removes it during reruns
        const observer = new MutationObserver(() => {
            if (!parentDoc.getElementById('neuroxa-sidebar-toggle')) {
                setupToggle();
            }
        });
        observer.observe(parentDoc.body, { childList: true, subtree: false });
    })();
    </script>
    """,
    height=0,
)


# ============ TOP BAR ============
st.markdown(
    '<div class="topbar">'
    '<div class="topbar-brand">Neuro<span class="x">x</span>a</div>'
    '<div class="topbar-status"><span class="dot"></span><span>Online</span></div>'
    '</div>',
    unsafe_allow_html=True,
)

current_chat = st.session_state.all_chats[st.session_state.current_chat_id]
messages = current_chat["messages"]


# ============ RENDER HELPERS ============
def render_user_message(content: str):
    safe = content.replace("<", "&lt;").replace(">", "&gt;")
    st.markdown(
        f'<div class="user-row"><div class="user-bubble">{safe}</div></div>',
        unsafe_allow_html=True,
    )


def render_assistant_message(content: str, model: str):
    cfg = MODELS[model]
    col_av, col_content = st.columns([1, 20], gap="small")
    with col_av:
        st.markdown(
            f'<div class="assistant-avatar"><img src="{cfg["avatar"]}" alt=""></div>',
            unsafe_allow_html=True,
        )
    with col_content:
        st.markdown('<div class="assistant-content">', unsafe_allow_html=True)
        st.markdown(content)
        st.markdown('</div>', unsafe_allow_html=True)


# ============ EMPTY STATE — model cards ============
if not messages:
    welcome_html = (
        '<div class="welcome">'
        '<div class="welcome-title">Welcome to Neuroxa</div>'
        '<div class="welcome-subtitle">Two specialised minds. One smart router. Start typing below.</div>'
        '<div class="model-grid">'
        '<div class="model-card piko">'
        '<div class="model-card-head">'
        f'<div class="model-card-avatar"><img src="{PIKO_AVATAR}" alt=""></div>'
        '<div class="model-card-name">Piko</div>'
        '<div class="model-card-tag">Chat</div>'
        '</div>'
        '<p class="model-card-desc">Friendly conversation, everyday questions, casual writing, ideas and brainstorming.</p>'
        '</div>'
        '<div class="model-card mano">'
        '<div class="model-card-head">'
        f'<div class="model-card-avatar"><img src="{MANO_AVATAR}" alt=""></div>'
        '<div class="model-card-name">Mano</div>'
        '<div class="model-card-tag">Code</div>'
        '</div>'
        '<p class="model-card-desc">Programming, debugging, technical design, API integrations, code reviews.</p>'
        '</div>'
        '</div>'
        '<div class="router-hint">'
        '<svg class="router-hint-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l3 7h7l-5.5 4.5L18 21l-6-4-6 4 1.5-7.5L2 9h7z"/></svg>'
        '<span>The router picks the right model automatically based on your message.</span>'
        '</div>'
        '</div>'
    )
    st.markdown(welcome_html, unsafe_allow_html=True)


# ============ RENDER EXISTING ============
for msg in messages:
    if msg["role"] == "user":
        render_user_message(msg["content"])
    else:
        render_assistant_message(msg["content"], msg.get("model", "Piko"))


# ============ INPUT ============
if prompt := st.chat_input("Message Neuroxa..."):
    if not groq_key:
        st.error("Groq API key missing. Add it to config.py and restart.")
        st.stop()

    messages.append({"role": "user", "content": prompt})

    if current_chat["title"] == "New chat":
        current_chat["title"] = make_chat_title(prompt)

    render_user_message(prompt)

    model_name = route_message(prompt)
    cfg = MODELS[model_name]

    col_av, col_content = st.columns([1, 20], gap="small")
    with col_av:
        st.markdown(
            f'<div class="assistant-avatar"><img src="{cfg["avatar"]}" alt=""></div>',
            unsafe_allow_html=True,
        )
    with col_content:
        st.markdown('<div class="assistant-content">', unsafe_allow_html=True)
        placeholder = st.empty()

        # Show typing dots while waiting for first token
        placeholder.markdown(
            '<div class="typing-dots"><span></span><span></span><span></span></div>',
            unsafe_allow_html=True,
        )

        try:
            history_for_api = [
                {"role": m["role"], "content": m["content"]} for m in messages
            ]
            full_response = ""
            first_token = True
            for token in stream_response(model_name, history_for_api, groq_key):
                if first_token:
                    placeholder.empty()
                    first_token = False
                full_response += token
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)

            messages.append({
                "role": "assistant",
                "content": full_response,
                "model": model_name,
            })
            save_history(st.session_state.all_chats)

        except Exception as e:
            placeholder.error(f"Error: {str(e)}")
            messages.append({
                "role": "assistant",
                "content": f"Error: {str(e)}",
                "model": model_name,
            })
            save_history(st.session_state.all_chats)
        st.markdown('</div>', unsafe_allow_html=True)