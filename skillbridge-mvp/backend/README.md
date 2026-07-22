# SkillBridge Backend

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the API:

```bash
python run.py
```

LLM scoring (optional)
----------------------

To enable LLM-based assessment scoring set an API key in your environment:

- `OPENAI_API_KEY` or `LLM_API_KEY` — API key for an OpenAI-compatible provider
- `LLM_MODEL` — optional model id (default `gpt-3.5-turbo`)

When set, the backend will call the provider to compute a score and level; if the call fails, the system falls back to the deterministic rule-based scorer.
