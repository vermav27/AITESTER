"""Core package — the deterministic engine behind the Test Plan Agent.

Layer map (B.L.A.S.T. / A.N.T. architecture, see ``llm.md``):

| Layer | Module | Determinism |
|---|---|---|
| L3 Tools | ``config_manager``, ``jira_client``, ``normalize``, ``checklist``, ``render``, ``ollama_client`` | fully deterministic |
| L1 Agent | ``agent`` | non-deterministic (LLM reasoning) |
| L2 Navigation | ``navigation`` | deterministic ordering + gate enforcement |

The Flask app in ``app/`` is a thin presentation layer over ``navigation.run``.
"""
