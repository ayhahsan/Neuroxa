# Neuroxa - A Dual-Model AI Assistant

**Neuroxa** is the brand. It runs on two specialised models with a smart router deciding who answers what:

| Model | Role | Engine | Provider |
|-------|------|--------|----------|
| **Piko** | General chat & friendly conversation | Llama 3.3 70B | Groq |
| **Mano** | Coding, debugging & engineering | DeepSeek R1 | OpenRouter |

Like Anthropic has Claude with Opus / Sonnet / Haiku, Neuroxa has Piko and Mano.

---

## Files in this project

```
neuroxa/
  app.py            Main Streamlit application
  config.py         Your API keys go here (DO NOT share)
  index.html        Marketing landing page
  piko.svg          Piko mascot illustration
  mano.svg          Mano mascot illustration
  requirements.txt  Python dependencies
  .gitignore        Protects keys from being uploaded to GitHub
  README.md         This file
```

---

## Setup (5 minutes)

### 1. Install dependencies

```bash
cd neuroxa
pip install -r requirements.txt
```

### 2. Get free API keys

**Groq** (powers Piko):
1. Visit https://console.groq.com
2. Sign up (Google login works)
3. Go to "API Keys" and create a new key
4. Key starts with `gsk_...`

**OpenRouter** (powers Mano):
1. Visit https://openrouter.ai
2. Sign up
3. Settings -> Keys -> Create Key
4. Key starts with `sk-or-v1-...`

### 3. Add keys to config.py

Open `config.py` in any text editor (Notepad, VS Code, etc.) and replace the placeholder values:

```python
GROQ_API_KEY = "gsk_your_actual_groq_key_here"
OPENROUTER_API_KEY = "sk-or-v1-your_actual_openrouter_key_here"
```

Save the file. **The quotes around the key are important - keep them.**

### 4. Run the app

```bash
streamlit run app.py
```

Browser opens at `http://localhost:8501`. Sidebar will show "Keys loaded from config.py" - you can chat directly without entering anything.

---

## Security: Never share config.py

Your `config.py` contains real API keys. Anyone who has these keys can use your free quota.

The included `.gitignore` already excludes `config.py` from git, so if you push this project to GitHub, your keys stay safe.

If you ever share the project (zip, GitHub, etc.), make sure to **remove your keys from config.py first** or replace them with placeholders.

---

## How Neuroxa Works

```
User types in Neuroxa
        |
        v
Router checks for code keywords
        |
        +-- coding signal? --+
        |                    |
        v                    v
    Piko (chat)          Mano (code)
    via Groq             via OpenRouter
        |                    |
        +--------+-----------+
                 v
         Streaming response
         badged with model name
```

Routing logic lives in `app.py` - see `CODE_KEYWORDS` and `route_message()`.

---

## Deploy on Streamlit Cloud (free)

For deploying to a live URL:

1. Push the code to a **private** GitHub repo (or remove keys from config.py before pushing)
2. Go to https://share.streamlit.io
3. New app -> select your repo -> choose `app.py`
4. In the deployed app's "Secrets" panel, paste:
   ```
   GROQ_API_KEY = "your_key"
   OPENROUTER_API_KEY = "your_key"
   ```

App will use these automatically (config.py first, secrets.toml fallback).

---

## Tech Stack

| Component       | Tech                           |
|-----------------|--------------------------------|
| App UI          | Streamlit                      |
| Landing page    | Plain HTML/CSS                 |
| API SDK         | OpenAI Python (compatible)     |
| Piko engine     | Llama 3.3 70B (Groq)           |
| Mano engine     | DeepSeek R1 (OpenRouter)       |
| Hosting         | Streamlit Cloud (free)         |

---

## Free Tier Limits

- **Groq**: daily request limits, generous for demos
- **OpenRouter**: free models have rate limits (~20 requests/minute, ~50/day shared across free models)
- For production traffic, paid keys recommended

---

## Customisation Ideas

- More models: Gemini, Mistral, Qwen via OpenRouter
- Specialised models: designer, translator, summariser
- Persistent chat history (SQLite/JSON)
- Export chat to PDF
- Voice input (`streamlit-mic-recorder`)
- File uploads (PDFs, code)
- Use mascots as chat avatars

---

Built for freelancing demos and client projects.