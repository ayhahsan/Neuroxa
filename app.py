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
from openai import OpenAI

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="Neuroxa",
    page_icon="https://api.iconify.design/lucide:sparkles.svg",
    layout="wide",
    initial_sidebar_state="expanded"
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
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist+Mono:wght@300;400;500;600&family=Geist:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<style>
    :root {
        --bg: #0E0D0B;
        --bg-soft: #16140F;
        --bg-elevated: #1C1A14;
        --bg-bubble: #1F1C16;
        --ink: #F4F0E6;
        --ink-dim: #A6A095;
        --ink-mute: #6B655A;
        --line: #2A2620;
        --piko: #FF8B6F;
        --mano: #DAFF3D;
    }

    .stApp {
        background: var(--bg) !important;
        color: var(--ink) !important;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header[data-testid="stHeader"],
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"], .stDeployButton, .stAppDeployButton,
    [data-testid="stSidebarHeader"] {
        display: none !important;
        visibility: hidden !important;
    }

    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 7rem !important;
        max-width: 880px !important;
    }

    .stApp, .stApp p, .stApp span, .stApp div, .stApp label {
        font-family: 'Geist', system-ui, sans-serif;
        color: var(--ink);
    }

    /* ========== SIDEBAR ========== */
    section[data-testid="stSidebar"] {
        background: var(--bg-soft) !important;
        border-right: 1px solid var(--line) !important;
        width: 280px !important;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem !important;
    }

    .sidebar-brand {
        font-family: 'Instrument Serif', serif;
        font-size: 28px;
        color: var(--ink);
        letter-spacing: -0.02em;
        margin-bottom: 1.5rem;
        padding: 0 0.5rem;
    }

    .sidebar-brand .x {
        background: linear-gradient(135deg, var(--piko) 0%, var(--mano) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .sidebar-label {
        font-family: 'Geist Mono', monospace;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        color: var(--ink-mute);
        margin: 1.5rem 0.5rem 0.75rem;
    }

    /* ALL buttons in sidebar - default style */
    section[data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
        border-radius: 8px !important;
        font-family: 'Geist', sans-serif !important;
        font-size: 13px !important;
        padding: 8px 14px !important;
        transition: all 0.15s !important;
        text-align: left !important;
        font-weight: 400 !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        white-space: normal !important;
        line-height: 1.4 !important;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: var(--bg-elevated) !important;
        border-color: var(--ink-dim) !important;
    }

    /* New chat button - PROMINENT, not blank */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: var(--ink) !important;
        color: var(--bg) !important;
        border: 1px solid var(--ink) !important;
        text-align: center !important;
        font-weight: 500 !important;
    }

    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: var(--piko) !important;
        border-color: var(--piko) !important;
        color: var(--bg) !important;
    }

    section[data-testid="stSidebar"] .stButton > button[kind="primary"] p,
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] div {
        color: var(--bg) !important;
    }

    /* ========== HEADER (compact) ========== */
    .neuroxa-header-wrap {
        text-align: center;
        padding: 0.5rem 0 1.5rem 0;
        border-bottom: 1px solid var(--line);
        margin-bottom: 1.5rem;
    }

    .neuroxa-header {
        font-family: 'Instrument Serif', serif !important;
        font-size: 3rem !important;
        font-weight: 400 !important;
        letter-spacing: -0.04em !important;
        color: var(--ink) !important;
        line-height: 1 !important;
        margin: 0 !important;
    }

    .neuroxa-header .x {
        background: linear-gradient(135deg, var(--piko) 0%, var(--mano) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .neuroxa-tagline {
        font-family: 'Instrument Serif', serif !important;
        font-style: italic !important;
        color: var(--ink-dim) !important;
        font-size: 0.95rem !important;
        margin-top: 0.25rem !important;
    }

    /* ========== CHAT LAYOUT - using Streamlit's native columns ========== */

    /* User row - bubble pushed right */
    .user-bubble {
        display: flex;
        justify-content: flex-end;
        margin: 1rem 0;
    }

    .user-bubble-inner {
        max-width: 75%;
        padding: 12px 16px;
        background: var(--bg-bubble);
        border: 1px solid var(--line);
        border-radius: 16px;
        border-top-right-radius: 4px;
        font-size: 15px;
        line-height: 1.6;
        color: var(--ink);
        word-wrap: break-word;
        white-space: pre-wrap;
    }

    /* Assistant row - avatar + content side by side */
    .assistant-row {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin: 1.25rem 0;
    }

    .assistant-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: var(--bg-elevated);
        border: 1px solid var(--line);
        flex-shrink: 0;
        overflow: hidden;
        margin-top: 2px;
    }

    .assistant-avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* Assistant content uses Streamlit's natural markdown flow */
    .assistant-content {
        flex: 1;
        font-size: 15px;
        line-height: 1.65;
        color: var(--ink);
        min-width: 0;
    }

    .assistant-content p {
        margin: 0 0 0.5rem 0 !important;
    }
    .assistant-content p:last-child {
        margin-bottom: 0 !important;
    }

    .assistant-content code:not(pre code) {
        background: var(--bg-elevated);
        color: var(--mano);
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid var(--line);
        font-family: 'Geist Mono', monospace;
        font-size: 0.88em;
    }

    .assistant-content pre {
        background: #0A0908 !important;
        border: 1px solid var(--line) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        margin: 0.75rem 0 !important;
        overflow-x: auto;
    }

    .assistant-content pre code {
        font-family: 'Geist Mono', monospace !important;
        font-size: 13px !important;
        line-height: 1.65 !important;
        color: var(--ink) !important;
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    .assistant-content strong { color: var(--ink); font-weight: 500; }

    /* ========== EMPTY STATE ========== */
    .empty-state {
        text-align: center;
        padding: 4rem 1rem 2rem;
    }

    .empty-state-title {
        font-family: 'Instrument Serif', serif;
        font-size: 36px;
        line-height: 1.1;
        color: var(--ink);
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    .empty-state-title em {
        font-style: italic;
        color: var(--ink-dim);
    }

    .empty-state-desc {
        color: var(--ink-dim) !important;
        font-size: 14px;
        max-width: 480px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* ========== CHAT INPUT ========== */
    [data-testid="stChatInput"] {
        background: var(--bg-soft) !important;
        border: 1px solid var(--line) !important;
        border-radius: 999px !important;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: var(--ink-dim) !important;
    }

    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: var(--ink) !important;
        font-family: 'Geist', sans-serif !important;
        font-size: 15px !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: var(--ink-mute) !important;
    }

    [data-testid="stBottom"] {
        background: linear-gradient(to top, var(--bg) 70%, transparent) !important;
    }

    [data-testid="stChatInput"] button {
        background: var(--ink) !important;
        color: var(--bg) !important;
    }

    [data-testid="stChatInput"] button:hover {
        background: var(--piko) !important;
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
    ::-webkit-scrollbar-thumb { background: var(--line); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--ink-mute); }

    hr {
        border-color: var(--line) !important;
        margin: 1rem 0 !important;
    }

    @media (max-width: 767px) {
        header[data-testid="stHeader"] {
            display: block !important;
            visibility: visible !important;
            background: transparent !important;
            height: auto !important;
        }
        [data-testid="stSidebarCollapsedControl"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# ============ MODEL CONFIGS ============
MODELS = {
    "Piko": {
        "model_id": "llama-3.3-70b-versatile",
        "avatar": PIKO_AVATAR,
        "system_prompt": (
            "You are Piko, one of the two models that power Neuroxa. "
            "You handle general conversation - friendly, warm, helpful. "
            "Match the user's language style: if they write in Hinglish (Hindi-English mix), "
            "reply in Hinglish. If English, reply in English. "
            "Keep responses conversational and concise. Do not use emojis. "
            "If you ever need to show ANY code, ALWAYS wrap it in markdown code blocks "
            "with the language tag like ```python ... ```. Never put code on the same line as prose. "
            "\n\nIMPORTANT - ABOUT YOUR KNOWLEDGE: Your training data has a cutoff date in late 2023. "
            "You do NOT know events, ages, or facts that have changed after that date. "
            "If asked about 'as of 2024', '2025', '2026' or current dates, do NOT do math to guess. "
            "Instead say: 'Mera knowledge late 2023 tak ka hai. Latest info ke liye verify kar lo.'"
        )
    },
    "Mano": {
        "model_id": "openai/gpt-oss-120b",
        "avatar": MANO_AVATAR,
        "system_prompt": (
            "You are Mano, one of the two models that power Neuroxa. "
            "You are a senior software engineer specializing in clean, production-ready code. "
            "Do not use emojis in code or explanations. "
            "MANDATORY: ALWAYS wrap code in markdown code blocks with the proper language tag "
            "like ```python ... ```. Use correct language tags (python, javascript, html, css, "
            "sql, bash, etc.). Structure: brief intro, code block, short explanation. "
            "Use `inline code` for variable names. Code ALWAYS in fenced block. "
            "If user writes Hinglish, mix Hinglish in explanations but keep code in English. "
            "\n\nIMPORTANT: Your training cutoff is mid-2024. For questions about current events "
            "or info that changes over time, tell user to verify rather than guess."
        )
    }
}

CODE_KEYWORDS = [
    "code", "function", "bug", "error", "exception", "debug", "script", "compile",
    "python", "javascript", "java", "c++", "cpp", "html", "css", "react", "node",
    "api", "sql", "database", "query", "algorithm", "syntax", "variable", "loop",
    "array", "list", "dict", "class", "method", "framework", "library", "package",
    "git", "github", "deploy", "server", "regex", "json", "xml", "build",
    "frontend", "backend", "fullstack", "devops", "docker", "kubernetes", "aws",
    "import", "module", "npm", "pip", "install", "terminal", "command", "shell",
    "runtime", "memory", "thread", "async", "await", "promise", "factorial",
    "recursive", "recursion", "fibonacci", "sort", "binary", "tree", "graph"
]


def route_message(msg: str) -> str:
    msg_lower = msg.lower()
    if any(kw in msg_lower for kw in CODE_KEYWORDS):
        return "Mano"
    if "```" in msg or msg.count("`") >= 2:
        return "Mano"
    code_phrases = ["likh ke de", "likh do", "write a", "create a function", "make a program"]
    if any(phrase in msg_lower for phrase in code_phrases):
        return "Mano"
    return "Piko"


# ============ KEY ============
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
    config_data = MODELS[model_name]
    client = get_client(api_key)
    messages = [{"role": "system", "content": config_data["system_prompt"]}] + history
    stream = client.chat.completions.create(
        model=config_data["model_id"],
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
            reverse=True
        )
        st.session_state.current_chat_id = sorted_chats[0]["id"]
    else:
        chat_id, chat = new_chat()
        st.session_state.all_chats[chat_id] = chat
        st.session_state.current_chat_id = chat_id

groq_key = load_key()


# ============ SIDEBAR ============
with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand">Neuro<span class="x">x</span>a</div>',
        unsafe_allow_html=True
    )

    if st.button("+ New chat", use_container_width=True, type="primary"):
        chat_id, chat = new_chat()
        st.session_state.all_chats[chat_id] = chat
        st.session_state.current_chat_id = chat_id
        save_history(st.session_state.all_chats)
        st.rerun()

    st.markdown('<div class="sidebar-label">Chats</div>', unsafe_allow_html=True)

    sorted_chats = sorted(
        st.session_state.all_chats.values(),
        key=lambda c: c.get("created_at", ""),
        reverse=True
    )

    for chat in sorted_chats:
        is_current = chat["id"] == st.session_state.current_chat_id
        title = chat.get("title", "New chat")
        prefix = "› " if is_current else "  "
        if st.button(
            prefix + title,
            key=f"chat_{chat['id']}",
            use_container_width=True
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
                    reverse=True
                )
                st.session_state.current_chat_id = remaining[0]["id"]
            else:
                chat_id, chat = new_chat()
                st.session_state.all_chats[chat_id] = chat
                st.session_state.current_chat_id = chat_id
                save_history(st.session_state.all_chats)
            st.rerun()


# ============ HEADER ============
st.markdown(
    '<div class="neuroxa-header-wrap">'
    '<h1 class="neuroxa-header">Neuro<span class="x">x</span>a</h1>'
    '<p class="neuroxa-tagline">Two minds, one smart router.</p>'
    '</div>',
    unsafe_allow_html=True
)

current_chat = st.session_state.all_chats[st.session_state.current_chat_id]
messages = current_chat["messages"]


# ============ RENDER FUNCTIONS ============
def render_user_message(content: str):
    """User message - right aligned bubble, no avatar."""
    safe = content.replace("<", "&lt;").replace(">", "&gt;")
    st.markdown(
        f'<div class="user-bubble"><div class="user-bubble-inner">{safe}</div></div>',
        unsafe_allow_html=True
    )


def render_assistant_message(content: str, model: str):
    """Assistant message - avatar + markdown content, no bubble box."""
    cfg = MODELS[model]
    # Use columns for proper layout - avatar narrow, content wide
    col_av, col_content = st.columns([1, 20], gap="small")
    with col_av:
        st.markdown(
            f'<div class="assistant-avatar"><img src="{cfg["avatar"]}" alt=""></div>',
            unsafe_allow_html=True
        )
    with col_content:
        # Wrap markdown in styled container
        with st.container():
            st.markdown(f'<div class="assistant-content">', unsafe_allow_html=True)
            st.markdown(content)
            st.markdown('</div>', unsafe_allow_html=True)


# ============ EMPTY STATE ============
if not messages:
    st.markdown(
        '<div class="empty-state">'
        '<div class="empty-state-title">How can I <em>help</em> you today?</div>'
        '<p class="empty-state-desc">'
        'Coding question hai toh Mano sambhalega, general baat hai toh Piko. '
        'Auto-routing on hai.'
        '</p>'
        '</div>',
        unsafe_allow_html=True
    )

# ============ RENDER EXISTING ============
for msg in messages:
    if msg["role"] == "user":
        render_user_message(msg["content"])
    else:
        render_assistant_message(msg["content"], msg.get("model", "Piko"))


# ============ INPUT ============
if prompt := st.chat_input("Type your message..."):
    if not groq_key:
        st.error("Groq API key missing. Edit config.py and restart.")
        st.stop()

    user_msg = {"role": "user", "content": prompt}
    messages.append(user_msg)

    if current_chat["title"] == "New chat":
        current_chat["title"] = make_chat_title(prompt)

    render_user_message(prompt)

    model_name = route_message(prompt)
    cfg = MODELS[model_name]

    # Render avatar via columns, then stream content
    col_av, col_content = st.columns([1, 20], gap="small")
    with col_av:
        st.markdown(
            f'<div class="assistant-avatar"><img src="{cfg["avatar"]}" alt=""></div>',
            unsafe_allow_html=True
        )
    with col_content:
        st.markdown('<div class="assistant-content">', unsafe_allow_html=True)
        placeholder = st.empty()
        try:
            history_for_api = [
                {"role": m["role"], "content": m["content"]}
                for m in messages
            ]
            full_response = ""
            for token in stream_response(model_name, history_for_api, groq_key):
                full_response += token
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)

            messages.append({
                "role": "assistant",
                "content": full_response,
                "model": model_name
            })
            save_history(st.session_state.all_chats)

        except Exception as e:
            placeholder.error(f"Error: {str(e)}")
            messages.append({
                "role": "assistant",
                "content": f"Error: {str(e)}",
                "model": model_name
            })
            save_history(st.session_state.all_chats)
        st.markdown('</div>', unsafe_allow_html=True)