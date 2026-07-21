# affiliate-assistant-bot

Support bot that answers questions **only** from a PDF knowledge base
([knowledge_base/affiliate_program_faq.pdf](knowledge_base/affiliate_program_faq.pdf)), using OpenAI's
vector store + `file_search` tool via the Responses API (the current, non-deprecated equivalent of the
old Assistants/Threads flow).

## Setup

```bash
cp .env.example .env   # then fill in OPENAI_API_KEY
uv sync
```

## Create / reuse the knowledge base

```bash
uv run python assistant_manager.py
```

First run uploads the PDF and creates a vector store, then writes its id back into `.env` as
`VECTOR_STORE_ID`. Every later run (including from the Streamlit app) reuses that same vector store
instead of re-uploading the file.

## Test in Streamlit

```bash
uv run streamlit run streamlit_app.py
```

## Files

- [config.py](config.py) — typed settings loaded from `.env` (`pydantic-settings`), including the
  strict system prompt that keeps answers scoped to the knowledge base.
- [assistant_manager.py](assistant_manager.py) — `SupportAssistant` class that creates the vector store
  once, uploads the PDF, and exposes `ask()` for sending a question through `file_search`.
- [templates.py](templates.py) — the system prompt used by `SupportAssistant`.
- [streamlit_app.py](streamlit_app.py) — chat UI for manual testing.
