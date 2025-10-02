---
name: Simple Test Agent
description: A simple agent for testing infrastructure
model: anthropic/claude-sonnet-4.5
temperature: 0.5
---

# Simple Test Agent

For testing purposes only.

<!-- System Prompt -->

```jinja2
You are a test agent. Respond concisely.
```

<!-- User Prompt -->

```jinja2
Query: {{ query }}
```

<!-- Output Schema -->

```python
from pydantic import BaseModel

class Output(BaseModel):
    result: str
```
