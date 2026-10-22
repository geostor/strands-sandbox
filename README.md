# FakeShell

A custom [Strands](https://strandsagents.com) sandbox.

## Run

```bash
uv venv .venv
uv pip install --python .venv 'strands-agents[otel,openai]'
export OPENAI_API_KEY="..."
.venv/bin/python demo.py
```

